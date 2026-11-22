"""R1C matrix-owned read drain; all network traffic is loopback simulator traffic.

Only the HTTP-only fixture doubles Telnet startup. Other seams are explicit
synchronization gates around real fetch/POST/close operations, never fake drains.
"""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock

import pytest

from orei_matrix import ConnectionState, OreiMatrix
from tools.simulator import DeviceState, Simulator


class GatedSimulator(Simulator):
    """Hold one real HTTP response after simulator dispatch has logged it."""

    def __init__(self):
        super().__init__(DeviceState.default(), host="127.0.0.1", https_port=0,
                         telnet_port=0, control_port=0, tls=False)
        self.hold_command = None
        self.received = asyncio.Event()
        self.release = asyncio.Event()
        self.finished = asyncio.Event()

    async def _handle_instr(self, request):
        command = (await request.json()).get("comhead")
        response = await super()._handle_instr(request)
        if command == self.hold_command:
            self.received.set()
            try:
                await self.release.wait()
            finally:
                self.finished.set()
        return response


@pytest.fixture
async def sim():
    async with GatedSimulator() as simulator:
        try:
            yield simulator
        finally:
            simulator.release.set()
            if simulator.received.is_set():
                await asyncio.wait_for(simulator.finished.wait(), 1)


@pytest.fixture
async def matrix(sim, monkeypatch):
    m = OreiMatrix("127.0.0.1", port=sim.https_port, use_https=False,
                   telnet_port=sim.telnet_port, user="Admin", password="admin")
    # The HTTP-only cases exercise actual HTTP login, retries and session close.
    monkeypatch.setattr(m, "_connect_telnet", AsyncMock(return_value=False))
    try:
        assert await m.connect()
        yield m
    finally:
        await m.disconnect()


async def cancelled(task):
    with pytest.raises(asyncio.CancelledError):
        await task


def assert_settled(matrix, tasks, session):
    assert all(task.done() for task in tasks)
    assert not matrix._fetch_tasks
    assert not matrix._inflight
    assert matrix._disconnect_task.done()
    assert matrix._session is None and session.closed
    assert matrix._telnet is None
    assert matrix._connect_task is matrix._relogin_task is matrix._reconnect_task is None
    assert matrix.connection_state is ConnectionState.DISCONNECTED


async def test_cancelled_waiter_keeps_shared_fetch_alive_until_disconnect(matrix, sim, monkeypatch):
    entered, release, joined = asyncio.Event(), asyncio.Event(), asyncio.Event()
    original = matrix._fetch_output_status

    async def gated_fetch():
        entered.set()
        await release.wait()
        return await original()

    monkeypatch.setattr(matrix, "_fetch_output_status", gated_fetch)
    first = asyncio.create_task(matrix.get_output_status())
    await asyncio.wait_for(entered.wait(), 1)
    fetch = matrix._inflight["output_status"][1]

    async def second_waiter():
        # Event.set does not yield; this waiter reaches the shield before the
        # test resumes, proving that both consumers joined the same work.
        joined.set()
        return await matrix.get_output_status()

    second = asyncio.create_task(second_waiter())
    await joined.wait()
    first.cancel()
    await cancelled(first)
    assert not fetch.done() and not second.done()
    assert len(matrix._fetch_tasks) == 1
    session = matrix._session
    log = list(sim.log)
    unrelated = asyncio.create_task(asyncio.Event().wait())
    try:
        await asyncio.wait_for(matrix.disconnect(), 1)
        assert not unrelated.done()
    finally:
        unrelated.cancel()
        await cancelled(unrelated)
    await cancelled(second)
    assert fetch.cancelled()
    assert_settled(matrix, [fetch], session)
    release.set()
    assert list(sim.log) == log


async def test_waiter_cancellation_without_disconnect_preserves_result(matrix, sim):
    sim.hold_command = "get output status"
    first = asyncio.create_task(matrix.get_output_status())
    await asyncio.wait_for(sim.received.wait(), 1)
    fetch = matrix._inflight["output_status"][1]
    first.cancel()
    await cancelled(first)
    assert not fetch.done()
    sim.release.set()
    result = await asyncio.wait_for(matrix.get_output_status(), 1)
    assert result["allconnect"] == [p.connected for p in sim.state.outputs]
    assert fetch.done() and not matrix._fetch_tasks
    assert sum(e["command"] == "get output status" for e in sim.log) == 1


async def test_late_read_continuation_cannot_reopen_disposed_transport(matrix, sim, monkeypatch):
    """A late fallback, even one consuming cancellation, cannot open a session.

    This also reproduces the original bug using only pre-existing matrix
    methods/fields: before the fix disconnect returned with the read alive,
    then releasing it allocated another session and logged in after teardown.
    """
    original = matrix._fetch_output_status
    entered, release = asyncio.Event(), asyncio.Event()

    async def late_fetch():
        entered.set()
        try:
            await release.wait()
        except asyncio.CancelledError:
            pass  # emulate a read's best-effort fallback during cancellation
        return await original()

    monkeypatch.setattr(matrix, "_fetch_output_status", late_fetch)
    waiter = asyncio.create_task(matrix.get_output_status())
    await asyncio.wait_for(entered.wait(), 1)
    fetch = matrix._inflight["output_status"][1]
    session = matrix._session
    waiter.cancel()
    await cancelled(waiter)
    log = list(sim.log)
    try:
        await asyncio.wait_for(matrix.disconnect(), 1)
        release.set()
        result = await asyncio.wait_for(fetch, 1)
        assert result is None
        assert session.closed and matrix._session is None
        assert list(sim.log) == log
    finally:
        release.set()
        await asyncio.gather(fetch, return_exceptions=True)
        await matrix.disconnect()


async def test_disconnect_tracks_superseded_generation_and_nested_fetch(matrix, monkeypatch):
    original = matrix._fetch_output_status
    entered = [asyncio.Event(), asyncio.Event()]
    release = asyncio.Event()
    calls = 0

    async def gated_fetch():
        nonlocal calls
        index = calls
        calls += 1
        entered[index].set()
        await release.wait()
        return await original()

    monkeypatch.setattr(matrix, "_fetch_output_status", gated_fetch)
    # cable_status owns a shielded output_status child as well.
    old = asyncio.create_task(matrix.get_all_cable_status(force_refresh=True))
    await asyncio.wait_for(entered[0].wait(), 1)
    old_fetch = matrix._inflight["output_status"][1]
    assert await matrix.switch_input(6, 1)  # actual write advances generation
    new = asyncio.create_task(matrix.get_output_status(force_refresh=True))
    await asyncio.wait_for(entered[1].wait(), 1)
    new_fetch = matrix._inflight["output_status"][1]
    assert old_fetch is not new_fetch
    assert len(matrix._fetch_tasks) == 3
    owned = set(matrix._fetch_tasks)
    session = matrix._session
    await asyncio.wait_for(matrix.disconnect(), 1)
    await cancelled(old)
    await cancelled(new)
    assert_settled(matrix, owned, session)
    assert all(task.cancelled() for task in owned)


async def test_generation_results_remain_isolated_after_write(matrix, monkeypatch):
    original = matrix._send_command
    old_response_ready, release_old = asyncio.Event(), asyncio.Event()
    calls = 0

    async def delayed_result(command, *args, **kwargs):
        nonlocal calls
        result = await original(command, *args, **kwargs)
        if command["comhead"] == "get video status":
            calls += 1
            if calls == 1:
                old_response_ready.set()
                await release_old.wait()
        return result

    monkeypatch.setattr(matrix, "_send_command", delayed_result)
    old = asyncio.create_task(matrix.get_status(force_refresh=True))
    await asyncio.wait_for(old_response_ready.wait(), 1)
    assert await matrix.switch_input(7, 1)
    current = await matrix.get_status(force_refresh=True)
    assert current["routing"][0] == 7
    release_old.set()
    stale = await old
    assert stale["routing"][0] != 7
    assert (await matrix.get_status())["routing"][0] == 7
    assert not matrix._fetch_tasks and not matrix._inflight


async def test_cancelled_concurrent_disconnect_waits_for_cleanup_and_reopens_explicitly(matrix, sim, monkeypatch):
    session = matrix._session
    close = session.close
    closing, release, second_entered = asyncio.Event(), asyncio.Event(), asyncio.Event()

    async def gated_close():
        closing.set()
        await release.wait()
        await close()

    monkeypatch.setattr(session, "close", gated_close)
    first = asyncio.create_task(matrix.disconnect())
    await asyncio.wait_for(closing.wait(), 1)
    cleanup = matrix._disconnect_task

    async def another_disconnect():
        second_entered.set()
        await matrix.disconnect()

    second = asyncio.create_task(another_disconnect())
    await second_entered.wait()
    first.cancel()
    # A loop callback proves the first cancellation was processed before a
    # second cancellation; no timing sleep decides whether cleanup is done.
    checkpoint = asyncio.get_running_loop().create_future()
    asyncio.get_running_loop().call_soon(checkpoint.set_result, None)
    await checkpoint
    first.cancel()
    assert matrix._disconnect_task is cleanup and not cleanup.done()
    assert not await matrix.connect()
    matrix.start_auto_reconnect()
    assert matrix._reconnect_task is None
    log = list(sim.log)
    assert await matrix._send_command({"comhead": "set poweronoff", "power": 0}) == (False, None)
    assert not await matrix._relogin()
    assert list(sim.log) == log
    release.set()
    await cancelled(first)
    await asyncio.wait_for(second, 1)
    assert_settled(matrix, [], session)
    await matrix.disconnect()  # repeated calls after settlement also work
    assert await matrix.connect()
    assert matrix._session is not session and not matrix._session.closed
    assert (await matrix.get_status(force_refresh=True))["routing"] == sim.state.routing


@pytest.mark.parametrize("command", ["get output status", "login"])
async def test_real_http_and_telnet_resources_settle_on_disconnect(sim, monkeypatch, command):
    m = OreiMatrix("127.0.0.1", port=sim.https_port, use_https=False,
                   telnet_port=sim.telnet_port, user="Admin", password="admin")
    try:
        assert await m.connect() and m.telnet_connected
        session, telnet = m._session, m._telnet
        # Expired authentication creates a shielded re-login child from the
        # real cached read, while the other case stops an active status POST.
        sim.hold_command = command
        if command == "login":
            sim.expire_sessions()
        waiter = asyncio.create_task(m.get_output_status(force_refresh=True))
        await asyncio.wait_for(sim.received.wait(), 1)
        owned = m._owned_transport_tasks()
        telnet_tasks = {telnet._listener_task, telnet._reconnect_task} - {None}
        waiter.cancel()
        await cancelled(waiter)
        assert any(not task.done() for task in owned)
        connect, login = AsyncMock(wraps=m.connect), AsyncMock(wraps=m._login)
        monkeypatch.setattr(m, "connect", connect)
        monkeypatch.setattr(m, "_login", login)
        await asyncio.wait_for(m.disconnect(), 1)
        assert_settled(m, owned, session)
        assert all(task.done() for task in telnet_tasks)
        assert not telnet.connected
        # Settle the already dispatched server handler before comparing logs.
        sim.hold_command = None
        sim.release.set()
        await asyncio.wait_for(sim.finished.wait(), 1)
        log = list(sim.log)
        assert await m._send_command({"comhead": "get output status"}) == (False, None)
        assert await m._send_command({"comhead": "set poweronoff", "power": 0}) == (False, None)
        assert not await m._relogin()
        assert (await m._post({"comhead": "login"})).kind == "transport"
        with pytest.raises(asyncio.CancelledError):
            await m.get_all_cable_status(force_refresh=True)
        connect.assert_not_awaited()
        login.assert_not_awaited()
        assert list(sim.log) == log
        assert await m.connect() and m.telnet_connected
        assert m._session is not session and not m._session.closed
        assert (await m.get_status(force_refresh=True))["routing"] == sim.state.routing
        assert connect.await_count == login.await_count == 1
    finally:
        sim.release.set()
        await m.disconnect()


async def test_disconnect_cancels_an_initial_shared_connect(sim, monkeypatch):
    m = OreiMatrix("127.0.0.1", port=sim.https_port, use_https=False,
                   telnet_port=sim.telnet_port, user="Admin", password="admin")
    monkeypatch.setattr(m, "_connect_telnet", AsyncMock(return_value=False))
    sim.hold_command = "login"
    waiter = asyncio.create_task(m.get_output_status())
    try:
        await asyncio.wait_for(sim.received.wait(), 1)
        session, tasks = m._session, m._owned_transport_tasks()
        await asyncio.wait_for(m.disconnect(), 1)
        await cancelled(waiter)
        assert_settled(m, tasks, session)
        m._connect_telnet.assert_not_awaited()
    finally:
        sim.release.set()
        await m.disconnect()


async def test_explicit_start_reconnects_after_disconnect(matrix, sim, monkeypatch):
    session = matrix._session
    await matrix.disconnect()
    assert session.closed
    monkeypatch.setattr(matrix, "_calculate_retry_delay", lambda attempt: 0)
    matrix.start_auto_reconnect()
    reconnect = matrix._reconnect_task
    assert reconnect is not None
    await asyncio.wait_for(reconnect, 1)
    assert matrix.connected
    assert matrix._session is not session and not matrix._session.closed
    assert (await matrix.get_status(force_refresh=True))["routing"] == sim.state.routing
