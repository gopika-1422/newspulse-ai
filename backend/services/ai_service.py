"""
services/ai_service.py — Google Gemini 2.0 Flash summarisation service

Key behaviours:
  - Strips HTML tags and junk before sending to Gemini
  - Correct model: gemini-2.0-flash
  - On failure: returns clean plain-text fallback (no HTML, no ugly error prefix)
  - Prints real error to terminal for easy debugging
"""
import re
import asyncio
import google.generativeai as genai
from config import GEMINI_API_KEY, GEMINI_MODEL

# Initialise Gemini client once
genai.configure(api_key=GEMINI_API_KEY)

_model = genai.GenerativeModel(
    model_name=GEMINI_MODEL,
    system_instruction=(
        "You are a professional news editor. "
        "Summarise news articles accurately and concisely in plain English. "
        "Never add information that is not in the original article. "
        "Never guess or hallucinate facts."
    ),
    generation_config=genai.GenerationConfig(
        max_output_tokens=300,
        temperature=0.3,      # low temperature = factual, consistent output
    ),
)

# ── Text cleaning regexes ─────────────────────────────────────────────────────
_RE_HTML       = re.compile(r"<[^>]+>")              # <any tag>
_RE_TRUNCATION = re.compile(r"\[\+\d+ chars?\]")     # NewsAPI "[+1234 chars]"
_RE_SPACES     = re.compile(r"\s{2,}")               # multiple whitespace


def _clean(raw: str) -> str:
    """
    Remove HTML tags, truncation markers, and collapse whitespace.
    Prevents <ul><li>...</li></ul> junk from reaching Gemini or the UI.
    """
    if not raw:
        return ""
    text = _RE_HTML.sub(" ", raw)
    text = _RE_TRUNCATION.sub("", text)
    text = _RE_SPACES.sub(" ", text)
    return text.strip()


# ── Prompt ────────────────────────────────────────────────────────────────────

def _prompt(title: str, content: str) -> str:
    return (
        f"Article Title: {title}\n\n"
        f"Article Content:\n{content}\n\n"
        "Write a summary of this news article in 3 to 5 clear, simple sentences. "
        "Only use facts from the article above. "
        "Do NOT add opinions, speculation, or any extra information."
    )


# ── Main summariser ───────────────────────────────────────────────────────────

async def summarise_article(title: str, content: str) -> str:
    """
    Clean content → send to Gemini → return 3-5 sentence summary.
    The blocking Gemini SDK call runs in a thread-pool executor so it
    does not block FastAPI's async event loop.
    """
    clean_content = _clean(content)

    # Not enough content to summarise → return clean snippet directly
    if not clean_content or len(clean_content) < 40:
        return clean_content[:300] or "No content available for summarisation."

    try:
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: _model.generate_content(_prompt(title, clean_content[:3000])),
        )
        return response.text.strip()

    except Exception as exc:
        # Print the REAL error to your terminal so you can diagnose it
        print(f"[ai_service] Gemini error — '{title[:55]}': {type(exc).__name__}: {exc}")
        # Return clean plain-text fallback — readable, no HTML, no error prefix
        snippet = clean_content[:350]
        return snippet + ("…" if len(clean_content) > 350 else "")
