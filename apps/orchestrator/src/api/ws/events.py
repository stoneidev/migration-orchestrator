import asyncio
from typing import Any

from fastapi import WebSocket


class EventBus:
    def __init__(self):
        self._connections: list[WebSocket] = []
        self._queue: asyncio.Queue | None = None

    def register(self, ws: WebSocket) -> None:
        self._connections.append(ws)

    def unregister(self, ws: WebSocket) -> None:
        if ws in self._connections:
            self._connections.remove(ws)

    def emit(self, event: str, data: dict[str, Any]) -> None:
        message = {"event": event, "data": data}
        for ws in self._connections:
            try:
                asyncio.get_event_loop().create_task(ws.send_json(message))
            except RuntimeError:
                # No running event loop (sync context like tests)
                if self._queue is None:
                    self._queue = asyncio.Queue()
                self._queue.put_nowait(message)

    async def receive_from_queue(self) -> dict | None:
        if self._queue and not self._queue.empty():
            return await self._queue.get()
        return None


event_bus = EventBus()
