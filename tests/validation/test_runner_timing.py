"""Validation runner plumbing on Windows: event ordering (TST-15) and per-scenario client addresses (TST-16)."""

from __future__ import annotations

import time
from typing import Any

import pytest
from aiohttp import web
from aiohttp.test_utils import TestServer

from tools.validate.clients.api import ApiClient
from tools.validate.clients.base import HubInfo
from tools.validate.runner import WsObserver


class _FakeWs:
    """Stands in for the aiohttp WebSocket; `answer` is appended as the hub's reply to get_status."""

    closed = False

    def __init__(self, observer: WsObserver, answer: str | None) -> None:
        self.observer, self.answer, self.sent = observer, answer, []

    async def send_json(self, data: dict[str, Any]) -> None:
        self.sent.append(data)
        if self.answer:
            self.observer.events.append({"t": self.observer.now(), "event": self.answer, "data": {}})


def _observer_with_welcome(answer: str | None) -> WsObserver:
    ws = WsObserver("ws://unused/ws", "10.0.0.1")
    ws.events.append({"t": ws.now(), "event": "connected", "data": {}})
    ws.events.append({"t": ws.now(), "event": "status", "data": {"welcome": True}})
    ws._ws = _FakeWs(ws, answer)  # type: ignore[assignment]
    return ws


async def test_sync_does_not_take_the_welcome_snapshot_for_the_answer(monkeypatch):
    """A coarse clock (Windows ticks every ~15.6 ms) gives the welcome snapshot the request's own time."""
    frozen = time.time()
    monkeypatch.setattr(time, "time", lambda: frozen)
    monkeypatch.setattr(time, "perf_counter", lambda: 1000.0)
    ws = _observer_with_welcome(answer=None)  # the hub never answers
    assert await ws.sync(timeout=0.3) is False
    assert ws._ws.sent == [{"command": "get_status"}]  # type: ignore[union-attr]


async def test_sync_returns_on_the_fresh_answer(monkeypatch):
    monkeypatch.setattr(time, "perf_counter", lambda: 1000.0)
    assert await _observer_with_welcome(answer="status").sync(timeout=2) is True
    assert await _observer_with_welcome(answer="error").sync(timeout=2) is False


def test_event_times_are_high_resolution():
    """Marks and event times come from the same high-resolution clock."""
    a = WsObserver.now()
    b = WsObserver.now()
    assert 0 <= b - a < 0.001


async def test_api_client_uses_the_scenario_address():
    """Each scenario has its own X-Forwarded-For (the hub rate-limits per address), the api client too."""
    seen: list[str | None] = []

    async def handler(request: web.Request) -> web.Response:
        seen.append(request.headers.get("X-Forwarded-For"))
        return web.json_response({"success": True})

    app = web.Application()
    app.router.add_get("/api/health", handler)
    async with TestServer(app) as server:
        client = ApiClient()
        await client.start(HubInfo(str(server.make_url("")).rstrip("/"), forwarded_for="10.77.0.1"))
        try:
            await client.request("GET", "/api/health")
            client.context = {"label": "s1", "forwarded_for": "10.77.0.2"}
            await client.request("GET", "/api/health")
            client.context = {"label": "s2", "forwarded_for": "10.77.0.3"}
            await client.request("GET", "/api/health")
        finally:
            await client.stop()
    assert seen == ["10.77.0.1", "10.77.0.2", "10.77.0.3"]


def test_since_refuses_a_wall_clock_mark():
    """A time.time() mark against perf_counter event times would silently match nothing."""
    ws = WsObserver("ws://unused/ws", "10.0.0.1")
    with pytest.raises(ValueError, match="WsObserver.now"):
        ws.since(time.time())
    assert ws.since(ws.now()) == []
