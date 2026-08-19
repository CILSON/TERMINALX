"""WebSocket connection manager for real-time data streaming."""

from __future__ import annotations

import json
import logging
from typing import Any

from fastapi import WebSocket

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages WebSocket connections and broadcasts."""

    def __init__(self) -> None:
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info("WS connected. Total: %d", len(self.active_connections))

    def disconnect(self, websocket: WebSocket) -> None:
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info("WS disconnected. Total: %d", len(self.active_connections))

    async def broadcast(self, channel: str, data: Any) -> None:
        """Send data to all connected clients on a channel."""
        message = json.dumps({"channel": channel, "data": data})
        disconnected = []
        for ws in self.active_connections:
            try:
                await ws.send_text(message)
            except Exception:
                disconnected.append(ws)
        for ws in disconnected:
            self.disconnect(ws)

    async def send_personal(self, websocket: WebSocket, channel: str, data: Any) -> None:
        """Send data to a specific client."""
        message = json.dumps({"channel": channel, "data": data})
        try:
            await websocket.send_text(message)
        except Exception:
            self.disconnect(websocket)

    @property
    def connection_count(self) -> int:
        return len(self.active_connections)


manager = ConnectionManager()
