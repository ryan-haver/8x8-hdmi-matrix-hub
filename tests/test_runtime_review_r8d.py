"""Independent public-disconnect fencing with an existing real reconnect owner."""

from __future__ import annotations

import asyncio
import json

import aiohttp
import pytest

from orei_matrix import Events
from tests.test_runtime_rollback_deadline_r1h import storage
from tests.test_runtime_rollback_reconnect_r1g import ready
from tests.test_runtime_rollback_reconnect_r1g import runtime_sim as runtime_sim
from tests.test_runtime_rollback_restoration_r1i import restored


async def test_real_disconnect_body_exception_fences_existing_reconnect(runtime_sim, tmp_path):
    """A synchronous public event listener raises inside real Orei disposal.

    Two actual HTTP login failures leave the second real response gated by the
    Simulator. The runtime's initial attempt has already handed off to the sole
    transport supervisor. The actual public disconnect body, its synchronous
    intentional-close fence and its real transport drain all execute unchanged.
    Composition must still retain the resulting public error conservatively.
    """
    runtime, sim, clients, _ = await runtime_sim(initial_faults=2)
    original, address, names = clients[0], runtime.address, runtime.service.names
    before = storage(runtime)
    sim.hold_login = 2
    await asyncio.wait_for(sim.received.wait(), 3)
    supervisor = original._reconnect_task
    assert supervisor is not None and not supervisor.done()
    assert sim.login_count == 2 and not sim.faults.any_http
    error = OSError("controlled disconnected event listener failure")
    fired = False

    def fail_once():
        nonlocal fired
        if not fired:
            fired = True
            raise error

    original.events.on(Events.DISCONNECTED, fail_once)
    listeners = {event: len(original.events.listeners(event)) for event in Events}
    try:
        started = asyncio.get_running_loop().time()
        result = await asyncio.wait_for(runtime.reconfigure(address, persist=True), 3)
        elapsed = asyncio.get_running_loop().time() - started
        assert not result.success and not result.connected
        assert fired and supervisor.done()
        restored(runtime, original, address, names, before)
        assert len(clients) == 1
        assert {event: len(original.events.listeners(event)) for event in Events} == listeners
        (retirement,) = runtime._retirements
        assert retirement.exception() is error and runtime._retirements[retirement] is original
        with pytest.raises(RuntimeError, match="Previous matrix cleanup"):
            await runtime.commands.power(False)
        assert sim.state.system["power"] == 1
        count_at_fence = sim.login_count
        sim.release.set()
        # This observation exceeds several real 20-40ms retry periods. Release
        # only delivers a failed response; it does not invoke a manual connect.
        await asyncio.sleep(0.5)
        evidence = {
            "injection": "DISCONNECTED listener inside actual disconnect body",
            "elapsed": elapsed,
            "login_count_at_fence": count_at_fence,
            "login_count_after_release": sim.login_count,
            "original_transport_connected": original.connected,
            "runtime_connected": runtime.snapshot().connected,
            "original_identity": runtime.service.client is original,
            "storage_unchanged": storage(runtime) == before,
            "error_retained": retirement in runtime._retirements and retirement.exception() is error,
            "logins": [entry for entry in sim.log if entry["channel"] == "http" and entry["command"] == "login"],
        }
        (tmp_path / "observation.json").write_text(json.dumps(evidence, indent=2), encoding="utf-8")
        assert sim.login_count == count_at_fence, evidence
        assert not original.connected
    finally:
        sim.release.set()
        await asyncio.wait_for(runtime.stop(), 3)
        assert not runtime._retirements and not runtime._raw_unlisten
        assert original._session is None and original._telnet is None
        assert original._connect_task is None and original._reconnect_task is None
        assert storage(runtime) == before
        original.events.remove_listener(Events.DISCONNECTED, fail_once)


async def test_late_successful_original_close_hands_off_and_restores_public_commands(
    runtime_sim, monkeypatch, tmp_path
):
    """A still-owned actual original close succeeds after bounded cancellation."""
    runtime, sim, clients, _ = await runtime_sim()
    original, address, names = clients[0], runtime.address, runtime.service.names
    before = storage(runtime)
    listeners = {event: len(original.events.listeners(event)) for event in Events}
    entered, release = asyncio.Event(), asyncio.Event()
    original_session = original._session
    actual_close = aiohttp.ClientSession.close

    async def close(session):
        if session is original_session:
            entered.set()
            await release.wait()
        await actual_close(session)

    monkeypatch.setattr(aiohttp.ClientSession, "close", close)
    sim.state.outputs[0].source = 6
    setup = asyncio.create_task(runtime.reconfigure(address, persist=True))
    try:
        await asyncio.wait_for(entered.wait(), 3)
        started = asyncio.get_running_loop().time()
        setup.cancel()
        with pytest.raises(asyncio.CancelledError):
            await asyncio.wait_for(asyncio.shield(setup), 6)
        elapsed = asyncio.get_running_loop().time() - started
        assert 5 <= elapsed < 6
        restored(runtime, original, address, names, before)
        assert len(clients) == sim.login_count == 1
        (retirement,) = runtime._retirements
        assert not retirement.done() and runtime._retirements[retirement] is original
        assert original._reconnect_task is None and not runtime.snapshot().connected
        release.set()
        await ready(lambda: runtime.snapshot().connected and runtime.snapshot().routing.get(1) == 6)
        assert not runtime._retirements and sim.login_count == 2
        assert {event: len(original.events.listeners(event)) for event in Events} == listeners
        assert await runtime.commands.switch(7, 1)
        assert sim.state.outputs[0].source == 7
        assert storage(runtime) == before and runtime.service.client is original
        (tmp_path / "observation.json").write_text(
            json.dumps({"cancel_elapsed": elapsed, "logins": sim.login_count, "routing": runtime.snapshot().routing}),
            encoding="utf-8",
        )
    finally:
        release.set()
        await asyncio.gather(setup, return_exceptions=True)
