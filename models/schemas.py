"""
models/schemas.py — Pydantic response models
"""
from pydantic import BaseModel
from typing import List, Optional


class ArticleResult(BaseModel):
    title: str
    summary: str
    url: str
    source: str
    published_at: Optional[str] = None
    image: Optional[str] = None


class NewsResponse(BaseModel):
    query: str
    total: int
    results: List[ArticleResult]
