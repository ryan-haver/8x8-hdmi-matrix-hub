"""Real-runtime rollback boundaries; synchronization wraps actual operations.

The shared SIM fixture shortens only transport retry backoff. HTTP and runtime
cleanup budgets are unchanged. Close gates always delegate aiohttp's real close;
the drain gate runs the real runtime cancellation/drain before holding its return.
"""

from __future__ import annotations

import asyncio
import logging

import aiohttp
import pytest

import hub.runtime.composition as composition
from hub.runtime.config import MatrixAddress
from tests.test_runtime_rollback_deadline_r1h import storage
from tests.test_runtime_rollback_reconnect_r1g import ready
from tests.test_runtime_rollback_reconnect_r1g import runtime_sim as runtime_sim

_LOG = logging.getLogger(__name__)


def restored(runtime, original, address, names, before):
    assert runtime.service.client is original and runtime.address == address
    assert runtime.service.names is names
    assert original.credentials() == ("original-user", "original-secret")
    assert runtime.snapshot().input_names[1] == "Saved console"
    assert runtime.snapshot().output_names[1] == "Saved screen"
    assert storage(runtime) == before


async def test_cancellation_after_actual_runtime_drain_resumes_refresh(runtime_sim, monkeypatch):
    runtime, sim, clients, _ = await runtime_sim()
    original, address, names = clients[0], runtime.address, runtime.service.names
    before = storage(runtime)
    entered, release = asyncio.Event(), asyncio.Event()
    actual_cancel = runtime._cancel

    async def drain(tasks):
        await actual_cancel(tasks)
        if asyncio.current_task() is setup:
            entered.set()
            await release.wait()

    monkeypatch.setattr(runtime, "_cancel", drain)
    setup = asyncio.create_task(runtime.reconfigure(address, persist=True))
    try:
        await asyncio.wait_for(entered.wait(), 3)
        setup.cancel()
        with pytest.raises(asyncio.CancelledError):
            await asyncio.wait_for(asyncio.shield(setup), 3)
        restored(runtime, original, address, names, before)
        assert len(clients) == sim.login_count == 1
        assert runtime._refresh_task is not None and not runtime._refresh_task.done()
        sim.state.outputs[0].source = 7
        await ready(lambda: runtime.snapshot().routing.get(1) == 7)
    finally:
        release.set()
        await asyncio.gather(setup, return_exceptions=True)


async def test_native_cancellation_at_original_close_restores_and_reads_actual_state(runtime_sim, monkeypatch):
    runtime, sim, clients, _ = await runtime_sim()
    original, address, names = clients[0], runtime.address, runtime.service.names
    before = storage(runtime)
    session = original._session
    actual_close = aiohttp.ClientSession.close
    fired = False

    async def close(current):
        nonlocal fired
        if current is session and not fired:
            fired = True
            asyncio.get_running_loop().call_soon(setup.cancel)
        await actual_close(current)

    monkeypatch.setattr(aiohttp.ClientSession, "close", close)
    sim.state.outputs[0].source = 7
    setup = asyncio.create_task(runtime.reconfigure(address, persist=True))
    with pytest.raises(asyncio.CancelledError):
        await asyncio.wait_for(asyncio.shield(setup), 3)
    assert fired and setup.cancelled() and len(clients) == 1
    restored(runtime, original, address, names, before)
    await ready(lambda: runtime.snapshot().connected and runtime.snapshot().routing.get(1) == 7)
    assert sum(client.connected for client in clients) == 1


async def test_cancelled_drain_hands_pending_original_login_to_existing_supervisor(runtime_sim, monkeypatch):
    runtime, sim, clients, _ = await runtime_sim()
    original, address, names = clients[0], runtime.address, runtime.service.names
    before = storage(runtime)
    await original.disconnect()
    await runtime.refresh()
    sim.hold_login = 2
    sim.faults.update({"http_status": 503, "comheads": ["login"], "http_fault_count": 1})
    runtime._connect_task = asyncio.create_task(runtime._initial_connect())
    await asyncio.wait_for(sim.received.wait(), 3)
    attempt = original._connect_task
    entered, release = asyncio.Event(), asyncio.Event()
    actual_cancel = runtime._cancel

    async def drain(tasks):
        await actual_cancel(tasks)
        if asyncio.current_task() is setup:
            entered.set()
            await release.wait()

    monkeypatch.setattr(runtime, "_cancel", drain)
    setup = asyncio.create_task(runtime.reconfigure(address, persist=True))
    try:
        await asyncio.wait_for(entered.wait(), 3)
        setup.cancel()
        with pytest.raises(asyncio.CancelledError):
            await asyncio.wait_for(asyncio.shield(setup), 3)
        restored(runtime, original, address, names, before)
        assert original._connect_task is attempt and not attempt.done()
        assert original._reconnect_task is not None
        sim.release.set()
        await ready(lambda: runtime.snapshot().connected and runtime.snapshot().routing.get(1) is not None)
        assert sim.login_count == 3 and len(clients) == 1
    finally:
        release.set()
        sim.release.set()
        await asyncio.gather(setup, return_exceptions=True)


@pytest.mark.parametrize("when", ["before_disposal", "after_disposal"])
async def test_candidate_disconnect_exception_cannot_skip_restoration_or_bypass_fence(runtime_sim, monkeypatch, when):
    runtime, sim, clients, _ = await runtime_sim()
    original, address, names = clients[0], runtime.address, runtime.service.names
    before = storage(runtime)
    actual_factory = runtime.matrix_factory
    actual_candidate_disconnect = None

    def factory(*args, **kwargs):
        nonlocal actual_candidate_disconnect
        candidate = actual_factory(*args, **kwargs)
        actual_disconnect = candidate.disconnect
        actual_candidate_disconnect = actual_disconnect

        async def disconnect():
            if when == "before_disposal" and not runtime._stopping:
                # Fault injection is a failed public call, never a pretend
                # drain. Shutdown must delegate the actual operation afterward.
                raise OSError("controlled failure before actual candidate disposal")
            await actual_disconnect()
            if when == "after_disposal":
                raise OSError("controlled failure after actual candidate disposal")

        candidate.disconnect = disconnect
        return candidate

    monkeypatch.setattr(runtime, "matrix_factory", factory)
    sim.faults.update({"http_status": 503, "comheads": ["login"], "http_fault_count": 1})
    target = MatrixAddress("localhost", sim.https_port, sim.telnet_port, "candidate-user", "candidate-secret")
    try:
        result = await asyncio.wait_for(runtime.reconfigure(target, persist=True), 3)
        assert not result.success and not result.connected
        restored(runtime, original, address, names, before)
        candidate = clients[1]
        assert not original.connected and original._reconnect_task is None
        (retirement,) = runtime._retirements
        assert runtime._retirements[retirement] is candidate
        assert isinstance(retirement.exception(), OSError)
        with pytest.raises(RuntimeError, match="Previous matrix cleanup"):
            await runtime.commands.power(False)
        assert sim.login_count == 2 and sim.state.system["power"] == 1
        # Production cannot infer that the injected AFTER exception was safe.
        # Both cases require an actual supported lifecycle drain before reuse.
        await asyncio.wait_for(runtime.stop(), 3)
        assert candidate._session is None and candidate._telnet is None
        assert candidate._connect_task is None and candidate._reconnect_task is None
        assert original._reconnect_task is None and not runtime._raw_unlisten
        assert storage(runtime) == before
    finally:
        if actual_candidate_disconnect:
            await actual_candidate_disconnect()


@pytest.mark.parametrize("original_close", [False, True])
async def test_unreleased_real_close_cannot_hold_cancelled_caller_forever(runtime_sim, monkeypatch, original_close):
    runtime, sim, clients, _ = await runtime_sim()
    original, address, names = clients[0], runtime.address, runtime.service.names
    before = storage(runtime)
    entered, release = asyncio.Event(), asyncio.Event()
    actual_close = aiohttp.ClientSession.close

    async def close(session):
        target = clients[0] if original_close else (clients[1] if len(clients) > 1 else None)
        if target is not None and session is target._session:
            entered.set()
            await release.wait()
        await actual_close(session)

    monkeypatch.setattr(aiohttp.ClientSession, "close", close)
    sim.faults.update({"http_status": 503, "comheads": ["login"], "http_fault_count": 1})
    target = MatrixAddress("localhost", sim.https_port, sim.telnet_port, "candidate-user", "candidate-secret")
    setup = asyncio.create_task(runtime.reconfigure(target, persist=True))
    try:
        await asyncio.wait_for(entered.wait(), 3)
        started = asyncio.get_running_loop().time()
        setup.cancel()
        done, _ = await asyncio.wait({setup}, timeout=composition.CLEANUP_TIMEOUT + 1)
        assert setup in done, "Caller still blocked by cancellation-resistant public disconnect"
        assert setup.cancelled() and asyncio.get_running_loop().time() - started < 6
        restored(runtime, original, address, names, before)
        # The held original HTTP session is not physically closed yet. Its
        # command fence, rather than a fabricated transport state, is decisive.
        assert not runtime.snapshot().connected and original._reconnect_task is None
        assert len(runtime._retirements) == 1
        (retirement,) = runtime._retirements
        assert not retirement.done()
        assert sim.login_count == (1 if original_close else 2)
    finally:
        release.set()
        await asyncio.gather(setup, return_exceptions=True)


@pytest.mark.parametrize("ending", ["recover", "disabled", "supersede", "stop"])
async def test_late_candidate_close_has_one_fenced_owner_and_current_handoff(runtime_sim, monkeypatch, ending):
    runtime, sim, clients, _ = await runtime_sim(auto_reconnect=ending != "disabled")
    original, address, names = clients[0], runtime.address, runtime.service.names
    before = storage(runtime)
    entered, release = asyncio.Event(), asyncio.Event()
    actual_close = aiohttp.ClientSession.close

    async def close(session):
        if len(clients) > 1 and session is clients[1]._session:
            entered.set()
            await release.wait()
        await actual_close(session)

    monkeypatch.setattr(aiohttp.ClientSession, "close", close)
    sim.state.outputs[0].source = 6
    sim.faults.update({"http_status": 503, "comheads": ["login"], "http_fault_count": 1})
    target = MatrixAddress("localhost", sim.https_port, sim.telnet_port, "candidate-user", "candidate-secret")
    setup = asyncio.create_task(runtime.reconfigure(target, persist=True))
    following = command = None
    try:
        await asyncio.wait_for(entered.wait(), 3)
        setup.cancel()
        await ready(lambda: runtime.service.client is original)
        restored(runtime, original, address, names, before)
        assert not setup.done() and original._reconnect_task is None
        command = asyncio.create_task(runtime.commands.power(False))
        await ready(lambda: command in runtime._operations)
        assert not command.done() and sim.state.system["power"] == 1
        # Another cancellation during settling must not restart its deadline.
        asyncio.get_running_loop().call_later(1, setup.cancel)
        with pytest.raises(asyncio.CancelledError):
            await asyncio.wait_for(asyncio.shield(setup), 6)
        assert len(runtime._retirements) == 1 and not original.connected
        (retirement,) = runtime._retirements
        assert not retirement.done() and not command.done()
        command.cancel()
        await asyncio.gather(command, return_exceptions=True)
        assert sim.login_count == 2 and sim.state.system["power"] == 1
        if ending == "supersede":
            following = asyncio.create_task(runtime.reconfigure(address))
            await ready(lambda: following in runtime._operations)
            assert len(clients) == 2 and not following.done()
        elif ending == "stop":
            following = asyncio.create_task(runtime.stop())
            await ready(lambda: runtime._stopping)
        release.set()
        await asyncio.wait_for(asyncio.shield(retirement), 3)
        candidate = clients[1]
        assert candidate._session is None and candidate._telnet is None
        assert candidate._connect_task is None and candidate._reconnect_task is None
        if following:
            result = await asyncio.wait_for(following, 3)
            if ending == "supersede":
                assert result.success and runtime.service.client is clients[2]
                assert not original.connected and original._connect_task is None
                assert original._reconnect_task is None
                await ready(lambda: runtime.snapshot().routing.get(1) == 6)
            else:
                count = sim.login_count
                await runtime.stop()
                assert sim.login_count == count == 2
                assert not runtime._raw_unlisten
                assert all(client._intentional_disconnect for client in clients)
                assert not [task for task in asyncio.all_tasks() if task.get_name() == "matrix_reconnect"]
        elif ending == "disabled":
            await runtime.refresh()
            assert not runtime.snapshot().connected and original._reconnect_task is None
            assert sim.login_count == 2
        else:
            await ready(lambda: runtime.snapshot().connected and runtime.snapshot().routing.get(1) == 6)
            assert sim.login_count == 3
        assert not runtime._retirements
        assert sum(client.connected for client in clients) <= 1
        assert storage(runtime) == before
    finally:
        release.set()
        if command:
            command.cancel()
        await asyncio.gather(*(task for task in (setup, command, following) if task), return_exceptions=True)


async def test_production_deadline_plus_unreleased_close_settles_within_two_phases(runtime_sim, monkeypatch):
    runtime, sim, clients, _ = await runtime_sim()
    original, address, names = clients[0], runtime.address, runtime.service.names
    before = storage(runtime)
    entered, release = asyncio.Event(), asyncio.Event()
    actual_close = aiohttp.ClientSession.close

    async def close(session):
        if len(clients) == 2 and session is clients[1]._session:
            entered.set()
            await release.wait()
        await actual_close(session)

    monkeypatch.setattr(aiohttp.ClientSession, "close", close)
    sim.faults.update({"http_status": 503, "comheads": ["login"], "http_fault_count": 1})
    target = MatrixAddress("localhost", sim.https_port, sim.telnet_port, "candidate-user", "candidate-secret")
    started = asyncio.get_running_loop().time()
    setup = asyncio.create_task(runtime.reconfigure(target, persist=True))
    try:
        await asyncio.wait_for(entered.wait(), 3)
        assert composition.CLEANUP_TIMEOUT == 5.0
        async with asyncio.timeout(7):
            while not setup.cancelling():
                await asyncio.sleep(0.01)
        # Task.cancel increments the count before the interrupted coroutine is
        # rescheduled. Observe its restoration, not that scheduler ordering.
        await ready(lambda: runtime.service.client is original)
        restored(runtime, original, address, names, before)
        assert not setup.done() and original._reconnect_task is None
        result = await asyncio.wait_for(asyncio.shield(setup), 6)
        elapsed = asyncio.get_running_loop().time() - started
        _LOG.info("Unreleased close returned after %.3fs across two production cleanup phases", elapsed)
        assert 10 <= elapsed < 11
        assert not result.success and not result.connected
        assert not setup.cancelled() and setup.cancelling() == 0
        restored(runtime, original, address, names, before)
        assert len(runtime._retirements) == 1
        (retirement,) = runtime._retirements
        assert not retirement.done()
        # Even shutdown gets one bounded public-drain phase, with no revival
        # if the real resource only closes after shutdown has returned.
        stopped = asyncio.get_running_loop().time()
        await asyncio.wait_for(runtime.stop(), 6)
        assert 5 <= asyncio.get_running_loop().time() - stopped < 6
        assert retirement in runtime._retirements and not retirement.done()
        count = sim.login_count
        release.set()
        await asyncio.wait_for(asyncio.shield(retirement), 3)
        assert not runtime._retirements and sim.login_count == count == 2
        assert original._reconnect_task is None and not runtime._raw_unlisten
        assert not [task for task in asyncio.all_tasks() if task.get_name() == "hub_matrix_retirement"]
    finally:
        release.set()
        await asyncio.gather(setup, return_exceptions=True)
