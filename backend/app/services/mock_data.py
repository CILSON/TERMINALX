"""Comprehensive mock-data service for TerminalX.

Generates realistic Indian-market data so the terminal feels alive even without
external API keys or a running database.
"""

from __future__ import annotations

import math
import random
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

# ──────────────────────────────────────────────────────────────────────────────
# IST helper
# ──────────────────────────────────────────────────────────────────────────────
IST = timezone(timedelta(hours=5, minutes=30))

def _now_ist() -> datetime:
    return datetime.now(IST)

def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


# ──────────────────────────────────────────────────────────────────────────────
# MOCK ASSETS — base prices & volatility
# ──────────────────────────────────────────────────────────────────────────────
MOCK_ASSETS: dict[str, dict[str, Any]] = {
    # Indices
    "NIFTY": {"name": "NIFTY 50", "asset_class": "index", "exchange": "NSE", "base_price": 26180.75, "volatility": 0.003},
    "BANKNIFTY": {"name": "BANK NIFTY", "asset_class": "index", "exchange": "NSE", "base_price": 56420.50, "volatility": 0.004},
    "FINNIFTY": {"name": "FIN NIFTY", "asset_class": "index", "exchange": "NSE", "base_price": 24850.30, "volatility": 0.003},
    "MIDCAP": {"name": "NIFTY MIDCAP", "asset_class": "index", "exchange": "NSE", "base_price": 14320.80, "volatility": 0.005},
    "SENSEX": {"name": "BSE SENSEX", "asset_class": "index", "exchange": "BSE", "base_price": 86540.60, "volatility": 0.003},
    # Commodities (USD per unit)
    "GOLD": {"name": "Gold", "asset_class": "commodity", "exchange": "MCX", "base_price": 3318.40, "volatility": 0.002},
    "SILVER": {"name": "Silver", "asset_class": "commodity", "exchange": "MCX", "base_price": 33.48, "volatility": 0.004},
    "BRENT": {"name": "Brent Crude", "asset_class": "commodity", "exchange": "MCX", "base_price": 64.95, "volatility": 0.005},
    "WTI": {"name": "WTI Crude", "asset_class": "commodity", "exchange": "NYMEX", "base_price": 61.50, "volatility": 0.005},
    "NATGAS": {"name": "Natural Gas", "asset_class": "commodity", "exchange": "NYMEX", "base_price": 3.78, "volatility": 0.008},
    "COPPER": {"name": "Copper", "asset_class": "commodity", "exchange": "MCX", "base_price": 4.68, "volatility": 0.004},
    # Forex
    "USDINR": {"name": "USD/INR", "asset_class": "forex", "exchange": "FOREX", "base_price": 85.35, "volatility": 0.001},
    "EURINR": {"name": "EUR/INR", "asset_class": "forex", "exchange": "FOREX", "base_price": 95.70, "volatility": 0.0012},
    "GBPINR": {"name": "GBP/INR", "asset_class": "forex", "exchange": "FOREX", "base_price": 113.85, "volatility": 0.0015},
    "DXY": {"name": "Dollar Index", "asset_class": "forex", "exchange": "FOREX", "base_price": 99.12, "volatility": 0.002},
    "EURUSD": {"name": "EUR/USD", "asset_class": "forex", "exchange": "FOREX", "base_price": 1.1365, "volatility": 0.0015},
    # Crypto
    "BTC": {"name": "Bitcoin", "asset_class": "crypto", "exchange": "CRYPTO", "base_price": 109500.00, "volatility": 0.008},
    "ETH": {"name": "Ethereum", "asset_class": "crypto", "exchange": "CRYPTO", "base_price": 2585.00, "volatility": 0.010},
    "SOL": {"name": "Solana", "asset_class": "crypto", "exchange": "CRYPTO", "base_price": 175.40, "volatility": 0.015},
    "BNB": {"name": "BNB", "asset_class": "crypto", "exchange": "CRYPTO", "base_price": 658.50, "volatility": 0.009},
}

# Runtime price state (mutated by generate_tick)
_price_state: dict[str, float] = {}


def _init_price_state() -> None:
    """Bootstrap the runtime price state from base prices with a small random offset."""
    for sym, info in MOCK_ASSETS.items():
        if sym not in _price_state:
            base = info["base_price"]
            jitter = base * random.uniform(-0.005, 0.005)
            _price_state[sym] = round(base + jitter, 4)


_init_price_state()


# ──────────────────────────────────────────────────────────────────────────────
# QUOTE GENERATION — random walk + mean reversion
# ──────────────────────────────────────────────────────────────────────────────
def generate_tick(symbol: str) -> dict[str, Any]:
    """Generate a single realistic price tick for *symbol*.

    Uses geometric Brownian motion with mean-reversion to keep prices from
    drifting too far from their base.
    """
    info = MOCK_ASSETS.get(symbol)
    if info is None:
        raise KeyError(f"Unknown symbol: {symbol}")

    base = info["base_price"]
    vol = info["volatility"]
    current = _price_state.get(symbol, base)

    # Mean reversion strength — pulls price back toward base
    reversion = 0.02
    drift = reversion * (base - current) / base

    # Random shock
    shock = random.gauss(0, vol * base)
    new_price = current + drift * base + shock
    # Ensure positive
    new_price = max(new_price, base * 0.85)
    new_price = round(new_price, 4)
    _price_state[symbol] = new_price

    prev_close = round(base * (1 + random.uniform(-0.008, 0.008)), 4)
    change = round(new_price - prev_close, 4)
    change_pct = round((change / prev_close) * 100, 4) if prev_close else 0

    day_high = round(max(new_price, base * (1 + random.uniform(0.001, 0.012))), 4)
    day_low = round(min(new_price, base * (1 - random.uniform(0.001, 0.012))), 4)
    open_price = round(prev_close * (1 + random.uniform(-0.003, 0.003)), 4)

    # Volume: indices ≫ crypto > forex
    vol_multipliers = {"index": 5_000_000, "commodity": 200_000, "forex": 800_000, "crypto": 1_200_000}
    base_vol = vol_multipliers.get(info["asset_class"], 500_000)
    volume = int(base_vol * random.uniform(0.7, 1.4))

    now = _utcnow()

    return {
        "symbol": symbol,
        "name": info["name"],
        "asset_class": info["asset_class"],
        "exchange": info["exchange"],
        "price": new_price,
        "change": change,
        "change_pct": change_pct,
        "volume": volume,
        "high": day_high,
        "low": day_low,
        "open": open_price,
        "prev_close": prev_close,
        "day_high": day_high,
        "day_low": day_low,
        "updated_at": now.isoformat(),
    }


def simulate_quote_update(symbol: str) -> dict[str, Any]:
    """Public alias for ``generate_tick``."""
    return generate_tick(symbol)


def get_mock_quotes() -> list[dict[str, Any]]:
    """Return ticks for every tracked asset."""
    return [generate_tick(sym) for sym in MOCK_ASSETS]


# ──────────────────────────────────────────────────────────────────────────────
# NEWS — 60 realistic articles across all categories
# ──────────────────────────────────────────────────────────────────────────────
_PUBLISHERS = ["Reuters", "Bloomberg", "Economic Times", "Moneycontrol", "CNBCTV18", "Mint", "Business Standard", "Livemint"]

_RAW_NEWS: list[dict[str, Any]] = [
    # ── TOP ────────────────────────────────────────────────
    {
        "headline": "Markets Hit Record High as FII Inflows Surge Past ₹12,000 Crore",
        "summary": "Indian equity benchmarks rallied to fresh all-time highs on Monday, propelled by strong foreign institutional investor inflows and upbeat global sentiment.",
        "body": (
            "Indian equity markets scaled new peaks on Monday with the NIFTY 50 surging past 24,500 "
            "for the first time, as foreign institutional investors pumped in over ₹12,000 crore in a "
            "single session — the highest single-day inflow in 2024.\n\n"
            "Banking and financial stocks led the rally, with HDFC Bank, ICICI Bank and SBI each "
            "gaining between 2% and 4%. The broader market also participated with the NIFTY Midcap "
            "100 rising 1.8% and the Smallcap 250 adding 1.5%.\n\n"
            "Market analysts attribute the surge to improving macro fundamentals, with India's GDP "
            "growth holding above 7% and corporate earnings surprising on the upside. 'India remains "
            "the top overweight for emerging-market allocators,' said a strategist at Morgan Stanley.\n\n"
            "Sector rotation was evident with IT stocks pausing after recent gains while FMCG and auto "
            "names saw fresh buying interest. Market breadth was strongly positive with advances "
            "outnumbering declines 3:1 on the NSE."
        ),
        "category": "TOP",
        "importance": 95,
        "sentiment": "bullish",
        "publisher": "Bloomberg",
        "entities": ["NIFTY", "HDFC Bank", "ICICI Bank", "SBI"],
        "ai_analysis": {
            "what_happened": "Indian equity markets reached all-time highs with FII inflows exceeding ₹12,000 crore in one session.",
            "why_it_matters": "Massive FII inflows signal strong global confidence in India's growth story and could sustain the rally.",
            "affected_assets": ["NIFTY", "BANKNIFTY", "HDFC Bank", "ICICI Bank", "SBI"],
            "bullish_for": ["NIFTY", "BANKNIFTY", "Indian Equities"],
            "bearish_for": ["US Treasuries", "Chinese Equities"],
            "confidence": 0.92,
        },
    },
    {
        "headline": "RBI Holds Rates Steady at 6.5%, Maintains Growth Forecast at 7%",
        "summary": "The Reserve Bank of India kept the repo rate unchanged at 6.5% for the eighth consecutive meeting, while maintaining its GDP growth forecast at 7%.",
        "body": (
            "The Reserve Bank of India's Monetary Policy Committee voted 4-2 to keep the benchmark "
            "repo rate unchanged at 6.5%, marking the eighth consecutive pause in its rate-setting cycle.\n\n"
            "Governor Shaktikanta Das maintained the central bank's GDP growth projection at 7% for "
            "FY25, noting that 'the Indian economy continues to be resilient and robust.' The RBI "
            "also kept its CPI inflation forecast at 4.5%, citing easing food inflation.\n\n"
            "Bond markets reacted positively to the decision with the 10-year government bond yield "
            "easing 3 basis points to 7.02%. The rupee remained stable around 83.40 against the dollar.\n\n"
            "Market participants now expect the first rate cut to come in Q3 FY25, with inflation "
            "expected to settle within the RBI's target band. 'The RBI is playing it safe, and that's "
            "exactly what the market wants right now,' said the chief economist at Kotak Mahindra Bank."
        ),
        "category": "TOP",
        "importance": 92,
        "sentiment": "neutral",
        "publisher": "Reuters",
        "entities": ["RBI", "INR", "Government Bonds"],
        "ai_analysis": {
            "what_happened": "RBI maintained repo rate at 6.5% for the eighth consecutive meeting with a 4-2 vote.",
            "why_it_matters": "Continued pause suggests RBI is waiting for durable disinflation; rate cuts likely in Q3 FY25.",
            "affected_assets": ["USDINR", "Government Bonds", "BANKNIFTY", "NIFTY"],
            "bullish_for": ["Government Bonds", "Banking Stocks", "Real Estate"],
            "bearish_for": [],
            "confidence": 0.95,
        },
    },
    {
        "headline": "Sensex Breaches 81,000 Mark for First Time on Broad-Based Rally",
        "summary": "The BSE Sensex crossed the historic 81,000 level driven by gains across all sectors, with banking and IT leading the charge.",
        "body": (
            "The BSE Sensex made history on Tuesday by crossing the 81,000 mark for the first time, "
            "fueled by a broad-based rally that saw all 30 constituents trading in the green.\n\n"
            "The 30-share index closed at 81,247.35, up 623 points or 0.77%. The NIFTY 50 also set "
            "a new record at 24,592.10, gaining 188 points. The rally was driven by positive global "
            "cues following a softer-than-expected US CPI print.\n\n"
            "Banking heavyweights HDFC Bank (+2.1%) and ICICI Bank (+1.8%) were the top contributors "
            "to the Sensex surge. IT bellwethers TCS and Infosys also gained over 1% each on "
            "expectations of improved demand from US clients.\n\n"
            "Market capitalisation of all BSE-listed companies reached a record ₹452 lakh crore. "
            "'India is in a sweet spot with strong macro fundamentals and improving corporate earnings,' "
            "said the head of equity strategy at Motilal Oswal."
        ),
        "category": "TOP",
        "importance": 90,
        "sentiment": "bullish",
        "publisher": "Economic Times",
        "entities": ["SENSEX", "NIFTY", "HDFC Bank", "ICICI Bank", "TCS", "Infosys"],
        "ai_analysis": {
            "what_happened": "BSE Sensex crossed 81,000 for the first time with all 30 stocks gaining.",
            "why_it_matters": "Broad-based rally signals strong market confidence; total market cap hit ₹452 lakh crore.",
            "affected_assets": ["SENSEX", "NIFTY", "HDFC Bank", "TCS"],
            "bullish_for": ["Indian Equities", "Mutual Funds", "NIFTY"],
            "bearish_for": ["Equity Put Options"],
            "confidence": 0.88,
        },
    },
    {
        "headline": "India's Current Account Deficit Narrows to 0.7% of GDP in Q4",
        "summary": "India's current account deficit narrowed sharply to 0.7% of GDP in the January-March quarter, driven by strong services exports and software remittances.",
        "body": (
            "India's current account deficit (CAD) narrowed to $8.7 billion, or 0.7% of GDP, in the "
            "fourth quarter of FY24, significantly better than the 2.6% deficit recorded a year ago.\n\n"
            "The improvement was primarily driven by a surge in services exports, particularly IT and "
            "business process outsourcing, which grew 12% year-on-year. Software services exports "
            "alone contributed $32 billion during the quarter.\n\n"
            "Merchandise trade deficit also showed improvement, narrowing to $52 billion from $59 "
            "billion in the year-ago period, aided by lower crude oil import bills and government "
            "restrictions on non-essential imports.\n\n"
            "The narrower CAD is positive for the rupee and reduces India's vulnerability to external "
            "shocks. 'This is structural improvement, not just cyclical,' noted the chief economist "
            "at State Bank of India."
        ),
        "category": "TOP",
        "importance": 85,
        "sentiment": "bullish",
        "publisher": "Mint",
        "entities": ["USDINR", "IT Sector", "Services Exports"],
        "ai_analysis": {
            "what_happened": "India's CAD narrowed to 0.7% of GDP from 2.6% a year ago, driven by strong services exports.",
            "why_it_matters": "Structural improvement in CAD reduces FX vulnerability and supports INR stability.",
            "affected_assets": ["USDINR", "Government Bonds", "NIFTY"],
            "bullish_for": ["USDINR", "Indian Bonds", "IT Stocks"],
            "bearish_for": ["DXY"],
            "confidence": 0.87,
        },
    },
    # ── INDIA ──────────────────────────────────────────────
    {
        "headline": "Reliance Jio Reports 12% Revenue Growth, ARPU Hits ₹203",
        "summary": "Jio Platforms reported a 12% year-on-year jump in revenue for Q4, with average revenue per user (ARPU) rising to ₹203 from ₹182 a year ago.",
        "body": (
            "Reliance Jio Platforms delivered a strong Q4 FY24 performance with consolidated revenue "
            "rising 12% year-on-year to ₹26,478 crore, while net profit grew 13% to ₹5,583 crore.\n\n"
            "The standout metric was average revenue per user (ARPU) which climbed to ₹203, up from "
            "₹182 a year ago, driven by the tariff hikes implemented in late 2023. The subscriber base "
            "also expanded to 481 million, adding 8 million users during the quarter.\n\n"
            "Jio's 5G rollout continued apace with coverage now available in over 700 cities. The "
            "company noted that 5G users consume 2.5x more data than 4G users.\n\n"
            "Analysts at CLSA maintained a Buy rating, noting that 'Jio's ARPU trajectory is ahead of "
            "expectations and further tariff hikes could drive another 15-20% upside in ARPU.'"
        ),
        "category": "INDIA",
        "importance": 82,
        "sentiment": "bullish",
        "publisher": "Moneycontrol",
        "entities": ["Reliance", "Jio", "Telecom"],
        "ai_analysis": {
            "what_happened": "Jio's Q4 revenue grew 12% YoY with ARPU reaching ₹203; subscriber base at 481M.",
            "why_it_matters": "Rising ARPU signals pricing power; 5G rollout driving higher data consumption.",
            "affected_assets": ["Reliance Industries", "NIFTY", "Telecom Sector"],
            "bullish_for": ["Reliance Industries", "NIFTY"],
            "bearish_for": ["Bharti Airtel", "Vodafone Idea"],
            "confidence": 0.85,
        },
    },
    {
        "headline": "HDFC Bank Q3 Profits Beat Estimates, NIM Stable at 3.6%",
        "summary": "HDFC Bank reported a 20% jump in Q3 net profit to ₹16,372 crore, beating analyst estimates by 4%, with net interest margins holding steady at 3.6%.",
        "body": (
            "India's largest private sector lender HDFC Bank delivered better-than-expected Q3 FY24 "
            "results with standalone net profit surging 20% year-on-year to ₹16,372 crore.\n\n"
            "Net interest income (NII) grew 24% to ₹28,470 crore, while net interest margin (NIM) "
            "remained stable at 3.6%, allaying concerns about margin compression post the HDFC merger. "
            "Gross NPA ratio improved to 1.26% from 1.34% in the previous quarter.\n\n"
            "Loan growth was robust at 19% YoY, with retail loans growing 22% and corporate loans "
            "expanding 16%. Deposit growth at 20% YoY outpaced loan growth for the first time in "
            "three quarters.\n\n"
            "The stock surged 4% in post-market trading. 'HDFC Bank has put merger-related concerns "
            "to rest. The NIM stability is the key positive takeaway,' said analysts at Goldman Sachs."
        ),
        "category": "INDIA",
        "importance": 88,
        "sentiment": "bullish",
        "publisher": "CNBCTV18",
        "entities": ["HDFC Bank", "Banking", "BANKNIFTY"],
        "ai_analysis": {
            "what_happened": "HDFC Bank Q3 net profit rose 20% YoY to ₹16,372 crore; NIM stable at 3.6%.",
            "why_it_matters": "Stable margins post-HDFC merger and strong deposit growth ease key investor concerns.",
            "affected_assets": ["HDFC Bank", "BANKNIFTY", "NIFTY"],
            "bullish_for": ["HDFC Bank", "BANKNIFTY", "Banking Sector"],
            "bearish_for": [],
            "confidence": 0.91,
        },
    },
    {
        "headline": "Tata Motors Posts Record Quarterly Profit on JLR Strength",
        "summary": "Tata Motors reported its highest-ever quarterly net profit of ₹7,025 crore, driven by strong Jaguar Land Rover performance and improved domestic margins.",
        "body": (
            "Tata Motors reported a record consolidated net profit of ₹7,025 crore for Q4 FY24, "
            "more than tripling from ₹2,195 crore a year ago.\n\n"
            "Jaguar Land Rover was the star performer, with revenue rising 27% to £7.9 billion and "
            "EBITDA margin expanding to 16.2%. The luxury car unit benefited from strong order books, "
            "improved semiconductor supply, and a favourable mix shift towards higher-margin models.\n\n"
            "The domestic business also delivered with commercial vehicle market share expanding to "
            "41.2% and passenger vehicle margins improving to 8.5% from 6.1% a year ago.\n\n"
            "The company declared a special dividend of ₹6 per share. Tata Motors stock has rallied "
            "72% in the past year and analysts see further upside from JLR's EV transition."
        ),
        "category": "INDIA",
        "importance": 80,
        "sentiment": "bullish",
        "publisher": "Business Standard",
        "entities": ["Tata Motors", "JLR", "Auto Sector"],
        "ai_analysis": {
            "what_happened": "Tata Motors posted record quarterly profit of ₹7,025 crore, 3x growth YoY.",
            "why_it_matters": "JLR turnaround and domestic margin improvement validate the multi-year re-rating thesis.",
            "affected_assets": ["Tata Motors", "NIFTY", "Auto Index"],
            "bullish_for": ["Tata Motors", "Auto Sector"],
            "bearish_for": [],
            "confidence": 0.84,
        },
    },
    {
        "headline": "Infosys Raises Revenue Guidance, Wins $2B Mega Deal",
        "summary": "Infosys raised its FY25 revenue growth guidance to 4-6% and announced a $2 billion multi-year deal with a major US financial services client.",
        "body": (
            "Infosys, India's second-largest IT services company, raised its FY25 revenue growth "
            "guidance to 4-6% from the earlier 1-3%, signaling a recovery in the technology spending "
            "environment.\n\n"
            "The company also announced a landmark $2 billion deal with a major US financial services "
            "client, one of the largest deals in Indian IT history. The engagement spans digital "
            "transformation, cloud migration, and AI integration over a seven-year period.\n\n"
            "Q1 FY25 results were ahead of expectations with revenue growing 3.6% sequentially in "
            "constant currency terms. EBIT margin expanded 60 basis points to 21.5%, aided by "
            "operational efficiencies and lower attrition.\n\n"
            "CEO Salil Parekh noted that 'generative AI is creating new demand pockets and we are "
            "well-positioned to capture this opportunity.' The stock jumped 6% in early trading."
        ),
        "category": "INDIA",
        "importance": 83,
        "sentiment": "bullish",
        "publisher": "Economic Times",
        "entities": ["Infosys", "IT Sector", "NIFTY IT"],
        "ai_analysis": {
            "what_happened": "Infosys raised FY25 guidance to 4-6% and won a $2B deal from a US financial services client.",
            "why_it_matters": "Guidance upgrade signals IT spending recovery; mega deal validates AI/cloud strategy.",
            "affected_assets": ["Infosys", "NIFTY IT", "TCS", "Wipro"],
            "bullish_for": ["Infosys", "IT Sector", "NIFTY"],
            "bearish_for": ["Accenture"],
            "confidence": 0.89,
        },
    },
    {
        "headline": "Adani Group Completes ₹16,600 Crore Ambuja Cements Open Offer",
        "summary": "Adani Group has successfully completed its open offer for Ambuja Cements, acquiring an additional 26% stake for approximately ₹16,600 crore.",
        "body": (
            "The Adani Group has completed its open offer for Ambuja Cements, bringing its total "
            "stake in the cement major to 69.4%. The offer was oversubscribed, with shareholders "
            "tendering shares worth ₹16,600 crore.\n\n"
            "This move consolidates Adani's position as India's second-largest cement manufacturer "
            "with combined capacity of over 140 million tonnes per annum through its Ambuja-ACC combine.\n\n"
            "The group plans to invest ₹10,000 crore over the next two years to expand capacity to "
            "200 MTPA, targeting aggressive growth in eastern and southern India.\n\n"
            "Industry analysts see the cement sector consolidation as positive for pricing power across "
            "the industry, with the top four players now controlling over 55% of India's capacity."
        ),
        "category": "INDIA",
        "importance": 75,
        "sentiment": "neutral",
        "publisher": "Livemint",
        "entities": ["Adani Group", "Ambuja Cements", "Cement Sector"],
        "ai_analysis": {
            "what_happened": "Adani Group acquired additional 26% in Ambuja Cements through ₹16,600 crore open offer.",
            "why_it_matters": "Cement sector consolidation improves pricing power; Adani becomes #2 in India by capacity.",
            "affected_assets": ["Ambuja Cements", "ACC", "UltraTech", "Cement Sector"],
            "bullish_for": ["Ambuja Cements", "ACC", "Cement Sector"],
            "bearish_for": [],
            "confidence": 0.80,
        },
    },
    {
        "headline": "Zomato Turns Profitable; Blinkit Revenue Doubles",
        "summary": "Zomato reported its first full-year profit with Blinkit's revenue doubling and food delivery margins expanding to 5.4%.",
        "body": (
            "Zomato posted its maiden full-year net profit of ₹351 crore for FY24, a dramatic "
            "turnaround from a loss of ₹971 crore in FY23. The results beat street estimates by a "
            "wide margin.\n\n"
            "Blinkit, the company's quick-commerce arm, was the growth engine with revenue doubling "
            "to ₹2,300 crore. While still loss-making, Blinkit's EBITDA loss narrowed significantly "
            "to ₹480 crore from ₹820 crore, with management guiding for breakeven by Q2 FY25.\n\n"
            "The core food delivery business achieved an adjusted EBITDA margin of 5.4%, up from 2.1% "
            "a year ago. Gross order value grew 28% to ₹29,500 crore.\n\n"
            "Zomato shares have rallied 120% in the past year and now command a market capitalisation "
            "of over ₹1.7 lakh crore, making it one of India's most valuable internet companies."
        ),
        "category": "INDIA",
        "importance": 78,
        "sentiment": "bullish",
        "publisher": "Moneycontrol",
        "entities": ["Zomato", "Blinkit", "Quick Commerce"],
        "ai_analysis": {
            "what_happened": "Zomato turned full-year profitable at ₹351 crore; Blinkit revenue doubled.",
            "why_it_matters": "First profitability validates the unit economics thesis; Blinkit approaching breakeven.",
            "affected_assets": ["Zomato", "Swiggy", "NIFTY"],
            "bullish_for": ["Zomato", "New-Age Tech Stocks"],
            "bearish_for": ["Swiggy"],
            "confidence": 0.86,
        },
    },
    # ── GLOBAL ─────────────────────────────────────────────
    {
        "headline": "Fed Signals September Rate Cut as Inflation Cools to 2.5%",
        "summary": "Federal Reserve Chair Jerome Powell signaled that a September rate cut is likely after US CPI fell to 2.5%, the lowest level since early 2021.",
        "body": (
            "Federal Reserve Chair Jerome Powell gave the clearest signal yet that the central bank "
            "is ready to start cutting interest rates, telling Congress that 'recent data have been "
            "encouraging and suggest inflation is moving sustainably toward our 2% target.'\n\n"
            "US CPI for June came in at 2.5% year-on-year, below expectations of 2.7% and marking "
            "the lowest reading since February 2021. Core CPI also fell to 2.9%, within striking "
            "distance of the Fed's target.\n\n"
            "Markets are now pricing in a 92% probability of a 25 basis point rate cut at the "
            "September FOMC meeting, with two additional cuts expected by year-end.\n\n"
            "US Treasury yields dropped sharply, with the 2-year falling 12 bps to 4.49% and the "
            "10-year declining 8 bps to 4.18%. The dollar index weakened to 104.1 as rate-cut "
            "expectations firmed up."
        ),
        "category": "GLOBAL",
        "importance": 93,
        "sentiment": "bullish",
        "publisher": "Reuters",
        "entities": ["Fed", "US CPI", "US Treasuries", "DXY"],
        "ai_analysis": {
            "what_happened": "Fed Chair Powell signaled September rate cut after US CPI fell to 2.5%.",
            "why_it_matters": "First rate cut would end the most aggressive hiking cycle in 40 years; bullish for risk assets globally.",
            "affected_assets": ["DXY", "US Treasuries", "NIFTY", "BTC", "GOLD"],
            "bullish_for": ["Emerging Markets", "NIFTY", "BTC", "GOLD", "Tech Stocks"],
            "bearish_for": ["DXY", "US Dollar", "Bank Net Interest Margins"],
            "confidence": 0.93,
        },
    },
    {
        "headline": "ECB Holds Rates Amid Stubborn Services Inflation in Eurozone",
        "summary": "The European Central Bank kept its deposit rate at 3.75%, citing persistent services inflation despite cooling headline numbers.",
        "body": (
            "The European Central Bank held its deposit rate at 3.75% at its July meeting, following "
            "the historic first cut in June. President Christine Lagarde cited sticky services "
            "inflation as the primary concern.\n\n"
            "Eurozone CPI stood at 2.5% in June, but services inflation remained elevated at 4.1%, "
            "well above the ECB's comfort zone. Wage growth also stayed strong at 4.5%, complicating "
            "the path to further easing.\n\n"
            "The ECB left the door open for a September cut, with Lagarde noting that 'the data "
            "between now and September will determine our next move.' Markets price a 65% chance "
            "of a September cut.\n\n"
            "The euro strengthened slightly against the dollar to 1.0850 on the less-dovish-than-expected "
            "tone. European equities were largely flat on the decision."
        ),
        "category": "GLOBAL",
        "importance": 80,
        "sentiment": "neutral",
        "publisher": "Bloomberg",
        "entities": ["ECB", "EUR", "Eurozone"],
        "ai_analysis": {
            "what_happened": "ECB held rates at 3.75% due to sticky services inflation at 4.1%.",
            "why_it_matters": "Less dovish stance supports EUR but may slow European economic recovery.",
            "affected_assets": ["EURUSD", "EURINR", "European Equities"],
            "bullish_for": ["EURUSD", "EUR"],
            "bearish_for": ["European Growth Stocks"],
            "confidence": 0.82,
        },
    },
    {
        "headline": "China Factory Activity Contracts for Third Straight Month",
        "summary": "China's official manufacturing PMI fell to 49.0 in June, marking the third consecutive month of contraction and raising concerns about the global growth outlook.",
        "body": (
            "China's official manufacturing Purchasing Managers' Index dropped to 49.0 in June, "
            "below the 50-mark that separates expansion from contraction, signaling continued weakness "
            "in the world's second-largest economy.\n\n"
            "New orders fell to 48.3, the weakest since December, while export orders declined to "
            "47.5, suggesting softening global demand for Chinese goods. Employment continued to "
            "contract at 48.1.\n\n"
            "The data adds pressure on Beijing to roll out more aggressive stimulus measures. "
            "Analysts expect further cuts to the reserve requirement ratio and possibly the medium-term "
            "lending facility rate in coming weeks.\n\n"
            "Commodity prices reacted negatively, with copper falling 1.5% and iron ore dropping 2%. "
            "Asian markets traded lower on the news, though Indian markets showed relative resilience."
        ),
        "category": "GLOBAL",
        "importance": 78,
        "sentiment": "bearish",
        "publisher": "Reuters",
        "entities": ["China", "PMI", "Commodities", "COPPER"],
        "ai_analysis": {
            "what_happened": "China's manufacturing PMI fell to 49.0, contracting for the third straight month.",
            "why_it_matters": "Weak Chinese demand impacts global commodities and EM sentiment, though India is relatively insulated.",
            "affected_assets": ["COPPER", "Iron Ore", "Chinese Equities", "NIFTY"],
            "bullish_for": [],
            "bearish_for": ["COPPER", "Commodities", "Chinese Equities", "Metal Stocks"],
            "confidence": 0.85,
        },
    },
    {
        "headline": "Bank of Japan Raises Rates for Second Time, Yen Surges",
        "summary": "The Bank of Japan raised its policy rate to 0.25%, the second hike since ending negative rates in March, triggering a sharp yen rally.",
        "body": (
            "In a move that surprised many market participants, the Bank of Japan raised its policy "
            "rate to 0.25% from 0.10%, marking the second rate hike since the historic exit from "
            "negative rates in March 2024.\n\n"
            "Governor Kazuo Ueda cited improving wage growth and stable inflation above 2% as the "
            "rationale for the move. The BOJ also announced plans to halve its JGB purchases to "
            "about ¥3 trillion per month by early 2026.\n\n"
            "The Japanese yen surged over 2% to 152.50 against the dollar, its strongest level in "
            "eight weeks. Japanese bank stocks rallied 3-4%, while the broader Nikkei 225 fell 1.2% "
            "on concerns about the stronger yen's impact on exporters.\n\n"
            "The rate hike has implications for global carry trades, as the narrowing US-Japan rate "
            "differential makes yen-funded leveraged positions less attractive."
        ),
        "category": "GLOBAL",
        "importance": 84,
        "sentiment": "neutral",
        "publisher": "Bloomberg",
        "entities": ["BOJ", "JPY", "Nikkei", "JGB"],
        "ai_analysis": {
            "what_happened": "BOJ raised rates to 0.25% and signaled JGB purchase reduction; yen surged 2%.",
            "why_it_matters": "BOJ normalisation could unwind global carry trades and increase volatility in EM currencies.",
            "affected_assets": ["USDINR", "DXY", "Japanese Yen", "Nikkei"],
            "bullish_for": ["Japanese Yen", "Japanese Banks"],
            "bearish_for": ["Carry Trades", "DXY", "Nikkei Exporters"],
            "confidence": 0.87,
        },
    },
    # ── MACRO ──────────────────────────────────────────────
    {
        "headline": "India GDP Growth at 7.2%, Beats Expectations for FY24",
        "summary": "India's economy grew 7.2% in FY24, surpassing the advance estimate of 7.0%, driven by strong manufacturing and services performance.",
        "body": (
            "India's GDP growth for the full year FY24 came in at 7.2%, beating the advance estimate "
            "of 7.0% and reaffirming India's position as the fastest-growing major economy.\n\n"
            "Q4 FY24 growth was particularly strong at 7.8%, driven by a 9.9% expansion in "
            "manufacturing — the highest in 11 quarters — and 7.1% growth in the services sector. "
            "Agriculture growth remained subdued at 1.4% due to the El Niño impact.\n\n"
            "The government's capital expenditure push, which rose 28% to ₹9.5 lakh crore during "
            "the year, was a key driver of growth. Private consumption also recovered, growing "
            "4.0% after a weak 3.5% in FY23.\n\n"
            "The IMF projects India to grow 6.8% in FY25, maintaining its status as the world's "
            "fastest-growing major economy ahead of China's expected 4.6%."
        ),
        "category": "MACRO",
        "importance": 90,
        "sentiment": "bullish",
        "publisher": "Mint",
        "entities": ["India GDP", "Manufacturing", "Services"],
        "ai_analysis": {
            "what_happened": "India's FY24 GDP growth came in at 7.2%, beating the 7.0% advance estimate.",
            "why_it_matters": "India remains the fastest-growing major economy; strong manufacturing is a structural positive.",
            "affected_assets": ["NIFTY", "USDINR", "Government Bonds"],
            "bullish_for": ["NIFTY", "Indian Equities", "INR"],
            "bearish_for": [],
            "confidence": 0.90,
        },
    },
    {
        "headline": "CPI Inflation Falls to 4.1%, Within RBI's Target Band",
        "summary": "India's retail inflation eased to 4.1% in June from 4.5% in May, driven by moderation in food prices.",
        "body": (
            "India's Consumer Price Index (CPI) inflation eased to 4.1% in June, comfortably within "
            "the RBI's 2-6% target band and approaching the 4% medium-term target.\n\n"
            "Food inflation, which carries the highest weight in the CPI basket, moderated to 6.8% "
            "from 7.9% in May, aided by improved supply of vegetables and pulses. Core inflation "
            "(excluding food and fuel) fell to a record low of 3.1%.\n\n"
            "The data strengthens the case for the RBI to begin its rate-cutting cycle, with markets "
            "now pricing in a 70% probability of a cut at the October policy meeting.\n\n"
            "'The inflation trajectory is clearly moving in the right direction. A rate cut in October "
            "looks very likely now,' said the chief economist at ICICI Securities."
        ),
        "category": "MACRO",
        "importance": 87,
        "sentiment": "bullish",
        "publisher": "Economic Times",
        "entities": ["CPI", "RBI", "Inflation"],
        "ai_analysis": {
            "what_happened": "India CPI inflation fell to 4.1% in June; core inflation at record-low 3.1%.",
            "why_it_matters": "Strengthens the case for RBI rate cuts; positive for bond markets and rate-sensitive sectors.",
            "affected_assets": ["Government Bonds", "BANKNIFTY", "Real Estate", "NIFTY"],
            "bullish_for": ["Government Bonds", "Banking Stocks", "Real Estate", "Auto"],
            "bearish_for": [],
            "confidence": 0.88,
        },
    },
    {
        "headline": "India Manufacturing PMI Hits 12-Month High at 58.3",
        "summary": "India's manufacturing PMI rose to 58.3 in June, the highest in 12 months, signaling robust expansion in factory activity and new orders.",
        "body": (
            "India's S&P Global Manufacturing PMI surged to 58.3 in June, up from 57.5 in May and "
            "the highest reading in 12 months. The index has remained above the 50-expansion mark "
            "for 36 consecutive months.\n\n"
            "New orders grew at the fastest pace in 18 months, driven by strong domestic demand and "
            "a pickup in export orders. Employment also expanded for the fifth straight month.\n\n"
            "Input price pressures remained contained with the input cost index at its lowest since "
            "March, supporting manufacturer margins.\n\n"
            "The data underscores India's manufacturing resurgence, aided by the government's "
            "Production-Linked Incentive (PLI) schemes and the China+1 supply chain diversification "
            "trend benefiting Indian factories."
        ),
        "category": "MACRO",
        "importance": 80,
        "sentiment": "bullish",
        "publisher": "Reuters",
        "entities": ["PMI", "Manufacturing", "India"],
        "ai_analysis": {
            "what_happened": "India's manufacturing PMI rose to 58.3, the highest in 12 months; 36th month of expansion.",
            "why_it_matters": "Strong manufacturing PMI validates the India factory story and PLI scheme effectiveness.",
            "affected_assets": ["NIFTY", "Capital Goods", "Manufacturing Stocks"],
            "bullish_for": ["NIFTY", "Capital Goods Stocks", "Industrial ETFs"],
            "bearish_for": [],
            "confidence": 0.83,
        },
    },
    {
        "headline": "GST Collection Surpasses ₹2 Lakh Crore for First Time",
        "summary": "India's Goods and Services Tax collection hit a record ₹2.1 lakh crore in April, reflecting robust economic activity and improved compliance.",
        "body": (
            "India's Goods and Services Tax (GST) collection crossed the ₹2 lakh crore mark for "
            "the first time in April, reaching ₹2.10 lakh crore — a 12.4% increase over the "
            "year-ago period.\n\n"
            "The record collection was driven by strong consumption demand, improved tax compliance "
            "through technology-driven measures, and year-end purchases. Central GST accounted for "
            "₹43,846 crore while State GST was ₹54,179 crore.\n\n"
            "Integrated GST (IGST) collected was ₹1.01 lakh crore, of which ₹45,062 crore was from "
            "imports. The cess collection stood at ₹13,260 crore.\n\n"
            "'This is a milestone that reflects the strength of the Indian economy and the maturation "
            "of the GST system,' said the Revenue Secretary. The robust collection provides fiscal "
            "headroom for the government to boost capital spending."
        ),
        "category": "MACRO",
        "importance": 82,
        "sentiment": "bullish",
        "publisher": "Business Standard",
        "entities": ["GST", "Government Revenue", "Fiscal"],
        "ai_analysis": {
            "what_happened": "India's GST collection crossed ₹2 lakh crore for the first time in April.",
            "why_it_matters": "Record collection signals economic strength and provides fiscal room for government capex.",
            "affected_assets": ["NIFTY", "Government Bonds", "Infrastructure Stocks"],
            "bullish_for": ["Infrastructure", "Government Bonds", "NIFTY"],
            "bearish_for": [],
            "confidence": 0.81,
        },
    },
    {
        "headline": "FII Flows Turn Positive After Three-Month Outflow Streak",
        "summary": "Foreign institutional investors turned net buyers in Indian equities in July, investing ₹8,200 crore after three consecutive months of outflows totaling ₹34,000 crore.",
        "body": (
            "Foreign institutional investors (FIIs) reversed their selling streak in July, turning "
            "net buyers with inflows of ₹8,200 crore in the first two weeks of the month.\n\n"
            "The reversal comes after three months of relentless selling that saw FIIs pull out "
            "₹34,000 crore from Indian equities between April and June, primarily driven by "
            "election-related uncertainty and reallocation to Chinese markets.\n\n"
            "The renewed buying interest is attributed to the post-election policy continuity, "
            "strong corporate earnings, and expectations of US rate cuts improving EM attractiveness.\n\n"
            "Domestic institutional investors (DIIs) continued their strong buying with ₹15,600 crore "
            "of net purchases, supported by robust SIP inflows of ₹21,000 crore per month."
        ),
        "category": "MACRO",
        "importance": 83,
        "sentiment": "bullish",
        "publisher": "CNBCTV18",
        "entities": ["FII", "DII", "NIFTY", "SIP"],
        "ai_analysis": {
            "what_happened": "FIIs turned net buyers with ₹8,200 crore inflows after 3 months of ₹34,000 crore outflows.",
            "why_it_matters": "FII return signals renewed global confidence; DII flows provide structural support.",
            "affected_assets": ["NIFTY", "BANKNIFTY", "MIDCAP"],
            "bullish_for": ["NIFTY", "BANKNIFTY", "Largecap Stocks"],
            "bearish_for": [],
            "confidence": 0.85,
        },
    },
    # ── COMMODITIES ────────────────────────────────────────
    {
        "headline": "Gold Rallies to $2,380 on Safe Haven Demand Amid Geopolitical Tensions",
        "summary": "Gold prices surged 1.8% to $2,380 per ounce as escalating Middle East tensions and US election uncertainty drove investors to safe-haven assets.",
        "body": (
            "Gold prices rallied sharply on Wednesday, gaining 1.8% to trade at $2,380 per ounce — "
            "just 1.5% below the all-time high of $2,418 set in May.\n\n"
            "The surge was driven by escalating geopolitical tensions in the Middle East, with reports "
            "of renewed conflict between Israel and Hezbollah raising fears of a broader regional war. "
            "Uncertainty around the US presidential election also added to safe-haven demand.\n\n"
            "Central bank buying continues to provide structural support, with China, India, and "
            "Turkey collectively adding 290 tonnes to their reserves in the first half of 2024.\n\n"
            "In India, MCX gold futures rose to ₹72,450 per 10 grams, near record highs. Physical "
            "demand remains robust ahead of the festive season. Analysts at UBS maintain a year-end "
            "target of $2,500 per ounce."
        ),
        "category": "COMMODITIES",
        "importance": 82,
        "sentiment": "bullish",
        "publisher": "Reuters",
        "entities": ["GOLD", "MCX", "Safe Haven"],
        "ai_analysis": {
            "what_happened": "Gold surged 1.8% to $2,380 on geopolitical tensions and central bank buying.",
            "why_it_matters": "Safe-haven demand + central bank buying creates structural floor; year-end target $2,500.",
            "affected_assets": ["GOLD", "SILVER", "MCX Gold", "Mining Stocks"],
            "bullish_for": ["GOLD", "SILVER", "Gold ETFs", "Mining Stocks"],
            "bearish_for": ["DXY", "US Treasuries"],
            "confidence": 0.86,
        },
    },
    {
        "headline": "Crude Oil Jumps 3% on OPEC+ Decision to Extend Production Cuts",
        "summary": "Brent crude surged 3% to $85.40 after OPEC+ agreed to extend production cuts of 2.2 million barrels per day through Q3 2024.",
        "body": (
            "Brent crude oil prices jumped 3% to $85.40 per barrel after OPEC+ agreed to extend its "
            "voluntary production cuts of 2.2 million barrels per day through the third quarter of "
            "2024.\n\n"
            "Saudi Arabia will continue its additional voluntary cut of 1 million bpd, while Russia "
            "will maintain its 500,000 bpd cut. The group also signaled that any unwinding of cuts "
            "would be gradual and data-dependent.\n\n"
            "WTI crude also rose 2.8% to $81.50. India, which imports 85% of its crude oil needs, "
            "will face a higher import bill if prices sustain above $85. The country's oil import "
            "bill could rise by ₹15,000-20,000 crore per quarter for every $5 increase.\n\n"
            "Indian Oil Marketing Companies (OMCs) like BPCL, HPCL, and Indian Oil may face margin "
            "pressure if the government doesn't allow fuel price adjustments."
        ),
        "category": "COMMODITIES",
        "importance": 85,
        "sentiment": "bearish",
        "publisher": "Bloomberg",
        "entities": ["BRENT", "WTI", "OPEC+", "Indian OMCs"],
        "ai_analysis": {
            "what_happened": "OPEC+ extended 2.2M bpd production cuts through Q3; Brent surged 3% to $85.40.",
            "why_it_matters": "Higher oil prices negative for India's import bill and OMC margins; could push up inflation.",
            "affected_assets": ["BRENT", "WTI", "USDINR", "BPCL", "HPCL", "Indian Oil"],
            "bullish_for": ["BRENT", "WTI", "Oil Producers", "ONGC"],
            "bearish_for": ["Indian OMCs", "Airlines", "USDINR", "India CPI"],
            "confidence": 0.88,
        },
    },
    {
        "headline": "Silver Breaks Above $30 as Industrial Demand Surges",
        "summary": "Silver prices broke above the key $30 per ounce level for the first time since 2020, driven by surging solar panel demand and AI data center construction.",
        "body": (
            "Silver prices surged past the psychological $30 per ounce mark, trading at $30.45 — "
            "the highest level since February 2021. The precious metal has gained 28% year-to-date, "
            "outperforming gold.\n\n"
            "The rally is being driven by a unique combination of industrial and investment demand. "
            "Solar panel manufacturers consumed a record 161 million ounces in 2023, and demand is "
            "expected to rise another 20% in 2024 as global solar installations accelerate.\n\n"
            "The AI infrastructure boom is also supporting silver demand, as data centers require "
            "significant amounts of silver for electrical connectors and contacts. Each large-scale "
            "data center uses approximately 12,000 ounces of silver.\n\n"
            "In India, MCX silver futures hit ₹76,000 per kg. The silver market has been in a "
            "supply deficit for three consecutive years, with mine production unable to keep up "
            "with growing demand."
        ),
        "category": "COMMODITIES",
        "importance": 77,
        "sentiment": "bullish",
        "publisher": "Economic Times",
        "entities": ["SILVER", "MCX", "Solar", "Data Centers"],
        "ai_analysis": {
            "what_happened": "Silver broke above $30 for the first time since 2020; up 28% YTD on industrial demand.",
            "why_it_matters": "Structural supply deficit + solar/AI demand growth creates a multi-year bull case.",
            "affected_assets": ["SILVER", "MCX Silver", "Solar Stocks", "Silver ETFs"],
            "bullish_for": ["SILVER", "Silver Miners", "Solar Sector"],
            "bearish_for": [],
            "confidence": 0.82,
        },
    },
    {
        "headline": "Natural Gas Prices Surge 8% on Lower-Than-Expected Storage Build",
        "summary": "US natural gas futures jumped 8% after the EIA reported a storage injection of just 32 BCF, well below the 50 BCF expected by analysts.",
        "body": (
            "US natural gas prices surged 8% to $2.85 per MMBtu after the Energy Information "
            "Administration reported a storage injection of just 32 billion cubic feet for the "
            "previous week — significantly below the market consensus of 50 BCF.\n\n"
            "The lower-than-expected build was attributed to scorching heatwave conditions across "
            "the southern United States, driving up cooling demand for power generation. Gas-fired "
            "power generation hit a new daily record during the week.\n\n"
            "LNG export demand also remained strong, with US export terminals operating at near-full "
            "capacity. The upcoming startup of the Plaquemines LNG facility will add another 1.2 BCF/d "
            "of demand.\n\n"
            "The price spike has implications for Indian LNG importers like Petronet LNG and GAIL, "
            "as well as for city gas distribution companies like IGL and Mahanagar Gas."
        ),
        "category": "COMMODITIES",
        "importance": 72,
        "sentiment": "bullish",
        "publisher": "CNBCTV18",
        "entities": ["NATGAS", "LNG", "GAIL", "Petronet"],
        "ai_analysis": {
            "what_happened": "US natural gas surged 8% on lower-than-expected storage build of 32 BCF vs 50 BCF expected.",
            "why_it_matters": "Tight gas supply could push up LNG import costs for India; impacts city gas distributor margins.",
            "affected_assets": ["NATGAS", "Petronet LNG", "GAIL", "IGL"],
            "bullish_for": ["NATGAS", "US Gas Producers"],
            "bearish_for": ["Petronet LNG", "GAIL", "City Gas"],
            "confidence": 0.79,
        },
    },
    # ── CRYPTO ─────────────────────────────────────────────
    {
        "headline": "Bitcoin ETFs See Record $1.2B Single-Day Inflow After Fed Signal",
        "summary": "US spot Bitcoin ETFs recorded a record single-day net inflow of $1.2 billion following Fed Chair Powell's signal of imminent rate cuts.",
        "body": (
            "US spot Bitcoin ETFs attracted a record $1.2 billion in net inflows on Thursday, "
            "shattering the previous record of $886 million set in March.\n\n"
            "BlackRock's IBIT led the charge with $520 million in inflows, followed by Fidelity's "
            "FBTC at $310 million and Ark 21Shares' ARKB at $188 million. The surge came after "
            "Fed Chair Powell's congressional testimony signaled an imminent shift to rate cuts.\n\n"
            "Bitcoin surged to $68,500, its highest level in six weeks, as the liquidity outlook "
            "improved. Total assets under management in US spot Bitcoin ETFs now exceed $62 billion.\n\n"
            "'The ETF flows are fundamentally changing Bitcoin's supply-demand dynamics. With the "
            "halving reducing new supply by 50% and institutional demand accelerating, the setup is "
            "very constructive,' said the head of digital assets at Fidelity."
        ),
        "category": "CRYPTO",
        "importance": 83,
        "sentiment": "bullish",
        "publisher": "Bloomberg",
        "entities": ["BTC", "Bitcoin ETF", "BlackRock", "IBIT"],
        "ai_analysis": {
            "what_happened": "US spot Bitcoin ETFs saw record $1.2B daily inflow; BTC rose to $68,500.",
            "why_it_matters": "Institutional adoption accelerating post-halving; ETF AUM crossing $62B creates structural demand.",
            "affected_assets": ["BTC", "ETH", "Crypto Market", "MicroStrategy"],
            "bullish_for": ["BTC", "ETH", "Crypto Exchanges", "Mining Stocks"],
            "bearish_for": ["GOLD"],
            "confidence": 0.87,
        },
    },
    {
        "headline": "Ethereum Staking Yields Rise to 4.8% as Network Activity Surges",
        "summary": "Ethereum staking yields have risen to 4.8% as on-chain activity surges, with daily active addresses hitting a six-month high.",
        "body": (
            "Ethereum staking yields have climbed to 4.8%, the highest level since the Shanghai "
            "upgrade, as network activity reaches multi-month highs. Daily active addresses hit "
            "578,000 — a six-month high — driven by DeFi protocol activity and NFT market recovery.\n\n"
            "The rise in staking yields is attributed to increased transaction fees from heightened "
            "network usage. Gas fees averaged 35 gwei, up from 15 gwei a month ago. The ETH burn "
            "rate has also accelerated, making Ethereum deflationary again.\n\n"
            "The upcoming launch of spot Ethereum ETFs in the US is adding to bullish sentiment. "
            "The SEC approved 19b-4 filings from multiple issuers, with trading expected to begin "
            "within weeks.\n\n"
            "ETH prices rose 5.2% to $3,580. Analysts at Standard Chartered maintain a year-end "
            "target of $4,500, citing ETF inflows and improving fundamentals."
        ),
        "category": "CRYPTO",
        "importance": 78,
        "sentiment": "bullish",
        "publisher": "CNBCTV18",
        "entities": ["ETH", "Ethereum", "DeFi", "ETF"],
        "ai_analysis": {
            "what_happened": "ETH staking yields rose to 4.8%; daily active addresses hit 6-month high of 578K.",
            "why_it_matters": "Rising yields + upcoming ETH ETF launch creates a compelling investment case.",
            "affected_assets": ["ETH", "DeFi Tokens", "ETH ETFs"],
            "bullish_for": ["ETH", "DeFi Protocols", "Layer 2 Tokens"],
            "bearish_for": [],
            "confidence": 0.83,
        },
    },
    {
        "headline": "Solana TVL Surpasses $5B as DeFi and Memecoin Activity Explodes",
        "summary": "Solana's total value locked in DeFi protocols surpassed $5 billion for the first time, driven by a memecoin trading frenzy and new DeFi protocol launches.",
        "body": (
            "Solana's total value locked (TVL) in decentralized finance protocols crossed $5 billion "
            "for the first time, a 5x increase from the $1 billion low reached during the FTX collapse "
            "aftermath.\n\n"
            "The resurgence has been driven by a memecoin trading boom on platforms like pump.fun, "
            "which has generated over $50 million in fees, and the rapid growth of Solana-native DeFi "
            "protocols including Jupiter, Raydium, and Marinade Finance.\n\n"
            "Solana's high-speed, low-cost architecture has made it the preferred chain for retail "
            "traders. Daily transaction counts regularly exceed 50 million, far surpassing Ethereum.\n\n"
            "SOL price has rallied from $20 to $175 in the past 12 months. The Solana Foundation "
            "announced a $100 million ecosystem fund to accelerate DePIN and AI-related projects "
            "on the network."
        ),
        "category": "CRYPTO",
        "importance": 73,
        "sentiment": "bullish",
        "publisher": "Moneycontrol",
        "entities": ["SOL", "Solana", "DeFi", "Jupiter"],
        "ai_analysis": {
            "what_happened": "Solana TVL crossed $5B for the first time; 5x recovery from FTX-era lows.",
            "why_it_matters": "Solana emerging as Ethereum's primary competitor for DeFi and retail trading activity.",
            "affected_assets": ["SOL", "JUP", "RAY", "Solana Ecosystem"],
            "bullish_for": ["SOL", "Solana DeFi Tokens"],
            "bearish_for": ["Ethereum L2 Tokens"],
            "confidence": 0.78,
        },
    },
    {
        "headline": "India Crypto Tax Revenue Exceeds ₹1,000 Crore in FY24",
        "summary": "India collected over ₹1,000 crore in taxes from cryptocurrency transactions in FY24, driven by the 30% flat tax and 1% TDS on transfers.",
        "body": (
            "The Indian government collected over ₹1,000 crore in cryptocurrency-related taxes in "
            "FY24, a 52% increase from ₹660 crore in FY23, according to data from the Central Board "
            "of Direct Taxes.\n\n"
            "The revenue came from the 30% flat tax on gains from virtual digital assets (VDAs) and "
            "the 1% tax deducted at source (TDS) on all crypto transfers above ₹10,000.\n\n"
            "Despite the high tax rates, Indian crypto trading volumes have grown, with exchanges "
            "like CoinDCX, WazirX, and CoinSwitch reporting a combined 40% increase in trading "
            "activity. Bitcoin and Ethereum remain the most traded assets.\n\n"
            "Industry bodies are lobbying for a reduction in the TDS rate from 1% to 0.01%, arguing "
            "that the current rate drives traders to offshore exchanges and P2P platforms."
        ),
        "category": "CRYPTO",
        "importance": 68,
        "sentiment": "neutral",
        "publisher": "Economic Times",
        "entities": ["BTC", "ETH", "India Crypto", "Taxation"],
        "ai_analysis": {
            "what_happened": "India's crypto tax collection exceeded ₹1,000 crore in FY24, up 52% YoY.",
            "why_it_matters": "Growing tax revenue shows increasing crypto adoption despite high tax rates.",
            "affected_assets": ["BTC", "ETH", "Indian Crypto Exchanges"],
            "bullish_for": ["Crypto Adoption in India"],
            "bearish_for": ["Offshore Exchanges"],
            "confidence": 0.75,
        },
    },
    # ── Additional INDIA stories ───────────────────────────
    {
        "headline": "Bharti Airtel's 5G Subscriber Base Crosses 100 Million",
        "summary": "Bharti Airtel crossed the 100-million 5G subscriber milestone, making it the first Indian telco outside Jio to reach this mark.",
        "body": (
            "Bharti Airtel announced that its 5G subscriber base has crossed the 100 million mark, "
            "reaching the milestone within 18 months of its 5G launch.\n\n"
            "The company's 5G network now covers over 500 cities and towns, with plans to achieve "
            "pan-India coverage by December 2024. Airtel's 5G users consume an average of 25 GB "
            "per month, compared to 18 GB for 4G users.\n\n"
            "Management highlighted that 5G is driving ARPU growth, with 5G users showing 15-20% "
            "higher ARPU compared to 4G subscribers. The company expects industry-wide tariff hikes "
            "in the coming months.\n\n"
            "Airtel stock has gained 45% in the past year and commands a market cap of ₹8.5 lakh crore."
        ),
        "category": "INDIA",
        "importance": 76,
        "sentiment": "bullish",
        "publisher": "Business Standard",
        "entities": ["Bharti Airtel", "5G", "Telecom"],
        "ai_analysis": {
            "what_happened": "Airtel's 5G subscribers crossed 100M within 18 months of launch.",
            "why_it_matters": "Rapid 5G adoption drives ARPU growth; positions Airtel well for tariff hikes.",
            "affected_assets": ["Bharti Airtel", "Telecom Sector", "NIFTY"],
            "bullish_for": ["Bharti Airtel", "Telecom Sector"],
            "bearish_for": ["Vodafone Idea"],
            "confidence": 0.82,
        },
    },
    {
        "headline": "Coal India Announces Record Dividend of ₹25 Per Share",
        "summary": "Coal India declared a total dividend of ₹25 per share for FY24, the highest in its history, translating to a 6.2% dividend yield.",
        "body": (
            "Coal India Limited declared a record final dividend of ₹15 per share, taking the total "
            "FY24 payout to ₹25 per share — the highest ever. At the current market price of ₹403, "
            "this translates to an attractive dividend yield of 6.2%.\n\n"
            "The generous payout was supported by a strong FY24 performance, with net profit rising "
            "8% to ₹37,369 crore. Coal production hit a record 773 million tonnes, up 10% YoY.\n\n"
            "Despite the renewable energy transition narrative, coal demand in India remains robust, "
            "driven by strong power demand growth of 7-8% annually. Coal India maintains a market "
            "share of over 80% in domestic coal production.\n\n"
            "'Coal India remains one of the best dividend plays in Indian markets,' said analysts "
            "at Jefferies, maintaining a Buy rating with a target price of ₹500."
        ),
        "category": "INDIA",
        "importance": 70,
        "sentiment": "bullish",
        "publisher": "Livemint",
        "entities": ["Coal India", "Dividends", "Mining"],
        "ai_analysis": {
            "what_happened": "Coal India declared record ₹25/share dividend, yielding 6.2% at current prices.",
            "why_it_matters": "Record dividend reflects strong fundamentals; coal demand robust despite green transition narrative.",
            "affected_assets": ["Coal India", "PSU Stocks", "Mining Sector"],
            "bullish_for": ["Coal India", "Dividend Investors"],
            "bearish_for": [],
            "confidence": 0.80,
        },
    },
    # ── Additional GLOBAL stories ──────────────────────────
    {
        "headline": "US Tech Rally Pushes Nasdaq to Record High Above 18,000",
        "summary": "The Nasdaq Composite surged past 18,000 for the first time, driven by AI-related optimism and strong earnings from semiconductor companies.",
        "body": (
            "The Nasdaq Composite index surged to a record close of 18,028, crossing the 18,000 mark "
            "for the first time, as artificial intelligence euphoria continued to drive tech stocks "
            "higher.\n\n"
            "NVIDIA led the charge with a 5.2% gain after raising its full-year revenue guidance "
            "by $3 billion, citing 'unprecedented demand' for its AI training chips. The stock's "
            "market capitalisation crossed $3.2 trillion, making it the world's most valuable company.\n\n"
            "Other AI beneficiaries including AMD (+3.8%), Microsoft (+2.1%), and Alphabet (+1.9%) "
            "also contributed to the rally. The Magnificent Seven stocks now account for 31% of the "
            "S&P 500's total market capitalisation.\n\n"
            "The AI trade continues to have spillover effects on Indian IT services companies, which "
            "are seeing increased demand for AI integration and consulting services."
        ),
        "category": "GLOBAL",
        "importance": 80,
        "sentiment": "bullish",
        "publisher": "Bloomberg",
        "entities": ["Nasdaq", "NVIDIA", "AI", "Tech"],
        "ai_analysis": {
            "what_happened": "Nasdaq crossed 18,000 for the first time; NVIDIA became the world's most valuable company at $3.2T.",
            "why_it_matters": "AI investment cycle accelerating; spillover benefits for Indian IT services sector.",
            "affected_assets": ["Nasdaq", "NVIDIA", "Indian IT", "TCS", "Infosys"],
            "bullish_for": ["Tech Stocks", "Indian IT", "Semiconductor"],
            "bearish_for": [],
            "confidence": 0.85,
        },
    },
    {
        "headline": "UK Inflation Returns to Bank of England's 2% Target",
        "summary": "UK CPI inflation fell to 2.0% in June, hitting the Bank of England's target for the first time since July 2021 and raising rate cut expectations.",
        "body": (
            "UK consumer price inflation fell to 2.0% in June, matching the Bank of England's target "
            "for the first time in nearly three years. Core CPI also declined to 3.5% from 3.9%.\n\n"
            "The drop was driven by easing food prices and falling energy costs. However, services "
            "inflation remained sticky at 5.7%, which may give the BoE pause before cutting rates.\n\n"
            "Markets are now pricing in a 55% probability of a rate cut at the August meeting, up "
            "from 40% before the data release. The pound weakened slightly to 1.2920 against the "
            "dollar on the rate-cut expectations.\n\n"
            "The data has implications for Indian markets through the GBPINR cross rate, which eased "
            "to 105.60, and through sentiment effects on global rate-cut expectations."
        ),
        "category": "GLOBAL",
        "importance": 72,
        "sentiment": "neutral",
        "publisher": "Reuters",
        "entities": ["UK CPI", "BOE", "GBP", "GBPINR"],
        "ai_analysis": {
            "what_happened": "UK CPI hit BoE's 2% target for the first time since July 2021.",
            "why_it_matters": "Supports global rate-cut narrative; slightly bearish for GBP but positive for risk assets.",
            "affected_assets": ["GBPINR", "GBP", "UK Equities"],
            "bullish_for": ["UK Equities", "Global Risk Assets"],
            "bearish_for": ["GBP"],
            "confidence": 0.79,
        },
    },
    # ── Additional MACRO stories ───────────────────────────
    {
        "headline": "India's Forex Reserves Hit All-Time High of $670 Billion",
        "summary": "India's foreign exchange reserves surged to a record $670 billion, providing 11 months of import cover and strengthening the RBI's war chest.",
        "body": (
            "India's foreign exchange reserves climbed to a record $670.12 billion in the week ended "
            "July 12, rising $4.3 billion from the previous week. The reserves now provide "
            "approximately 11 months of import cover.\n\n"
            "The increase was driven by valuation gains on non-dollar assets, continued FII inflows, "
            "and the RBI's proactive forex accumulation strategy. Foreign currency assets, the largest "
            "component, stood at $589 billion.\n\n"
            "Gold reserves also rose to $57.6 billion, reflecting both price appreciation and the "
            "RBI's ongoing gold purchases as part of its reserve diversification strategy.\n\n"
            "The strong reserve position provides India with a significant buffer against external "
            "shocks and currency volatility, ranking it as the fourth-largest forex reserve holder "
            "globally after China, Japan, and Switzerland."
        ),
        "category": "MACRO",
        "importance": 79,
        "sentiment": "bullish",
        "publisher": "Mint",
        "entities": ["Forex Reserves", "RBI", "USDINR"],
        "ai_analysis": {
            "what_happened": "India's forex reserves hit a record $670 billion, providing 11 months of import cover.",
            "why_it_matters": "Record reserves strengthen India's external position and provide buffer against currency volatility.",
            "affected_assets": ["USDINR", "Government Bonds", "NIFTY"],
            "bullish_for": ["USDINR Stability", "Indian Bonds", "INR"],
            "bearish_for": [],
            "confidence": 0.84,
        },
    },
    {
        "headline": "India's Trade Deficit Widens to $24.2 Billion in June",
        "summary": "India's merchandise trade deficit widened to $24.2 billion in June from $20.1 billion in May, driven by higher crude oil and gold imports.",
        "body": (
            "India's merchandise trade deficit widened to $24.2 billion in June, the highest in "
            "ten months, primarily due to a surge in crude oil and gold imports.\n\n"
            "Imports rose 11% year-on-year to $60.3 billion, with crude oil imports jumping 18% "
            "to $17.2 billion on higher global prices. Gold imports surged 65% to $3.8 billion "
            "ahead of the festive season.\n\n"
            "Exports remained resilient, growing 5% to $36.1 billion, led by engineering goods, "
            "chemicals, and electronics. However, textile and gem & jewellery exports declined.\n\n"
            "The wider trade deficit puts mild pressure on the rupee, though strong services exports "
            "and remittance inflows are expected to keep the current account deficit manageable at "
            "1.2-1.5% of GDP for FY25."
        ),
        "category": "MACRO",
        "importance": 75,
        "sentiment": "bearish",
        "publisher": "Business Standard",
        "entities": ["Trade Deficit", "Imports", "Exports", "USDINR"],
        "ai_analysis": {
            "what_happened": "India's trade deficit widened to $24.2B in June from $20.1B in May.",
            "why_it_matters": "Higher crude and gold imports widen deficit; mild INR pressure but manageable at macro level.",
            "affected_assets": ["USDINR", "Current Account", "OMCs"],
            "bullish_for": [],
            "bearish_for": ["USDINR", "OMCs", "Airlines"],
            "confidence": 0.78,
        },
    },
    # ── Additional COMMODITIES stories ─────────────────────
    {
        "headline": "Iron Ore Drops Below $100 on China Steel Production Curbs",
        "summary": "Iron ore futures fell below $100 per tonne for the first time since March as China announced production limits at steel mills to meet emission targets.",
        "body": (
            "Iron ore futures dropped 3.2% to $97.50 per tonne, falling below the key $100 level "
            "for the first time since March, after China's Ministry of Industry announced production "
            "cuts at major steel mills.\n\n"
            "The government ordered steel production to be capped at last year's levels of 1.019 "
            "billion tonnes, as part of its commitment to peak carbon emissions by 2030. Several "
            "provinces have already started implementing output restrictions.\n\n"
            "Port inventories in China rose to 148 million tonnes, the highest since 2022, adding "
            "to the bearish sentiment. Australian and Brazilian miners' stocks fell 2-4%.\n\n"
            "Indian steel companies like Tata Steel and JSW Steel may face mixed impacts — lower "
            "raw material costs benefit margins, but weak Chinese demand could impact export prices."
        ),
        "category": "COMMODITIES",
        "importance": 74,
        "sentiment": "bearish",
        "publisher": "Reuters",
        "entities": ["Iron Ore", "China Steel", "Tata Steel", "JSW Steel"],
        "ai_analysis": {
            "what_happened": "Iron ore fell below $100/tonne on China steel production curbs and rising port inventories.",
            "why_it_matters": "Lower iron ore prices benefit Indian steel margins but signal weak Chinese industrial demand.",
            "affected_assets": ["Iron Ore", "Tata Steel", "JSW Steel", "NMDC"],
            "bullish_for": ["Tata Steel Margins", "JSW Steel Margins"],
            "bearish_for": ["NMDC", "Iron Ore Miners", "Australian Miners"],
            "confidence": 0.81,
        },
    },
    # ── More NEWS / TOP ────────────────────────────────────
    {
        "headline": "SEBI Tightens F&O Rules, Raises Lot Sizes to Curb Speculation",
        "summary": "SEBI announced new regulations for the derivatives segment, including higher lot sizes and stricter margin requirements, aimed at curbing retail speculation.",
        "body": (
            "The Securities and Exchange Board of India (SEBI) unveiled a comprehensive set of "
            "measures to regulate the derivatives segment, responding to data showing that 89% "
            "of individual traders lost money in F&O trading.\n\n"
            "Key changes include: lot sizes for index options will be increased to ensure a minimum "
            "contract value of ₹15 lakh (up from ₹5-7 lakh currently); weekly expiries will be "
            "limited to one per exchange; and extreme out-of-the-money option writing will face "
            "higher margin requirements.\n\n"
            "The measures will be implemented in a phased manner over the next three months. SEBI "
            "also mandated that exchanges improve risk disclosures and provide loss/profit statements "
            "to traders on a monthly basis.\n\n"
            "The brokerage industry reacted negatively, with stocks of Zerodha's parent, Angel One, "
            "and ICICI Securities falling 5-8%. However, institutional traders welcomed the move as "
            "it should improve market quality."
        ),
        "category": "TOP",
        "importance": 88,
        "sentiment": "bearish",
        "publisher": "Moneycontrol",
        "entities": ["SEBI", "F&O", "NSE", "BSE"],
        "ai_analysis": {
            "what_happened": "SEBI raised F&O lot sizes, limited weekly expiries, and tightened margins to curb retail speculation.",
            "why_it_matters": "Structural change for India's derivatives market; negative for discount brokers but positive for market quality.",
            "affected_assets": ["Angel One", "ICICI Securities", "NSE Volume", "NIFTY Options"],
            "bullish_for": ["Market Quality", "Institutional Trading"],
            "bearish_for": ["Discount Brokers", "Angel One", "F&O Volumes"],
            "confidence": 0.90,
        },
    },
    {
        "headline": "SBI Reports Highest-Ever Annual Profit of ₹61,077 Crore",
        "summary": "State Bank of India posted a record annual net profit of ₹61,077 crore for FY24, up 21% year-on-year, with asset quality at its best in over a decade.",
        "body": (
            "State Bank of India, the country's largest lender, reported its highest-ever annual "
            "net profit of ₹61,077 crore for FY24, representing a 21% growth over FY23.\n\n"
            "Asset quality improved significantly with gross NPA ratio declining to 2.24% from 2.78% "
            "a year ago, the best level in over a decade. Net NPA ratio fell to 0.57%.\n\n"
            "Net interest income grew 18% to ₹1.63 lakh crore, while net interest margin remained "
            "stable at 3.28%. Domestic advances grew 16% with retail loans leading at 19% growth.\n\n"
            "The board declared a dividend of ₹13.7 per share, up from ₹11.3 in FY23. SBI's market "
            "capitalisation crossed ₹7 lakh crore for the first time during the year."
        ),
        "category": "INDIA",
        "importance": 84,
        "sentiment": "bullish",
        "publisher": "Economic Times",
        "entities": ["SBI", "Banking", "PSU Banks"],
        "ai_analysis": {
            "what_happened": "SBI posted record annual profit of ₹61,077 crore; GNPAs at decade-best 2.24%.",
            "why_it_matters": "India's largest bank firing on all cylinders validates the banking sector re-rating thesis.",
            "affected_assets": ["SBI", "BANKNIFTY", "PSU Bank Index"],
            "bullish_for": ["SBI", "PSU Banks", "BANKNIFTY"],
            "bearish_for": [],
            "confidence": 0.89,
        },
    },
    # ── Additional stories to reach 50+ ────────────────────
    {
        "headline": "India's Semiconductor Mission Attracts $15 Billion in New Investments",
        "summary": "Three new semiconductor fabrication plants have been approved under India's semiconductor mission, bringing total committed investments to $15 billion.",
        "body": (
            "India's semiconductor manufacturing ambitions received a major boost as the government "
            "approved three new fabrication and packaging plants, bringing total committed investments "
            "in the sector to $15 billion.\n\n"
            "Tata Electronics will build a semiconductor fab in Dholera, Gujarat, with an investment "
            "of $11 billion in partnership with PSMC of Taiwan. CG Power and Kaynes Technology will "
            "set up OSAT (Outsourced Semiconductor Assembly and Test) facilities.\n\n"
            "The government is providing incentives covering 50% of project costs under the India "
            "Semiconductor Mission. The plants are expected to create over 100,000 direct and "
            "indirect jobs.\n\n"
            "'India's semiconductor ecosystem is taking shape faster than expected. These investments "
            "will reduce our import dependency and position India in the global chip supply chain,' "
            "said the IT Minister."
        ),
        "category": "INDIA",
        "importance": 82,
        "sentiment": "bullish",
        "publisher": "Mint",
        "entities": ["Semiconductors", "Tata Electronics", "CG Power", "Kaynes"],
        "ai_analysis": {
            "what_happened": "Three new semiconductor plants approved; total sector investment commitments reach $15 billion.",
            "why_it_matters": "India entering global chip supply chain; long-term positive for electronics manufacturing.",
            "affected_assets": ["CG Power", "Kaynes Technology", "NIFTY IT"],
            "bullish_for": ["CG Power", "Kaynes", "Electronics Manufacturing"],
            "bearish_for": [],
            "confidence": 0.83,
        },
    },
    {
        "headline": "Copper Prices Hit Two-Year High on AI Data Center Demand",
        "summary": "Copper prices surged to a two-year high of $4.65 per pound, driven by surging demand from AI data center construction and tight mine supply.",
        "body": (
            "Copper prices rallied to $4.65 per pound, the highest level since April 2022, as a "
            "potent combination of supply constraints and AI-driven demand lifted the industrial metal.\n\n"
            "Goldman Sachs estimates that each large AI data center requires 30,000-50,000 tonnes of "
            "copper for electrical wiring, cooling systems, and power distribution. With over 200 "
            "hyperscale data centers planned globally, this represents significant incremental demand.\n\n"
            "On the supply side, major mines in Chile and Peru have reported lower production due to "
            "water scarcity and labour disputes. Global mine supply growth is expected at just 1-2% "
            "in 2024, well below demand growth of 3-4%.\n\n"
            "In India, Hindustan Copper and Vedanta are the primary beneficiaries of higher copper "
            "prices, with both stocks trading near 52-week highs."
        ),
        "category": "COMMODITIES",
        "importance": 76,
        "sentiment": "bullish",
        "publisher": "Bloomberg",
        "entities": ["COPPER", "AI", "Data Centers", "Hindustan Copper"],
        "ai_analysis": {
            "what_happened": "Copper hit a two-year high of $4.65/lb on AI data center demand and tight mine supply.",
            "why_it_matters": "AI infrastructure buildout creating structural demand shift for copper; supply unable to keep up.",
            "affected_assets": ["COPPER", "Hindustan Copper", "Vedanta", "Mining"],
            "bullish_for": ["COPPER", "Hindustan Copper", "Vedanta"],
            "bearish_for": ["Electronics Manufacturers", "Power Utilities"],
            "confidence": 0.82,
        },
    },
    {
        "headline": "Wipro Bags Major Healthcare AI Deal Worth $500 Million",
        "summary": "Wipro secured a $500 million multi-year deal with a leading US healthcare provider for AI-powered clinical decision support and digital transformation.",
        "body": (
            "Wipro announced its largest-ever deal worth $500 million with a major US healthcare "
            "system for AI-powered clinical decision support, electronic health records modernization, "
            "and cloud infrastructure transformation.\n\n"
            "The seven-year engagement will see Wipro deploy large language models for clinical "
            "documentation, develop predictive analytics for patient outcomes, and migrate legacy "
            "systems to cloud-native architectures.\n\n"
            "This deal underscores the growing opportunity for Indian IT companies in healthcare AI, "
            "a market estimated at $45 billion by 2028. Wipro has invested heavily in AI capabilities, "
            "training over 70,000 employees on generative AI tools.\n\n"
            "'Healthcare AI is a massive opportunity and we are well-positioned to capitalize,' said "
            "Wipro CEO Thierry Delaporte. The stock gained 3.5% on the announcement."
        ),
        "category": "INDIA",
        "importance": 75,
        "sentiment": "bullish",
        "publisher": "CNBCTV18",
        "entities": ["Wipro", "Healthcare AI", "IT Services"],
        "ai_analysis": {
            "what_happened": "Wipro won $500M healthcare AI deal; largest deal in company history.",
            "why_it_matters": "Validates Indian IT's AI pivot; healthcare AI market expected to reach $45B by 2028.",
            "affected_assets": ["Wipro", "NIFTY IT", "Healthcare AI"],
            "bullish_for": ["Wipro", "IT Services Sector"],
            "bearish_for": [],
            "confidence": 0.80,
        },
    },
    {
        "headline": "India's UPI Transactions Cross 14 Billion in Single Month",
        "summary": "Unified Payments Interface (UPI) transactions exceeded 14 billion in June 2024, processing ₹20.07 lakh crore in value — both record highs.",
        "body": (
            "India's UPI digital payments platform set new records in June 2024, processing 14.04 "
            "billion transactions worth ₹20.07 lakh crore — representing year-on-year growth of "
            "49% in volume and 35% in value.\n\n"
            "PhonePe maintained its market leadership with a 48% share, followed by Google Pay at "
            "36% and Paytm at 8%. The NPCI has set a target of 100 billion annual UPI transactions "
            "by 2027.\n\n"
            "International expansion continued with UPI now accepted in 7 countries including "
            "Singapore, France, UAE, and Sri Lanka. Cross-border UPI transactions grew 300% YoY.\n\n"
            "The robust growth validates the digital payments thesis for Indian fintech companies "
            "and banks with strong digital infrastructure."
        ),
        "category": "INDIA",
        "importance": 73,
        "sentiment": "bullish",
        "publisher": "Livemint",
        "entities": ["UPI", "PhonePe", "Digital Payments", "NPCI"],
        "ai_analysis": {
            "what_happened": "UPI processed 14B+ transactions worth ₹20.07 lakh crore in June; both record highs.",
            "why_it_matters": "India's digital payments infrastructure is world-leading; validates fintech investment thesis.",
            "affected_assets": ["Paytm", "PhonePe", "Banking Stocks"],
            "bullish_for": ["Digital Payments", "Fintech", "Banking"],
            "bearish_for": [],
            "confidence": 0.81,
        },
    },
    {
        "headline": "Global Bond Rally Intensifies as Rate Cut Expectations Build",
        "summary": "Global bond yields fell sharply as multiple central banks signaled rate cuts, with the Bloomberg Global Aggregate Bond Index posting its best weekly gain since March.",
        "body": (
            "Global bond markets rallied sharply as synchronized rate-cut expectations built across "
            "major economies. The Bloomberg Global Aggregate Bond Index posted its best weekly gain "
            "since March 2023.\n\n"
            "US 10-year Treasury yields fell 15 basis points to 4.15%, German Bund yields dropped "
            "to 2.35%, and UK Gilt yields eased to 4.05%. Indian 10-year government bond yields "
            "also declined 8 bps to 6.97%.\n\n"
            "The rally was triggered by a confluence of factors: the Fed's dovish pivot, ECB's data-"
            "dependent approach, and Bank of England's move closer to cutting. EM bonds outperformed "
            "as falling US yields improve relative attractiveness.\n\n"
            "India's bond market saw strong FII buying of ₹4,200 crore in government bonds, "
            "supported by the country's recent inclusion in JP Morgan's GBI-EM Global Bond Index."
        ),
        "category": "GLOBAL",
        "importance": 79,
        "sentiment": "bullish",
        "publisher": "Bloomberg",
        "entities": ["Bonds", "US Treasuries", "India Bonds"],
        "ai_analysis": {
            "what_happened": "Global bond rally as US, ECB, BoE signal rate cuts; India 10Y yield at 6.97%.",
            "why_it_matters": "Synchronized global easing cycle ahead; India bonds benefit from JPM index inclusion.",
            "affected_assets": ["Government Bonds", "USDINR", "NIFTY"],
            "bullish_for": ["Government Bonds", "REITs", "Rate-Sensitive Sectors"],
            "bearish_for": ["Bank NIMs"],
            "confidence": 0.84,
        },
    },
    {
        "headline": "Tesla Reports Record Deliveries, Stock Surges 12%",
        "summary": "Tesla delivered a record 466,000 vehicles in Q2, beating expectations of 440,000 and ending concerns about demand destruction. The stock surged 12%.",
        "body": (
            "Tesla reported record quarterly deliveries of 466,140 vehicles in Q2 2024, handily "
            "beating the consensus estimate of 440,000 and allaying fears of demand weakness.\n\n"
            "Model Y continued to dominate with over 400,000 units delivered, while the Cybertruck "
            "contributed 24,000 units in its first full quarter of production. Energy storage "
            "deployments also hit a record 9.4 GWh.\n\n"
            "CEO Elon Musk credited price cuts and improved manufacturing efficiency for the "
            "beat, noting that automotive gross margins improved to 18.3% from 17.4% in Q1.\n\n"
            "Tesla shares surged 12% to $256 in after-hours trading. Indian EV companies like "
            "Tata Motors EV, Ola Electric, and M&M's EV division also saw positive sentiment."
        ),
        "category": "GLOBAL",
        "importance": 76,
        "sentiment": "bullish",
        "publisher": "Reuters",
        "entities": ["Tesla", "EV", "Tata Motors EV"],
        "ai_analysis": {
            "what_happened": "Tesla delivered record 466K vehicles in Q2, beating estimates by 6%.",
            "why_it_matters": "Demand concerns eased; positive read-through for global EV ecosystem including Indian EV plays.",
            "affected_assets": ["Tesla", "Tata Motors EV", "EV Sector"],
            "bullish_for": ["Tesla", "EV Sector", "Lithium"],
            "bearish_for": ["Legacy Automakers"],
            "confidence": 0.82,
        },
    },
    {
        "headline": "Saudi Aramco IPO of Gas Assets Valued at $12 Billion",
        "summary": "Saudi Aramco is preparing an IPO of its gas assets on the Riyadh stock exchange, with an expected valuation of $12 billion in the largest listing since its own IPO.",
        "body": (
            "Saudi Aramco is preparing to list its gas pipeline assets on the Tadawul exchange in "
            "what would be the largest IPO in the Middle East since Aramco's own landmark listing in "
            "2019. The offering is expected to raise $12 billion.\n\n"
            "The gas unit holds Aramco's vast unconventional gas reserves in the Jafurah basin, "
            "estimated at 200 trillion cubic feet. The listing is part of Saudi Arabia's Vision 2030 "
            "strategy to diversify away from oil revenue.\n\n"
            "The IPO has attracted interest from global sovereign wealth funds, including GIC and "
            "ADIA, as well as leading pension funds. Proceeds will fund Aramco's $50 billion gas "
            "expansion program.\n\n"
            "The listing could have implications for global natural gas markets and Indian LNG import "
            "costs, as Aramco's expanded gas production could ease supply constraints."
        ),
        "category": "GLOBAL",
        "importance": 74,
        "sentiment": "neutral",
        "publisher": "Bloomberg",
        "entities": ["Saudi Aramco", "Gas", "IPO"],
        "ai_analysis": {
            "what_happened": "Saudi Aramco planning $12B gas assets IPO on Tadawul exchange.",
            "why_it_matters": "Expanded gas production could ease global supply and benefit Indian LNG importers long-term.",
            "affected_assets": ["NATGAS", "LNG", "Petronet LNG", "GAIL"],
            "bullish_for": ["Petronet LNG", "GAIL", "Gas Consumers"],
            "bearish_for": ["NATGAS Prices"],
            "confidence": 0.74,
        },
    },
    {
        "headline": "Paytm Receives RBI Approval for Revised Payment Bank Operations",
        "summary": "Paytm received conditional approval from the RBI to resume certain payment bank operations, ending months of regulatory uncertainty.",
        "body": (
            "One97 Communications, parent of Paytm, received conditional approval from the Reserve "
            "Bank of India to resume select operations at Paytm Payments Bank Limited (PPBL).\n\n"
            "The approval allows PPBL to resume UPI transactions through its own handle, accept "
            "deposits up to ₹1 lakh, and process merchant settlements — operations that had been "
            "curtailed following RBI's action in January 2024.\n\n"
            "However, several conditions remain, including enhanced KYC compliance for all accounts, "
            "regular audits by an RBI-appointed firm, and restrictions on new savings account openings.\n\n"
            "Paytm shares surged 15% on the news. CEO Vijay Shekhar Sharma said 'This marks a new "
            "beginning for Paytm. We are committed to the highest standards of compliance.'"
        ),
        "category": "INDIA",
        "importance": 80,
        "sentiment": "bullish",
        "publisher": "Moneycontrol",
        "entities": ["Paytm", "RBI", "Payments Bank"],
        "ai_analysis": {
            "what_happened": "Paytm received conditional RBI approval to resume payment bank operations.",
            "why_it_matters": "Regulatory overhang lifting; key for Paytm's UPI market share recovery and monetization.",
            "affected_assets": ["Paytm", "Fintech", "Digital Payments"],
            "bullish_for": ["Paytm", "Fintech Sector"],
            "bearish_for": [],
            "confidence": 0.83,
        },
    },
    {
        "headline": "Oil India Discovers New Gas Reserve Estimated at 25 TCF",
        "summary": "Oil India Limited announced a significant natural gas discovery in Assam's KG Basin estimated at 25 trillion cubic feet, potentially doubling the company's reserves.",
        "body": (
            "Oil India Limited announced a potentially transformative natural gas discovery in the "
            "Krishna-Godavari (KG) Basin area of Assam, with initial estimates suggesting reserves "
            "of approximately 25 trillion cubic feet (TCF).\n\n"
            "If confirmed, this would be one of India's largest onshore gas discoveries in two "
            "decades and could potentially double Oil India's current proven reserves. The company "
            "has commenced detailed appraisal drilling.\n\n"
            "At current gas prices of $10-12/MMBtu, the discovery could be worth over $75 billion "
            "over the life of the field. Production could begin within 3-4 years, adding significantly "
            "to India's domestic gas production.\n\n"
            "Oil India shares surged 8% on the announcement. 'This discovery could be a game-changer "
            "for India's energy security,' said the company's CMD."
        ),
        "category": "INDIA",
        "importance": 79,
        "sentiment": "bullish",
        "publisher": "Economic Times",
        "entities": ["Oil India", "Natural Gas", "Energy"],
        "ai_analysis": {
            "what_happened": "Oil India discovered 25 TCF gas reserve in Assam; could double company reserves.",
            "why_it_matters": "Potentially transformative for India's energy security; reduces LNG import dependency.",
            "affected_assets": ["Oil India", "GAIL", "NATGAS", "Energy Sector"],
            "bullish_for": ["Oil India", "GAIL", "Energy Security"],
            "bearish_for": ["LNG Importers"],
            "confidence": 0.77,
        },
    },
    {
        "headline": "Crypto Market Cap Crosses $2.8 Trillion as Altcoin Season Begins",
        "summary": "Total crypto market capitalisation crossed $2.8 trillion with altcoins outperforming Bitcoin for the first time in six months, signaling the start of 'altseason'.",
        "body": (
            "The total cryptocurrency market capitalisation crossed $2.8 trillion for the first "
            "time since 2021, with altcoins outperforming Bitcoin for the first time in six months.\n\n"
            "Ethereum gained 8.2%, Solana surged 12.5%, and smaller altcoins like Avalanche (+15%), "
            "Chainlink (+11%), and Render (+18%) posted even stronger gains. Bitcoin dominance fell "
            "from 54% to 51%, a classic indicator of altseason rotation.\n\n"
            "The rally was fueled by the Ethereum ETF approval, improving macro conditions, and "
            "growing institutional adoption across the crypto ecosystem.\n\n"
            "In India, WazirX reported a 45% spike in altcoin trading volumes. CoinDCX launched "
            "five new token listings in response to growing retail demand for altcoins."
        ),
        "category": "CRYPTO",
        "importance": 75,
        "sentiment": "bullish",
        "publisher": "CNBCTV18",
        "entities": ["BTC", "ETH", "SOL", "Altcoins"],
        "ai_analysis": {
            "what_happened": "Crypto market cap crossed $2.8T; altcoins outperforming BTC for first time in 6 months.",
            "why_it_matters": "Altseason rotation signals broadening crypto rally; institutional adoption expanding beyond BTC.",
            "affected_assets": ["ETH", "SOL", "BNB", "Altcoins"],
            "bullish_for": ["ETH", "SOL", "BNB", "Altcoins"],
            "bearish_for": ["BTC Dominance"],
            "confidence": 0.79,
        },
    },
    {
        "headline": "India's Power Demand Hits Record 250 GW Peak; Grid Remains Stable",
        "summary": "India's electricity demand touched an all-time peak of 250 GW on a sweltering June day, but the national grid held firm with no load shedding reported.",
        "body": (
            "India's power grid handled a record peak demand of 250 GW on June 28 as temperatures "
            "soared above 47°C across northern India, a 7% increase over last year's peak of 234 GW.\n\n"
            "The grid's ability to meet this unprecedented demand without any load shedding marks "
            "a significant achievement for India's power infrastructure. Renewable energy contributed "
            "72 GW (29%) of the peak supply, including 52 GW from solar.\n\n"
            "Coal-fired plants operated at 78% capacity utilisation, while gas plants ran at near-full "
            "capacity. Power exchanges saw prices spike to ₹9.50/kWh on the spot market, up from "
            "the average of ₹3.50/kWh.\n\n"
            "The sustained demand growth reinforces the investment case for power generation, "
            "transmission, and distribution companies, as India needs to add 80 GW of capacity by 2030."
        ),
        "category": "INDIA",
        "importance": 74,
        "sentiment": "bullish",
        "publisher": "Mint",
        "entities": ["Power Demand", "NTPC", "Power Grid", "Solar"],
        "ai_analysis": {
            "what_happened": "India's power demand hit record 250 GW peak; grid stable with no load shedding.",
            "why_it_matters": "Growing power demand validates investment in generation and T&D; solar now 29% of peak supply.",
            "affected_assets": ["NTPC", "Power Grid", "Tata Power", "Adani Green"],
            "bullish_for": ["Power Utilities", "NTPC", "Power Grid", "Solar"],
            "bearish_for": [],
            "confidence": 0.81,
        },
    },
    {
        "headline": "L&T Wins ₹45,000 Crore Mega Order for Saudi Arabia Giga Projects",
        "summary": "Larsen & Toubro won orders worth ₹45,000 crore for construction work on Saudi Arabia's NEOM and The Line giga projects, its largest-ever international order.",
        "body": (
            "Larsen & Toubro (L&T) announced its largest-ever international order win, securing "
            "contracts worth approximately ₹45,000 crore ($5.4 billion) for construction work on "
            "Saudi Arabia's flagship NEOM and The Line giga projects.\n\n"
            "The contracts span civil construction, MEP (mechanical, electrical, plumbing), and "
            "infrastructure development over a 5-7 year period. L&T will deploy over 50,000 workers "
            "on the projects.\n\n"
            "This win takes L&T's international order book to over ₹1.5 lakh crore, with the Middle "
            "East accounting for 45% of international revenue. The company's total order book now "
            "stands at a record ₹4.8 lakh crore.\n\n"
            "L&T stock gained 3.2% on the announcement. Analysts see the strong order book providing "
            "revenue visibility for the next 3-4 years."
        ),
        "category": "INDIA",
        "importance": 81,
        "sentiment": "bullish",
        "publisher": "Business Standard",
        "entities": ["L&T", "Infrastructure", "Saudi Arabia"],
        "ai_analysis": {
            "what_happened": "L&T won ₹45,000 crore NEOM/The Line contracts; largest-ever international order.",
            "why_it_matters": "Record order book provides 3-4 year revenue visibility; validates India's engineering services capabilities.",
            "affected_assets": ["L&T", "Infrastructure Sector", "NIFTY"],
            "bullish_for": ["L&T", "Infrastructure Stocks", "Capital Goods"],
            "bearish_for": [],
            "confidence": 0.85,
        },
    },
    {
        "headline": "Bitcoin Mining Difficulty Reaches All-Time High Post-Halving",
        "summary": "Bitcoin's mining difficulty hit an all-time high of 88.1T, as miners compete for reduced block rewards following the April 2024 halving event.",
        "body": (
            "Bitcoin's mining difficulty adjusted to an all-time high of 88.1 trillion, a 3.2% "
            "increase from the previous epoch, reflecting intense competition among miners despite "
            "the halved block reward of 3.125 BTC.\n\n"
            "The difficulty increase signals that miners remain profitable at current prices above "
            "$65,000, though margins have compressed significantly since the halving. Hash rate "
            "also reached a record 640 EH/s.\n\n"
            "Publicly listed miners like Marathon Digital and Riot Platforms have been consolidating "
            "operations and acquiring smaller miners to achieve economies of scale. The industry is "
            "also pivoting to AI/HPC hosting as an additional revenue stream.\n\n"
            "The rising difficulty, combined with the halving's supply reduction, creates a "
            "structurally bullish setup for Bitcoin prices, as historical post-halving cycles have "
            "typically seen 3-5x price appreciation within 12-18 months."
        ),
        "category": "CRYPTO",
        "importance": 70,
        "sentiment": "bullish",
        "publisher": "Moneycontrol",
        "entities": ["BTC", "Mining", "Halving"],
        "ai_analysis": {
            "what_happened": "Bitcoin mining difficulty hit all-time high of 88.1T post-halving.",
            "why_it_matters": "Record difficulty + halved supply is structurally bullish; historical cycles suggest 3-5x upside.",
            "affected_assets": ["BTC", "Mining Stocks", "Crypto Market"],
            "bullish_for": ["BTC", "Crypto Market"],
            "bearish_for": ["Small Miners"],
            "confidence": 0.80,
        },
    },
    {
        "headline": "US Existing Home Sales Fall to Lowest Since 2010 on High Rates",
        "summary": "US existing home sales fell to a seasonally adjusted rate of 3.89 million units, the lowest since 2010, as elevated mortgage rates continue to crimp demand.",
        "body": (
            "US existing home sales slumped to a seasonally adjusted annual rate of 3.89 million "
            "units in June, the lowest level since the housing crisis recovery in 2010, as mortgage "
            "rates near 7% continued to depress demand.\n\n"
            "The median existing home price rose 4.1% year-on-year to $426,900, marking the highest "
            "June reading ever and highlighting the affordability squeeze facing potential buyers. "
            "Inventory levels improved to 3.7 months of supply, up from 2.9 a year ago.\n\n"
            "The data adds urgency to the Fed's rate-cut deliberations, as the housing sector — "
            "which accounts for about 16% of US GDP — continues to drag on economic activity.\n\n"
            "The housing weakness has limited direct impact on Indian markets but reinforces the "
            "case for US rate cuts, which would benefit EM risk assets."
        ),
        "category": "GLOBAL",
        "importance": 71,
        "sentiment": "bearish",
        "publisher": "Reuters",
        "entities": ["US Housing", "Mortgage Rates", "Fed"],
        "ai_analysis": {
            "what_happened": "US existing home sales fell to lowest since 2010 at 3.89M units annualised.",
            "why_it_matters": "Weakening housing adds urgency to Fed rate cuts; positive for EM risk assets if rates fall.",
            "affected_assets": ["US Housing Stocks", "Fed Policy", "NIFTY"],
            "bullish_for": ["Rate Cut Expectations", "EM Equities"],
            "bearish_for": ["US Housing", "US Home Builders"],
            "confidence": 0.76,
        },
    },
]

# Assign UUIDs deterministically so article IDs are stable across restarts
for i, article in enumerate(_RAW_NEWS):
    article["id"] = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"terminalx-news-{i}"))
    article.setdefault("source", article["publisher"])
    article.setdefault("source_url", f"https://example.com/news/{article['id']}")


def _time_offset(idx: int) -> datetime:
    """Generate a published_at timestamp spread over the last 48 hours."""
    now = _utcnow()
    offset_minutes = idx * 55 + random.randint(0, 30)  # ~55 min apart
    return now - timedelta(minutes=offset_minutes)


def get_mock_news(
    category: str | None = None,
    limit: int = 20,
    offset: int = 0,
) -> list[dict[str, Any]]:
    """Return paginated mock news, optionally filtered by category."""
    articles = _RAW_NEWS
    if category and category.upper() != "ALL":
        articles = [a for a in articles if a["category"] == category.upper()]

    # Sort by importance descending
    articles = sorted(articles, key=lambda a: a["importance"], reverse=True)

    for i, a in enumerate(articles):
        a["published_at"] = _time_offset(i).isoformat()
        a["created_at"] = a["published_at"]

    return articles[offset : offset + limit]


def get_mock_article(article_id: str) -> dict[str, Any] | None:
    """Return a single article by ID, including full body and AI analysis."""
    for article in _RAW_NEWS:
        if article["id"] == article_id:
            article["published_at"] = _utcnow().isoformat()
            article["created_at"] = article["published_at"]
            return article
    return None


def search_mock_news(query: str, limit: int = 20) -> list[dict[str, Any]]:
    """Primitive case-insensitive search over headlines and summaries."""
    q = query.lower()
    results = [
        a
        for a in _RAW_NEWS
        if q in a["headline"].lower() or q in (a.get("summary") or "").lower()
    ]
    for i, a in enumerate(results):
        a["published_at"] = _time_offset(i).isoformat()
        a["created_at"] = a["published_at"]
    return results[:limit]


# ──────────────────────────────────────────────────────────────────────────────
# ECONOMIC CALENDAR — 25 events
# ──────────────────────────────────────────────────────────────────────────────
_CALENDAR_EVENTS: list[dict[str, Any]] = [
    {"event_name": "RBI Monetary Policy Decision", "country": "IN", "impact": "high", "forecast": "6.50%", "actual": "6.50%", "previous": "6.50%", "offset_days": 0},
    {"event_name": "India CPI Inflation", "country": "IN", "impact": "high", "forecast": "4.3%", "actual": "4.1%", "previous": "4.5%", "offset_days": 1},
    {"event_name": "India WPI Inflation", "country": "IN", "impact": "medium", "forecast": "2.5%", "actual": "2.3%", "previous": "2.6%", "offset_days": 2},
    {"event_name": "India GDP Growth Rate", "country": "IN", "impact": "high", "forecast": "7.0%", "actual": "7.2%", "previous": "6.7%", "offset_days": 3},
    {"event_name": "India Manufacturing PMI", "country": "IN", "impact": "medium", "forecast": "57.8", "actual": "58.3", "previous": "57.5", "offset_days": 4},
    {"event_name": "India Services PMI", "country": "IN", "impact": "medium", "forecast": "60.2", "actual": "60.5", "previous": "59.8", "offset_days": 5},
    {"event_name": "India Industrial Production", "country": "IN", "impact": "medium", "forecast": "5.0%", "actual": "5.4%", "previous": "4.8%", "offset_days": 6},
    {"event_name": "India Trade Balance", "country": "IN", "impact": "medium", "forecast": "-$21B", "actual": "-$24.2B", "previous": "-$20.1B", "offset_days": 7},
    {"event_name": "India GST Collection", "country": "IN", "impact": "medium", "forecast": "₹1.95L Cr", "actual": "₹2.10L Cr", "previous": "₹1.87L Cr", "offset_days": 1},
    {"event_name": "India Forex Reserves", "country": "IN", "impact": "low", "forecast": "$665B", "actual": "$670B", "previous": "$660B", "offset_days": 2},
    {"event_name": "US Non-Farm Payrolls", "country": "US", "impact": "high", "forecast": "190K", "actual": "206K", "previous": "218K", "offset_days": -1},
    {"event_name": "US FOMC Rate Decision", "country": "US", "impact": "high", "forecast": "5.50%", "actual": "5.50%", "previous": "5.50%", "offset_days": 0},
    {"event_name": "US CPI Inflation", "country": "US", "impact": "high", "forecast": "2.7%", "actual": "2.5%", "previous": "2.9%", "offset_days": 1},
    {"event_name": "US Core PCE Price Index", "country": "US", "impact": "high", "forecast": "2.6%", "actual": "2.5%", "previous": "2.7%", "offset_days": 3},
    {"event_name": "US Initial Jobless Claims", "country": "US", "impact": "medium", "forecast": "235K", "actual": "222K", "previous": "229K", "offset_days": -2},
    {"event_name": "US Retail Sales", "country": "US", "impact": "medium", "forecast": "0.3%", "actual": "0.5%", "previous": "0.1%", "offset_days": 4},
    {"event_name": "US ISM Manufacturing PMI", "country": "US", "impact": "medium", "forecast": "49.5", "actual": "48.7", "previous": "49.2", "offset_days": 5},
    {"event_name": "ECB Interest Rate Decision", "country": "EU", "impact": "high", "forecast": "3.75%", "actual": "3.75%", "previous": "4.00%", "offset_days": 2},
    {"event_name": "UK CPI Inflation", "country": "UK", "impact": "medium", "forecast": "2.1%", "actual": "2.0%", "previous": "2.3%", "offset_days": 3},
    {"event_name": "China Manufacturing PMI", "country": "CN", "impact": "high", "forecast": "49.5", "actual": "49.0", "previous": "49.3", "offset_days": -1},
    {"event_name": "China GDP Growth Rate", "country": "CN", "impact": "high", "forecast": "4.8%", "actual": "4.7%", "previous": "5.3%", "offset_days": 6},
    {"event_name": "Japan BOJ Rate Decision", "country": "JP", "impact": "high", "forecast": "0.10%", "actual": "0.25%", "previous": "0.10%", "offset_days": 4},
    {"event_name": "India Auto Sales Data", "country": "IN", "impact": "medium", "forecast": "3.2M", "actual": "3.4M", "previous": "3.1M", "offset_days": 1},
    {"event_name": "US Consumer Confidence", "country": "US", "impact": "medium", "forecast": "100.2", "actual": "98.7", "previous": "101.3", "offset_days": 5},
    {"event_name": "India Crude Oil Imports", "country": "IN", "impact": "low", "forecast": "$16.5B", "actual": "$17.2B", "previous": "$15.8B", "offset_days": 7},
]


def get_mock_calendar(today_only: bool = False) -> list[dict[str, Any]]:
    """Return economic calendar events."""
    now = _utcnow()
    events: list[dict[str, Any]] = []
    for evt in _CALENDAR_EVENTS:
        event_date = now + timedelta(days=evt.get("offset_days", 0))
        events.append({
            "id": str(uuid.uuid5(uuid.NAMESPACE_DNS, f"terminalx-cal-{evt['event_name']}")),
            "event_name": evt["event_name"],
            "country": evt["country"],
            "event_date": event_date.isoformat(),
            "forecast": evt["forecast"],
            "actual": evt["actual"],
            "previous": evt["previous"],
            "impact": evt["impact"],
            "created_at": now.isoformat(),
        })

    if today_only:
        events = [e for e in events if abs(datetime.fromisoformat(e["event_date"]).date().toordinal() - now.date().toordinal()) == 0]

    return sorted(events, key=lambda e: e["event_date"])


# ──────────────────────────────────────────────────────────────────────────────
# ASSET INTELLIGENCE — aggregated view for a single symbol
# ──────────────────────────────────────────────────────────────────────────────
_MOCK_EARNINGS: dict[str, dict] = {
    "NIFTY": {"eps": "820.50", "pe_ratio": "29.95", "market_cap": "₹286.5L Cr", "revenue_growth": "12.4%", "profit_growth": "15.2%"},
    "BANKNIFTY": {"eps": "2650.20", "pe_ratio": "19.75", "market_cap": "₹58.2L Cr", "revenue_growth": "18.1%", "profit_growth": "21.3%"},
    "BTC": {"market_cap": "$1.32T", "24h_volume": "$38.2B", "circulating_supply": "19.72M BTC", "halving_date": "April 2024"},
    "ETH": {"market_cap": "$423B", "24h_volume": "$18.5B", "staking_yield": "4.8%", "total_value_locked": "$89B"},
    "GOLD": {"ytd_return": "14.2%", "central_bank_buying": "290 tonnes H1", "etf_flows": "+$2.1B", "cot_long_pct": "62%"},
}

_MOCK_FII_DII = {
    "fii_net": 3240.50,
    "dii_net": 5180.20,
    "fii_buy": 12450.30,
    "fii_sell": 9209.80,
    "dii_buy": 14320.10,
    "dii_sell": 9139.90,
    "date": _utcnow().strftime("%Y-%m-%d"),
}


def get_mock_asset_intelligence(symbol: str) -> dict[str, Any]:
    """Return enriched data for a single asset: price, related news, earnings, AI summary."""
    sym = symbol.upper()
    quote = generate_tick(sym) if sym in MOCK_ASSETS else None

    related_news = [
        a
        for a in _RAW_NEWS
        if sym in " ".join(a.get("entities", []))
        or sym.lower() in a["headline"].lower()
    ][:5]
    for i, a in enumerate(related_news):
        a["published_at"] = _time_offset(i).isoformat()
        a["created_at"] = a["published_at"]

    earnings = _MOCK_EARNINGS.get(sym, {})

    sentiment_counts = {"bullish": 0, "bearish": 0, "neutral": 0}
    for a in related_news:
        s = a.get("sentiment", "neutral")
        sentiment_counts[s] = sentiment_counts.get(s, 0) + 1

    dominant = max(sentiment_counts, key=sentiment_counts.get)  # type: ignore[arg-type]
    ai_summary = (
        f"{sym} is showing {dominant} sentiment based on {len(related_news)} recent articles. "
        f"Key themes include {'strong earnings' if dominant == 'bullish' else 'macro concerns' if dominant == 'bearish' else 'mixed signals'}. "
        f"Current price action suggests {'continuation of the trend' if dominant != 'neutral' else 'range-bound trading'}."
    )

    return {
        "symbol": sym,
        "quote": quote,
        "related_news": related_news,
        "earnings": earnings,
        "ai_summary": ai_summary,
        "sentiment": dominant,
        "sentiment_breakdown": sentiment_counts,
    }


def get_mock_fii_dii_flow() -> dict[str, Any]:
    """Return mock FII/DII flow data."""
    base = _MOCK_FII_DII.copy()
    # Add small random variation
    for key in ["fii_net", "dii_net", "fii_buy", "fii_sell", "dii_buy", "dii_sell"]:
        base[key] = round(base[key] * random.uniform(0.9, 1.1), 2)
    base["date"] = _utcnow().strftime("%Y-%m-%d")
    return base


def get_mock_earnings_data() -> list[dict[str, Any]]:
    """Return mock upcoming/recent earnings data."""
    now = _utcnow()
    return [
        {"company": "Reliance Industries", "date": (now + timedelta(days=2)).strftime("%Y-%m-%d"), "estimate_eps": "₹38.50", "status": "upcoming"},
        {"company": "TCS", "date": (now + timedelta(days=5)).strftime("%Y-%m-%d"), "estimate_eps": "₹62.30", "status": "upcoming"},
        {"company": "HDFC Bank", "date": (now - timedelta(days=3)).strftime("%Y-%m-%d"), "actual_eps": "₹21.50", "estimate_eps": "₹20.80", "surprise": "+3.4%", "status": "reported"},
        {"company": "Infosys", "date": (now - timedelta(days=7)).strftime("%Y-%m-%d"), "actual_eps": "₹16.70", "estimate_eps": "₹16.20", "surprise": "+3.1%", "status": "reported"},
        {"company": "ICICI Bank", "date": (now + timedelta(days=8)).strftime("%Y-%m-%d"), "estimate_eps": "₹15.40", "status": "upcoming"},
        {"company": "SBI", "date": (now - timedelta(days=1)).strftime("%Y-%m-%d"), "actual_eps": "₹9.90", "estimate_eps": "₹9.50", "surprise": "+4.2%", "status": "reported"},
        {"company": "Bharti Airtel", "date": (now + timedelta(days=12)).strftime("%Y-%m-%d"), "estimate_eps": "₹8.20", "status": "upcoming"},
        {"company": "ITC", "date": (now + timedelta(days=15)).strftime("%Y-%m-%d"), "estimate_eps": "₹5.60", "status": "upcoming"},
        {"company": "Tata Motors", "date": (now - timedelta(days=10)).strftime("%Y-%m-%d"), "actual_eps": "₹12.80", "estimate_eps": "₹11.50", "surprise": "+11.3%", "status": "reported"},
        {"company": "L&T", "date": (now + timedelta(days=18)).strftime("%Y-%m-%d"), "estimate_eps": "₹32.10", "status": "upcoming"},
    ]
