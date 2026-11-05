"""TerminalX — FastAPI application entry point."""

from __future__ import annotations

import json
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import init_redis, close_redis, redis_pool
from app.websocket import manager
from app.tasks.scheduler import start_scheduler, stop_scheduler

from app.routers import (
    quotes,
    news,
    calendar,
    portfolio,
    watchlist,
    alerts,
    commands,
    ai,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup / shutdown lifecycle."""
    logger.info("═══ TerminalX starting ═══")
    logger.info("Mock data mode: %s", settings.USE_MOCK_DATA)
    logger.info("Gemini AI: %s", "ENABLED" if settings.GEMINI_API_KEY else "DISABLED (no key)")

    # Init Redis
    redis = None
    try:
        redis = await init_redis()
        logger.info("Redis connected")
    except Exception as e:
        logger.warning("Redis unavailable, running without cache: %s", e)

    # Start background scheduler
    await start_scheduler(redis)

    yield

    # Shutdown
    await stop_scheduler()
    await close_redis()
    logger.info("═══ TerminalX stopped ═══")


app = FastAPI(
    title="TerminalX API",
    description="Bloomberg-style market intelligence terminal",
    version="1.0.0",
    lifespan=lifespan,
)

# ── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://terminalx-e74p.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── REST Routers ──────────────────────────────────────────────────────────────
app.include_router(quotes.router)
app.include_router(news.router)
app.include_router(calendar.router)
app.include_router(portfolio.router)
app.include_router(watchlist.router)
app.include_router(alerts.router)
app.include_router(commands.router)
app.include_router(ai.router)


# ── WebSocket ─────────────────────────────────────────────────────────────────
@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    """Main WebSocket endpoint for real-time data streaming."""
    await manager.connect(ws)
    try:
        while True:
            data = await ws.receive_text()
            try:
                msg = json.loads(data)
                # Handle client messages (subscribe, ping, etc.)
                if msg.get("type") == "ping":
                    await manager.send_personal(ws, "pong", {"status": "ok"})
            except json.JSONDecodeError:
                pass
    except WebSocketDisconnect:
        manager.disconnect(ws)


# ── Health check ──────────────────────────────────────────────────────────────
@app.get("/api/health")
async def health():
    return {
        "status": "ok",
        "mock_mode": settings.USE_MOCK_DATA,
        "ws_connections": manager.connection_count,
    }


@app.get("/")
async def root():
    return {"name": "TerminalX API", "version": "1.0.0", "docs": "/docs"}
