"""Tests for the simulator's listeners: HTTPS device API, Telnet, control API, faults."""

import asyncio
import json
import time

import aiohttp
import pytest

from tools.simulator import protocol as proto
from tools.simulator.telnet_commands import banner_bytes

LOGIN = {"comhead": "login", "user": "Admin", "password": "admin"}


@pytest.fixture
async def http():
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
        yield session


async def instr(http, sim, payload, *, timeout=2.0):
    """POST one command; returns (status, text)."""
    async with http.post(
        f"{sim.device_url}{proto.INSTR_PATH}", json=payload, timeout=aiohttp.ClientTimeout(total=timeout)
    ) as resp:
        return resp.status, await resp.text()


async def cmd(http, sim, payload):
    status, text = await instr(http, sim, payload)
    assert status == 200
    return json.loads(text)


async def control(http, sim, method, path, body=None):
    async with http.request(method, f"{sim.control_url}/_sim/{path}", json=body) as resp:
        return resp.status, await resp.json() if resp.content_type == "application/json" else await resp.text()


# ================================================================ device HTTPS


async def test_https_with_text_plain_responses(http, simulator):
    assert simulator.device_url.startswith("https://")
    async with http.post(f"{simulator.device_url}/cgi-bin/instr", json=LOGIN) as resp:
        assert resp.status == 200
        assert resp.content_type == "text/plain"  # like the real device
        assert json.loads(await resp.text()) == {"comhead": "login", "result": proto.LOGIN_OK_RESULT}


async def test_login_required_and_wrong_password(http, simulator):
    # not logged in yet
    assert await cmd(http, simulator, {"comhead": "get video status"}) == {
        "comhead": "get video status",
        "result": proto.RESULT_FAIL,
    }
    bad = await cmd(http, simulator, {**LOGIN, "password": "nope"})
    assert bad == {"comhead": "login", "result": proto.LOGIN_FAIL_RESULT}
    await cmd(http, simulator, LOGIN)
    video = await cmd(http, simulator, {"comhead": "get video status", "language": 0})
    assert video["allinputname"][0] == "PS3"
    # a failed login drops the session again
    await cmd(http, simulator, {**LOGIN, "password": "nope"})
    assert "allsource" not in await cmd(http, simulator, {"comhead": "get video status"})


async def test_session_ttl_and_expiry(http, simulator):
    simulator.session_ttl_s = 0.05
    await cmd(http, simulator, LOGIN)
    assert "allsource" in await cmd(http, simulator, {"comhead": "get video status"})
    await asyncio.sleep(0.1)
    assert "allsource" not in await cmd(http, simulator, {"comhead": "get video status"})


@pytest.mark.parametrize("style, status, marker", [("html", 200, "login.html"), ("http401", 401, "Unauthorized")])
async def test_session_expired_styles(http, simulator, style, status, marker):
    simulator.faults.update({"session_expired_style": style})
    got_status, text = await instr(http, simulator, {"comhead": "get video status"})
    assert got_status == status and marker in text


async def test_write_mutates_state_and_is_logged(http, simulator):
    await cmd(http, simulator, LOGIN)
    assert (await cmd(http, simulator, {"comhead": "video switch", "language": 0, "source": [1, 6]}))["result"] == 1
    assert simulator.state.outputs[0].source == 6
    entry = simulator.log[-1]
    assert entry["channel"] == "http" and entry["command"] == "video switch" and entry["mutated"]
    assert simulator.log[0]["payload"]["password"] == "***"


async def test_unknown_comhead_is_recorded(http, simulator):
    await cmd(http, simulator, LOGIN)
    resp = await cmd(http, simulator, {"comhead": "get flux capacitor"})
    assert resp["result"] == proto.UNKNOWN_COMMAND_RESULT
    assert [e["command"] for e in simulator.unrecognised()] == ["get flux capacitor"]


async def test_garbage_body(http, simulator):
    async with http.post(f"{simulator.device_url}/cgi-bin/instr", data=b"{nope") as resp:
        assert json.loads(await resp.text())["result"] == proto.RESULT_FAIL


async def test_set_reboot_takes_device_offline(http, simulator):
    simulator.reboot_seconds = 0.6
    await cmd(http, simulator, LOGIN)
    assert (await cmd(http, simulator, {"comhead": "set reboot"}))["result"] == 1
    await asyncio.sleep(0.15)
    assert simulator.rebooting
    # Linux refuses the connection; Windows keeps retrying the SYN (timeout).
    with pytest.raises((aiohttp.ClientError, asyncio.TimeoutError)):
        await instr(http, simulator, LOGIN, timeout=0.2)
    for _ in range(50):
        if not simulator.rebooting:
            break
        await asyncio.sleep(0.05)
    assert not simulator.rebooting
    # sessions do not survive a reboot
    assert "allsource" not in await cmd(http, simulator, {"comhead": "get video status"})


# ================================================================ HTTP faults


async def test_fault_http_500_with_count(http, simulator):
    simulator.faults.update({"http_status": 500, "http_fault_count": 2})
    assert (await instr(http, simulator, LOGIN))[0] == 500
    assert (await instr(http, simulator, LOGIN))[0] == 500
    assert (await instr(http, simulator, LOGIN))[0] == 200
    assert simulator.faults.http_status is None


async def test_fault_comhead_filter(http, simulator):
    simulator.faults.update({"http_status": 503, "comheads": ["get output status"]})
    await cmd(http, simulator, LOGIN)
    assert (await instr(http, simulator, {"comhead": "get video status"}))[0] == 200
    assert (await instr(http, simulator, {"comhead": "get output status"}))[0] == 503


async def test_fault_malformed_json(http, simulator):
    await cmd(http, simulator, LOGIN)
    simulator.faults.update({"malformed_json": True})
    status, text = await instr(http, simulator, {"comhead": "get video status"})
    assert status == 200
    with pytest.raises(ValueError):
        json.loads(text)


async def test_fault_drop_connection(http, simulator):
    simulator.faults.update({"drop_http": True})
    with pytest.raises(aiohttp.ClientError):
        await instr(http, simulator, LOGIN)


async def test_fault_hang_until_client_timeout_then_release(http, simulator):
    simulator.faults.update({"hang_http": True})
    with pytest.raises(asyncio.TimeoutError):
        await instr(http, simulator, LOGIN, timeout=0.2)
    simulator.clear_faults()
    assert (await instr(http, simulator, LOGIN))[0] == 200


async def test_fault_latency(http, simulator):
    simulator.faults.update({"latency_ms": 150})
    start = time.monotonic()
    await instr(http, simulator, LOGIN)
    assert time.monotonic() - start >= 0.12  # Windows timer granularity


async def test_fault_wrong_password_and_reject_writes(http, simulator):
    simulator.faults.update({"wrong_password": True})
    assert (await cmd(http, simulator, LOGIN))["result"] == proto.LOGIN_FAIL_RESULT
    simulator.faults.update({"wrong_password": False, "reject_writes": True})
    await cmd(http, simulator, LOGIN)
    resp = await cmd(http, simulator, {"comhead": "set output hdcp", "output": 1, "hdcp": 1})
    assert resp["result"] == proto.RESULT_FAIL and simulator.state.outputs[0].hdcp == 3
    assert "allsource" in await cmd(http, simulator, {"comhead": "get video status"})  # reads still work


# ================================================================ Telnet


async def telnet_open(sim):
    reader, writer = await asyncio.open_connection(sim.host, sim.telnet_port)
    expected = banner_bytes(sim.state)  # IAC option negotiation, then the banner text (V1.10.01)
    received = await asyncio.wait_for(reader.readexactly(len(expected)), 1)
    assert received == expected
    return reader, writer, received


async def telnet_cmd(reader, writer, command):
    """Send one command; returns the answer's first line after the device's echo."""
    writer.write(command.encode() + b"!\r\n")
    await writer.drain()
    echo = (await asyncio.wait_for(reader.readline(), 1)).decode()
    assert echo == command + "!\r\n"
    return (await asyncio.wait_for(reader.readline(), 1)).decode()


async def test_telnet_banner_commands_and_push(simulator):
    reader, writer, greeting = await telnet_open(simulator)
    try:
        assert greeting.startswith(b"\xff\xfb\x03") and b"fw version :v1.10.01" in greeting
        assert await telnet_cmd(reader, writer, "r link out 1") == "hdmi output 1: connect\r\n"
        # two commands in one packet, extra CR/LF between them
        writer.write(b"r link in 3!\r\n\r\nr link in 2!\r\n")
        assert (await reader.readline()).decode() == "r link in 3!\r\n"
        assert (await reader.readline()).decode() == "hdmi input 3: disconnect\r\n"
        assert (await reader.readline()).decode() == "r link in 2!\r\n"
        assert (await reader.readline()).decode() == "hdmi input 2: connect\r\n"
        await simulator.cable_event("output", 1, False)
        assert (await asyncio.wait_for(reader.readline(), 1)).decode() == "hdmi output 1: disconnect\r\n"
        assert simulator.state.outputs[0].connected == 0
        assert await telnet_cmd(reader, writer, "bogus") == "E00\r\n"
    finally:
        writer.close()


async def test_telnet_close_mid_command(simulator):
    reader, writer, _ = await telnet_open(simulator)
    simulator.faults.update({"telnet_close_mid_command": True})
    writer.write(b"status!\r\n")
    data = await asyncio.wait_for(reader.read(), 1)  # until EOF
    assert data and b"mac address" not in data
    writer.close()


async def test_telnet_refuse(simulator):
    simulator.faults.update({"telnet_refuse": True})
    reader, writer = await asyncio.open_connection(simulator.host, simulator.telnet_port)
    assert await asyncio.wait_for(reader.read(), 1) == b""
    writer.close()


# ================================================================ control API


async def test_control_state_roundtrip(http, simulator):
    status, doc = await control(http, simulator, "GET", "state")
    assert status == 200 and doc["inputs"][0]["name"] == "PS3"
    doc["inputs"][0]["name"] = "Xbox"
    status, doc = await control(http, simulator, "PUT", "state", doc)
    assert status == 200 and simulator.state.inputs[0].name == "Xbox"
    status, doc = await control(http, simulator, "PATCH", "state", {"outputs": {"1": {"connected": 0}}})
    assert status == 200 and simulator.state.outputs[1].connected == 0
    status, _ = await control(http, simulator, "PUT", "state", {"outputs": [{}]})
    assert status == 400
    status, doc = await control(http, simulator, "POST", "reset")
    assert status == 200 and doc["inputs"][0]["name"] == "PS3" and simulator.state.outputs[1].connected == 1


async def test_control_put_state_as_default(http, simulator):
    doc = simulator.state.to_dict()
    doc["system"]["power"] = 0
    await control(http, simulator, "PUT", "state?as_default=true", doc)
    await control(http, simulator, "POST", "reset")
    assert simulator.state.system["power"] == 0


async def test_control_faults_and_log(http, simulator):
    status, faults = await control(http, simulator, "POST", "faults", {"http_status": 500})
    assert status == 200 and faults["http_status"] == 500
    assert (await instr(http, simulator, LOGIN))[0] == 500
    status, _ = await control(http, simulator, "POST", "faults", {"not_a_fault": 1})
    assert status == 400
    status, faults = await control(http, simulator, "DELETE", "faults")
    assert faults["http_status"] is None
    await instr(http, simulator, LOGIN)
    status, log = await control(http, simulator, "GET", "log?channel=http&limit=1")
    assert status == 200 and len(log) == 1 and log[0]["command"] == "login"
    await control(http, simulator, "DELETE", "log")
    assert len(simulator.log) == 0


async def test_control_events_and_health(http, simulator):
    status, doc = await control(http, simulator, "POST", "event", {"type": "signal", "port": 3, "present": True})
    assert status == 200 and doc["inputs"][2]["signal"] == 1
    status, doc = await control(
        http, simulator, "POST", "event", {"type": "cable", "port_type": "input", "port": 8, "connected": True}
    )
    assert doc["inputs"][7]["cable"] == 1
    status, _ = await control(http, simulator, "POST", "event", {"type": "meteor"})
    assert status == 400
    status, health = await control(http, simulator, "GET", "health")
    assert health["https_port"] == simulator.https_port and health["rebooting"] is False


async def test_control_reboot_and_expire(http, simulator):
    await cmd(http, simulator, LOGIN)
    await control(http, simulator, "POST", "sessions/expire")
    assert not simulator.sessions
    status, body = await control(http, simulator, "POST", "reboot", {"seconds": 0.2})
    assert status == 200 and body["rebooting"]
    await asyncio.sleep(0.05)
    status, health = await control(http, simulator, "GET", "health")  # control stays up
    assert health["rebooting"] is True
    await asyncio.sleep(0.4)
    assert (await instr(http, simulator, LOGIN))[0] == 200
