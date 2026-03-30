"""
services/rss_service.py
RSS feed fetcher — works with ZERO API keys.
Covers Google News RSS (global + India), Hindu, NDTV, Times of India.
Used as guaranteed fallback when Guardian/NewsAPI return nothing.
"""
import asyncio
import re
import feedparser
from datetime import datetime, timezone
from models.schemas import ArticleResult
from services.ai_service import summarise_article

# ── RSS Feed registry ─────────────────────────────────────────────────────────
# Google News RSS supports any search query — no key needed
GNEWS_RSS = "https://news.google.com/rss/search?q={query}&hl=en-IN&gl=IN&ceid=IN:en"

# Static Indian news feeds (always available)
STATIC_INDIA_FEEDS = [
    ("The Hindu",        "https://www.thehindu.com/news/national/feeder/default.rss"),
    ("NDTV",            "https://feeds.feedburner.com/ndtvnews-india-news"),
    ("Times of India",  "https://timesofindia.indiatimes.com/rssfeeds/296589292.cms"),
    ("India Today",     "https://www.indiatoday.in/rss/1206514"),
]

# ── Helpers ───────────────────────────────────────────────────────────────────
_RE_HTML    = re.compile(r"<[^>]+>")
_RE_SPACES  = re.compile(r"\s{2,}")


def _strip(text: str) -> str:
    if not text:
        return ""
    text = _RE_HTML.sub(" ", text)
    text = _RE_SPACES.sub(" ", text)
    return text.strip()


def _parse_date(entry) -> str | None:
    """Try to extract a publish date from a feed entry."""
    try:
        t = entry.get("published_parsed") or entry.get("updated_parsed")
        if t:
            return datetime(*t[:6], tzinfo=timezone.utc).isoformat()
    except Exception:
        pass
    return None


def _entry_to_dict(entry, source_name: str) -> dict:
    content = ""
    if hasattr(entry, "content"):
        content = _strip(entry.content[0].get("value", ""))
    if not content:
        content = _strip(entry.get("summary", ""))
    return {
        "title":   _strip(entry.get("title", "No title")),
        "url":     entry.get("link", "#"),
        "source":  source_name,
        "date":    _parse_date(entry),
        "content": content,
        "image":   None,
    }


# ── Fetchers ──────────────────────────────────────────────────────────────────

def _fetch_feed_sync(url: str, source: str, limit: int = 5) -> list[dict]:
    """Synchronous feedparser call — will be run in executor."""
    try:
        feed = feedparser.parse(url)
        results = []
        for entry in feed.entries[:limit]:
            d = _entry_to_dict(entry, source)
            if d["title"] and d["url"] != "#":
                results.append(d)
        return results
    except Exception as exc:
        print(f"[rss_service] Feed error ({source}): {exc}")
        return []


async def fetch_rss_by_query(query: str, limit: int = 10) -> list[ArticleResult]:
    """
    Fetch articles via Google News RSS for any query.
    No API key required.
    """
    url = GNEWS_RSS.format(query=query.replace(" ", "+"))
    loop = asyncio.get_event_loop()

    raw = await loop.run_in_executor(
        None, lambda: _fetch_feed_sync(url, "Google News", limit)
    )

    if not raw:
        return []

    summaries = await asyncio.gather(*[
        summarise_article(title=a["title"], content=a["content"])
        for a in raw
    ])

    return [
        ArticleResult(
            title=a["title"],
            summary=summaries[i],
            url=a["url"],
            source=a["source"],
            published_at=a["date"],
            image=a["image"],
        )
        for i, a in enumerate(raw)
    ]


async def fetch_india_rss(limit_per_feed: int = 3) -> list[ArticleResult]:
    """
    Fetch from multiple static Indian RSS feeds concurrently.
    Used when query is India-related and other sources fail.
    """
    loop = asyncio.get_event_loop()

    raw_lists = await asyncio.gather(*[
        loop.run_in_executor(
            None,
            lambda url=url, name=name: _fetch_feed_sync(url, name, limit_per_feed)
        )
        for name, url in STATIC_INDIA_FEEDS
    ])

    all_articles: list[dict] = []
    for lst in raw_lists:
        all_articles.extend(lst)

    if not all_articles:
        return []

    summaries = await asyncio.gather(*[
        summarise_article(title=a["title"], content=a["content"])
        for a in all_articles
    ])

    return [
        ArticleResult(
            title=a["title"],
            summary=summaries[i],
            url=a["url"],
            source=a["source"],
            published_at=a["date"],
            image=a["image"],
        )
        for i, a in enumerate(all_articles)
    ]
