"""Event scoring engine — scores news events by importance and market impact."""

from __future__ import annotations

from typing import Any

from app.services.ai_analyzer import analyze_article


async def score_event(headline: str, body: str = "") -> dict[str, Any]:
    """Score a news event for importance and market impact.

    Returns dict with: importance (0-100), market_impact (0-100),
    affected_assets, sentiment.
    """
    analysis = await analyze_article(headline, body)

    # Derive importance from confidence and number of affected assets
    confidence = analysis.get("confidence", 0.5)
    n_assets = len(analysis.get("affected_assets", []))
    importance = min(100, int(confidence * 80 + n_assets * 5))

    # Market impact based on bullish/bearish strength
    n_bull = len(analysis.get("bullish_for", []))
    n_bear = len(analysis.get("bearish_for", []))
    market_impact = min(100, int((n_bull + n_bear) * 15 + confidence * 30))

    sentiment = "neutral"
    if n_bull > n_bear:
        sentiment = "bullish"
    elif n_bear > n_bull:
        sentiment = "bearish"

    return {
        "headline": headline,
        "importance": importance,
        "market_impact": market_impact,
        "affected_assets": analysis.get("affected_assets", []),
        "bullish_for": analysis.get("bullish_for", []),
        "bearish_for": analysis.get("bearish_for", []),
        "sentiment": sentiment,
        "confidence": confidence,
    }
