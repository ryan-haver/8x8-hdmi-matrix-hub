"""Hub behaviour under simulated device faults.

Tests marked ``xfail(strict=True)`` document known bugs from the findings
register (docs/REMEDIATION_PLAN.md §4). They must keep failing until the
Phase 1 fix lands; the fix PR then removes the marker (strict xfail turns an
unexpected pass into a failure, so nobody forgets).
"""

import asyncio

import aiohttp
import pytest

import orei_matrix

from .conftest import defuse_telnet_supervisor

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


# ---------------------------------------------------------------- known bugs (register)


@pytest.mark.xfail(strict=True, reason="BE-05: login treated as success when comhead=='login' (orei_matrix.py:251)")
async def test_wrong_password_is_not_connected(matrix, simulator):
    simulator.faults.update({"wrong_password": True})
    assert await matrix.connect() is False
    assert matrix.connected is False


@pytest.mark.xfail(strict=True, reason="BE-04: 'connected' not cleared on transport errors (orei_matrix.py:373-377)")
async def test_dropped_connection_clears_connected(matrix, simulator):
    await matrix.connect()
    simulator.faults.update({"drop_http": True, "http_fault_count": 1})
    assert await matrix.get_video_status() is None
    assert matrix.connected is False


@pytest.mark.xfail(strict=True, reason="BE-04: 'connected' not cleared on timeouts (orei_matrix.py:369-372)")
async def test_timeout_clears_connected(matrix, simulator, monkeypatch):
    real_timeout = aiohttp.ClientTimeout
    # The hub hard-codes a 5 s timeout; shrink it so the test stays fast.
    monkeypatch.setattr(orei_matrix.aiohttp, "ClientTimeout", lambda total=None, **kw: real_timeout(total=0.2))
    await matrix.connect()
    simulator.faults.update({"hang_http": True, "http_fault_count": 1})
    assert await matrix.get_video_status() is None
    assert matrix._last_error == "Command timeout"
    assert matrix.connected is False


@pytest.mark.xfail(strict=True, reason="BE-04: no re-login on session expiry; empty status returned as success")
async def test_session_expiry_triggers_relogin(matrix, simulator):
    await matrix.connect()
    simulator.expire_sessions()
    status = await matrix.get_status(force_refresh=True)
    assert status.get("routing") == simulator.state.routing


@pytest.mark.xfail(strict=True, reason="BE-04: hub never re-authenticates after the matrix reboots")
async def test_recovers_after_device_reboot(matrix, simulator):
    await matrix.connect()
    await simulator.reboot(0.2)
    status = await matrix.get_status(force_refresh=True)
    assert status.get("routing") == simulator.state.routing


@pytest.mark.xfail(strict=True, reason="BE-12: write methods report success on HTTP 200 regardless of result")
async def test_rejected_output_setting_reports_failure(matrix, simulator):
    await matrix.connect()
    simulator.faults.update({"reject_writes": True})
    assert await matrix.set_output_hdcp(1, 1) is False


@pytest.mark.xfail(strict=True, reason="BE-12: switch_input_to_all returns True on failure (orei_matrix.py:582-585)")
async def test_rejected_switch_all_reports_failure(matrix, simulator):
    await matrix.connect()
    simulator.faults.update({"reject_writes": True})
    assert await matrix.switch_input_to_all(4) is False


@pytest.mark.xfail(
    strict=True,
    reason="BE-01: push listener swallows CancelledError and the supervisor restarts it, so disconnect() hangs",
)
async def test_telnet_disconnect_completes(matrix_with_telnet):
    await matrix_with_telnet.connect()
    assert matrix_with_telnet.telnet_connected
    await asyncio.sleep(0.2)  # let the push listener enter its read loop
    telnet = matrix_with_telnet._telnet
    disconnect = asyncio.ensure_future(telnet.disconnect())
    done, _ = await asyncio.wait([disconnect], timeout=0.5)
    # Unstick it without cancelling disconnect() itself (that would let the
    # supervisor hot-spin): make the next restart raise, then cancel again.
    defuse_telnet_supervisor(matrix_with_telnet)
    telnet._listener_task.cancel()
    await asyncio.wait_for(disconnect, 2)
    assert done, "TelnetClient.disconnect() did not finish within 0.5 s"


@pytest.mark.xfail(
    strict=True,
    reason="SIM-01 (new): Telnet EOF is not detected (telnet_client.py:271-273), so a dropped connection "
    "stays 'connected' and cable status silently reads as all-disconnected",
)
async def test_telnet_drop_mid_command_is_detected(matrix_with_telnet, simulator):
    m = matrix_with_telnet
    await m.connect()
    await asyncio.sleep(0.2)
    # Stop the push listener first: once the socket hits EOF it busy-loops
    # without ever yielding (SIM-02, telnet_client.py:478-495) and would
    # freeze this test's event loop.
    listener = m._telnet._listener_task
    defuse_telnet_supervisor(m)
    listener.cancel()
    await asyncio.wait([listener], timeout=1)
    assert listener.done()

    simulator.faults.update({"telnet_close_mid_command": True, "telnet_fault_count": 1})
    cables = await m.get_all_cable_status(force_refresh=True)
    assert m.telnet_connected is False or cables["outputs"][1] is True
