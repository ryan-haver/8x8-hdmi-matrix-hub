"""Unit tests of the hub's event stream (src/rest_api/events.py): diffing, snapshots and slow clients.

The end-to-end contract (real hub app, simulator, schema) is tests/sim/test_sim_ws_contract.py.
"""

from __future__ import annotations

import asyncio
import json
from typing import Any

import pytest

from rest_api import events as ev


class FakeWs:
    """Stands in for aiohttp's WebSocketResponse: records what it is sent; can be made to stall."""

    def __init__(self, stall: bool = False) -> None:
        self.sent: list[dict[str, Any]] = []
        self.closed = False
        self._stall = stall

    async def send_str(self, text: str) -> None:
        if self._stall:
            await asyncio.Event().wait()
        self.sent.append(json.loads(text))

    async def close(self) -> None:
        self.closed = True

    def events(self, name: str) -> list[dict[str, Any]]:
        return [m["data"] for m in self.sent if m["event"] == name]


class FakeMatrix:
    host = "192.0.2.1"
    connected = True
    telnet_connected = False


STATUS = {"routing": [2, 2, 1, 1, 5, 6, 1, 1], "power": "on", "input_names": [f"In{i}" for i in range(1, 9)],
          "output_names": [f"Out{i}" for i in range(1, 9)], "preset_names": []}
OUTPUTS = {"allconnect": [1, 1, 0, 0, 0, 0, 0, 0], "allaudiomute": [0] * 8}
INPUTS = {"inactive": [0, 1, 0, 0, 1, 1, 0, 0]}
CABLES = {"inputs": {i: i != 3 for i in range(1, 9)}, "outputs": {i: i < 3 for i in range(1, 9)}}


@pytest.fixture
def stream(monkeypatch):
    matrix = FakeMatrix()
    monkeypatch.setattr("rest_api.utils._matrix_device", matrix)
    s = ev.EventStream(poll_interval=60)
    s._device = matrix
    return s


async def _drain() -> None:
    for _ in range(5):
        await asyncio.sleep(0)


async def test_changes_are_published_once_and_unknown_values_are_ignored(stream):
    ws = FakeWs()
    stream.add_client(ws)
    stream._apply(STATUS, OUTPUTS, INPUTS, None)
    stream._apply({**STATUS, "routing": [0, 7, 1, 1, 5, 6, 1, 1]}, OUTPUTS, INPUTS, None)  # 0 = unknown
    stream._apply({**STATUS, "routing": [0, 7, 1, 1, 5, 6, 1, 1]}, OUTPUTS, INPUTS, None)
    await _drain()
    assert ws.events("routing_change") == [
        {"output": 2, "input": 7, "input_name": "In7", "previous_input": 2}
    ]
    assert len(ws.events("status")) == 1  # the first complete read


async def test_a_first_reading_after_the_snapshot_sends_a_fresh_snapshot(stream):
    """Cables become known once Telnet is up (after the first read): no change event, a new snapshot."""
    ws = FakeWs()
    stream.add_client(ws)
    stream._apply(STATUS, OUTPUTS, INPUTS, None)
    await _drain()
    assert [o["cableConnected"] for o in ws.events("status")[0]["inputs"]][:3] == [None, None, None]
    stream._apply(STATUS, OUTPUTS, INPUTS, CABLES)
    await _drain()
    assert ws.events("cable_change") == []
    snapshots = ws.events("status")
    assert len(snapshots) == 2
    assert [o["cableConnected"] for o in snapshots[1]["inputs"]][:3] == [True, True, False]
    stream._apply(STATUS, OUTPUTS, INPUTS, {**CABLES, "inputs": {**CABLES["inputs"], 3: True}})
    await _drain()
    assert ws.events("cable_change") == [{"type": "input", "port": 3, "connected": True, "name": "In3"}]
    assert len(ws.events("status")) == 2


async def test_link_changes_are_published(stream):
    ws = FakeWs()
    stream.add_client(ws)
    stream._check_link(stream._device)
    stream._device.connected = False
    stream._check_link(stream._device)
    stream._device.connected = True
    stream._check_link(stream._device)
    await _drain()
    assert [e["connected"] for e in ws.events("matrix_connection")] == [False, True]


async def test_publish_never_waits_for_a_stalled_client(stream, monkeypatch):
    monkeypatch.setattr(ev, "SEND_TIMEOUT", 0.2)
    stalled, healthy = FakeWs(stall=True), FakeWs()
    stream.add_client(stalled)
    stream.add_client(healthy)
    stream.publish("power_change", {"power": "off"})  # returns at once
    await asyncio.sleep(0.4)
    assert healthy.events("power_change") == [{"power": "off"}]
    assert stalled.closed  # dropped after SEND_TIMEOUT
    assert stream.client_count == 1


async def test_a_client_that_falls_too_far_behind_is_dropped(stream, monkeypatch):
    monkeypatch.setattr(ev, "QUEUE_LIMIT", 3)
    stalled = FakeWs(stall=True)
    stream.add_client(stalled)
    for _ in range(5):
        stream.publish("power_change", {"power": "on"})
    await _drain()
    assert stream.client_count == 0
    assert stalled.closed


def test_poll_interval_from_env(monkeypatch):
    monkeypatch.setenv("STATUS_POLL_INTERVAL", "2.5")
    assert ev.poll_interval_from_env() == 2.5
    monkeypatch.setenv("STATUS_POLL_INTERVAL", "0.01")
    assert ev.poll_interval_from_env() == ev.MIN_POLL_INTERVAL
    monkeypatch.setenv("STATUS_POLL_INTERVAL", "soon")
    assert ev.poll_interval_from_env() == ev.DEFAULT_POLL_INTERVAL
