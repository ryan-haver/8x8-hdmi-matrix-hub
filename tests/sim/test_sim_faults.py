"""Hub behaviour under simulated device faults.

Known bugs from the findings register (docs/REMEDIATION_PLAN.md §4) are
recorded as ``xfail(strict=True)`` tests until their fix lands; the fix then
removes the marker (strict xfail turns an unexpected pass into a failure, so
nobody forgets). The "register regressions" section below holds the tests
whose markers Phase 1 removed.
"""

import asyncio

import aiohttp
import pytest

import orei_matrix
import telnet_client

from .conftest import LoopLagProbe

# ---------------------------------------------------------------- behaviour that works today


async def test_http_500_marks_disconnected(matrix, simulator):
    await matrix.connect()
    simulator.faults.update({"http_status": 500, "http_fault_count": 1})
    assert await matrix.get_video_status() is None
    assert matrix.connected is False


async def test_malformed_json_is_reported(matrix, simulator):
    await matrix.connect()
    simulator.faults.update({"malformed_json": True, "http_fault_count": 1})
    assert await matrix.get_video_status() is None
    assert "Unparseable" in matrix._last_error
    assert await matrix.get_video_status() is not None  # fault was one-shot


async def test_latency_within_client_timeout(matrix, simulator):
    await matrix.connect()
    simulator.faults.update({"latency_ms": 50})
    assert (await matrix.get_status(force_refresh=True))["routing"]


async def test_explicit_reconnect_after_reboot(matrix, simulator):
    await matrix.connect()
    await simulator.reboot(0.2)
    await matrix.disconnect()
    assert await matrix.connect()
    assert (await matrix.get_status(force_refresh=True))["routing"] == simulator.state.routing


# ---------------------------------------------------------------- register regressions (fixed in Phase 1)


async def test_wrong_password_is_not_connected(matrix, simulator):
    simulator.faults.update({"wrong_password": True})
    assert await matrix.connect() is False
    assert matrix.connected is False


async def test_dropped_connection_clears_connected(matrix, simulator):
    await matrix.connect()
    simulator.faults.update({"drop_http": True, "http_fault_count": 1})
    assert await matrix.get_video_status() is None
    assert matrix.connected is False


async def test_timeout_clears_connected(matrix, simulator, monkeypatch):
    real_timeout = aiohttp.ClientTimeout
    # The hub hard-codes a 5 s timeout; shrink it so the test stays fast.
    monkeypatch.setattr(orei_matrix.aiohttp, "ClientTimeout", lambda total=None, **kw: real_timeout(total=0.2))
    await matrix.connect()
    simulator.faults.update({"hang_http": True, "http_fault_count": 1})
    assert await matrix.get_video_status() is None
    assert matrix._last_error == "Command timeout"
    assert matrix.connected is False


async def test_session_expiry_triggers_relogin(matrix, simulator):
    await matrix.connect()
    simulator.expire_sessions()
    status = await matrix.get_status(force_refresh=True)
    assert status.get("routing") == simulator.state.routing


async def test_recovers_after_device_reboot(matrix, simulator):
    await matrix.connect()
    await simulator.reboot(0.2)
    status = await matrix.get_status(force_refresh=True)
    assert status.get("routing") == simulator.state.routing


async def test_rejected_output_setting_reports_failure(matrix, simulator):
    await matrix.connect()
    simulator.faults.update({"reject_writes": True})
    assert await matrix.set_output_hdcp(1, 1) is False


async def test_rejected_switch_all_reports_failure(matrix, simulator):
    await matrix.connect()
    simulator.faults.update({"reject_writes": True})
    assert await matrix.switch_input_to_all(4) is False


#: Every HTTP write method, with arguments the simulator would accept.
_WRITES = {
    "recall_preset": (3,),
    "save_preset": (3,),
    "switch_input": (4, 2),
    "switch_input_to_all": (4,),
    "power_on": (),
    "power_off": (),
    "set_panel_lock": (True,),
    "set_beep": (False,),
    "set_input_name": (2, "Xbox"),
    "set_output_name": (2, "Den"),
    "set_output_enable": (3, False),
    "set_output_hdcp": (3, 2),
    "set_output_hdr": (3, 2),
    "set_output_scaler": (3, 2),
    "set_output_arc": (3, True),
    "set_output_audio_mute": (3, True),
    "set_cec_enable": ("output", 3, True),
    "set_cec_enabled": (3, True, True),
    "set_cec_enabled_bulk": ([True] * 8, [True] * 8),
    "set_lcd_timeout": (2,),
    "set_input_edid": (2, 5),
    "copy_edid_from_output": (2, 1),
    "set_ext_audio_mode": (1,),
    "set_ext_audio_enable": (2, True),
    "set_ext_audio_source": (2, 3),
    "send_cec": ("PLAY", 1),
}


@pytest.mark.parametrize("method", sorted(_WRITES))
async def test_every_write_reports_rejection(matrix, simulator, method):
    """BE-12: HTTP 200 with a failure result is a failed write, for every write method."""
    await matrix.connect()
    before = simulator.state.to_dict()
    simulator.faults.update({"reject_writes": True})
    assert await getattr(matrix, method)(*_WRITES[method]) is False
    assert simulator.state.to_dict() == before


@pytest.mark.parametrize("method", sorted(_WRITES))
async def test_every_write_reports_success(matrix, simulator, method):
    await matrix.connect()
    assert await getattr(matrix, method)(*_WRITES[method]) is True


async def test_telnet_disconnect_completes(matrix_with_telnet):
    """BE-01: cancelling the push listener ends it; disconnect() returns within 1 s."""
    await matrix_with_telnet.connect()
    assert matrix_with_telnet.telnet_connected
    await asyncio.sleep(0.2)  # let the push listener enter its read loop
    telnet = matrix_with_telnet._telnet
    listener = telnet._listener_task
    await asyncio.wait_for(telnet.disconnect(), 1)
    assert listener.done()
    assert not matrix_with_telnet.telnet_connected


async def test_telnet_drop_mid_command_is_detected(matrix_with_telnet, simulator):
    """BE-29 / SIM-01: EOF mid-response marks Telnet down; cables fall back to HTTP."""
    m = matrix_with_telnet
    await m.connect()
    await asyncio.sleep(0.2)
    simulator.faults.update({"telnet_close_mid_command": True, "telnet_fault_count": 1})
    with LoopLagProbe() as probe:
        cables = await m.get_all_cable_status(force_refresh=True)
    assert m.telnet_connected is False
    # Outputs come from HTTP allconnect; inputs are unknown, not "disconnected".
    assert cables["outputs"] == {i + 1: bool(o.connected) for i, o in enumerate(simulator.state.outputs)}
    assert set(cables["inputs"].values()) == {None}
    assert probe.max_lag < 0.2


async def test_telnet_eof_on_device_reboot_does_not_freeze_loop(matrix_with_telnet, simulator):
    """BE-28 / SIM-02: the push listener used to spin on b"" after a reboot.

    Now EOF stops the listener, telnet_connected turns false, the event loop
    stays responsive and the client reconnects once the device is back.
    """
    m = matrix_with_telnet
    await m.connect()
    telnet = m._telnet
    old_listener = telnet._listener_task
    await asyncio.sleep(0.2)  # listener is in its read loop

    with LoopLagProbe() as probe:
        await simulator.reboot(0.3)  # listeners down 0.3 s, then back up
        assert old_listener.done()
        for _ in range(100):
            if m.telnet_connected:
                break
            await asyncio.sleep(0.05)
    assert probe.max_lag < 0.2, f"event loop stalled for {probe.max_lag:.2f}s"
    assert m.telnet_connected, "Telnet did not reconnect after the reboot"
    assert telnet._listener_task is not old_listener and not telnet._listener_task.done()
    # And it works again.
    assert (await m.get_all_cable_status(force_refresh=True))["outputs"][1] is True


async def test_telnet_eof_state_goes_false_immediately(matrix_with_telnet, simulator, monkeypatch):
    """BE-29: after EOF, telnet_connected is false (it used to stay true)."""
    m = matrix_with_telnet
    await m.connect()
    monkeypatch.setattr(m._telnet, "_schedule_reconnect", lambda: None)  # observe the dropped state
    await asyncio.sleep(0.2)
    await simulator.reboot(0.2)
    for _ in range(40):
        if not m.telnet_connected:
            break
        await asyncio.sleep(0.05)
    assert m.telnet_connected is False
    assert m._telnet._writer is None  # socket closed (BE-11)


async def test_telnet_refused_connection_fails_fast(fast_hub, simulator):
    """Device accepts the socket and closes it at once: connect() fails, no spin."""
    simulator.faults.update({"telnet_refuse": True})
    client = telnet_client.TelnetClient("127.0.0.1", simulator.telnet_port)
    with LoopLagProbe() as probe:
        assert await asyncio.wait_for(client.connect(), 3) is False
    assert client.state is telnet_client.TelnetState.DISCONNECTED
    assert client._writer is None and client._listener_task is None
    assert probe.max_lag < 0.2
    await client.disconnect()


async def test_telnet_connect_is_single_flight(fast_hub, simulator):
    """BE-11: concurrent connect() calls open one socket."""
    client = telnet_client.TelnetClient("127.0.0.1", simulator.telnet_port)
    try:
        results = await asyncio.gather(*(client.connect() for _ in range(5)))
        assert results == [True] * 5
        connects = [e for e in simulator.log if e["channel"] == "telnet" and e["command"] == "<connect>"]
        assert len(connects) == 1
    finally:
        await client.disconnect()


async def test_cable_poll_sends_one_status_command(matrix_with_telnet, simulator):
    """BE-30: one `status!` per cable poll (it used to send two)."""
    m = matrix_with_telnet
    await m.connect()
    simulator.log.clear()
    cables = await m.get_all_cable_status(force_refresh=True)
    assert cables["inputs"] == {i + 1: bool(p.cable) for i, p in enumerate(simulator.state.inputs)}
    status_cmds = [e for e in simulator.log if e["channel"] == "telnet" and e["command"] == "status"]
    assert len(status_cmds) == 1
