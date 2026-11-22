"""Real socket rollback delivery gates across the production cleanup deadline.

The shared fixture uses actual HTTPS/Telnet and speeds transport backoff. This
module gives HTTP responses a longer budget so the production five-second
cleanup limit always cancels the waiter while its real login remains pending.
The unmodified R8B review separately covers the default HTTP budget. The final
case covers structural clients without cache or reconnect capabilities.
"""

from __future__ import annotations

import asyncio
import logging

import pytest

import hub.runtime.composition as composition
import orei_matrix
from hub import cli
from hub.runtime.config import MatrixAddress
from orei_matrix import ConnectionState
from tests.test_runtime_rollback_reconnect_r1g import (
    assert_no_candidate_owner,
    assert_one_owner,
    assert_recovered,
    outage,
    ready,
)
from tests.test_runtime_rollback_reconnect_r1g import (
    runtime_sim as runtime_sim,
)

_LOG = logging.getLogger(__name__)


@pytest.fixture(autouse=True)
def pending_http_response_budget(monkeypatch):
    # aiohttp rounds five-second HTTP deadlines to whole seconds. At some
    # phases that expires before the test resumes after cleanup. A longer
    # network budget isolates cancellation of a still-pending real socket
    # login; neither the production cleanup deadline nor connect is replaced.
    monkeypatch.setattr(orei_matrix, "HTTP_TIMEOUT", 15.0)
    assert composition.CLEANUP_TIMEOUT == 5.0


def storage(runtime):
    return {
        str(path): path.read_bytes()
        for directory in {runtime.prepared.paths.config_dir, runtime.prepared.paths.data_dir}
        for path in directory.rglob("*")
        if path.is_file()
    }


async def deadline_result(setup, started):
    assert composition.CLEANUP_TIMEOUT == 5.0
    result = await asyncio.wait_for(asyncio.shield(setup), 7)
    elapsed = asyncio.get_running_loop().time() - started
    _LOG.info("Production cleanup deadline returned after %.3fs", elapsed)
    assert 5 <= elapsed < 7
    assert not result.success and not result.connected
    return result


def assert_restored(runtime, clients, address, names, saved_storage):
    assert not runtime._stopping
    assert runtime.service.client is clients[0] and runtime.address == address
    assert runtime.service.names is names
    assert clients[0].credentials() == ("original-user", "original-secret")
    assert runtime.snapshot().input_names[1] == "Saved console"
    assert runtime.snapshot().output_names[1] == "Saved screen"
    assert runtime._refresh_task is not None and not runtime._refresh_task.done()
    assert storage(runtime) == saved_storage
    assert_no_candidate_owner(clients)


async def held_rollback(runtime, sim, address):
    sim.hold_login = 3
    outage(sim)
    started = asyncio.get_running_loop().time()
    setup = asyncio.create_task(runtime.reconfigure(address, persist=True))
    await asyncio.wait_for(sim.received.wait(), 3)
    assert sim.login_count == 3 and not sim.faults.any_http
    assert sum(entry.get("fault") == "http_503" for entry in sim.log) == 2
    _LOG.info("Third real login response held; both HTTP 503 faults consumed")
    return setup, started


@pytest.mark.parametrize("new_address", [False, True])
async def test_production_deadline_hands_pending_rollback_to_one_transport_owner(runtime_sim, new_address):
    runtime, sim, clients, _ = await runtime_sim()
    original, address, names = clients[0], runtime.address, runtime.service.names
    saved_storage = storage(runtime)
    sim.state.outputs[0].source = 6
    candidate = (
        MatrixAddress("localhost", sim.https_port, sim.telnet_port, "candidate-user", "candidate-secret")
        if new_address
        else address
    )
    setup, started = await held_rollback(runtime, sim, candidate)
    attempt = original._connect_task
    await deadline_result(setup, started)
    assert attempt is original._connect_task and not attempt.done()
    assert_restored(runtime, clients, address, names, saved_storage)
    assert_one_owner(runtime, original)
    reconnect = original._reconnect_task
    assert reconnect is not None and not reconnect.done()
    # Refresh remains serialized and never starts another login or supervisor.
    await runtime.refresh()
    assert original._connect_task is attempt and sim.login_count == 3
    assert_one_owner(runtime, original)
    sim.release.set()
    assert not await asyncio.wait_for(asyncio.shield(attempt), 2)
    await assert_recovered(runtime, sim, original)
    await asyncio.wait_for(asyncio.shield(reconnect), 3)
    assert original._reconnect_task is reconnect
    assert_restored(runtime, clients, address, names, saved_storage)
    assert sum(client.connected for client in clients) == 1


async def test_late_successful_rollback_joins_existing_attempt_without_duplicate_login(runtime_sim):
    runtime, sim, clients, _ = await runtime_sim()
    original, address, names = clients[0], runtime.address, runtime.service.names
    saved_storage = storage(runtime)
    sim.hold_login = 3
    # Candidate fails; the held original-client login has already succeeded at
    # the SIM, but the transport cannot know until the real response arrives.
    sim.faults.update({"http_status": 503, "comheads": ["login"], "http_fault_count": 1})
    started = asyncio.get_running_loop().time()
    setup = asyncio.create_task(runtime.reconfigure(address, persist=True))
    await asyncio.wait_for(sim.received.wait(), 3)
    attempt = original._connect_task
    await deadline_result(setup, started)
    assert_one_owner(runtime, original)
    reconnect = original._reconnect_task
    assert reconnect is not None and not reconnect.done()
    sim.release.set()
    assert await asyncio.wait_for(asyncio.shield(attempt), 2)
    await ready(lambda: runtime.snapshot().connected and runtime.snapshot().routing.get(1) is not None)
    await asyncio.wait_for(asyncio.shield(reconnect), 3)
    assert sim.login_count == 3 and not sim.faults.any_http
    assert sum(entry.get("fault") == "http_503" for entry in sim.log) == 1
    assert original._connect_task is attempt and original._reconnect_task is reconnect
    assert_restored(runtime, clients, address, names, saved_storage)


@pytest.mark.parametrize("cancel_candidate", [False, True])
async def test_caller_cancellation_survives_rollback_cleanup_and_recovers(runtime_sim, cancel_candidate):
    runtime, sim, clients, _ = await runtime_sim()
    original, address, names = clients[0], runtime.address, runtime.service.names
    saved_storage = storage(runtime)
    if cancel_candidate:
        sim.hold_login = 2
        outage(sim)
        setup = asyncio.create_task(runtime.reconfigure(address, persist=True))
        await asyncio.wait_for(sim.received.wait(), 3)
        # The candidate response remains gated while disconnect cancels its
        # socket. Gate the next real response independently by login number.
        sim.hold_login = 3
        sim.received.clear()
        started = asyncio.get_running_loop().time()
        setup.cancel()
        await asyncio.wait_for(sim.received.wait(), 3)
    else:
        setup, _ = await held_rollback(runtime, sim, address)
        started = asyncio.get_running_loop().time()
        setup.cancel()
    attempt = original._connect_task
    with pytest.raises(asyncio.CancelledError):
        await asyncio.wait_for(asyncio.shield(setup), 7 if cancel_candidate else 3)
    elapsed = asyncio.get_running_loop().time() - started
    assert 5 <= elapsed < 7 if cancel_candidate else elapsed < 3
    assert setup.cancelled()
    assert attempt is original._connect_task and not attempt.done()
    assert_restored(runtime, clients, address, names, saved_storage)
    assert_one_owner(runtime, original)
    assert original._reconnect_task is not None
    sim.release.set()
    assert not await asyncio.wait_for(asyncio.shield(attempt), 2)
    await assert_recovered(runtime, sim, original)
    assert_restored(runtime, clients, address, names, saved_storage)


async def test_deadline_respects_disabled_auto_reconnect(runtime_sim):
    runtime, sim, clients, _ = await runtime_sim(auto_reconnect=False)
    original, address, names = clients[0], runtime.address, runtime.service.names
    saved_storage = storage(runtime)
    setup, started = await held_rollback(runtime, sim, address)
    attempt = original._connect_task
    await deadline_result(setup, started)
    assert original.auto_reconnect is False and original._reconnect_task is None
    sim.release.set()
    assert not await asyncio.wait_for(asyncio.shield(attempt), 2)
    await runtime.refresh()
    assert not runtime.snapshot().connected and sim.login_count == 3
    assert original._reconnect_task is None
    assert_restored(runtime, clients, address, names, saved_storage)


@pytest.mark.parametrize("backoff", [False, True])
async def test_stop_after_deadline_drains_pending_login_or_transport_backoff(runtime_sim, backoff):
    runtime, sim, clients, _ = await runtime_sim()
    original, address = clients[0], runtime.address
    saved_storage = storage(runtime)
    setup, started = await held_rollback(runtime, sim, address)
    attempt = original._connect_task
    await deadline_result(setup, started)
    assert original._reconnect_task is not None
    if backoff:
        # Additional actual failures keep the sole supervisor in backoff.
        sim.faults.update({"http_status": 503, "comheads": ["login"], "http_fault_count": 100})
        sim.release.set()
        assert not await asyncio.wait_for(asyncio.shield(attempt), 2)
        await ready(
            lambda: sim.login_count >= 4
            and original._connect_task.done()
            and original.connection_state is ConnectionState.BACKOFF
        )
    assert_one_owner(runtime, original)
    await asyncio.wait_for(runtime.stop(), 3)
    count = sim.login_count
    sim.clear_faults()
    sim.release.set()
    # A completed disconnect fences all transport work before response release.
    await runtime.stop()
    assert sim.login_count == count
    assert storage(runtime) == saved_storage and runtime.address == address
    assert_no_candidate_owner(clients)
    for client in clients:
        assert not client.connected and client._intentional_disconnect
        assert client._session is None and client._telnet is None
        assert client._connect_task is None and client._reconnect_task is None
    assert not [task for task in asyncio.all_tasks() if task.get_name() in {"matrix_reconnect", "hub_runtime_refresh"}]
    with pytest.raises(RuntimeError, match="stopping"):
        await runtime.connect()


async def test_next_reconfigure_retires_deadline_supervisor_and_pending_attempt(runtime_sim):
    runtime, sim, clients, _ = await runtime_sim()
    original = clients[0]
    setup, started = await held_rollback(runtime, sim, runtime.address)
    attempt = original._connect_task
    await deadline_result(setup, started)
    reconnect = original._reconnect_task
    assert reconnect is not None and not reconnect.done()
    # A new successful login is ungated even while response three is held.
    assert (await asyncio.wait_for(runtime.reconfigure(runtime.address), 3)).success
    assert reconnect.done() and attempt.done()
    assert original._session is None and original._telnet is None
    assert original._connect_task is None and original._reconnect_task is None
    assert runtime.service.client is clients[-1] and clients[-1].connected
    assert sum(client.connected for client in clients) == 1
    assert not [task for task in asyncio.all_tasks() if task.get_name() == "matrix_reconnect"]
    sim.release.set()


async def test_deadline_with_structural_cacheless_client_without_optional_reconnect(tmp_path, monkeypatch):
    from tests.test_runtime_composition_r1 import MatrixFactory

    monkeypatch.setattr("rest_api.utils._runtime", None)
    env = {
        "DATA_DIR": str(tmp_path / "data"),
        "UC_CONFIG_HOME": str(tmp_path / "config"),
        "MATRIX_HOST": "refused",
        "UC_ENABLED": "false",
        "FLIC_ENABLED": "false",
    }
    factory = MatrixFactory()
    runtime = composition.build_runtime(cli.load_settings(env), environ=env, matrix_factory=factory)
    original, address, names = factory.instances[0], runtime.address, runtime.service.names
    original.connect_gate = asyncio.Event()
    assert not hasattr(original, "start_auto_reconnect")
    assert not hasattr(original, "clear_cec_cache") and not hasattr(original, "invalidate_preset_cache")
    saved_storage = storage(runtime)
    try:
        started = asyncio.get_running_loop().time()
        setup = asyncio.create_task(runtime.reconfigure(address, persist=True))
        await asyncio.wait_for(original.connect_entered.wait(), 3)
        await deadline_result(setup, started)
        assert runtime.service.client is original and runtime.address == address
        assert runtime.service.names is names and storage(runtime) == saved_storage
        assert not original.connected and all(not client.connected for client in factory.instances)
        assert not runtime.reconfiguring
    finally:
        await runtime.stop()
