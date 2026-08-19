"""AI API router — Gemini-powered market intelligence endpoints."""

from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

from app.services.ai_analyzer import (
    analyze_article,
    generate_market_brief,
    ask_market_question,
)
from app.services.market_data import fetch_all_quotes
from app.services.news_fetcher import fetch_news, fetch_article

router = APIRouter(prefix="/api/ai", tags=["ai"])


class AskRequest(BaseModel):
    question: str


@router.get("/market-brief")
async def market_brief():
    """Generate AI-powered daily market brief."""
    quotes = await fetch_all_quotes()
    news = await fetch_news(limit=10)
    headlines = [a["headline"] for a in news]

    brief = await generate_market_brief(quotes, headlines)
    return {"brief": brief, "generated": True}


@router.get("/analyze/{article_id}")
async def analyze_single_article(article_id: str):
    """On-demand AI analysis of a specific article."""
    article = await fetch_article(article_id)
    if not article:
        return {"error": "Article not found"}, 404

    analysis = await analyze_article(
        article.get("headline", ""),
        article.get("body", article.get("summary", "")),
    )
    return {"article_id": article_id, "analysis": analysis}


@router.post("/ask")
async def ask_ai(request: AskRequest):
    """Ask AI any market question with live context."""
    quotes = await fetch_all_quotes()
    result = await ask_market_question(request.question, quotes)
    return result
