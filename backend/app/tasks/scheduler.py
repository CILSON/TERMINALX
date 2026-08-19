"""Background task scheduler for periodic data ingestion."""

from __future__ import annotations

import asyncio
import json
import logging

from app.config import settings
from app.services.market_data import update_all_quotes
from app.websocket import manager

logger = logging.getLogger(__name__)

_running = False
_task: asyncio.Task | None = None


async def _quote_update_loop(redis_client=None) -> None:
    """Continuously update quotes and broadcast via WebSocket."""
    interval = (
        settings.QUOTE_UPDATE_INTERVAL_MOCK
        if settings.USE_MOCK_DATA
        else settings.QUOTE_UPDATE_INTERVAL_LIVE
    )
    while _running:
        try:
            quotes = await update_all_quotes(redis_client)
            # Broadcast to all WS clients
            if manager.connection_count > 0:
                await manager.broadcast("quotes", quotes)
        except Exception as e:
            logger.error("Quote update error: %s", e)
        await asyncio.sleep(interval)


async def start_scheduler(redis_client=None) -> None:
    """Start the background scheduler tasks."""
    global _running, _task
    _running = True
    _task = asyncio.create_task(_quote_update_loop(redis_client))
    logger.info("Scheduler started (interval: %ss)",
                settings.QUOTE_UPDATE_INTERVAL_MOCK if settings.USE_MOCK_DATA
                else settings.QUOTE_UPDATE_INTERVAL_LIVE)


async def stop_scheduler() -> None:
    """Stop the background scheduler."""
    global _running, _task
    _running = False
    if _task:
        _task.cancel()
        try:
            await _task
        except asyncio.CancelledError:
            pass
        _task = None
    logger.info("Scheduler stopped")
