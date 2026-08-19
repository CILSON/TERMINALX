"""News API router."""

from __future__ import annotations

from fastapi import APIRouter, Query

from app.services.news_fetcher import fetch_news, fetch_article, search_news
from app.services.ai_analyzer import analyze_article

router = APIRouter(prefix="/api/news", tags=["news"])


@router.get("/search")
async def search(q: str = Query(..., min_length=1), limit: int = Query(20, le=100)):
    """Full-text search across news articles."""
    results = await search_news(q, limit=limit)
    return {"results": results, "query": q, "count": len(results)}


@router.get("")
async def list_news(
    category: str | None = Query(None),
    limit: int = Query(20, le=100),
    offset: int = Query(0, ge=0),
):
    """Return paginated news, optionally filtered by category."""
    articles = await fetch_news(category=category, limit=limit, offset=offset)
    return {"articles": articles, "count": len(articles), "offset": offset}


@router.get("/{article_id}")
async def get_article_endpoint(article_id: str):
    """Return a single article with Gemini AI analysis."""
    article = await fetch_article(article_id)
    if not article:
        return {"error": "Article not found"}, 404

    # Run Gemini analysis on-demand for this article
    ai = await analyze_article(
        article.get("headline", ""),
        article.get("body", article.get("summary", "")),
    )
    article["ai_analysis"] = ai
    return article

