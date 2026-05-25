"""WebSocket event broadcasting.

The orchestrator emits live progress events to a small fleet of browser
clients. ``emit`` is called from many threads (background tasks, the
Claude CLI watchdog, sync route handlers), so we need:

* concurrency-safe ``register`` / ``unregister`` / broadcast
* automatic cleanup of websockets that have closed underneath us
* a safe way to schedule async sends from sync callers — done via
  ``run_coroutine_threadsafe`` on the event loop captured at startup.
"""

from __future__ import annotations

import asyncio
from typing import Any

from fastapi import WebSocket


class EventBus:
    def __init__(self) -> None:
        self._connections: set[WebSocket] = set()
        self._lock = asyncio.Lock()
        self._loop: asyncio.AbstractEventLoop | None = None

    def set_loop(self, loop: asyncio.AbstractEventLoop) -> None:
        self._loop = loop

    async def register(self, ws: WebSocket) -> None:
        async with self._lock:
            self._connections.add(ws)

    async def unregister(self, ws: WebSocket) -> None:
        async with self._lock:
            self._connections.discard(ws)

    async def _broadcast(self, message: dict[str, Any]) -> None:
        async with self._lock:
            targets = list(self._connections)

        dead: list[WebSocket] = []
        for ws in targets:
            try:
                await ws.send_json(message)
            except Exception:
                dead.append(ws)

        if dead:
            async with self._lock:
                for ws in dead:
                    self._connections.discard(ws)

    def emit(self, event: str, data: dict[str, Any]) -> None:
        """Schedule an event broadcast. Safe to call from any thread."""
        message = {"event": event, "data": data}
        loop = self._loop
        if loop is None or not loop.is_running():
            return
        try:
            asyncio.run_coroutine_threadsafe(self._broadcast(message), loop)
        except RuntimeError:
            # Event loop closed mid-flight; nothing to do.
            pass

    async def shutdown(self) -> None:
        async with self._lock:
            targets = list(self._connections)
            self._connections.clear()
        for ws in targets:
            try:
                await ws.close()
            except Exception:
                pass


event_bus = EventBus()
