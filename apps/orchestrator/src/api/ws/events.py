import asyncio
import threading
from typing import Any

from fastapi import WebSocket


class EventBus:
    def __init__(self):
        self._connections: list[WebSocket] = []
        self._loop: asyncio.AbstractEventLoop | None = None

    def set_loop(self, loop: asyncio.AbstractEventLoop) -> None:
        self._loop = loop

    def register(self, ws: WebSocket) -> None:
        self._connections.append(ws)

    def unregister(self, ws: WebSocket) -> None:
        if ws in self._connections:
            self._connections.remove(ws)

    def emit(self, event: str, data: dict[str, Any]) -> None:
        message = {"event": event, "data": data}
        for ws in list(self._connections):
            try:
                if self._loop and self._loop.is_running():
                    self._loop.call_soon_threadsafe(
                        asyncio.ensure_future,
                        ws.send_json(message),
                    )
                else:
                    # Try direct
                    asyncio.get_event_loop().create_task(ws.send_json(message))
            except RuntimeError:
                pass


event_bus = EventBus()
