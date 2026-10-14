"""Validation runner plumbing on Windows: event ordering (TST-15) and per-scenario client addresses (TST-16)."""

from __future__ import annotations

import time
from typing import Any

import pytest
from aiohttp import web
from aiohttp.test_utils import TestServer

from src.driver import check_port_available
from tools.validate.clients.api import ApiClient
from tools.validate.clients.base import ActionResult, HubInfo
from tools.validate.device import SimDevice
from tools.validate.model import Action, CommandGap, Scenario
from tools.validate.runner import Runner, RunOptions, WsObserver
from tools.validate.stack import HubProcess, free_port


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


class _FakeSimDevice(SimDevice):
    def __init__(self, entries: list[dict[str, Any]]) -> None:
        super().__init__("http://unused")
        self._entries = entries

    async def log(self, limit: int = 500) -> list[dict[str, Any]]:
        return self._entries[:limit]


async def test_command_gap_tolerates_windows_timer_quantum_and_rejects_short_waits():
    """Windows asyncio.sleep(0.5) wakes on 15.625 ms GetTickCount64 ticks and simulator logs round to 1 ms,
    so a genuine 0.5 s wait can measure 0.495-0.499 s; shorter or missing waits still fail."""
    runner = Runner(RunOptions())
    sc = Scenario(
        id="t.gap",
        title="t",
        features=("F-DOM-013",),
        action=Action("route"),
        expect=(),
        covers=("src/rest_api/scenes.py",),
    )
    client = ApiClient()
    ws = WsObserver("ws://unused/ws", "10.0.0.1")
    gap = CommandGap("set beep", "video switch", 0.5)

    for t1, t2, expected in (
        (1000.001, 1000.500, "pass"),  # 0.499 s (1 ms rounding / localhost transit)
        (1000.005, 1000.500, "pass"),  # 0.495 s (Windows 15.625 ms timer tick seen in CI)
        (1000.050, 1000.500, "fail"),  # 0.450 s (genuinely short wait)
    ):
        runner.device = _FakeSimDevice([
            {"t": t1, "channel": "http", "command": "set beep"},
            {"t": t2, "channel": "http", "command": "video switch"},
        ])
        verdict = await runner._check(gap, sc, client, ActionResult("route", ok=True), {}, 0.0, ws, client, 0, [])
        assert verdict["result"] == expected, (t1, t2, verdict)

    runner.device = _FakeSimDevice([{"t": 1000.0, "channel": "http", "command": "set beep"}])
    missing = await runner._check(gap, sc, client, ActionResult("route", ok=True), {}, 0.0, ws, client, 0, [])
    assert missing["result"] == "fail"


def test_free_port_skips_ports_bound_on_all_interfaces(monkeypatch):
    """TST-18: on Windows a socket bound to 0.0.0.0:port still lets bind(('127.0.0.1', port)) succeed,
    and then driver.py's check_port_available(('0.0.0.0', port)) fails with WinError 10013."""
    import socket as _socket

    with _socket.socket(_socket.AF_INET, _socket.SOCK_STREAM) as holder:
        holder.bind(("0.0.0.0", 0))
        held_port = int(holder.getsockname()[1])

        real_socket = _socket.socket
        first_call = True

        class _ProbeSocket(real_socket):
            def bind(self, address):  # type: ignore[override]
                nonlocal first_call
                host, port = address
                if first_call and port == 0:
                    first_call = False
                    return super().bind((host, held_port))
                return super().bind(address)

        monkeypatch.setattr("tools.validate.stack.socket.socket", _ProbeSocket)
        picked = free_port("127.0.0.1")
        assert picked != held_port
        assert check_port_available(picked) is True


def test_hub_process_retries_when_an_auto_picked_port_is_taken_before_bind(tmp_path, monkeypatch):
    """TST-18: if another process grabs the ephemeral port between free_port() and the hub's bind,
    HubProcess retries on a fresh port instead of failing the test."""
    import socket as _socket

    holder = _socket.socket(_socket.AF_INET, _socket.SOCK_STREAM)
    holder.bind(("0.0.0.0", 0))
    stolen_port = int(holder.getsockname()[1])

    real_free_port = free_port
    calls = 0

    def _steal_first_uc_port(host: str = "127.0.0.1") -> int:
        nonlocal calls
        calls += 1
        if calls == 2:  # 1st call = api_port, 2nd call = uc_port
            return stolen_port
        return real_free_port(host)

    monkeypatch.setattr("tools.validate.stack.free_port", _steal_first_uc_port)
    hub = HubProcess(
        matrix_host="127.0.0.1",
        matrix_port=real_free_port(),
        telnet_port=real_free_port(),
        log_dir=tmp_path / "hub-logs",
        mode="uc",
        uc_restore=False,
        stop_timeout=3,
        extra_env={"MATRIX_HOST": ""},
    )
    try:
        hub.launch()
        health = hub.wait_ready(timeout=25)
        assert health
        assert hub.uc_port != stolen_port
        assert hub.starts >= 2
    finally:
        hub.stop()
        holder.close()

