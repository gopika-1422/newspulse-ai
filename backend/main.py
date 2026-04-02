"""
main.py — FastAPI entry point
Run:  cd backend && uvicorn main:app --reload --port 8000
"""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from routes.news import router as news_router
from config import GUARDIAN_API_KEY, NEWSAPI_KEY, GEMINI_API_KEY

print("\n" + "="*58)
print("  NewsPulse AI — India Edition  v3.1")
print("="*58)
print(f"  Gemini AI     : {'✅ Ready' if GEMINI_API_KEY else '❌ MISSING — add GEMINI_API_KEY to .env'}")
print(f"  Guardian API  : {'✅ Ready' if GUARDIAN_API_KEY else '⚠️  Not set (optional)'}")
print(f"  NewsAPI       : {'✅ Ready' if NEWSAPI_KEY else '⚠️  Not set (optional)'}")
print(f"  Google RSS    : ✅ Always active — no key needed")
print(f"  Indian RSS    : ✅ Always active — The Hindu, NDTV, TOI")
print("="*58)

if not GEMINI_API_KEY:
    print("\n  ‼️  GEMINI_API_KEY is required for AI summaries!")
    print("  Get it free: https://aistudio.google.com/app/apikey")
    print("  Save it in:  backend\\.env\n")

app = FastAPI(
    title="NewsPulse AI",
    description="Regional Indian & global news summarised by Google Gemini 2.0 Flash",
    version="3.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

app.include_router(news_router, prefix="/api")

FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))
if os.path.isdir(FRONTEND_DIR):
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

    @app.get("/", include_in_schema=False)
    async def serve_frontend():
        return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))
