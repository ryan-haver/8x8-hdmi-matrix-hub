"""OreiMatrix connection state machine against the simulator (BE-04, BE-05, BE-11, BE-17).

States: DISCONNECTED -> CONNECTING -> CONNECTED / DEGRADED (Telnet down) -> BACKOFF.
"""

import asyncio

import pytest

from orei_matrix import ConnectionState, Events

from .conftest import LoopLagProbe


def _logins(simulator) -> list[dict]:
    return [e for e in simulator.log if e["channel"] == "http" and e["command"] == "login"]


async def _wait_for(predicate, timeout: float = 3.0) -> bool:
    loop = asyncio.get_running_loop()
    deadline = loop.time() + timeout
    while loop.time() < deadline:
        if predicate():
            return True
        await asyncio.sleep(0.02)
    return predicate()


def _record_events(matrix) -> list[str]:
    seen: list[str] = []
    matrix.events.on(Events.CONNECTED, lambda: seen.append("connected"))
    matrix.events.on(Events.DISCONNECTED, lambda: seen.append("disconnected"))
    return seen


async def test_http_only_is_degraded(matrix):
    assert matrix.connection_state is ConnectionState.DISCONNECTED
    assert await matrix.connect()
    assert matrix.connection_state is ConnectionState.DEGRADED  # Telnet disabled in this fixture
    assert matrix.connected


async def test_telnet_up_is_connected_and_drop_is_degraded(matrix_with_telnet, simulator, monkeypatch):
    m = matrix_with_telnet
    assert await m.connect()
    assert m.connection_state is ConnectionState.CONNECTED
    monkeypatch.setattr(m._telnet, "_schedule_reconnect", lambda: None)
    await asyncio.sleep(0.2)
    # Drop only Telnet: EOF on the next command.
    simulator.faults.update({"telnet_close_mid_command": True, "telnet_fault_count": 1})
    await m.get_all_cable_status(force_refresh=True)
    assert m.connection_state is ConnectionState.DEGRADED
    assert m.connected  # HTTP still works


@pytest.mark.parametrize(
    "fault",
    [
        {"drop_http": True, "http_fault_count": 1},
        {"http_status": 500, "http_fault_count": 3},
        {"malformed_json": True, "http_fault_count": 3},
    ],
    ids=["dropped", "http500", "non-json"],
)
async def test_transport_failure_leaves_connected_and_reconnects(matrix, simulator, fault):
    """BE-04: transport errors transition out of CONNECTED, emit DISCONNECTED, then recover.

    A dropped connection is a transport error at once; an HTTP error or an
    unparseable answer only when the health read (two tries) fails too (HIL-12).
    """
    await matrix.connect()
    events = _record_events(matrix)
    simulator.faults.update(fault)
    assert await matrix.get_video_status() is None
    assert matrix.connected is False
    assert matrix.connection_state is ConnectionState.BACKOFF
    assert events == ["disconnected"]
    simulator.clear_faults()
    # The matrix-owned reconnect supervisor brings it back without any caller.
    assert await _wait_for(lambda: matrix.connected)
    assert events == ["disconnected", "connected"]
    assert (await matrix.get_status(force_refresh=True))["routing"] == simulator.state.routing


async def test_intentional_disconnect_does_not_reconnect(matrix, simulator):
    await matrix.connect()
    events = _record_events(matrix)
    await matrix.disconnect()
    logins = len(_logins(simulator))
    await asyncio.sleep(0.2)
    assert matrix.connection_state is ConnectionState.DISCONNECTED
    assert matrix._reconnect_task is None
    assert len(_logins(simulator)) == logins
    assert events == ["disconnected"]


async def test_disconnect_during_backoff_stops_reconnecting(matrix, simulator, monkeypatch):
    import orei_matrix

    monkeypatch.setattr(orei_matrix, "INITIAL_RETRY_DELAY", 5.0)
    await matrix.connect()
    simulator.faults.update({"drop_http": True, "http_fault_count": 1})
    await matrix.get_video_status()
    assert matrix.connection_state is ConnectionState.BACKOFF
    task = matrix._reconnect_task
    await asyncio.wait_for(matrix.disconnect(), 1)
    assert task.done()
    assert matrix.connection_state is ConnectionState.DISCONNECTED


async def test_connect_is_single_flight(matrix, simulator):
    """BE-11: concurrent connect() calls share one login."""
    results = await asyncio.gather(*(matrix.connect() for _ in range(5)))
    assert results == [True] * 5
    assert len(_logins(simulator)) == 1


@pytest.mark.parametrize("style", ["json", "html", "http401"])
async def test_session_expiry_relogs_in_once(matrix, simulator, style):
    """BE-04: one re-login, then the command succeeds, whatever 'not logged in' looks like."""
    await matrix.connect()
    simulator.faults.update({"session_expired_style": style})
    simulator.expire_sessions()
    events = _record_events(matrix)
    status = await matrix.get_status(force_refresh=True)
    assert status["routing"] == simulator.state.routing
    assert len(_logins(simulator)) == 2
    assert matrix.connected and events == []


async def test_session_expiry_before_write_relogs_in(matrix, simulator):
    await matrix.connect()
    simulator.expire_sessions()
    assert await matrix.switch_input(5, 2) is True
    assert simulator.state.outputs[1].source == 5
    assert len(_logins(simulator)) == 2


async def test_failed_relogin_fails_command_and_backs_off(matrix, simulator, monkeypatch):
    import orei_matrix

    monkeypatch.setattr(orei_matrix, "INITIAL_RETRY_DELAY", 5.0)
    await matrix.connect()
    simulator.faults.update({"wrong_password": True})
    simulator.expire_sessions()
    assert await matrix.get_video_status() is None
    assert matrix.connection_state is ConnectionState.BACKOFF
    assert len(_logins(simulator)) == 2  # exactly one re-login attempt


async def test_wrong_password_login_fails(matrix, simulator):
    """BE-05: the echoed comhead 'login' is not success; result 'fail' is failure."""
    simulator.faults.update({"wrong_password": True})
    assert await matrix.connect() is False
    assert matrix.connection_state is ConnectionState.DISCONNECTED
    assert matrix._last_error == "Authentication failed"


async def test_command_lock_not_held_during_backoff(matrix, simulator, monkeypatch):
    """BE-17: during an outage callers fail fast and the command lock stays free.

    The old _send_command held _command_lock across connect_with_retry(2),
    i.e. across 1 s + 2 s backoff sleeps, so every caller queued behind it.
    """
    import orei_matrix

    monkeypatch.setattr(orei_matrix, "INITIAL_RETRY_DELAY", 0.5)
    monkeypatch.setattr(orei_matrix, "MAX_RETRY_DELAY", 1.0)
    await matrix.connect()
    # Device "down": every request (login included) is dropped at once.
    # (A real refused connect is slow on Windows localhost, ~2 s.)
    simulator.faults.update({"drop_http": True})
    loop = asyncio.get_running_loop()

    with LoopLagProbe() as probe:
        start = loop.time()
        assert await matrix.get_video_status() is None  # transport error -> BACKOFF
        assert matrix.connection_state is ConnectionState.BACKOFF
        # More callers during the outage: one quick connect attempt each, no backoff wait.
        results = await asyncio.gather(*(matrix.get_video_status() for _ in range(3)))
        assert results == [None, None, None]
        assert loop.time() - start < 0.5
        assert not matrix._command_lock.locked()
        assert matrix.connection_state is ConnectionState.BACKOFF  # the reconnect loop is sleeping

        simulator.clear_faults()  # device back
        assert await _wait_for(lambda: matrix.connected, timeout=5)
    assert probe.max_lag < 0.2
    assert (await matrix.get_status(force_refresh=True))["routing"] == simulator.state.routing


async def test_system_reboot_reconnects(matrix, simulator):
    """A reboot request is not an intentional disconnect: the hub reconnects."""
    await matrix.connect()
    events = _record_events(matrix)
    assert await matrix.system_reboot()
    assert matrix.connected is False
    assert await _wait_for(lambda: matrix.connected, timeout=5)
    assert events[:2] == ["disconnected", "connected"]
