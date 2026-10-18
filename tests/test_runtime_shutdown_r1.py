"""Rollback and shutdown of partial startup, commands and address changes."""

import asyncio
import socket

import pytest

from hub.core.event_bus import EventBus
from hub.runtime.config import MatrixAddress
from tests import test_runtime_composition_r1 as shared

runtime_builder = shared.runtime_builder


async def test_bind_failure_rolls_back_runner_and_never_connects(runtime_builder):
    runtime, factory = runtime_builder()
    with socket.socket() as bound:
        bound.bind(("0.0.0.0", runtime.settings.api_port))
        bound.listen()
        with pytest.raises(OSError):
            await runtime.start()
    assert factory.instances[0].calls == ["disconnect"]
    assert runtime.server.runner is None
    await runtime.stop()


async def test_stop_cancels_slow_initial_connect_and_is_idempotent(runtime_builder):
    runtime, factory = runtime_builder()
    matrix = factory.instances[0]
    matrix.connect_gate = asyncio.Event()
    await runtime.start()
    await matrix.connect_entered.wait()
    await asyncio.wait_for(asyncio.gather(runtime.stop(), runtime.stop()), 2)
    assert not matrix.connected
    assert runtime._connect_task.done() and runtime._refresh_task.done()
    with pytest.raises(RuntimeError, match="stopping"):
        await runtime.commands.power(True)


async def test_cancelled_reconfigure_closes_candidate_and_restores_old(runtime_builder):
    runtime, factory = runtime_builder()
    await runtime.connect()
    original = runtime.matrix_factory

    def blocked(*args, **kwargs):
        candidate = original(*args, **kwargs)
        candidate.connect_gate = asyncio.Event()
        return candidate

    runtime.matrix_factory = blocked
    setup = asyncio.create_task(
        runtime.reconfigure(MatrixAddress("candidate", password="candidate-secret"), persist=True)
    )
    while len(factory.instances) < 2:
        await asyncio.sleep(0)
    await factory.instances[-1].connect_entered.wait()
    setup.cancel()
    with pytest.raises(asyncio.CancelledError):
        await setup
    assert runtime.address.host == "simulator"
    assert factory.instances[0].connected
    assert not factory.instances[1].connected
    assert factory.maximum == 1
    await runtime.stop()


async def test_integration_partial_start_failure_still_closes_rest(runtime_builder):
    runtime, factory = runtime_builder()

    class Loader:
        integrations = {}

        def load(self):
            return {}

        def routes(self):
            return []

        def health_summary(self):
            return {}

        async def start(self, client):
            raise RuntimeError("bridge failed")

        async def stop(self):
            self.stopped = True

    runtime.loader = Loader()
    with pytest.raises(RuntimeError, match="bridge failed"):
        await runtime.start()
    assert runtime.loader.stopped
    assert not runtime.server.running
    assert "connect" not in factory.instances[0].calls


async def test_bus_drain_cancels_blocked_delivery_at_deadline():
    bus = EventBus()
    finished = asyncio.Event()

    async def blocked(event):
        try:
            await asyncio.Event().wait()
        finally:
            finished.set()

    bus.subscribe(blocked)
    bus.publish("blocked", {})
    await bus.drain(timeout=0.02)
    assert finished.is_set()


async def test_stop_continues_after_integration_cleanup_failure(runtime_builder):
    runtime, factory = runtime_builder()
    await runtime.start()
    await runtime._connect_task

    async def broken():
        raise RuntimeError("cleanup failed")

    runtime.loader.stop = broken
    await runtime.stop()
    assert not runtime.server.running
    assert not factory.instances[0].connected
    assert runtime.local._closed


async def test_shutdown_closes_open_websocket_without_runner_grace_period(runtime_builder):
    import aiohttp

    runtime, _ = runtime_builder()
    await runtime.start()
    await runtime._connect_task
    async with aiohttp.ClientSession() as session:
        ws = await session.ws_connect(f"http://127.0.0.1:{runtime.settings.api_port}/ws")
        await ws.receive_json()
        await asyncio.wait_for(runtime.stop(), 2)
        while not ws.closed:
            message = await ws.receive(timeout=1)
            if message.type in {aiohttp.WSMsgType.CLOSE, aiohttp.WSMsgType.CLOSED}:
                break
        await ws.close()


async def test_cancelled_integration_start_cleans_rest_and_all_owned_tasks(runtime_builder):
    runtime, _ = runtime_builder()
    entered = asyncio.Event()

    class Loader:
        integrations = {}

        def load(self):
            return {}

        def routes(self):
            return []

        def health_summary(self):
            return {}

        async def start(self, client):
            entered.set()
            await asyncio.Event().wait()

        async def stop(self):
            self.stopped = True

    runtime.loader = Loader()
    start = asyncio.create_task(runtime.start())
    await entered.wait()
    start.cancel()
    with pytest.raises(asyncio.CancelledError):
        await start
    assert runtime.loader.stopped
    assert runtime.server.runner is None
    assert runtime._refresh_task is None


async def test_old_disconnect_failure_never_opens_candidate(runtime_builder):
    runtime, factory = runtime_builder()
    await runtime.connect()

    async def fail():
        raise OSError("close failed")

    original = factory.instances[0].disconnect
    factory.instances[0].disconnect = fail
    result = await runtime.reconfigure(MatrixAddress("new", password="candidate-secret"))
    assert not result.success
    assert len(factory.instances) == 1
    factory.instances[0].disconnect = original
    await runtime.stop()


async def test_shutdown_allows_inflight_action_restoration_but_rejects_new_mutations(runtime_builder):
    runtime, factory = runtime_builder()
    await runtime.connect()
    entered = asyncio.Event()

    async def action(*args, **kwargs):
        try:
            await runtime.matrix.switch_input(7, 1)
            entered.set()
            await asyncio.Event().wait()
        finally:
            await runtime.matrix.switch_input(1, 1)

    runtime.action_runner.register("preset", action)
    task = asyncio.create_task(runtime.run_action("preset", "1"))
    await entered.wait()
    await runtime.stop()
    with pytest.raises(asyncio.CancelledError):
        await task
    assert factory.instances[0].routes[0] == 1
    assert factory.instances[0].calls.count(("switch", 1, 1)) == 1
    with pytest.raises(RuntimeError, match="stopping"):
        await runtime.commands.switch(5, 1)
