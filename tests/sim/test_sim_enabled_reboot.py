"""Enabled reboot through the real REST app; no manual reconnect or hardware writes."""

import asyncio
import copy
import time
from unittest.mock import AsyncMock

import pytest

import orei_matrix
from telnet_client import TelnetClient

from .test_sim_ws_contract import _connect

PATHS = (
    "/api/system/reboot",
    "/api/system-shortcuts/system_reboot/execute",
    "/api/shortcuts/system_reboot/execute",
)


async def wait_until(predicate, timeout=5):
    deadline = time.monotonic() + timeout
    while not predicate():
        assert time.monotonic() < deadline, "reboot lifecycle did not complete"
        await asyncio.sleep(0.02)


@pytest.fixture(autouse=True)
def reboot_timing(monkeypatch, fast_hub):
    monkeypatch.setenv("STATUS_POLL_INTERVAL", "0.2")
    # Reconnect after the simulator's delayed reboot actually starts.
    monkeypatch.setattr(orei_matrix, "INITIAL_RETRY_DELAY", 0.1)
    monkeypatch.setattr(orei_matrix, "MAX_RETRY_DELAY", 0.2)


def commands(simulator, channel):
    return [e for e in simulator.log if e.get("channel") == channel and e.get("command") == "reboot"]


@pytest.mark.parametrize("path", PATHS)
@pytest.mark.parametrize("transport", ("http", "telnet"))
async def test_enabled_reboot_recovers_without_manual_connect(data_hub, matrix, simulator, monkeypatch, path, transport):
    if transport == "telnet":
        monkeypatch.setattr(matrix, "_connect_telnet", orei_matrix.OreiMatrix._connect_telnet.__get__(matrix))
        assert await matrix._connect_telnet()
        assert matrix.telnet_connected
    enabled = await data_hub.put("/api/system-shortcuts/system_reboot", json={"enabled": True})
    assert enabled.status == 200
    ws = await _connect(data_hub)
    try:
        await ws.wait("status")
        before = copy.deepcopy(simulator.state.to_dict())
        simulator.log.clear()
        started = time.monotonic()
        response = await data_hub.post(path, json={})
        assert response.status == 200, await response.text()
        assert (await response.json())["success"] is True
        await wait_until(lambda: simulator.rebooting)
        await ws.wait("matrix_connection", {"connected": False}, since=started)
        await wait_until(lambda: not simulator.rebooting and matrix.connected)
        await ws.wait("matrix_connection", {"connected": True}, since=started)
        if transport == "telnet":
            await wait_until(lambda: matrix.telnet_connected)
        assert bool(matrix.telnet_connected) == (transport == "telnet")
        assert len(commands(simulator, transport)) == 1
        assert not commands(simulator, "http" if transport == "telnet" else "telnet")
        assert len([e for e in simulator.log if e.get("channel") == "sim" and e["command"].startswith("reboot (")]) == 1
        assert simulator.state.to_dict() == before
        health = await (await data_hub.get("/api/health")).json()
        assert health["data"]["matrix"]["connected"] is True
        # A new REST write proves the recovered connection is usable.
        routed = await data_hub.post("/api/output/1/source", json={"input": 5})
        assert routed.status == 200
        assert simulator.state.routing[0] == 5
        assert not [e for e in simulator.log if e.get("warnings")]
        ws.check_contract()
    finally:
        await ws.close()


@pytest.mark.parametrize("path", PATHS)
async def test_refused_http_reboot_is_not_retried(data_hub, matrix, simulator, path):
    assert (await data_hub.put("/api/system-shortcuts/system_reboot", json={"enabled": True})).status == 200
    before = copy.deepcopy(simulator.state.to_dict())
    simulator.faults.update({"reject_writes": True, "comheads": ["reboot"]})
    simulator.log.clear()
    response = await data_hub.post(path, json={})
    assert response.status == 500
    assert (await response.json())["success"] is False
    await asyncio.sleep(0.2)
    assert len(commands(simulator, "http")) == 1
    assert not commands(simulator, "telnet")
    assert not simulator.rebooting
    assert not [e for e in simulator.log if e.get("channel") == "sim" and e["command"].startswith("reboot (")]
    assert simulator.state.to_dict() == before
    assert matrix.connected


async def test_dropped_http_reboot_is_not_retried(data_hub, simulator):
    simulator.faults.update({"drop_http": True, "http_fault_count": 1, "comheads": ["reboot"]})
    simulator.log.clear()
    response = await data_hub.post("/api/system/reboot", json={})
    assert response.status == 500
    await asyncio.sleep(0.3)
    assert len(commands(simulator, "http")) == 1
    assert not [e for e in simulator.log if e.get("channel") == "sim" and e["command"].startswith("reboot (")]


async def test_silent_telnet_reboot_falls_back_to_one_http_reboot(matrix_with_telnet, simulator):
    matrix = matrix_with_telnet
    assert await matrix.connect()
    simulator.log.clear()
    simulator.faults.update({"telnet_silent": True, "telnet_fault_count": 1})
    assert await matrix.system_reboot()
    await wait_until(lambda: simulator.rebooting)
    await wait_until(lambda: not simulator.rebooting and matrix.connected and matrix.telnet_connected)
    assert len(commands(simulator, "telnet")) == 1
    assert commands(simulator, "telnet")[0]["fault"] == "telnet_silent"
    assert len(commands(simulator, "http")) == 1
    assert len([e for e in simulator.log if e.get("channel") == "sim" and e["command"].startswith("reboot (")]) == 1


@pytest.mark.parametrize("response,expected", (
    ("reboot!\r\nreboot...\r\n", True),
    ("E00\r\n", False), ("E01", False), ("", False), ("reboot!\r\n", False),
))
async def test_telnet_reboot_requires_an_acknowledgement(monkeypatch, response, expected):
    client = TelnetClient("127.0.0.1")
    send = AsyncMock(return_value=response)
    monkeypatch.setattr(client, "_send_raw", send)
    assert await client.reboot() is expected
    send.assert_awaited_once_with("reboot")
