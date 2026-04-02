# 📰 NewsPulse AI — India Edition

<div align="center">

![NewsPulse AI Banner](https://img.shields.io/badge/NewsPulse-AI%20Powered-blueviolet?style=for-the-badge&logo=google&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-green?style=for-the-badge&logo=fastapi&logoColor=white)
![Gemini](https://img.shields.io/badge/Gemini-2.0%20Flash-orange?style=for-the-badge&logo=google&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)

**Real-time news summarizer powered by Google Gemini 2.0 Flash**
Built for Indian regional news — Puducherry, Tamil Nadu, Kerala, and 30+ regions

[🚀 Features](#-features) • [📦 Installation](#-installation) • [🔑 API Keys](#-api-keys) • [▶️ Running](#️-running-the-app) • [📁 Project Structure](#-project-structure)

</div>

---

## 📸 Preview

```
🔍 Search: "Tamil Nadu Election"
   ↓
🌐 Fetches from Guardian + NewsAPI + Google RSS + Indian RSS
   ↓
🤖 Gemini 2.0 Flash summarises each article in 3–5 sentences
   ↓
🃏 Displays clean cards with title, summary, source & date
```

---

## ✨ Features

| Feature | Details |
|---------|---------|
| 🤖 **AI Summaries** | Google Gemini 2.0 Flash — 3–5 factual sentences per article |
| 🇮🇳 **Indian Regional** | Covers Puducherry, Tamil Nadu, Kerala, Karnataka, Delhi & 30+ regions |
| 📡 **4-Layer Fallback** | Guardian → NewsAPI → Google RSS → Indian RSS (works even with no API keys) |
| ⚡ **Async** | All articles summarised concurrently — fast results |
| 🗄️ **Caching** | 10-minute TTL cache per query — avoids redundant API calls |
| 🔍 **Smart Queries** | Auto-expands regional queries (e.g. "Puducherry" → searches Pondicherry too) |
| 📄 **Pagination** | Shows 5 cards, "Load More" for the rest |
| 🌙 **Dark UI** | Clean editorial dark theme — no build step needed |
| 🛡️ **Error Handling** | Graceful fallback on API failure, quota limits, network errors |

---

## 📦 Installation

### Prerequisites
- Python **3.10+** → https://python.org/downloads
- Git → https://git-scm.com/downloads

### Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/newspulse-ai.git
cd newspulse-ai
```

### Install dependencies
```bash
pip install -r requirements.txt
```

---

## 🔑 API Keys

All keys are **free**. You need at least **GEMINI_API_KEY** to get AI summaries.
The app still fetches news via RSS even without Guardian/NewsAPI keys.

### 1. Google Gemini API Key ✅ Required

| Step | Action |
|------|--------|
| 1 | Go to **https://aistudio.google.com/app/apikey** |
| 2 | Sign in with Google |
| 3 | Click **"Create API Key"** |
| 4 | Copy the key — starts with `AIzaSy...` |

> Free tier — no billing needed. Model: `gemini-2.0-flash`

---

### 2. The Guardian API Key ⭐ Recommended

| Step | Action |
|------|--------|
| 1 | Go to **https://open-platform.theguardian.com/access/** |
| 2 | Click **"Register developer key"** |
| 3 | Fill the form — key arrives by email in minutes |

> Free — unlimited requests. Best India/South Asia coverage.

---

### 3. NewsAPI Key 🔄 Optional Fallback

| Step | Action |
|------|--------|
| 1 | Go to **https://newsapi.org/register** |
| 2 | Sign up — key shown instantly |

> Free — 100 requests/day.

---

### Create your `.env` file

```bash
# macOS / Linux
cp backend/.env.example backend/.env

# Windows PowerShell
Copy-Item backend\.env.example backend\.env
```

Edit `backend/.env`:
```env
GUARDIAN_API_KEY=your_guardian_key_here
NEWSAPI_KEY=your_newsapi_key_here
GEMINI_API_KEY=AIzaSy_your_gemini_key_here
```

> ⚠️ The `.env` file must be inside the `backend/` folder
> ⚠️ Never commit `.env` to GitHub — it's already in `.gitignore`

---

## ▶️ Running the App

```bash
cd backend
uvicorn main:app --reload --port 8000
```

You should see:
```
========================================================
  NewsPulse AI — India Edition  v3.1
========================================================
  Gemini AI     : ✅ Ready
  Guardian API  : ✅ Ready
  NewsAPI       : ✅ Ready
  Google RSS    : ✅ Always active — no key needed
  Indian RSS    : ✅ Always active — The Hindu, NDTV, TOI
========================================================
```

Open your browser → **http://localhost:8000** ✅

### Windows PowerShell (all steps)
```powershell
pip install -r requirements.txt
Copy-Item backend\.env.example backend\.env
notepad backend\.env
cd backend
python -m uvicorn main:app --reload --port 8000
```

---

## 📁 Project Structure

```
newspulse-ai/
│
├── 📄 requirements.txt          # Python dependencies
├── 📄 README.md                 # This file
│
├── 🖥️ frontend/
│   └── index.html               # Complete UI — dark editorial theme
│
└── ⚙️ backend/
    ├── main.py                  # FastAPI app entry point
    ├── config.py                # Settings loaded from .env
    ├── .env.example             # Template — copy → rename → fill keys
    │
    ├── 📂 routes/
    │   └── news.py              # GET /api/news?q=topic
    │
    ├── 📂 models/
    │   └── schemas.py           # Pydantic response models
    │
    └── 📂 services/
        ├── ai_service.py        # Gemini 2.0 Flash summarisation
        ├── news_service.py      # 4-layer news fetcher + orchestration
        ├── rss_service.py       # RSS fallback (Google News + Indian feeds)
        └── query_builder.py     # Indian regional query expansion
```

---

## 🌏 How Regional Search Works

The `query_builder.py` automatically expands Indian regional queries:

| You type | Expanded query sent to APIs |
|----------|-----------------------------|
| `Puducherry` | `("Puducherry" OR "Pondicherry" OR "Puducherry UT") India` |
| `Tamil Nadu election` | `("Tamil Nadu" OR "Chennai" OR "TN politics") election India` |
| `Kerala politics` | `("Kerala" OR "Thiruvananthapuram" OR "Kochi") politics India` |
| `Chennai startup` | `("Chennai" OR "Tamil Nadu") startup India` |
| `cricket` | `cricket` ← global topic, no change |

**Covered regions:** Tamil Nadu · Puducherry · Kerala · Karnataka · Andhra Pradesh · Telangana · Delhi · Mumbai · Maharashtra · UP · Bihar · Rajasthan · Gujarat · Punjab · West Bengal · Assam · Manipur · and 15+ more cities

---

## 🔄 4-Layer News Fallback

```
Query received
     │
     ▼
┌─────────────────────────┐
│  Layer 1: The Guardian  │ ← Best quality, strong India coverage
│  (needs GUARDIAN key)   │
└──────────┬──────────────┘
           │ < 3 results?
           ▼
┌─────────────────────────┐
│  Layer 2: NewsAPI.org   │ ← Broad English news
│  (needs NEWSAPI key)    │
└──────────┬──────────────┘
           │ < 3 results?
           ▼
┌─────────────────────────┐
│  Layer 3: Google RSS    │ ← ✅ NO KEY NEEDED — always works
│  news.google.com/rss    │
└──────────┬──────────────┘
           │ < 3 results + India query?
           ▼
┌─────────────────────────┐
│  Layer 4: Indian RSS    │ ← ✅ NO KEY NEEDED
│  Hindu · NDTV · TOI     │
└─────────────────────────┘
```

---

## 🧪 API Testing

```bash
# Test any topic
curl "http://localhost:8000/api/news?q=cricket"
curl "http://localhost:8000/api/news?q=Puducherry"
curl "http://localhost:8000/api/news?q=Tamil+Nadu+election"
```

Sample JSON response:
```json
{
  "query": "cricket",
  "total": 8,
  "results": [
    {
      "title": "India beats Australia in final over thriller",
      "summary": "India defeated Australia in a nail-biting match...",
      "url": "https://...",
      "source": "The Guardian",
      "published_at": "2026-03-31T10:00:00Z",
      "image": "https://..."
    }
  ]
}
```

Interactive API docs → **http://localhost:8000/docs**

---

## ❗ Troubleshooting

| Problem | Fix |
|---------|-----|
| `No articles found` | Keys not set — app still uses RSS fallback automatically |
| `WARNING — Missing env variables` | `.env` file not in `backend/` folder or not saved correctly |
| `pip not found` | Use `pip3` instead of `pip` |
| `ModuleNotFoundError` | Run `pip install -r requirements.txt` from project root |
| Port already in use | Change `--port 8000` to `--port 8001`, visit `localhost:8001` |
| `.env` saved as `.env.txt` | In Notepad → Save As → "All Files" → type `.env` |
| Summaries show raw HTML | Update to latest ZIP — HTML stripping is already fixed |

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Python 3.10+ · FastAPI · Uvicorn |
| **AI** | Google Gemini 2.0 Flash (google-generativeai) |
| **News APIs** | The Guardian · NewsAPI.org |
| **RSS Fallback** | feedparser · Google News RSS · The Hindu · NDTV · TOI |
| **HTTP Client** | httpx (async) |
| **Caching** | cachetools TTLCache |
| **Frontend** | HTML + CSS + Vanilla JS (no build step) |
| **Fonts** | Playfair Display · DM Sans (Google Fonts) |

---

## 🚀 Deployment (optional)

To deploy on **Railway** (free):
1. Push code to GitHub
2. Go to → https://railway.app → New Project → Deploy from GitHub
3. Add environment variables (your API keys) in Railway dashboard
4. Set start command: `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT`

---

## 📜 License

MIT License — free to use, modify, and distribute.

---

## 🙏 Credits

- **Google Gemini** — AI summarisation
- **The Guardian Open Platform** — Primary news source
- **NewsAPI.org** — News fallback
- **Google News RSS** — Always-available fallback

---

<div align="center">

Built with ❤️ using FastAPI + Google Gemini · Made for India 🇮🇳

</div>
