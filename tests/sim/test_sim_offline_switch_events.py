"""Offline route refusals emit the documented failure event (SW-API-CLIENT-02-C1).

A valid route submitted while the matrix is already disconnected must still be
reported as a refused route: the documented ``switch_failed`` / ``switch_all_failed``
event is emitted, the response stays 503 with no device mutation, and a malformed
offline request does not publish invalid ports. Connected routing and the existing
inside-command failure event are preserved unchanged.

These are focused simulator regressions over the real hub app; the shared
``data_hub`` / ``matrix`` / ``simulator`` fixtures come from ``tests/sim/conftest.py``.
"""

from __future__ import annotations

import asyncio
import contextlib
import json
import time
from typing import Any

import aiohttp
import pytest

from .conftest import sim_writes


class _Ws:
    """A minimal /ws client that records events for offline-route assertions."""

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

    async def close(self) -> None:
        await self.ws.close()
        self._task.cancel()


async def _connect(client) -> _Ws:
    ws = _Ws(await client.ws_connect("/ws"))
    await ws.wait("connected")
    return ws


async def _baseline(ws: _Ws) -> None:
    with contextlib.suppress(AssertionError):
        await ws.wait("status", timeout=3)


async def _read_status(client, status=200):
    response = await client.get("/api/status")
    assert response.status == status, await response.text()
    return await response.json()


async def test_offline_single_output_emits_switch_failed(data_hub, matrix, simulator):
    """A valid single-output route while disconnected: switch_failed, 503, no mutation."""
    before = (await _read_status(data_hub))["data"]["routing"]
    ws = await _connect(data_hub)
    await _baseline(ws)
    await matrix.disconnect()
    t0 = time.monotonic()
    response = await data_hub.post("/api/switch", json={"input": 3, "output": 1})
    assert response.status == 503
    body = await response.json()
    assert body == {"success": False, "data": None, "error": "Matrix not connected"}
    await ws.wait("switch_failed", {"input": 3, "output": 1}, since=t0)
    assert sim_writes(simulator) == []
    assert (await _read_status(data_hub, 503))["error"] == "Matrix not connected"
    await matrix.connect()
    assert (await _read_status(data_hub))["data"]["routing"] == before
    await ws.close()


async def test_offline_route_all_emits_switch_all_failed(data_hub, matrix, simulator):
    """A valid route-to-all while disconnected: switch_all_failed, 503, no mutation."""
    before = (await _read_status(data_hub))["data"]["routing"]
    ws = await _connect(data_hub)
    await _baseline(ws)
    await matrix.disconnect()
    t0 = time.monotonic()
    response = await data_hub.post("/api/switch", json={"input": 4})
    assert response.status == 503
    body = await response.json()
    assert body == {"success": False, "data": None, "error": "Matrix not connected"}
    await ws.wait("switch_all_failed", {"input": 4}, since=t0)
    assert ws.events("switch_failed", t0) == []
    assert sim_writes(simulator) == []
    await matrix.connect()
    assert (await _read_status(data_hub))["data"]["routing"] == before
    await ws.close()


async def test_offline_output_source_emits_switch_failed(data_hub, matrix, simulator):
    """The alternate output-source route while disconnected: switch_failed, 503, no mutation."""
    before = (await _read_status(data_hub))["data"]["routing"]
    ws = await _connect(data_hub)
    await _baseline(ws)
    await matrix.disconnect()
    t0 = time.monotonic()
    response = await data_hub.post("/api/output/2/source", json={"input": 5})
    assert response.status == 503
    body = await response.json()
    assert body == {"success": False, "data": None, "error": "Matrix not connected"}
    await ws.wait("switch_failed", {"input": 5, "output": 2}, since=t0)
    assert sim_writes(simulator) == []
    await matrix.connect()
    assert (await _read_status(data_hub))["data"]["routing"] == before
    await ws.close()


@pytest.mark.parametrize("path,payload", [
    ("/api/switch", {"input": 9, "output": 1}),      # invalid input port
    ("/api/switch", {"input": 1, "output": 9}),      # invalid output port
    ("/api/switch", {"input": 1, "output": 1, "extra": True}),  # unknown field
    ("/api/switch", {}),                              # missing input
    ("/api/switch", {"input": 1, "output": "oops"}),  # non-integer output
    ("/api/output/2/source", {"input": 9}),          # invalid input on source route
])
async def test_offline_malformed_request_is_503_without_events(
    data_hub, matrix, simulator, path, payload,
):
    """Malformed/invalid offline routes keep 503 and publish no ports."""
    ws = await _connect(data_hub)
    await _baseline(ws)
    await matrix.disconnect()
    t0 = time.monotonic()
    response = await data_hub.post(path, json=payload)
    assert response.status == 503
    body = await response.json()
    assert body == {"success": False, "data": None, "error": "Matrix not connected"}
    await asyncio.sleep(0.2)
    assert ws.events("switch_failed", t0) == []
    assert ws.events("switch_all_failed", t0) == []
    assert sim_writes(simulator) == []
    await ws.close()


async def test_connected_route_still_routes_and_reads_back(data_hub, simulator):
    """Connected positive control: a valid route still succeeds and mutates the device."""
    response = await data_hub.post("/api/switch", json={"input": 6, "output": 1})
    assert response.status == 200, await response.text()
    assert (await _read_status(data_hub))["data"]["routing"]["1"] == 6
    assert simulator.state.outputs[0].source == 6


async def test_connected_inside_command_failure_still_emits_once(data_hub, simulator):
    """Connected control: a refused write still returns 500 and one switch_failed event."""
    ws = await _connect(data_hub)
    await _baseline(ws)
    simulator.faults.update({"reject_writes": True})
    t0 = time.monotonic()
    response = await data_hub.post("/api/output/3/source", json={"input": 2})
    assert response.status == 500
    await ws.wait("switch_failed", {"input": 2, "output": 3}, since=t0)
    await asyncio.sleep(3 * 0.5)
    assert len(ws.events("switch_failed", t0)) == 1
    await ws.close()


@pytest.mark.parametrize("path,payload,event,data", [
    ("/api/switch", {"input": 3, "output": 1}, "switch_failed", {"input": 3, "output": 1}),
    ("/api/switch", {"input": 4}, "switch_all_failed", {"input": 4}),
    ("/api/output/2/source", {"input": 5}, "switch_failed", {"input": 5, "output": 2}),
])
async def test_unconfigured_matrix_valid_route_emits_event(data_hub, simulator, monkeypatch, path, payload, event, data):
    """An unconfigured matrix still refuses a valid route with the exact failure event and 503."""
    import rest_api.utils as api_utils

    ws = await _connect(data_hub)
    await _baseline(ws)
    monkeypatch.setattr(api_utils, "_matrix_device", None)
    t0 = time.monotonic()
    response = await data_hub.post(path, json=payload)
    assert response.status == 503
    body = await response.json()
    assert body == {"success": False, "data": None, "error": "Matrix device not configured"}
    await ws.wait(event, data, since=t0)
    assert sim_writes(simulator) == []
    await ws.close()


async def test_unconfigured_matrix_malformed_route_publishes_no_event(data_hub, simulator, monkeypatch):
    """An unconfigured matrix with malformed input: 503 'not configured', no event, no write."""
    import rest_api.utils as api_utils

    ws = await _connect(data_hub)
    await _baseline(ws)
    monkeypatch.setattr(api_utils, "_matrix_device", None)
    t0 = time.monotonic()
    response = await data_hub.post("/api/switch", json={"input": 9, "output": 1})
    assert response.status == 503
    body = await response.json()
    assert body == {"success": False, "data": None, "error": "Matrix device not configured"}
    await asyncio.sleep(0.2)
    assert ws.events("switch_failed", t0) == []
    assert ws.events("switch_all_failed", t0) == []
    assert sim_writes(simulator) == []
    await ws.close()
