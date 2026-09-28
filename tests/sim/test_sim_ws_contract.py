"""The /ws contract (docs/api/WEBSOCKET.md) against the real hub app and the simulator.

The hub owns the event stream (UC-17): its status poller and the matrix's own
events (writes, Telnet pushes, link changes) produce every live event, whatever
made the change (REST, the Remote, Home Assistant, Flic, the front panel), and
each change is announced once. Every message a test receives is checked against
``docs/api/websocket.schema.json``.
"""

from __future__ import annotations

import asyncio
import contextlib
import json
import time
from pathlib import Path
from typing import Any

import aiohttp
import pytest

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = ROOT / "docs" / "api" / "websocket.schema.json"

#: Short poll interval so front-panel changes show up quickly in these tests.
POLL = 0.5


@pytest.fixture(autouse=True)
def _fast_poll(monkeypatch):
    monkeypatch.setenv("STATUS_POLL_INTERVAL", str(POLL))


@pytest.fixture
async def telnet_hub(aiohttp_client, matrix_with_telnet, monkeypatch, tmp_path):
    """Like ``data_hub`` (tests/sim/conftest.py), with the matrix's Telnet link up (cable pushes)."""
    import rest_api.utils as api_utils
    from rest_api import reset_rate_limiter, set_matrix_device
    from rest_api.app import create_rest_app

    from .conftest import REST_GLOBALS

    for name in REST_GLOBALS:
        monkeypatch.setattr(api_utils, name, getattr(api_utils, name))
    monkeypatch.setattr(api_utils, "_input_names", {})
    monkeypatch.setattr(api_utils, "_output_names", {})
    reset_rate_limiter()
    assert await matrix_with_telnet.connect()
    assert matrix_with_telnet.telnet_connected
    set_matrix_device(matrix_with_telnet, config_dir=str(tmp_path), data_dir=str(tmp_path))
    client = await aiohttp_client(create_rest_app(data_dir=tmp_path))
    yield client
    reset_rate_limiter()


def _validator():
    jsonschema = pytest.importorskip("jsonschema")
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator.check_schema(schema)
    return jsonschema.Draft202012Validator(schema)


class Ws:
    """A /ws client that records every message and checks it against the contract schema."""

    def __init__(self, ws: aiohttp.ClientWebSocketResponse) -> None:
        self.ws = ws
        self.messages: list[dict[str, Any]] = []
        self._task = asyncio.ensure_future(self._pump())

    async def _pump(self) -> None:
        async for msg in self.ws:
            if msg.type == aiohttp.WSMsgType.TEXT:
                self.messages.append({"t": time.monotonic(), **json.loads(msg.data)})

    def events(self, name: str, since: float = 0.0) -> list[dict[str, Any]]:
        return [m["data"] for m in self.messages if m.get("event") == name and m["t"] >= since]

    async def wait(self, name: str, match: dict[str, Any] | None = None, since: float = 0.0,
                   timeout: float = 3.0) -> dict[str, Any]:
        deadline = time.monotonic() + timeout
        while True:
            for data in self.events(name, since):
                if all(data.get(k) == v for k, v in (match or {}).items()):
                    return data
            if time.monotonic() > deadline:
                seen = [(m.get("event"), m.get("data")) for m in self.messages if m["t"] >= since]
                raise AssertionError(f"no '{name}' {match or ''} within {timeout}s; received {seen}")
            await asyncio.sleep(0.05)

    def check_contract(self) -> None:
        validator = _validator()
        for m in self.messages:
            body = {k: v for k, v in m.items() if k != "t"}
            errors = sorted(validator.iter_errors(body), key=str)
            assert not errors, f"{body} breaks the contract: {errors[0].message}"

    async def close(self) -> None:
        await self.ws.close()
        self._task.cancel()


async def _connect(client) -> Ws:
    ws = Ws(await client.ws_connect("/ws"))
    await ws.wait("connected")
    return ws


async def _baseline(ws: Ws) -> None:
    """Give the hub's poller time to read the matrix once (a change needs a value to differ from).

    The snapshot sent after ``connected`` shows it has; the checks that prove a finding come after this, so
    a hub without a snapshot fails there, not here.
    """
    with contextlib.suppress(AssertionError):
        await ws.wait("status", timeout=3)


# --------------------------------------------------------------------------- hub-owned stream


async def test_grid_route_is_announced_to_other_clients(data_hub, simulator):
    """VAL-05: the matrix grid posts /api/output/{n}/source, which never broadcast."""
    ws = await _connect(data_hub)
    await _baseline(ws)
    t0 = time.monotonic()
    resp = await data_hub.post("/api/output/1/source", json={"input": 5})
    assert resp.status == 200
    assert simulator.state.routing[0] == 5
    event = await ws.wait("routing_change", {"output": 1, "input": 5}, since=t0)
    assert event["previous_input"] == 2  # seed routing: output 1 shows input 2
    assert event["input_name"] == "Shield"
    ws.check_contract()
    await ws.close()


async def test_a_front_panel_change_reaches_clients_without_a_remote(data_hub, simulator):
    """UC-17: in the core-only hub (no Remote integration) the hub's own poller feeds /ws."""
    ws = await _connect(data_hub)
    await _baseline(ws)
    t0 = time.monotonic()
    simulator.state.outputs[3].source = 7  # changed on the device, not through the hub
    await ws.wait("routing_change", {"output": 4, "input": 7}, since=t0, timeout=4 * POLL + 2)
    ws.check_contract()
    await ws.close()


async def test_each_change_is_announced_once(data_hub, simulator):
    """One routing change through REST -> exactly one routing_change, and no optimistic `switch` event."""
    ws = await _connect(data_hub)
    await _baseline(ws)
    t0 = time.monotonic()
    resp = await data_hub.post("/api/switch", json={"input": 6, "output": 2})
    assert resp.status == 200
    await ws.wait("routing_change", {"output": 2, "input": 6}, since=t0)
    await asyncio.sleep(3 * POLL)  # several more polls: nothing is announced again
    assert len([e for e in ws.events("routing_change", t0) if e["output"] == 2]) == 1
    assert ws.events("switch", t0) == []
    ws.check_contract()
    await ws.close()


async def test_route_all_announces_every_output_that_changed(data_hub, simulator):
    ws = await _connect(data_hub)
    await _baseline(ws)
    before = list(simulator.state.routing)
    t0 = time.monotonic()
    resp = await data_hub.post("/api/switch", json={"input": 4})
    assert resp.status == 200
    changed = {i + 1 for i, src in enumerate(before) if src != 4}
    deadline = time.monotonic() + 3
    while {e["output"] for e in ws.events("routing_change", t0)} != changed and time.monotonic() < deadline:
        await asyncio.sleep(0.05)
    assert {e["output"] for e in ws.events("routing_change", t0)} == changed
    assert all(e["input"] == 4 for e in ws.events("routing_change", t0))
    ws.check_contract()
    await ws.close()


async def test_mute_is_announced_after_the_matrix_accepted_it(data_hub, simulator):
    ws = await _connect(data_hub)
    await _baseline(ws)
    t0 = time.monotonic()
    resp = await data_hub.post("/api/output/2/mute", json={"muted": True})
    assert resp.status == 200
    await ws.wait("audio_mute", {"output": 2, "muted": True}, since=t0)
    assert all("optimistic" not in e for e in ws.events("audio_mute", t0))
    ws.check_contract()
    await ws.close()


async def test_a_rejected_mute_is_not_announced_as_done(data_hub, simulator):
    """The old handler broadcast `audio_mute` before sending the command; a refused write still told every client."""
    ws = await _connect(data_hub)
    await _baseline(ws)
    simulator.faults.update({"reject_writes": True})
    t0 = time.monotonic()
    resp = await data_hub.post("/api/output/2/mute", json={"muted": True})
    assert resp.status == 500
    await asyncio.sleep(3 * POLL)
    assert ws.events("audio_mute", t0) == []
    await ws.close()


async def test_preset_recall_is_announced_after_success_and_its_routing_follows(data_hub, simulator):
    ws = await _connect(data_hub)
    await _baseline(ws)
    t0 = time.monotonic()
    resp = await data_hub.post("/api/preset/1")
    assert resp.status == 200
    event = await ws.wait("preset_recall", {"preset": 1}, since=t0)
    assert "optimistic" not in event
    changed = [i + 1 for i, (a, b) in enumerate(zip(simulator.initial_state.routing, simulator.state.routing, strict=True))
               if a != b]
    for output in changed:
        await ws.wait("routing_change", {"output": output}, since=t0)
    ws.check_contract()
    await ws.close()


async def test_a_failed_switch_is_announced(data_hub, simulator):
    ws = await _connect(data_hub)
    await _baseline(ws)
    simulator.faults.update({"reject_writes": True})
    t0 = time.monotonic()
    resp = await data_hub.post("/api/output/3/source", json={"input": 2})
    assert resp.status == 500
    await ws.wait("switch_failed", {"output": 3, "input": 2}, since=t0)
    ws.check_contract()
    await ws.close()


async def test_names_are_announced_when_they_change(data_hub, simulator):
    ws = await _connect(data_hub)
    await _baseline(ws)
    t0 = time.monotonic()
    resp = await data_hub.post("/api/input/3/name", json={"name": "Retro PC"})
    assert resp.status == 200
    await ws.wait("input_name_change", {"input": 3, "name": "Retro PC"}, since=t0)
    ws.check_contract()
    await ws.close()


async def test_signal_changes_are_announced(data_hub, simulator):
    ws = await _connect(data_hub)
    await _baseline(ws)
    t0 = time.monotonic()
    simulator.state.inputs[2].signal = 1
    await ws.wait("signal_change", {"input": 3, "has_signal": True}, since=t0, timeout=4 * POLL + 2)
    ws.check_contract()
    await ws.close()


async def test_power_changes_are_announced(data_hub, simulator):
    ws = await _connect(data_hub)
    await _baseline(ws)
    t0 = time.monotonic()
    resp = await data_hub.post("/api/power/off")
    assert resp.status == 200
    await ws.wait("power_change", {"power": "off"}, since=t0)
    ws.check_contract()
    await ws.close()


async def test_a_cable_push_is_announced_before_the_next_poll(telnet_hub, simulator, monkeypatch):
    """The matrix pushes cable events over Telnet; the hub reads them at once instead of waiting for a poll."""
    monkeypatch.setenv("STATUS_POLL_INTERVAL", "30")  # only the push can explain a quick event
    ws = await _connect(telnet_hub)
    await _baseline(ws)
    t0 = time.monotonic()
    await simulator.cable_event("output", 1, False)
    await ws.wait("cable_change", {"type": "output", "port": 1, "connected": False}, since=t0, timeout=3)
    await ws.wait("connection_change", {"output": 1, "connected": False}, since=t0, timeout=3)
    ws.check_contract()
    await ws.close()


# --------------------------------------------------------------------------- connection and snapshot


async def test_welcome_carries_the_protocol_and_the_matrix_link_then_a_snapshot(data_hub, simulator):
    ws = await _connect(data_hub)
    welcome = ws.events("connected")[0]
    assert welcome["protocol"] == 1
    assert welcome["matrix"]["connected"] is True
    status = await ws.wait("status", timeout=5)
    assert status["routing"] == {str(i + 1): src for i, src in enumerate(simulator.state.routing)}
    # BE-31: the snapshot's output details carry the real names, not the hub's (empty) name cache
    assert [o["name"] for o in status["outputs_detail"][:2]] == ["TV", "Soundbar"]
    assert status["connected"] is True
    ws.check_contract()
    await ws.close()


async def test_get_status_answers_a_status_snapshot(data_hub, simulator):
    ws = await _connect(data_hub)
    await _baseline(ws)
    t0 = time.monotonic()
    await ws.ws.send_json({"command": "get_status"})
    status = await ws.wait("status", since=t0)
    assert status["input_names"]["2"] == "AppleTV"
    ws.check_contract()
    await ws.close()


async def test_link_loss_and_recovery_are_announced(data_hub, simulator):
    ws = await _connect(data_hub)
    await _baseline(ws)
    t0 = time.monotonic()
    simulator.faults.update({"drop_http": True})
    down = await ws.wait("matrix_connection", {"connected": False}, since=t0, timeout=4 * POLL + 5)
    assert down["state"] in ("backoff", "connecting", "disconnected")
    simulator.clear_faults()
    await ws.wait("matrix_connection", {"connected": True}, since=t0, timeout=15)
    ws.check_contract()
    await ws.close()


# --------------------------------------------------------------------------- heartbeat (API-10)


async def test_ping_is_answered_in_both_the_contract_and_the_old_client_form(data_hub):
    """The web client sent {type: 'ping'} while the server only understood {command: 'ping'} (API-10)."""
    ws = await _connect(data_hub)
    t0 = time.monotonic()
    await ws.ws.send_json({"command": "ping"})
    await ws.wait("pong", since=t0)
    t1 = time.monotonic()
    await ws.ws.send_json({"type": "ping"})
    await ws.wait("pong", since=t1)
    assert ws.events("error", t0) == []
    ws.check_contract()
    await ws.close()


async def test_the_server_keeps_idle_clients_alive_with_protocol_pings(data_hub, monkeypatch):
    """Protocol-level heartbeat (ping frames the browser answers by itself), not an app message clients ignore."""
    import rest_api.websocket as hub_ws

    monkeypatch.setattr(hub_ws, "HEARTBEAT_SECONDS", 0.3, raising=False)
    async with data_hub.ws_connect("/ws", autoping=False) as ws:
        deadline = time.monotonic() + 3
        kinds = []
        while time.monotonic() < deadline:
            msg = await ws.receive(timeout=3)
            kinds.append(msg.type)
            if msg.type == aiohttp.WSMsgType.PING:
                await ws.pong(msg.data)
                break
        assert aiohttp.WSMsgType.PING in kinds


# --------------------------------------------------------------------------- slow clients (API-09)


async def test_a_stalled_client_cannot_hold_up_a_command(data_hub, simulator, monkeypatch):
    """API-09: a broadcast awaited each client in turn, before the command was sent."""
    ws = await _connect(data_hub)
    await _baseline(ws)
    stalled = asyncio.Event()

    async def never_returns(self, data, compress=None):
        stalled.set()
        await asyncio.Event().wait()

    monkeypatch.setattr(aiohttp.web.WebSocketResponse, "send_str", never_returns)
    started = time.monotonic()
    resp = await asyncio.wait_for(data_hub.post("/api/switch", json={"input": 3, "output": 1}), timeout=5)
    assert resp.status == 200
    assert time.monotonic() - started < 2
    assert simulator.state.routing[0] == 3
    await ws.close()


# --------------------------------------------------------------------------- truthful /api/status (VAL-04)


async def test_status_is_not_made_up_when_the_status_read_fails(data_hub, simulator):
    """VAL-04: the link is up (health reads answer) but `get video status` fails: no 200 with default names."""
    await data_hub.get("/api/status")
    simulator.faults.update({"http_status": 500, "comheads": ["get video status"]})
    await asyncio.sleep(3.2)  # the hub's status cache (3 s) expires
    resp = await data_hub.get("/api/status")
    body = await resp.json()
    assert resp.status == 503, body
    assert body["success"] is False
    assert body["data"]["connected"] is True  # the link itself is up; the status read failed
    assert "input_names" not in body["data"]


async def test_status_describes_the_link_when_the_matrix_is_offline(data_hub, simulator, matrix):
    simulator.faults.update({"drop_http": True})
    await matrix.get_status(force_refresh=True)  # the hub notices the link is gone
    assert not matrix.connected
    resp = await data_hub.get("/api/status")
    body = await resp.json()
    assert resp.status == 503
    assert body["success"] is False
    assert body["data"]["connected"] is False
    assert body["data"]["state"] in ("backoff", "connecting", "disconnected")
