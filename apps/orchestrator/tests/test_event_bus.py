"""EventBus concurrency / cleanup behaviour (Phase 3)."""

from __future__ import annotations

import asyncio

import pytest

from src.api.ws.events import EventBus


class _FakeWebSocket:
    def __init__(self, fail: bool = False):
        self.sent: list[dict] = []
        self.fail = fail
        self.closed = False

    async def send_json(self, message: dict) -> None:
        if self.fail:
            raise RuntimeError("connection closed")
        self.sent.append(message)

    async def close(self) -> None:
        self.closed = True


@pytest.mark.asyncio
async def test_register_and_broadcast_delivers_to_all():
    bus = EventBus()
    bus.set_loop(asyncio.get_running_loop())
    ws1, ws2 = _FakeWebSocket(), _FakeWebSocket()
    await bus.register(ws1)
    await bus.register(ws2)

    await bus._broadcast({"event": "hello", "data": {}})

    assert {"event": "hello", "data": {}} in ws1.sent
    assert {"event": "hello", "data": {}} in ws2.sent


@pytest.mark.asyncio
async def test_dead_connections_are_pruned_after_failure():
    bus = EventBus()
    bus.set_loop(asyncio.get_running_loop())
    alive = _FakeWebSocket()
    dead = _FakeWebSocket(fail=True)
    await bus.register(alive)
    await bus.register(dead)

    await bus._broadcast({"event": "tick", "data": {}})

    # dead got dropped
    assert dead not in bus._connections
    # alive still there
    assert alive in bus._connections


@pytest.mark.asyncio
async def test_emit_without_loop_is_noop():
    bus = EventBus()  # no set_loop called
    # Should not raise; just silently drop.
    bus.emit("ignored", {"x": 1})


@pytest.mark.asyncio
async def test_concurrent_register_unregister_preserves_invariants():
    bus = EventBus()
    bus.set_loop(asyncio.get_running_loop())
    sockets = [_FakeWebSocket() for _ in range(50)]

    async def register_all():
        for s in sockets:
            await bus.register(s)

    async def unregister_half():
        for s in sockets[::2]:
            await bus.unregister(s)

    await asyncio.gather(register_all(), unregister_half())

    # Each socket appears at most once.
    assert len(bus._connections) <= len(sockets)


@pytest.mark.asyncio
async def test_shutdown_closes_and_clears_connections():
    bus = EventBus()
    bus.set_loop(asyncio.get_running_loop())
    sockets = [_FakeWebSocket() for _ in range(3)]
    for s in sockets:
        await bus.register(s)

    await bus.shutdown()

    assert bus._connections == set()
    assert all(s.closed for s in sockets)
