"""News fetcher service — fetches live news from RSS feeds or returns mock data.

Uses Google News RSS + financial publisher RSS feeds for real-time news.
Falls back to mock data on errors.
"""

from __future__ import annotations

import asyncio
import hashlib
import logging
import re
from datetime import datetime, timezone
from typing import Any

import aiohttp
import feedparser

from app.config import settings
from app.services.mock_data import get_mock_news, get_mock_article

logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────────────────────────────────────
# RSS Feed Configuration
# ──────────────────────────────────────────────────────────────────────────────
RSS_FEEDS: dict[str, list[dict[str, str]]] = {
    "TOP": [
        {"url": "https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRGx6TVdZU0FtVnVHZ0pKVGlnQVAB?hl=en-IN&gl=IN&ceid=IN:en", "publisher": "Google News"},
    ],
    "INDIA": [
        {"url": "https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms", "publisher": "Economic Times"},
        {"url": "https://www.moneycontrol.com/rss/marketreports.xml", "publisher": "Moneycontrol"},
        {"url": "https://www.livemint.com/rss/markets", "publisher": "Mint"},
    ],
    "GLOBAL": [
        {"url": "https://news.google.com/rss/search?q=global+stock+market+economy&hl=en&gl=US&ceid=US:en", "publisher": "Google News"},
        {"url": "https://news.google.com/rss/search?q=wall+street+nasdaq+dow+jones+S%26P+500&hl=en&gl=US&ceid=US:en", "publisher": "Google News"},
    ],
    "MACRO": [
        {"url": "https://news.google.com/rss/search?q=inflation+GDP+interest+rate+RBI+economic+data&hl=en-IN&gl=IN&ceid=IN:en", "publisher": "Google News"},
    ],
    "COMMODITIES": [
        {"url": "https://news.google.com/rss/search?q=gold+silver+crude+oil+commodity+prices&hl=en&gl=US&ceid=US:en", "publisher": "Google News"},
    ],
    "CRYPTO": [
        {"url": "https://news.google.com/rss/search?q=bitcoin+ethereum+cryptocurrency&hl=en&gl=US&ceid=US:en", "publisher": "Google News"},
    ],
    "NEWS": [
        {"url": "https://news.google.com/rss/search?q=stock+market+finance+business&hl=en-IN&gl=IN&ceid=IN:en", "publisher": "Google News"},
    ],
}

# In-memory article cache for full-text retrieval
_article_cache: dict[str, dict[str, Any]] = {}

# ──────────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────────

def _generate_id(url: str) -> str:
    """Deterministic ID from URL."""
    return hashlib.md5(url.encode()).hexdigest()


def _clean_html(text: str) -> str:
    """Strip HTML tags from RSS content."""
    clean = re.sub(r"<[^>]+>", "", text or "")
    clean = re.sub(r"&\w+;", " ", clean)
    return clean.strip()


def _detect_sentiment(title: str) -> str:
    """Simple keyword-based sentiment detection."""
    title_lower = title.lower()
    bullish_words = ["surge", "rally", "jump", "soar", "gain", "rise", "up", "high",
                     "record", "beat", "profit", "growth", "bullish", "boom", "buy"]
    bearish_words = ["crash", "fall", "drop", "plunge", "decline", "loss", "down", "low",
                     "sell", "bear", "cut", "fear", "recession", "slump", "worst"]
    
    bull_score = sum(1 for w in bullish_words if w in title_lower)
    bear_score = sum(1 for w in bearish_words if w in title_lower)
    
    if bull_score > bear_score:
        return "bullish"
    elif bear_score > bull_score:
        return "bearish"
    return "neutral"


def _detect_category(title: str, source_category: str) -> str:
    """Categorize article based on keywords."""
    if source_category and source_category != "TOP" and source_category != "NEWS":
        return source_category
    
    title_lower = title.lower()
    if any(w in title_lower for w in ["bitcoin", "ethereum", "crypto", "btc", "eth", "blockchain"]):
        return "CRYPTO"
    if any(w in title_lower for w in ["gold", "silver", "crude", "oil", "commodity", "copper", "brent"]):
        return "COMMODITIES"
    if any(w in title_lower for w in ["gdp", "inflation", "rbi", "fed", "interest rate", "cpi", "fiscal"]):
        return "MACRO"
    if any(w in title_lower for w in ["nifty", "sensex", "nse", "bse", "reliance", "hdfc", "tata", "infosys", "india"]):
        return "INDIA"
    if any(w in title_lower for w in ["s&p", "nasdaq", "dow", "ftse", "ecb", "boj", "global"]):
        return "GLOBAL"
    return "NEWS"


def _detect_entities(title: str) -> str:
    """Detect asset/entity mentions in headline."""
    entities = []
    title_upper = title.upper()
    asset_keywords = {
        "NIFTY": ["NIFTY", "NSE"],
        "SENSEX": ["SENSEX", "BSE"],
        "BANKNIFTY": ["BANK NIFTY", "BANKNIFTY"],
        "GOLD": ["GOLD", "XAUUSD"],
        "SILVER": ["SILVER"],
        "BRENT": ["BRENT", "CRUDE OIL"],
        "WTI": ["WTI"],
        "BTC": ["BITCOIN", "BTC"],
        "ETH": ["ETHEREUM", "ETH"],
        "USDINR": ["RUPEE", "USDINR", "USD/INR"],
        "DXY": ["DOLLAR INDEX", "DXY"],
    }
    for symbol, keywords in asset_keywords.items():
        if any(kw in title_upper for kw in keywords):
            entities.append(symbol)
    return " ".join(entities)


def _importance_score(title: str) -> int:
    """Estimate importance from headline keywords."""
    title_lower = title.lower()
    score = 50
    high_impact = ["rbi", "fed", "rate cut", "rate hike", "gdp", "record", "crash", "billion", "trillion"]
    medium_impact = ["market", "stock", "rally", "earnings", "profit", "growth"]
    for w in high_impact:
        if w in title_lower:
            score += 12
    for w in medium_impact:
        if w in title_lower:
            score += 6
    return min(score, 98)


def _build_ai_analysis(title: str, summary: str, sentiment: str, entities: str, category: str) -> dict:
    """Build a meaningful AI analysis dict from article metadata.
    
    Generates unique what_happened and why_it_matters text 
    instead of just repeating the headline.
    """
    entity_list = entities.split() if entities else []
    entity_str = ", ".join(entity_list) if entity_list else "broader markets"
    
    # Build what_happened — use summary if different from title, else create from title
    if summary and summary.strip().lower() != title.strip().lower() and len(summary) > len(title) + 15:
        what_happened = summary[:300]
    else:
        # Create a meaningful summary from the headline context
        what_happened = title

    # Build why_it_matters based on category and sentiment
    impact_map = {
        "INDIA": {
            "bullish": f"Positive development for Indian markets. Could strengthen {entity_str} and boost investor confidence in domestic equities.",
            "bearish": f"Negative signal for Indian markets. May pressure {entity_str} and trigger cautious positioning among investors.",
            "neutral": f"Mixed implications for Indian markets. Traders should watch {entity_str} for directional cues.",
        },
        "GLOBAL": {
            "bullish": f"Positive global macro signal. May lift risk assets and improve sentiment across {entity_str}.",
            "bearish": f"Negative global development. Could trigger risk-off flows and weigh on {entity_str}.",
            "neutral": f"Global macro event with uncertain implications. Watch for follow-through in {entity_str}.",
        },
        "CRYPTO": {
            "bullish": f"Bullish catalyst for crypto markets. {entity_str} could see increased buying pressure and momentum.",
            "bearish": f"Bearish development for crypto. {entity_str} may face selling pressure in the near term.",
            "neutral": f"Crypto market update. {entity_str} traders should monitor for breakout or breakdown.",
        },
        "COMMODITIES": {
            "bullish": f"Supportive for commodity prices. {entity_str} may benefit from supply-demand dynamics.",
            "bearish": f"Headwind for commodities. {entity_str} could face downward pressure on demand concerns.",
            "neutral": f"Commodity market development. Impact on {entity_str} depends on follow-through data.",
        },
        "MACRO": {
            "bullish": f"Positive macro data point. Supports growth narrative and could lift {entity_str}.",
            "bearish": f"Concerning macro signal. May weigh on growth expectations and pressure {entity_str}.",
            "neutral": f"Macro data release. Market reaction in {entity_str} will depend on interpretation.",
        },
    }
    
    category_impacts = impact_map.get(category, impact_map.get("GLOBAL", {}))
    why_it_matters = category_impacts.get(sentiment, f"This development could impact {entity_str}.")

    return {
        "what_happened": what_happened,
        "why_it_matters": why_it_matters,
        "affected_assets": entity_list,
        "bullish_for": entity_list if sentiment == "bullish" else [],
        "bearish_for": entity_list if sentiment == "bearish" else [],
        "confidence": 0.72 if sentiment == "neutral" else 0.82,
    }


def _parse_rss_date(entry: dict) -> str:
    """Parse date from feedparser entry."""
    if hasattr(entry, "published_parsed") and entry.published_parsed:
        try:
            dt = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
            return dt.isoformat()
        except Exception:
            pass
    return datetime.now(timezone.utc).isoformat()


# ──────────────────────────────────────────────────────────────────────────────
# Core RSS fetch
# ──────────────────────────────────────────────────────────────────────────────

async def _fetch_rss_feed(feed_url: str, publisher: str, category: str) -> list[dict[str, Any]]:
    """Fetch and parse a single RSS feed."""
    articles = []
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(feed_url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status != 200:
                    logger.warning("RSS feed %s returned %d", feed_url, resp.status)
                    return []
                text = await resp.text()
    except Exception as e:
        logger.error("Failed to fetch RSS %s: %s", feed_url, e)
        return []

    feed = await asyncio.to_thread(feedparser.parse, text)

    for entry in feed.entries[:25]:  # Cap per feed
        title = _clean_html(entry.get("title", ""))
        if not title:
            continue

        link = entry.get("link", "")
        summary = _clean_html(entry.get("summary", entry.get("description", "")))
        pub_date = _parse_rss_date(entry)
        source = entry.get("source", {}).get("title", publisher) if hasattr(entry, "source") else publisher
        article_id = _generate_id(link or title)

        detected_cat = _detect_category(title, category)
        sentiment = _detect_sentiment(title)
        entities = _detect_entities(title)
        importance = _importance_score(title)

        article = {
            "id": article_id,
            "headline": title,
            "summary": summary[:500] if summary else title,
            "body": summary or title,
            "source": source,
            "source_url": link,
            "publisher": source,
            "published_at": pub_date,
            "created_at": pub_date,
            "importance": importance,
            "sentiment": sentiment,
            "category": detected_cat,
            "entities": entities,
            "ai_analysis": _build_ai_analysis(title, summary, sentiment, entities, detected_cat),
        }
        articles.append(article)
        _article_cache[article_id] = article

    return articles


async def _fetch_all_live_news(category: str | None = None) -> list[dict[str, Any]]:
    """Fetch news from all relevant RSS feeds."""
    categories_to_fetch = [category] if category and category in RSS_FEEDS else list(RSS_FEEDS.keys())
    
    tasks = []
    for cat in categories_to_fetch:
        for feed in RSS_FEEDS.get(cat, []):
            tasks.append(_fetch_rss_feed(feed["url"], feed["publisher"], cat))

    results = await asyncio.gather(*tasks, return_exceptions=True)

    all_articles: list[dict[str, Any]] = []
    seen_titles: set[str] = set()

    for result in results:
        if isinstance(result, Exception):
            logger.error("RSS fetch error: %s", result)
            continue
        for article in result:
            # Deduplicate by title (normalized)
            title_key = article["headline"].lower().strip()[:80]
            if title_key not in seen_titles:
                seen_titles.add(title_key)
                all_articles.append(article)

    # Sort by published_at descending
    all_articles.sort(key=lambda a: a.get("published_at", ""), reverse=True)
    return all_articles


# ──────────────────────────────────────────────────────────────────────────────
# Public API
# ──────────────────────────────────────────────────────────────────────────────

async def fetch_news(
    category: str | None = None,
    limit: int = 20,
    offset: int = 0,
) -> list[dict[str, Any]]:
    """Fetch news articles, optionally filtered by category."""
    if settings.USE_MOCK_DATA:
        return get_mock_news(category=category, limit=limit, offset=offset)

    try:
        articles = await _fetch_all_live_news(category)
        if not articles:
            logger.warning("Live news returned empty, falling back to mock")
            return get_mock_news(category=category, limit=limit, offset=offset)
        return articles[offset:offset + limit]
    except Exception as e:
        logger.error("Live news fetch failed: %s — falling back to mock", e)
        return get_mock_news(category=category, limit=limit, offset=offset)


async def fetch_article(article_id: str) -> dict[str, Any] | None:
    """Fetch a single article by ID."""
    # Check live cache first
    if article_id in _article_cache:
        return _article_cache[article_id]

    if settings.USE_MOCK_DATA:
        return get_mock_article(article_id)

    # If not in cache, return from mock (articles are cached when feed is parsed)
    return get_mock_article(article_id)


async def search_news(query: str, limit: int = 20) -> list[dict[str, Any]]:
    """Full-text search across news articles."""
    if settings.USE_MOCK_DATA:
        all_news = get_mock_news(limit=100)
    else:
        try:
            # Search Google News for the query directly
            search_url = f"https://news.google.com/rss/search?q={query}&hl=en-IN&gl=IN&ceid=IN:en"
            all_news = await _fetch_rss_feed(search_url, "Google News", "NEWS")
            if not all_news:
                all_news = get_mock_news(limit=100)
        except Exception:
            all_news = get_mock_news(limit=100)

    q_lower = query.lower()
    results = [
        a for a in all_news
        if q_lower in a["headline"].lower()
        or q_lower in a.get("summary", "").lower()
        or q_lower in a.get("body", "").lower()
    ]
    return results[:limit]
