"""Cancellation propagates after serialized preset restoration and scene waits."""

import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from rest_api.control import handle_preset_save
from tests import test_runtime_action_parity_r4 as shared
from tests.test_runtime_action_parity_r4 import commands, profile

action_runtime = shared.action_runtime


@pytest.mark.parametrize("repeat_cancel", [False, True])
async def test_cancelled_save_restores_before_other_commands(action_runtime, monkeypatch, repeat_cancel):
    runtime, client, sim = action_runtime
    original = [o.source for o in sim.state.outputs]
    save_entered = asyncio.Event()
    restore_entered = asyncio.Event()
    restore_release = asyncio.Event()
    matrix = runtime.service.client
    real_save, real_switch = matrix.save_preset, matrix.switch_input

    async def blocked_save(slot):
        assert await real_save(slot)
        save_entered.set()
        await asyncio.Event().wait()

    async def blocked_restore(source, output):
        if repeat_cancel and output == 1 and source == original[0]:
            restore_entered.set()
            await restore_release.wait()
        return await real_switch(source, output)

    monkeypatch.setattr(matrix, "save_preset", blocked_save)
    monkeypatch.setattr(matrix, "switch_input", blocked_restore)
    request = SimpleNamespace(match_info={"preset": "6"}, can_read_body=True,
                              json=AsyncMock(return_value={"routing": {"1": 8, "2": 7}}))
    sim.log.clear()
    task = asyncio.create_task(handle_preset_save(request))
    await asyncio.wait_for(save_entered.wait(), 2)
    contender = asyncio.create_task(runtime.local.switch(6, 3))
    await asyncio.sleep(0.01)
    assert not contender.done()
    task.cancel()
    if repeat_cancel:
        await asyncio.wait_for(restore_entered.wait(), 2)
        task.cancel()
        await asyncio.sleep(0)
        restore_release.set()
    with pytest.raises(asyncio.CancelledError):
        await asyncio.wait_for(task, 2)
    assert await asyncio.wait_for(contender, 2)
    assert [o.source for o in sim.state.outputs[:2]] == original[:2]
    assert sim.state.presets[5].routing[:2] == [8, 7]
    seq = [item[0] for item in commands(sim)]
    assert seq == ["video switch", "video switch", "preset save",
                   "video switch", "video switch", "video switch"]
    assert runtime._operations == set()


async def test_cancelled_scene_wait_does_not_retry_completed_steps(action_runtime):
    runtime, client, sim = action_runtime
    await profile(client)
    response = await client.post("/api/v2/scenes", json={"name": "Wait",
        "steps": [{"type": "profile", "id": "movie"},
                  {"type": "wait", "id": "pause", "params": {"seconds": 20}}]})
    assert response.status == 201, await response.text()
    scene_id = (await response.json())["data"]["scene"]["id"]
    sim.log.clear()
    task = asyncio.create_task(runtime.local.run_action("scene", scene_id))
    async with asyncio.timeout(2):
        while len(commands(sim)) < 7:
            await asyncio.sleep(0.001)
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task
    assert [o.source for o in sim.state.outputs[:2]] == [4, 5]
    assert len(commands(sim)) == 7
    assert not runtime.managers.scenes.get_scene(scene_id).execution_history
    assert await runtime.local.switch(2, 1)


async def test_cancelled_cycle_clears_observation_before_later_success(action_runtime, monkeypatch):
    from hub.runtime.actions import _cycle_observation
    from rest_api.control import _cycle_input

    runtime, _, sim = action_runtime
    assert await runtime.local.switch(3, 1)
    matrix = runtime.service.client
    real = matrix.switch_input
    entered = asyncio.Event()

    async def blocked(source, output):
        entered.set()
        await asyncio.Event().wait()

    monkeypatch.setattr(matrix, "switch_input", blocked)

    async def cancelled_request():
        _cycle_observation.set((7, 8))
        try:
            await _cycle_input("next", 1, cycle=False)
        except asyncio.CancelledError:
            assert _cycle_observation.get() is None
            raise

    task = asyncio.create_task(cancelled_request())
    await asyncio.wait_for(entered.wait(), 1)
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task
    monkeypatch.setattr(matrix, "switch_input", real)
    assert await _cycle_input("previous", 1, cycle=False) == (3, 2, True)
    assert _cycle_observation.get() is None
    assert sim.state.outputs[0].source == 2
