"""
config.py — All settings loaded from backend/.env
"""
import os
from dotenv import load_dotenv

load_dotenv()

# ── News sources ───────────────────────────────────────────────
# Primary: The Guardian (best India/regional coverage, free)
GUARDIAN_API_KEY: str  = os.getenv("GUARDIAN_API_KEY", "")
GUARDIAN_BASE_URL: str = "https://content.guardianapis.com/search"

# Fallback: NewsAPI.org (used when Guardian returns < 3 results)
NEWSAPI_KEY: str       = os.getenv("NEWSAPI_KEY", "")
NEWSAPI_BASE_URL: str  = "https://newsapi.org/v2/everything"

# ── AI summarisation ───────────────────────────────────────────
GEMINI_API_KEY: str    = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL: str      = "gemini-2.0-flash"   # correct current model name

# ── App settings ───────────────────────────────────────────────
MAX_ARTICLES: int      = 10
CACHE_TTL_SECONDS: int = 600   # 10-minute in-memory cache per query
