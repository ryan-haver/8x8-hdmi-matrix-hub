"""Unexpected action failures stay private across actual runtime projections."""

import asyncio
import inspect
import json
import logging
import re
from unittest.mock import AsyncMock

import pytest

from hub.core.matrix_service import MatrixService
from hub.domain.action_runner import ActionRunner
from hub.runtime.actions import run_action_envelope
from tests.test_hub_core_matrix_service import FakeMatrix
from tests.test_runtime_preset_errors_r4b import preset_runtime as preset_runtime

SECRET = r"private-password=canary-r4c at C:\private\matrix.cfg host 10.9.8.7"
REF = re.compile(r"Internal server error \(ref: ([0-9a-f]{8})\)")


def assert_private(value, caplog):
    """Every public ref has the original exception and traceback in private logs."""
    text = value if isinstance(value, str) else repr(value)
    assert SECRET not in text
    for fragment in ("canary-r4c", "private-password", "matrix.cfg", "10.9.8.7", "RuntimeError"):
        assert fragment not in text
    refs = set(REF.findall(text))
    assert refs, text
    for ref in refs:
        records = [record for record in caplog.records if f"[{ref}]" in record.getMessage()]
        assert len(records) == 1
        assert SECRET in records[0].getMessage()
        assert records[0].exc_info[0] is RuntimeError
        assert records[0].exc_info[2] is not None
    return refs


class OwnedPresetClient(FakeMatrix):
    """Class method cannot be replaced; track each owned call and cleanup."""

    def __init__(self):
        super().__init__()
        self.__dict__ = GuardedMethods(vars(self))
        self.mode = "success"
        self.started = asyncio.Event()
        self.finished = 0
        self.recalls = 0

    def __setattr__(self, name, value):
        if name == "recall_preset":
            raise AssertionError("A caller attempted to replace the owned method")
        super().__setattr__(name, value)

    async def recall_preset(self, preset):
        assert inspect.getattr_static(self, "recall_preset") is OwnedPresetClient.recall_preset
        assert "recall_preset" not in vars(self)
        self.recalls += 1
        self.started.set()
        try:
            if self.mode == "error":
                self.connected = False
                raise RuntimeError(SECRET)
            if self.mode == "cancel":
                await asyncio.Event().wait()
            if self.mode == "false":
                return False
            self.connected = True
            return await super().recall_preset(preset)
        finally:
            self.finished += 1
            if self.mode == "cancel":
                self.connected = False


class GuardedMethods(dict):
    """Detect even temporary __dict__ interception before a coroutine starts."""

    def __setitem__(self, key, value):
        assert key != "recall_preset", "Client method interception violates ownership"
        super().__setitem__(key, value)


async def test_runner_strict_service_never_intercepts_owned_method(caplog):
    client = OwnedPresetClient()
    service = MatrixService(client)
    client.mode = "error"
    with caplog.at_level(logging.ERROR):
        result = await ActionRunner(preset_executor=service).run("preset", "1")
    assert result.code == "execution_error"
    assert (result.steps_completed, result.total_steps) == (0, 1)
    assert client.finished == client.recalls == 1
    assert service.client is client
    assert "recall_preset" not in vars(client)
    assert_private(result.to_response_dict(), caplog)
    assert SECRET not in repr(service.snapshot())


@pytest.mark.parametrize("mode", ["false", "error", "cancel"])
async def test_strict_service_keeps_owner_generation_connection_and_next_success(mode):
    client = OwnedPresetClient()
    service = MatrixService(client)
    assert await service.connect()
    events = []
    unsubscribe = service.bus.subscribe(events.append)
    generation = service._write_generation
    client.mode = mode
    try:
        if mode == "error":
            with pytest.raises(RuntimeError, match="canary-r4c"):
                await service.recall_preset(1, propagate_errors=True)
        elif mode == "cancel":
            task = asyncio.create_task(service.recall_preset(1, propagate_errors=True))
            await asyncio.wait_for(client.started.wait(), 1)
            task.cancel()
            with pytest.raises(asyncio.CancelledError):
                await task
        else:
            assert await service.recall_preset(1, propagate_errors=True) is False
        await service.bus.drain(timeout=1)
        assert service.client is client
        assert client.finished == client.recalls == 1
        assert service._write_generation == generation
        assert service.connected is client.connected
        assert not [event for event in events if event.topic == "presets"]
        assert SECRET not in repr(service.snapshot())
        assert inspect.getattr_static(client, "recall_preset") is OwnedPresetClient.recall_preset
        assert "recall_preset" not in vars(client)

        client.mode = "success"
        client.presets[1] = [3] * client.size
        assert await service.recall_preset(1, propagate_errors=True) is True
        await service.bus.drain(timeout=1)
        assert client.finished == client.recalls == 2
        assert service._write_generation == generation + 1
        assert service.routing == dict.fromkeys(range(1, client.size + 1), 3)
        assert service.connected is True
        assert service.last_error is None
        assert len([event for event in events if event.topic == "presets"]) == 1
    finally:
        unsubscribe()
        await service.disconnect()


async def test_service_default_still_returns_false_on_client_exception():
    client = OwnedPresetClient()
    service = MatrixService(client)
    client.mode = "error"
    assert await service.recall_preset(1) is False
    assert service._write_generation == 0
    assert client.finished == 1


async def test_runtime_preset_cancellation_releases_transaction_and_keeps_client_method(
    preset_runtime, monkeypatch
):
    runtime, _, _ = preset_runtime
    client = runtime.service.client
    real_recall = client.recall_preset
    started = asyncio.Event()
    cleaned = asyncio.Event()

    async def blocked_recall(number):
        assert client.recall_preset is blocked_recall
        started.set()
        try:
            await asyncio.Event().wait()
        finally:
            cleaned.set()

    monkeypatch.setattr(client, "recall_preset", blocked_recall)
    generation = runtime.service._write_generation
    task = asyncio.create_task(runtime.run_action("preset", "1"))
    await asyncio.wait_for(started.wait(), 1)
    assert task in runtime._operations
    assert runtime.transaction._owner is task
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task
    assert cleaned.is_set()
    assert runtime.service.client is client
    assert client.recall_preset is blocked_recall
    assert runtime.service._write_generation == generation
    assert task not in runtime._operations
    assert runtime.transaction._owner is None
    monkeypatch.setattr(client, "recall_preset", real_recall)
    result = await asyncio.wait_for(runtime.run_action("preset", "1"), 3)
    assert result.success and (result.steps_completed, result.total_steps) == (1, 1)
    assert runtime.service._write_generation == generation + 1


@pytest.mark.parametrize("delegated", [False, True])
async def test_runtime_nonpreset_unhandled_exception_is_safe_on_rest_and_envelope(
    preset_runtime, monkeypatch, caplog, delegated
):
    runtime, client, _ = preset_runtime
    response = await client.post("/api/profile", json={
        "id": "movie", "name": "Movie", "outputs": {"1": {"input": 4}}
    })
    assert response.status == 200
    if delegated:
        def broken_executor(*args, **kwargs):
            raise RuntimeError(SECRET)

        runtime.action_runner.register("profile", broken_executor)
    else:
        # The REST handler's existing preflight lookup succeeds. Inject an
        # unexpected error at the runner's own authorization boundary.
        async def broken_authorization(*args):
            raise RuntimeError(SECRET)

        monkeypatch.setattr("hub.domain.action_runner._passcode_refusal", broken_authorization)
        profile = runtime.managers.profiles.get_profile("movie")
        monkeypatch.setattr(profile, "is_password_protected", lambda: True)
    with caplog.at_level(logging.ERROR):
        response = await client.post("/api/profile/movie/recall")
        assert response.status == 500
        assert_private(await response.text(), caplog)
        result = await runtime.run_action("profile", "movie")
        assert result.code == "execution_error"
        assert (result.success, result.partial, result.status_code) == (False, False, 500)
        assert (result.steps_completed, result.total_steps) == (0, 0)
        assert result.error == f"Internal server error (ref: {result.data['error_id']})"
        assert_private(result.to_response_dict(), caplog)
        envelope = await run_action_envelope(runtime, "profile", "movie")
        assert envelope["status"] == envelope["data"]["status_code"] == 500
        assert envelope["data"]["result"]["code"] == "execution_error"
        assert envelope["data"]["steps_completed"] == envelope["data"]["total_steps"] == 0
        assert_private(envelope, caplog)
        assert_private(await runtime.local.run_action("profile", "movie"), caplog)
    assert not runtime._operations
    assert runtime.transaction._owner is None


async def test_profile_power_macro_exception_retains_partial_output_execution(
    preset_runtime, monkeypatch, caplog
):
    runtime, client, sim = preset_runtime
    response = await client.post("/api/profile", json={
        "id": "movie", "name": "Movie", "outputs": {"1": {"input": 4}}, "power_on_macro": "wake"
    })
    assert response.status == 200
    monkeypatch.setattr(runtime.managers.macros, "get_macro", lambda _: object())
    execute = AsyncMock(side_effect=RuntimeError(SECRET))
    monkeypatch.setattr(runtime.managers.macros, "execute_macro", execute)
    with caplog.at_level(logging.ERROR):
        result = await runtime.run_action("profile", "movie")
    assert (result.success, result.partial, result.status_code) == (False, True, 207)
    assert (result.steps_completed, result.total_steps) == (1, 2)
    assert result.data["failed_outputs"] == []
    assert sim.state.outputs[0].source == 4
    execute.assert_awaited_once_with("wake")
    assert_private(result.to_response_dict(), caplog)


async def test_registered_rest_profile_preflight_lookup_exception_is_private(preset_runtime, monkeypatch, caplog):
    runtime, client, _ = preset_runtime

    def broken_lookup(*args):
        raise RuntimeError(SECRET)

    monkeypatch.setattr(runtime.managers.profiles, "get_profile", broken_lookup)
    with caplog.at_level(logging.ERROR):
        response = await client.post("/api/profile/movie/recall")
    assert response.status == 500
    payload = await response.json()
    assert payload["success"] is False and payload["data"] is None
    assert REF.fullmatch(payload["error"])
    assert_private(payload, caplog)
    assert not runtime._operations


@pytest.mark.parametrize("kind", ["macro", "scene"])
async def test_real_macro_step_exception_is_safe_in_runner_rest_and_scene_history(
    preset_runtime, monkeypatch, caplog, kind
):
    runtime, client, _ = preset_runtime
    manager = runtime.managers.macros
    manager.create_macro("Private failure", [
        {"command": "POWER_ON", "targets": ["output_1"]},
        {"command": "POWER_ON", "targets": ["output_2"]},
    ], macro_id="private")
    sender = AsyncMock(side_effect=[True, RuntimeError(SECRET)])
    monkeypatch.setattr(manager, "_cec_sender", sender)
    if kind == "scene":
        response = await client.post("/api/v2/scenes", json={
            "name": "Private scene", "steps": [{"type": "macro", "id": "private"}]
        })
        assert response.status == 201
        action_id = (await response.json())["data"]["scene"]["id"]
        route = f"/api/v2/scenes/{action_id}/execute"
    else:
        action_id, route = "private", "/api/cec/macro/private/execute"
    with caplog.at_level(logging.ERROR):
        result = await runtime.run_action(kind, action_id)
        assert result.success is False
        assert (result.status_code, result.steps_completed, result.total_steps) == (
            (207, 1, 2) if kind == "macro" else (500, 0, 1)
        )
        assert_private(result.to_response_dict(), caplog)
        sender.side_effect = [True, RuntimeError(SECRET)]
        response = await client.post(route)
        assert response.status == 500
        if kind == "scene":
            assert_private(await response.text(), caplog)
        else:
            # The historical macro route omits step details on failure.
            assert await response.json() == {"success": False, "data": None, "error": "Execution failed"}
    assert sender.await_count == 4
    if kind == "scene":
        scene = runtime.managers.scenes.get_scene(action_id)
        assert len(scene.execution_history) == 2
        assert_private(scene.to_dict(), caplog)
        disk = json.loads((runtime.prepared.paths.data_dir / "scenes_v2.json").read_text())
        assert_private(disk, caplog)


async def test_legacy_preset_executor_keeps_old_signature():
    class Legacy:
        async def recall_preset(self, number):
            assert number == 2
            return True

    result = await ActionRunner(preset_executor=Legacy()).run("preset", "2")
    assert result.success and (result.steps_completed, result.total_steps) == (1, 1)


@pytest.mark.parametrize("kind", ["shortcut", "scene"])
async def test_shortcut_exception_is_safe_through_runtime_rest_and_scene(
    preset_runtime, monkeypatch, caplog, kind
):
    runtime, client, _ = preset_runtime
    sender = AsyncMock(side_effect=RuntimeError(SECRET))
    monkeypatch.setattr(runtime.service.client, "set_beep", sender)
    if kind == "scene":
        response = await client.post("/api/v2/scenes", json={
            "name": "Private shortcut", "steps": [{"type": "system_action", "id": "beep_on"}]
        })
        assert response.status == 201
        action_id = (await response.json())["data"]["scene"]["id"]
        route = f"/api/v2/scenes/{action_id}/execute"
    else:
        action_id, route = "beep_on", "/api/shortcuts/beep_on/execute"
    with caplog.at_level(logging.ERROR):
        result = await runtime.run_action(kind, action_id)
        assert (result.success, result.partial, result.status_code) == (False, False, 500)
        assert (result.steps_completed, result.total_steps) == (0, 1)
        assert_private(result.to_response_dict(), caplog)
        response = await client.post(route)
        assert response.status == 500
        assert_private(await response.text(), caplog)
        assert_private(await run_action_envelope(runtime, kind, action_id), caplog)
    assert sender.await_count == 3


async def test_macro_validation_and_false_refusal_keep_expected_messages(preset_runtime, monkeypatch):
    runtime, _, _ = preset_runtime
    manager = runtime.managers.macros
    manager.create_macro("Validation", [{"command": "POWER_ON", "targets": ["bad_target"]}], macro_id="invalid")
    result = await runtime.run_action("macro", "invalid")
    assert result.status_code == 500 and result.total_steps == 1 and result.steps_completed == 0
    assert result.step_results[0].error == "Error sending to bad_target: Invalid target type: bad"
    sender = AsyncMock(return_value=False)
    monkeypatch.setattr(manager, "_cec_sender", sender)
    manager.update_macro("invalid", steps=[{"command": "POWER_ON", "targets": ["output_1"]}])
    result = await runtime.run_action("macro", "invalid")
    assert result.status_code == 500 and result.total_steps == 1 and result.steps_completed == 0
    assert result.step_results[0].error == "Failed to send POWER_ON to output_1"
