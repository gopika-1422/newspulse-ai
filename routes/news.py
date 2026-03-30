"""
routes/news.py — GET /api/news?q=<topic>
"""
from fastapi import APIRouter, Query, HTTPException
import httpx

from services.news_service import fetch_news
from models.schemas import NewsResponse

router = APIRouter()


@router.get(
    "/news",
    response_model=NewsResponse,
    summary="Fetch & summarise news articles",
)
async def get_news(
    q: str = Query(
        ...,
        min_length=1,
        max_length=200,
        description="Topic to search, e.g. 'Puducherry election' or 'AI'",
    ),
):
    """
    Fetch the latest news for the given topic (last 7 days),
    summarise each article with Google Gemini, and return structured JSON.
    """
    try:
        return await fetch_news(q.strip())

    except httpx.HTTPStatusError as exc:
        code = exc.response.status_code
        if code == 401:
            raise HTTPException(
                status_code=502,
                detail="News API key is invalid. Check your .env file.",
            )
        if code == 429:
            raise HTTPException(
                status_code=502,
                detail="News API rate limit reached. Please wait and try again.",
            )
        raise HTTPException(status_code=502, detail=f"News API returned HTTP {code}.")

    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=503,
            detail=f"Could not connect to news API: {exc}",
        )

    except ValueError as exc:
        raise HTTPException(status_code=502, detail=str(exc))

    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
