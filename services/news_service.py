"""
services/news_service.py — 4-layer news fetcher

Layer 1: The Guardian API      (if GUARDIAN_API_KEY set)
Layer 2: NewsAPI.org           (if NEWSAPI_KEY set AND < 3 results)
Layer 3: Google News RSS       ← NO KEY NEEDED, always runs if < 3 results
Layer 4: Static Indian RSS     ← NO KEY NEEDED, for India topics only
"""
import re
import asyncio
import httpx
from datetime import datetime, timedelta, timezone
from cachetools import TTLCache

from config import (
    GUARDIAN_API_KEY, GUARDIAN_BASE_URL,
    NEWSAPI_KEY, NEWSAPI_BASE_URL,
    MAX_ARTICLES, CACHE_TTL_SECONDS,
)
from services.ai_service import summarise_article
from services.query_builder import expand_query, is_india_query
from services.rss_service import fetch_rss_by_query, fetch_india_rss
from models.schemas import ArticleResult, NewsResponse

_cache: TTLCache = TTLCache(maxsize=128, ttl=CACHE_TTL_SECONDS)

_RE_HTML     = re.compile(r"<[^>]+>")
_RE_TRUNCATE = re.compile(r"\[\+\d+ chars?\]")
_RE_SPACES   = re.compile(r"\s{2,}")


def _clean(text: str) -> str:
    if not text:
        return ""
    text = _RE_HTML.sub(" ", text)
    text = _RE_TRUNCATE.sub("", text)
    text = _RE_SPACES.sub(" ", text)
    return text.strip()


def _days_ago_iso(days: int) -> str:
    dt = datetime.now(timezone.utc) - timedelta(days=days)
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


# ── Guardian ──────────────────────────────────────────────────────────────────
async def _fetch_guardian(query: str, expanded: str, client: httpx.AsyncClient) -> list[ArticleResult]:
    if not GUARDIAN_API_KEY:
        print("[news_service] Layer 1 (Guardian) skipped — no key")
        return []
    params = {
        "q": expanded, "lang": "en", "page-size": MAX_ARTICLES,
        "from-date": _days_ago_iso(7)[:10], "order-by": "relevance",
        "show-fields": "headline,bodyText,thumbnail,trailText",
        "api-key": GUARDIAN_API_KEY,
    }
    try:
        resp = await client.get(GUARDIAN_BASE_URL, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()
    except Exception as exc:
        print(f"[news_service] Layer 1 (Guardian) error: {exc}")
        return []
    raw = data.get("response", {}).get("results", [])
    print(f"[news_service] Layer 1 (Guardian) → {len(raw)} results")
    if not raw:
        return []
    summaries = await asyncio.gather(*[
        summarise_article(
            title=a.get("fields", {}).get("headline") or a.get("webTitle", ""),
            content=_clean(a.get("fields", {}).get("bodyText") or a.get("fields", {}).get("trailText") or ""),
        ) for a in raw
    ])
    return [
        ArticleResult(
            title=a.get("fields", {}).get("headline") or a.get("webTitle", "No title"),
            summary=summaries[i], url=a.get("webUrl", "#"),
            source="The Guardian", published_at=a.get("webPublicationDate"),
            image=a.get("fields", {}).get("thumbnail"),
        ) for i, a in enumerate(raw)
    ]


# ── NewsAPI ───────────────────────────────────────────────────────────────────
async def _fetch_newsapi(query: str, expanded: str, client: httpx.AsyncClient) -> list[ArticleResult]:
    if not NEWSAPI_KEY:
        print("[news_service] Layer 2 (NewsAPI) skipped — no key")
        return []
    days = 30 if is_india_query(query) else 7
    params = {
        "q": expanded, "language": "en", "pageSize": MAX_ARTICLES,
        "from": _days_ago_iso(days), "sortBy": "relevancy", "apiKey": NEWSAPI_KEY,
    }
    try:
        resp = await client.get(NEWSAPI_BASE_URL, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()
    except Exception as exc:
        print(f"[news_service] Layer 2 (NewsAPI) error: {exc}")
        return []
    if data.get("status") != "ok":
        print(f"[news_service] Layer 2 (NewsAPI) error msg: {data.get('message')}")
        return []
    raw = [
        a for a in data.get("articles", [])
        if a.get("title") and a["title"] != "[Removed]"
        and a.get("url") not in (None, "", "https://removed.com")
    ]
    print(f"[news_service] Layer 2 (NewsAPI) → {len(raw)} results")
    if not raw:
        return []
    texts = [_clean(a.get("content") or "") or _clean(a.get("description") or "") for a in raw]
    summaries = await asyncio.gather(*[
        summarise_article(title=raw[i].get("title", ""), content=texts[i])
        for i in range(len(raw))
    ])
    return [
        ArticleResult(
            title=a.get("title", "No title"), summary=summaries[i],
            url=a.get("url", "#"), source=a.get("source", {}).get("name", "Unknown"),
            published_at=a.get("publishedAt"), image=a.get("urlToImage"),
        ) for i, a in enumerate(raw)
    ]


# ── Dedup ─────────────────────────────────────────────────────────────────────
def _dedup(articles: list[ArticleResult]) -> list[ArticleResult]:
    seen_urls: set[str] = set()
    seen_titles: set[str] = set()
    out = []
    for a in articles:
        uk = a.url.strip().lower()
        tk = a.title.strip().lower()[:60]
        if uk in seen_urls or tk in seen_titles:
            continue
        seen_urls.add(uk)
        seen_titles.add(tk)
        out.append(a)
    return out


# ── Main ─────────────────────────────────────────────────────────────────────
async def fetch_news(query: str) -> NewsResponse:
    cache_key = query.strip().lower()
    if cache_key in _cache:
        print(f"[news_service] Cache hit: '{query}'")
        return _cache[cache_key]

    expanded = expand_query(query)
    print(f"\n[news_service] ── Starting fetch ──")
    print(f"[news_service] Query    : '{query}'")
    print(f"[news_service] Expanded : '{expanded}'")

    combined: list[ArticleResult] = []

    # Layer 1 + 2 via HTTP APIs
    async with httpx.AsyncClient() as client:
        guardian = await _fetch_guardian(query, expanded, client)
        combined = _dedup(guardian)

        if len(combined) < 3:
            newsapi = await _fetch_newsapi(query, expanded, client)
            combined = _dedup(combined + newsapi)

    # Layer 3: Google News RSS — always available, no key needed
    if len(combined) < 3:
        print(f"[news_service] Layer 3 (Google News RSS) — fetching…")
        try:
            rss = await fetch_rss_by_query(expanded, limit=MAX_ARTICLES)
            print(f"[news_service] Layer 3 (Google News RSS) → {len(rss)} results")
            combined = _dedup(combined + rss)
        except Exception as exc:
            print(f"[news_service] Layer 3 error: {exc}")

    # Layer 4: Static Indian RSS — no key needed, India queries only
    if len(combined) < 3 and is_india_query(query):
        print(f"[news_service] Layer 4 (Indian RSS feeds) — fetching…")
        try:
            india_rss = await fetch_india_rss(limit_per_feed=3)
            print(f"[news_service] Layer 4 (Indian RSS) → {len(india_rss)} results")
            combined = _dedup(combined + india_rss)
        except Exception as exc:
            print(f"[news_service] Layer 4 error: {exc}")

    combined = combined[:MAX_ARTICLES]
    print(f"[news_service] ── Final: {len(combined)} articles ──\n")

    response = NewsResponse(query=query, total=len(combined), results=combined)
    _cache[cache_key] = response
    return response
