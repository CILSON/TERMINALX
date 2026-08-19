"""AI analysis service — uses Google Gemini 2.0 Flash for real-time market intelligence.

Provides:
- Article analysis (sentiment, assets, impact)
- Asset intelligence summaries
- Market briefs
- Free-form market Q&A
"""

from __future__ import annotations

import asyncio
import json
import logging
import time
from typing import Any

from app.config import settings

logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────────────────────────────────────
# Rate limiter — 15 requests per minute
# ──────────────────────────────────────────────────────────────────────────────
_request_times: list[float] = []
_semaphore = asyncio.Semaphore(5)  # Max 5 concurrent calls
_RPM_LIMIT = 15

def _rate_limit_ok() -> bool:
    """Check if we're within RPM limit."""
    now = time.time()
    _request_times[:] = [t for t in _request_times if now - t < 60]
    return len(_request_times) < _RPM_LIMIT

def _record_request():
    _request_times.append(time.time())


# ──────────────────────────────────────────────────────────────────────────────
# Gemini model initialization
# ──────────────────────────────────────────────────────────────────────────────
_model = None

def _get_model():
    global _model
    if _model is None and settings.GEMINI_API_KEY:
        try:
            import google.generativeai as genai
            genai.configure(api_key=settings.GEMINI_API_KEY)
            _model = genai.GenerativeModel(
                "gemini-2.0-flash",
                generation_config={
                    "temperature": 0.3,
                    "max_output_tokens": 1500,
                    "response_mime_type": "application/json",
                },
            )
            logger.info("Gemini 2.0 Flash initialized")
        except Exception as e:
            logger.error("Failed to init Gemini: %s", e)
    return _model


def _has_gemini() -> bool:
    return bool(settings.GEMINI_API_KEY)


def _parse_json_response(text: str) -> dict:
    """Parse JSON from Gemini response, handling markdown fences."""
    text = text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1].rsplit("```", 1)[0]
    return json.loads(text)


# ──────────────────────────────────────────────────────────────────────────────
# 1. ARTICLE ANALYSIS
# ──────────────────────────────────────────────────────────────────────────────

async def analyze_article(headline: str, body: str) -> dict[str, Any]:
    """Analyze a news article for market intelligence."""
    if not _has_gemini() or not _rate_limit_ok():
        return _keyword_analysis(headline)

    async with _semaphore:
        try:
            _record_request()
            model = _get_model()
            if not model:
                return _keyword_analysis(headline)

            prompt = f"""You are a senior financial analyst at a Bloomberg terminal.
Analyze this news article for Indian market traders.

Return JSON with these fields:
- "what_happened": Concise 1-2 sentence summary of the key event
- "why_it_matters": 1-2 sentences on market implications for Indian traders
- "affected_assets": Array of ticker symbols affected (use: NIFTY, BANKNIFTY, SENSEX, GOLD, SILVER, BRENT, WTI, USDINR, DXY, BTC, ETH, or specific stock names)
- "bullish_for": Array of assets this is positive for
- "bearish_for": Array of assets this is negative for  
- "confidence": Float 0.0-1.0 for your confidence

Headline: {headline}

Article: {body[:2500]}"""

            response = await asyncio.to_thread(model.generate_content, prompt)
            result = _parse_json_response(response.text)
            # Ensure all required fields
            return {
                "what_happened": result.get("what_happened", headline),
                "why_it_matters": result.get("why_it_matters", "Monitoring for market impact."),
                "affected_assets": result.get("affected_assets", []),
                "bullish_for": result.get("bullish_for", []),
                "bearish_for": result.get("bearish_for", []),
                "confidence": min(max(result.get("confidence", 0.7), 0), 1),
            }
        except Exception as e:
            logger.error("Gemini article analysis failed: %s", e)
            return _keyword_analysis(headline)


# ──────────────────────────────────────────────────────────────────────────────
# 2. ASSET INTELLIGENCE
# ──────────────────────────────────────────────────────────────────────────────

async def analyze_asset(
    symbol: str,
    name: str,
    price: float,
    change_pct: float,
    day_high: float,
    day_low: float,
    news_headlines: list[str],
) -> dict[str, Any]:
    """Generate a comprehensive AI-powered asset intelligence summary."""
    if not _has_gemini() or not _rate_limit_ok():
        return _fallback_asset_summary(symbol, name, price, change_pct, news_headlines)

    async with _semaphore:
        try:
            _record_request()
            model = _get_model()
            if not model:
                return _fallback_asset_summary(symbol, name, price, change_pct, news_headlines)

            news_block = "\n".join(f"- {h}" for h in news_headlines[:8])

            prompt = f"""You are a Bloomberg terminal AI generating an asset intelligence brief.

Asset: {name} ({symbol})
Current Price: {price:,.2f}
Today's Change: {change_pct:+.2f}%
Day Range: {day_low:,.2f} – {day_high:,.2f}

Recent Headlines:
{news_block if news_block else "No recent news available."}

Return JSON with:
- "summary": 3-4 sentence market analysis combining price action and news sentiment. Be specific about levels, trends, catalysts. Write like a Bloomberg terminal analyst.
- "outlook": One of "bullish", "bearish", "neutral"
- "key_levels": Object with "support" (number) and "resistance" (number) — estimate from day range
- "risk_factors": Array of 2-3 short risk strings
- "catalysts": Array of 2-3 short catalyst strings"""

            response = await asyncio.to_thread(model.generate_content, prompt)
            return _parse_json_response(response.text)
        except Exception as e:
            logger.error("Gemini asset analysis failed: %s", e)
            return _fallback_asset_summary(symbol, name, price, change_pct, news_headlines)


# ──────────────────────────────────────────────────────────────────────────────
# 3. MARKET BRIEF
# ──────────────────────────────────────────────────────────────────────────────

async def generate_market_brief(
    quotes: list[dict],
    top_headlines: list[str],
) -> dict[str, Any]:
    """Generate a comprehensive daily market brief."""
    if not _has_gemini() or not _rate_limit_ok():
        return _fallback_market_brief(quotes)

    async with _semaphore:
        try:
            _record_request()
            model = _get_model()
            if not model:
                return _fallback_market_brief(quotes)

            # Build market snapshot
            mkt_lines = []
            for q in quotes[:12]:
                sym = q.get("symbol", "")
                price = q.get("price", 0)
                chg = q.get("change_pct", 0)
                mkt_lines.append(f"{sym}: {price:,.2f} ({chg:+.2f}%)")

            news_block = "\n".join(f"- {h}" for h in top_headlines[:10])

            prompt = f"""You are a senior market strategist writing the morning brief for a Bloomberg-style terminal. 
Target audience: Indian swing traders and investors.

Market Snapshot:
{chr(10).join(mkt_lines)}

Top Headlines:
{news_block}

Return JSON with:
- "title": Catchy 5-8 word market brief title
- "summary": 4-5 sentence market overview covering key moves, themes, and what to watch
- "top_movers": Array of objects with "symbol", "direction" ("up"/"down"), "reason" (1 sentence)
- "watchlist": Array of 3-4 symbols to watch today with 1-line reason each
- "risk_radar": 1-2 sentence risk assessment"""

            response = await asyncio.to_thread(model.generate_content, prompt)
            return _parse_json_response(response.text)
        except Exception as e:
            logger.error("Gemini market brief failed: %s", e)
            return _fallback_market_brief(quotes)


# ──────────────────────────────────────────────────────────────────────────────
# 4. ASK AI — free-form market Q&A
# ──────────────────────────────────────────────────────────────────────────────

async def ask_market_question(
    question: str,
    context_quotes: list[dict] | None = None,
) -> dict[str, Any]:
    """Answer a free-form market question."""
    if not _has_gemini() or not _rate_limit_ok():
        return _fallback_ask(question, context_quotes)

    async with _semaphore:
        try:
            _record_request()
            model = _get_model()
            if not model:
                return _fallback_ask(question, context_quotes)

            context = ""
            if context_quotes:
                lines = [f"{q['symbol']}: {q['price']:,.2f} ({q['change_pct']:+.2f}%)" for q in context_quotes[:10]]
                context = f"\n\nCurrent Market Data:\n" + "\n".join(lines)

            prompt = f"""You are a Bloomberg terminal AI assistant for Indian market traders.
Answer this market question concisely and actionably.{context}

Question: {question}

Return JSON with:
- "answer": Clear, data-driven answer (3-5 sentences). Reference specific levels, data, and assets.
- "related_assets": Array of relevant ticker symbols
- "sentiment": Overall sentiment of your answer ("bullish", "bearish", "neutral")"""

            response = await asyncio.to_thread(model.generate_content, prompt)
            return _parse_json_response(response.text)
        except Exception as e:
            logger.error("Gemini Q&A failed: %s", e)
            return _fallback_ask(question, context_quotes)


# ──────────────────────────────────────────────────────────────────────────────
# FALLBACKS — keyword-based analysis when Gemini is unavailable
# ──────────────────────────────────────────────────────────────────────────────

def _keyword_analysis(headline: str) -> dict[str, Any]:
    """Keyword-based analysis fallback."""
    hl = headline.lower()
    affected, bullish, bearish = [], [], []

    asset_map = {
        "nifty": "NIFTY", "sensex": "SENSEX", "bank nifty": "BANKNIFTY",
        "gold": "GOLD", "silver": "SILVER", "crude": "BRENT", "oil": "WTI",
        "bitcoin": "BTC", "ethereum": "ETH", "crypto": "BTC",
        "rupee": "USDINR", "dollar": "DXY", "rbi": "BANKNIFTY",
    }
    for kw, sym in asset_map.items():
        if kw in hl:
            affected.append(sym)

    if not affected:
        affected = ["NIFTY"]

    bull_words = ["surge", "rally", "beat", "high", "growth", "profit", "rise", "gain", "record"]
    bear_words = ["fall", "drop", "cut", "weak", "loss", "crash", "slump", "decline"]

    if any(w in hl for w in bull_words):
        bullish = affected[:3]
    elif any(w in hl for w in bear_words):
        bearish = affected[:3]

    return {
        "what_happened": headline,
        "why_it_matters": f"This could impact {', '.join(affected)}. Monitor for follow-through price action.",
        "affected_assets": list(set(affected)),
        "bullish_for": bullish,
        "bearish_for": bearish,
        "confidence": 0.65,
    }


def _fallback_asset_summary(
    symbol: str, name: str, price: float, change_pct: float, headlines: list[str]
) -> dict[str, Any]:
    """Fallback asset summary without AI."""
    direction = "up" if change_pct > 0 else "down" if change_pct < 0 else "flat"
    summary = f"{name} is trading {direction} {abs(change_pct):.2f}% at {price:,.2f}."
    if headlines:
        summary += f" Latest: \"{headlines[0][:80]}\"."
    return {
        "summary": summary,
        "outlook": "bullish" if change_pct > 0.5 else "bearish" if change_pct < -0.5 else "neutral",
        "key_levels": {"support": round(price * 0.98, 2), "resistance": round(price * 1.02, 2)},
        "risk_factors": ["Macro uncertainty", "Global risk sentiment"],
        "catalysts": ["Earnings season", "Policy announcements"],
    }


def _fallback_market_brief(quotes: list[dict]) -> dict[str, Any]:
    """Fallback market brief without AI."""
    gainers = sorted(quotes, key=lambda q: q.get("change_pct", 0), reverse=True)[:3]
    losers = sorted(quotes, key=lambda q: q.get("change_pct", 0))[:3]

    movers = []
    for q in gainers:
        movers.append({"symbol": q["symbol"], "direction": "up", "reason": f"Up {q.get('change_pct', 0):.2f}%"})
    for q in losers:
        movers.append({"symbol": q["symbol"], "direction": "down", "reason": f"Down {abs(q.get('change_pct', 0)):.2f}%"})

    return {
        "title": "Market Overview — Key Levels in Focus",
        "summary": "Markets are mixed today with sector rotation in play. Monitor key support and resistance levels.",
        "top_movers": movers,
        "watchlist": [{"symbol": q["symbol"], "reason": "Active mover"} for q in gainers[:3]],
        "risk_radar": "Standard market volatility. No exceptional risk events flagged.",
    }


def _fallback_ask(question: str, context_quotes: list[dict] | None = None) -> dict[str, Any]:
    """Data-driven fallback for Q&A when Gemini is unavailable."""
    q_lower = question.lower()
    related = []
    sentiment = "neutral"

    # Identify related assets from the question
    asset_map = {
        "nifty": "NIFTY", "sensex": "SENSEX", "bank nifty": "BANKNIFTY", "banknifty": "BANKNIFTY",
        "gold": "GOLD", "silver": "SILVER", "crude": "BRENT", "oil": "WTI",
        "bitcoin": "BTC", "btc": "BTC", "ethereum": "ETH", "eth": "ETH",
        "rupee": "USDINR", "dollar": "DXY", "forex": "USDINR",
    }
    for kw, sym in asset_map.items():
        if kw in q_lower and sym not in related:
            related.append(sym)

    # Build data-driven answer from context
    answer_parts = []
    if context_quotes:
        relevant_quotes = [q for q in context_quotes if q["symbol"] in related] if related else context_quotes[:5]
        if relevant_quotes:
            for q in relevant_quotes[:3]:
                direction = "up" if q.get("change_pct", 0) > 0 else "down"
                answer_parts.append(
                    f"{q['symbol']} is currently at {q['price']:,.2f} ({direction} {abs(q.get('change_pct', 0)):.2f}%)"
                )
            avg_change = sum(q.get("change_pct", 0) for q in relevant_quotes) / len(relevant_quotes)
            sentiment = "bullish" if avg_change > 0.3 else "bearish" if avg_change < -0.3 else "neutral"

    if answer_parts:
        answer = f"Based on current market data: {'. '.join(answer_parts)}. "
        answer += "Monitor key technical levels for directional cues. Consider the broader macro environment for context."
    else:
        answer = "I can provide market data and analysis. Try asking about specific assets like NIFTY, GOLD, BTC, or the overall market trend."

    if not related and context_quotes:
        related = [q["symbol"] for q in context_quotes[:3]]

    return {"answer": answer, "related_assets": related, "sentiment": sentiment}

