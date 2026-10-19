"""WP-C3: the domain layer — ActionRunner (API-19) and VisibilityStore (DI-5, API-20).

Three subjects, one work package:

- :class:`ActionRunner` runs every kind of action (profile, scene, macro,
  shortcut, preset) and answers with the same ``ActionRunResult``: 200 for a
  full run, 207 for a partial one, 403 for a refused passcode, 404 for an
  unknown action.
- :class:`VisibilityStore` reads and writes the favorite / dashboard flags of
  all five kinds of item through one interface.
- API-22: a profile's per-output ``scaler`` and ``arc`` survive create, edit,
  disk, and every read that returns a profile — under either spelling of the
  scaler field.
"""

import json
import os
from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock, patch

import pytest

from cec_macros import MacroManager
from config import ProfileManager, SceneOutput
from hub.domain import ACTION_KINDS, VISIBILITY_KINDS, ActionRunner, ActionRunResult, StepResult, VisibilityStore
from password import hash_passcode, reset_pin_lockout
from rest_api import create_rest_app, set_matrix_device
from scene_manager import SceneManager, SceneStep
from system_shortcuts import SystemShortcutManager

PIN = "1234"
WRONG_PIN = "9999"

# The passcode refusal codes the REST layer publishes (SEC-04 / SEC-05 / SEC-06).
REQUIRED = "passcode_required"
INVALID = "invalid_passcode"
LOCKED = "passcode_locked"


# =============================================================================
# Fixtures
# =============================================================================


class FakeMatrix:
    """
    The matrix ActionRunner writes to.

    Every call is recorded so a test can assert what was asked of the device;
    the writes named in ``refuse`` answer False (the matrix refused them), and
    ``script`` answers a named write one value at a time.
    """

    def __init__(self, refuse: set[str] | None = None, script: dict[str, list[bool]] | None = None) -> None:
        self.refuse = refuse or set()
        self.script = script or {}
        self.calls: list[tuple[str, tuple]] = []

    async def _write(self, name: str, *args: Any) -> bool:
        self.calls.append((name, args))
        answers = self.script.get(name)
        if answers is not None:
            return answers.pop(0) if answers else False
        return name not in self.refuse

    async def switch_input(self, input_num: int, output_num: int) -> bool:
        return await self._write("switch_input", input_num, output_num)

    async def set_output_enable(self, output_num: int, enabled: bool) -> bool:
        return await self._write("set_output_enable", output_num, enabled)

    async def set_output_audio_mute(self, output_num: int, muted: bool) -> bool:
        return await self._write("set_output_audio_mute", output_num, muted)

    async def set_output_hdr(self, output_num: int, mode: int) -> bool:
        return await self._write("set_output_hdr", output_num, mode)

    async def set_output_hdcp(self, output_num: int, mode: int) -> bool:
        return await self._write("set_output_hdcp", output_num, mode)

    async def set_output_scaler(self, output_num: int, mode: int) -> bool:
        return await self._write("set_output_scaler", output_num, mode)

    async def set_output_arc(self, output_num: int, enabled: bool) -> bool:
        return await self._write("set_output_arc", output_num, enabled)

    async def recall_preset(self, preset_num: int) -> bool:
        return await self._write("recall_preset", preset_num)

    async def set_beep(self, enabled: bool) -> bool:
        return await self._write("set_beep", enabled)

    def asked(self, name: str) -> list[tuple]:
        """The arguments every call of ``name`` was made with."""
        return [args for called, args in self.calls if called == name]


@pytest.fixture(autouse=True)
def _cheap_pins(monkeypatch, tmp_path):
    """Cheap PBKDF2, clean attempt limiter, and hermetic legacy data path."""
    import persistence

    monkeypatch.setenv("MATRIX_PASSWORD_ITERATIONS", "1000")
    monkeypatch.setattr(persistence, "get_legacy_data_paths", lambda: [tmp_path / "_empty_legacy"])
    reset_pin_lockout()
    yield
    reset_pin_lockout()


@pytest.fixture
def matrix() -> FakeMatrix:
    """A matrix that accepts everything."""
    return FakeMatrix()


@pytest.fixture
def profile_manager(tmp_path) -> ProfileManager:
    return ProfileManager(config_dir=str(tmp_path / "profiles"))


@pytest.fixture
def scene_manager(tmp_path) -> SceneManager:
    return SceneManager(data_dir=tmp_path / "scenes")


@pytest.fixture
def macro_manager(tmp_path) -> MacroManager:
    manager = MacroManager(config_dir=str(tmp_path / "macros"))
    manager.set_cec_sender(AsyncMock(return_value=True))
    return manager


@pytest.fixture
def shortcut_manager(tmp_path) -> SystemShortcutManager:
    return SystemShortcutManager(tmp_path / "shortcuts")


@pytest.fixture
def runner(matrix, profile_manager, scene_manager, macro_manager, shortcut_manager) -> ActionRunner:
    """A runner with every manager the hub owns."""
    return ActionRunner(
        matrix,
        profile_manager=profile_manager,
        scene_manager=scene_manager,
        macro_manager=macro_manager,
        shortcut_manager=shortcut_manager,
    )


def make_profile(manager: ProfileManager, profile_id: str, outputs: dict | None = None, **extra) -> Any:
    return manager.create_profile(profile_id, profile_id.title(), outputs or {1: {"input": 2}}, **extra)


def make_scene(manager: SceneManager, *steps: SceneStep, **extra) -> Any:
    scene, error = manager.create_scene("Evening", steps=list(steps), **extra)
    assert error is None, error
    return scene


def make_macro(manager: MacroManager, macro_id: str, commands: list[str], *, continue_on_error: bool = False):
    macro = manager.create_macro(
        macro_id.title(), macro_id=macro_id, steps=[{"command": c, "targets": ["output_1"]} for c in commands]
    )
    macro.continue_on_error = continue_on_error
    manager.save()
    return macro


# =============================================================================
# ActionRunner: profiles (API-19)
# =============================================================================


async def test_profile_run_applies_every_output(runner, matrix, profile_manager):
    make_profile(profile_manager, "movie", {1: {"input": 2}, 2: {"input": 3}})

    result = await runner.run("profile", "movie")

    assert (result.success, result.partial, result.status_code) == (True, False, 200)
    assert (result.steps_completed, result.total_steps) == (2, 2)
    assert matrix.asked("switch_input") == [(2, 1), (3, 2)]
    assert result.data["applied"] == ["Output 1 → Input 2", "Output 2 → Input 3"]
    assert [step.action for step in result.step_results] == ["output:1", "output:2"]


async def test_profile_run_writes_the_saved_scaler_and_arc(runner, matrix, profile_manager):
    """API-22 / API-29: what the profile stores is what the device is told."""
    make_profile(profile_manager, "movie", {1: {"input": 2, "scaler_mode": 4, "arc": True}})

    result = await runner.run("profile", "movie")

    assert result.status_code == 200
    assert matrix.asked("set_output_scaler") == [(1, 4)]
    assert matrix.asked("set_output_arc") == [(1, True)]


async def test_profile_run_leaves_unset_settings_untouched(runner, matrix, profile_manager):
    make_profile(profile_manager, "movie", {1: {"input": 2}})

    await runner.run("profile", "movie")

    assert matrix.asked("set_output_scaler") == []
    assert matrix.asked("set_output_arc") == []


async def test_profile_run_that_fails_one_output_is_partial(profile_manager, profile_manager_unused=None):
    matrix = FakeMatrix(script={"set_output_enable": [False, True]})
    make_profile(profile_manager, "movie", {1: {"input": 2}, 2: {"input": 3}})
    runner = ActionRunner(matrix, profile_manager=profile_manager)

    result = await runner.run("profile", "movie")

    assert (result.success, result.partial, result.status_code) == (False, True, 207)
    assert (result.steps_completed, result.total_steps) == (1, 2)
    assert result.data["failed_outputs"] == [1]
    assert result.errors == ["output 1: stream on not applied"]
    assert result.step_results[0].error == "output 1: stream on not applied"


async def test_profile_run_that_fails_every_output_is_500(profile_manager):
    matrix = FakeMatrix(refuse={"set_output_enable"})
    make_profile(profile_manager, "movie", {1: {"input": 2}, 2: {"input": 3}})
    runner = ActionRunner(matrix, profile_manager=profile_manager)

    result = await runner.run("profile", "movie")

    assert (result.success, result.partial, result.status_code) == (False, False, 500)
    assert result.steps_completed == 0


async def test_unknown_profile_is_404(runner, matrix, profile_manager):
    result = await runner.run("profile", "nope")

    assert (result.success, result.status_code) == (False, 404)
    assert result.code == "not_found"
    assert matrix.calls == []


async def test_protected_profile_without_a_passcode_is_refused(runner, matrix, profile_manager):
    make_profile(profile_manager, "kids", password_protected=True, passcode_hash=hash_passcode(PIN))

    result = await runner.run("profile", "kids")

    assert (result.success, result.status_code) == (False, 403)
    assert result.code == REQUIRED
    assert result.data["requires_passcode"] is True
    assert matrix.calls == []


async def test_wrong_passcode_is_refused(runner, profile_manager):
    make_profile(profile_manager, "kids", password_protected=True, passcode_hash=hash_passcode(PIN))

    result = await runner.run("profile", "kids", passcode=WRONG_PIN)

    assert (result.success, result.status_code) == (False, 403)
    assert result.code == INVALID


async def test_correct_passcode_runs_the_profile(runner, matrix, profile_manager):
    make_profile(profile_manager, "kids", password_protected=True, passcode_hash=hash_passcode(PIN))

    result = await runner.run("profile", "kids", passcode=PIN)

    assert (result.success, result.status_code) == (True, 200)
    assert matrix.asked("switch_input") == [(2, 1)]


async def test_repeated_wrong_passcodes_lock_the_profile_out(runner, profile_manager):
    """SEC-06: the fifth wrong passcode starts the lockout, the next is answered 429."""
    make_profile(profile_manager, "kids", password_protected=True, passcode_hash=hash_passcode(PIN))

    refused = [await runner.run("profile", "kids", passcode=WRONG_PIN) for _ in range(5)]

    assert [result.code for result in refused] == [INVALID] * 5
    locked = await runner.run("profile", "kids", passcode=PIN)
    assert locked.status_code == 429
    assert locked.code == LOCKED
    assert locked.data["retry_after"] >= 1


async def test_profile_power_on_macro_runs_once(runner, matrix, profile_manager, macro_manager):
    make_macro(macro_manager, "tv_on", ["POWER_ON"])
    make_profile(profile_manager, "movie", power_on_macro="tv_on")

    result = await runner.run("profile", "movie")

    assert result.status_code == 200
    assert result.steps_completed == result.total_steps == 2  # the macro, then output 1
    assert result.step_results[0].action == "macro:tv_on"
    assert result.data["power_on_macro"]["success"] is True


async def test_profile_power_on_macro_failure_makes_the_run_partial(runner, profile_manager, macro_manager):
    macro_manager.set_cec_sender(AsyncMock(return_value=False))
    make_macro(macro_manager, "tv_on", ["POWER_ON"])
    make_profile(profile_manager, "movie", power_on_macro="tv_on")

    result = await runner.run("profile", "movie")

    assert (result.success, result.partial, result.status_code) == (False, True, 207)
    assert result.step_results[0].success is False
    assert "Power-on macro 'tv_on'" in result.errors[0]


async def test_profile_power_on_macro_without_a_macro_manager_is_reported(matrix, profile_manager):
    make_profile(profile_manager, "movie", power_on_macro="tv_on")
    runner = ActionRunner(matrix, profile_manager=profile_manager)

    result = await runner.run("profile", "movie")

    assert result.status_code == 207
    assert "Macro not found: tv_on" in result.errors[0]


async def test_profile_without_a_matrix_is_503(profile_manager):
    make_profile(profile_manager, "movie")
    result = await ActionRunner(profile_manager=profile_manager).run("profile", "movie")

    assert (result.success, result.status_code) == (False, 503)
    assert result.code == "not_configured"


async def test_profile_without_a_manager_is_503(matrix):
    result = await ActionRunner(matrix).run("profile", "movie")

    assert (result.success, result.status_code) == (False, 503)


async def test_an_unexpected_failure_is_reported_as_500(matrix):
    class BrokenProfiles:
        def get_profile(self, profile_id):
            raise RuntimeError("profiles are on fire")

    result = await ActionRunner(matrix, profile_manager=BrokenProfiles()).run("profile", "movie")

    assert (result.success, result.partial, result.status_code) == (False, False, 500)
    assert result.code == "execution_error"
    assert result.errors == ["profiles are on fire"]


# =============================================================================
# ActionRunner: scenes
# =============================================================================


async def test_scene_run_applies_every_step(runner, matrix, profile_manager, scene_manager):
    make_profile(profile_manager, "first", {1: {"input": 2}})
    make_profile(profile_manager, "second", {2: {"input": 3}})
    scene = make_scene(scene_manager, SceneStep("profile", "first"), SceneStep("profile", "second"))

    result = await runner.run("scene", scene.id)

    assert (result.success, result.partial, result.status_code) == (True, False, 200)
    assert (result.steps_completed, result.total_steps) == (2, 2)
    assert matrix.asked("switch_input") == [(2, 1), (3, 2)]


async def test_scene_run_with_a_failing_step_is_partial(profile_manager, scene_manager):
    matrix = FakeMatrix(script={"set_output_enable": [True, False]})
    make_profile(profile_manager, "first", {1: {"input": 2}})
    make_profile(profile_manager, "second", {2: {"input": 3}})
    scene = make_scene(scene_manager, SceneStep("profile", "first"), SceneStep("profile", "second"))
    runner = ActionRunner(matrix, profile_manager=profile_manager, scene_manager=scene_manager)

    result = await runner.run("scene", scene.id)

    assert (result.success, result.partial, result.status_code) == (False, True, 207)
    assert (result.steps_completed, result.total_steps) == (1, 2)
    assert result.step_results[1].error is not None


async def test_scene_run_where_nothing_is_applied_is_500(profile_manager, scene_manager):
    matrix = FakeMatrix(refuse={"switch_input"})
    make_profile(profile_manager, "first", {1: {"input": 2}})
    scene = make_scene(scene_manager, SceneStep("profile", "first"))
    runner = ActionRunner(matrix, profile_manager=profile_manager, scene_manager=scene_manager)

    result = await runner.run("scene", scene.id)

    assert (result.success, result.partial, result.status_code) == (False, False, 500)


async def test_unknown_scene_is_404(runner, matrix):
    result = await runner.run("scene", "nope")

    assert (result.success, result.status_code) == (False, 404)
    assert result.code == "not_found"
    assert matrix.calls == []


async def test_protected_scene_without_a_passcode_is_refused(runner, matrix, profile_manager, scene_manager):
    make_profile(profile_manager, "first", {1: {"input": 2}})
    scene = make_scene(scene_manager, SceneStep("profile", "first"), password_protected=True, passcode=PIN)

    result = await runner.run("scene", scene.id)

    assert (result.success, result.status_code) == (False, 403)
    assert result.code == REQUIRED
    assert matrix.calls == []


async def test_wrong_scene_passcode_is_refused(runner, profile_manager, scene_manager):
    make_profile(profile_manager, "first", {1: {"input": 2}})
    scene = make_scene(scene_manager, SceneStep("profile", "first"), password_protected=True, passcode=PIN)

    result = await runner.run("scene", scene.id, passcode=WRONG_PIN)

    assert (result.success, result.status_code) == (False, 403)
    assert result.code == INVALID


async def test_correct_scene_passcode_runs_the_scene(runner, matrix, profile_manager, scene_manager):
    make_profile(profile_manager, "first", {1: {"input": 2}})
    scene = make_scene(scene_manager, SceneStep("profile", "first"), password_protected=True, passcode=PIN)

    result = await runner.run("scene", scene.id, passcode=PIN)

    assert (result.success, result.status_code) == (True, 200)
    assert matrix.asked("switch_input") == [(2, 1)]


async def test_scene_without_a_matrix_is_503(profile_manager, scene_manager):
    scene = make_scene(scene_manager, SceneStep("macro", "any"))
    result = await ActionRunner(profile_manager=profile_manager, scene_manager=scene_manager).run("scene", scene.id)

    assert result.status_code == 503


# =============================================================================
# ActionRunner: macros
# =============================================================================


async def test_macro_run_applies_every_step(runner, macro_manager):
    make_macro(macro_manager, "tv_on", ["POWER_ON", "POWER_ON"])

    result = await runner.run("macro", "tv_on")

    assert (result.success, result.partial, result.status_code) == (True, False, 200)
    assert (result.steps_completed, result.total_steps) == (2, 2)
    assert macro_manager._cec_sender.await_count == 2


async def test_macro_run_with_a_failing_step_is_partial(runner, macro_manager):
    macro_manager.set_cec_sender(AsyncMock(side_effect=[True, False]))
    make_macro(macro_manager, "tv_on", ["POWER_ON", "POWER_ON"], continue_on_error=True)

    result = await runner.run("macro", "tv_on")

    assert (result.success, result.partial, result.status_code) == (False, True, 207)
    assert (result.steps_completed, result.total_steps) == (1, 2)
    assert result.step_results[1].success is False
    assert "Failed to send POWER_ON" in result.errors[0]


async def test_macro_run_where_every_step_fails_is_500(runner, macro_manager):
    macro_manager.set_cec_sender(AsyncMock(return_value=False))
    make_macro(macro_manager, "tv_on", ["POWER_ON"])

    result = await runner.run("macro", "tv_on")

    assert (result.success, result.partial, result.status_code) == (False, False, 500)
    assert result.steps_completed == 0


async def test_unknown_macro_is_404(runner, macro_manager):
    result = await runner.run("macro", "nope")

    assert (result.success, result.status_code) == (False, 404)
    assert result.code == "not_found"


class StubMacros:
    """A macro manager that records the arguments it was run with."""

    def __init__(self, outcome: dict) -> None:
        self.outcome = outcome
        self.kwargs: dict[str, Any] = {}

    def get_macro(self, macro_id: str):
        return object() if macro_id == "m" else None

    async def execute_macro(self, macro_id: str, **kwargs) -> dict:
        self.kwargs = kwargs
        return self.outcome


async def test_macro_run_uses_the_supplied_timeout():
    macros = StubMacros({"success": True, "results": []})
    runner = ActionRunner(FakeMatrix(), macro_manager=macros)

    result = await runner.run("macro", "m", params={"timeout_s": 5, "continue_on_error": True})

    assert result.status_code == 200
    assert macros.kwargs == {"timeout_s": 5.0, "continue_on_error": True}


@pytest.mark.parametrize(
    ("params", "message"),
    [
        ({"timeout_s": 0}, "timeout_s must be a positive number"),
        ({"timeout_s": "5"}, "timeout_s must be a positive number"),
        ({"continue_on_error": "yes"}, "continue_on_error must be true or false"),
    ],
)
async def test_macro_run_refuses_params_it_cannot_pass_on(params, message):
    result = await ActionRunner(FakeMatrix(), macro_manager=StubMacros({"success": True})).run("macro", "m", params=params)

    assert (result.success, result.status_code) == (False, 400)
    assert result.errors == [message]


# =============================================================================
# ActionRunner: shortcuts
# =============================================================================


async def test_shortcut_run_applies_the_shortcut(runner, matrix):
    result = await runner.run("shortcut", "route_all_to_output")

    assert (result.success, result.partial, result.status_code) == (True, False, 200)
    assert matrix.asked("switch_input") == [(1, 1)]


async def test_shortcut_run_passes_its_params(runner, matrix):
    result = await runner.run("shortcut", "route_all_to_output", params={"input": 2, "output": 3})

    assert result.status_code == 200
    assert matrix.asked("switch_input") == [(2, 3)]


async def test_shortcut_run_the_matrix_refuses_is_500(profile_manager, shortcut_manager):
    matrix = FakeMatrix(refuse={"switch_input"})
    runner = ActionRunner(matrix, shortcut_manager=shortcut_manager)

    result = await runner.run("shortcut", "route_all_to_output")

    assert (result.success, result.partial, result.status_code) == (False, False, 500)
    assert result.errors == ["Failed to route Input 1 → Output 1"]


async def test_unknown_shortcut_is_404(runner):
    result = await runner.run("shortcut", "no_such_shortcut")

    assert (result.success, result.status_code) == (False, 404)
    assert result.code == "not_found"


async def test_disabled_shortcut_is_refused(runner, shortcut_manager, matrix):
    shortcut_manager.update_prefs("route_all_to_output", enabled=False)

    result = await runner.run("shortcut", "route_all_to_output")

    assert (result.success, result.status_code) == (False, 400)
    assert result.code == "disabled"
    assert matrix.calls == []


# =============================================================================
# ActionRunner: presets
# =============================================================================


async def test_preset_run_recalls_the_slot(runner, matrix):
    result = await runner.run("preset", "3")

    assert (result.success, result.partial, result.status_code) == (True, False, 200)
    assert matrix.asked("recall_preset") == [(3,)]
    assert result.data == {"preset": 3, "name": "Preset 3"}


async def test_preset_run_the_matrix_refuses_is_500(profile_manager):
    runner = ActionRunner(FakeMatrix(refuse={"recall_preset"}))

    result = await runner.run("preset", "1")

    assert (result.success, result.status_code) == (False, 500)
    assert result.errors == ["Failed to recall preset 1"]


@pytest.mark.parametrize("preset", ["0", "9", "abc", "", "1.5"])
async def test_preset_that_does_not_exist_is_404(matrix, preset):
    result = await ActionRunner(matrix).run("preset", preset)

    assert (result.success, result.status_code) == (False, 404)
    assert matrix.calls == []


async def test_preset_run_uses_a_registered_executor(matrix):
    """A preset executor is whatever recalls presets; the matrix is the default."""
    recalls = []

    async def recall(preset_num: int) -> bool:
        recalls.append(preset_num)
        return True

    result = await ActionRunner(matrix, preset_executor=recall).run("preset", 5)

    assert result.status_code == 200
    assert recalls == [5]


# =============================================================================
# ActionRunner: the registry and the shared result shape
# =============================================================================


async def test_unknown_kind_is_refused(matrix):
    result = await ActionRunner(matrix).run("widget", "x")

    assert (result.success, result.status_code) == (False, 400)
    assert result.code == "unknown_kind"


async def test_kind_names_are_normalised(runner, profile_manager, matrix):
    make_profile(profile_manager, "movie")
    result = await runner.run("  PROFILE ", "movie")

    assert result.status_code == 200
    assert result.kind == "profile"


async def test_registered_executor_replaces_the_default_path(matrix, profile_manager):
    seen = {}

    def executor(action_id, *, passcode=None, params=None):
        seen.update(action_id=action_id, passcode=passcode, params=params)
        return ActionRunResult("profile", action_id, True, False, 200, 1, 1, [StepResult(0, "stub", True)], [], {"stub": True})

    make_profile(profile_manager, "movie")
    runner = ActionRunner(matrix, profile_manager=profile_manager)
    runner.register("profile", executor)

    result = await runner.run("profile", "movie", passcode=PIN, params={"a": 1})

    assert seen == {"action_id": "movie", "passcode": PIN, "params": {"a": 1}}
    assert result.data == {"stub": True}
    assert matrix.calls == []  # the default path never ran


async def test_registered_executor_may_be_an_object_with_run_action(matrix):
    class Executor:
        async def run_action(self, action_id, *, passcode=None, params=None):
            return {"success": True, "step_results": [{"step_index": 0, "action": "x", "success": True}], "data": {"n": 1}}

    runner = ActionRunner(matrix)
    runner.register("macro", Executor())

    result = await runner.run("macro", "m")

    assert (result.status_code, result.steps_completed, result.total_steps) == (200, 1, 1)
    assert result.data == {"n": 1}


async def test_failing_registered_executor_is_500(matrix):
    def executor(action_id, *, passcode=None, params=None):
        raise RuntimeError("executor exploded")

    runner = ActionRunner(matrix)
    runner.register("preset", executor)

    result = await runner.run("preset", "1")

    assert (result.success, result.partial, result.status_code) == (False, False, 500)
    assert result.code == "execution_error"
    assert result.errors == ["executor exploded"]


def test_register_rejects_an_unknown_kind(matrix):
    with pytest.raises(ValueError, match="Unknown action kind"):
        ActionRunner(matrix).register("widget", lambda action_id, **kwargs: None)


def test_the_runner_knows_its_five_kinds(runner):
    assert runner.kinds == ACTION_KINDS
    assert set(ACTION_KINDS) == {"profile", "scene", "macro", "shortcut", "preset"}


def test_to_response_dict_has_the_hub_envelope():
    result = ActionRunResult(
        kind="profile",
        action_id="movie",
        success=False,
        partial=True,
        status_code=207,
        steps_completed=1,
        total_steps=2,
        step_results=[StepResult(0, "output:1", True), StepResult(1, "output:2", False, "output 2: stream off")],
        errors=["output 2: stream off not applied"],
        data={"profile": "Movie"},
    )

    body = result.to_response_dict()

    assert body["success"] is False
    assert body["error"] == "output 2: stream off not applied"
    assert body["data"]["kind"] == "profile"
    assert body["data"]["id"] == "movie"
    assert body["data"]["partial"] is True
    assert body["data"]["status_code"] == 207
    assert body["data"]["steps_completed"] == 1
    assert body["data"]["total_steps"] == 2
    assert body["data"]["step_results"][1] == {
        "step_index": 1,
        "action": "output:2",
        "success": False,
        "error": "output 2: stream off",
        "data": None,
    }
    assert body["data"]["result"] == {"profile": "Movie"}


def test_a_successful_result_has_no_error():
    result = ActionRunResult("preset", "1", True, False, 200)

    assert result.error is None
    assert result.code is None
    assert result.to_response_dict()["error"] is None


def test_from_runtime_binds_the_running_hub_managers(mock_matrix, tmp_path):
    from rest_api.utils import set_macro_manager, set_profile_manager

    profiles = ProfileManager(config_dir=str(tmp_path / "profiles"))
    set_matrix_device(mock_matrix)
    set_profile_manager(profiles)
    set_macro_manager(MacroManager(config_dir=str(tmp_path / "macros")))

    runner = ActionRunner.from_runtime()

    assert runner.matrix_device is mock_matrix
    assert runner.profile_manager is profiles
    assert runner.macro_manager is not None


# =============================================================================
# VisibilityStore (DI-5 / API-20)
# =============================================================================


@pytest.fixture
def preset_store(tmp_path):
    """The real device-settings store, in this test's private data directory."""
    from rest_api import device_settings

    device_settings.init_device_settings(tmp_path)
    return device_settings


@pytest.fixture
def store(profile_manager, scene_manager, macro_manager, shortcut_manager, preset_store) -> VisibilityStore:
    return VisibilityStore(
        profiles=profile_manager,
        scenes=scene_manager,
        macros=macro_manager,
        shortcuts=shortcut_manager,
        presets=preset_store,
    )


def test_snapshot_has_every_kind(store, profile_manager, macro_manager):
    make_profile(profile_manager, "movie")
    make_macro(macro_manager, "tv_on", ["POWER_ON"])

    snapshot = store.snapshot()

    assert list(snapshot) == list(VISIBILITY_KINDS)
    assert snapshot["profiles"] == {"movie": {"favorite": False, "show_on_dashboard": False}}
    assert snapshot["macros"] == {"tv_on": {"favorite": False, "show_on_dashboard": False}}
    assert snapshot["presets"] == {
        str(number): {"favorite": False, "show_on_dashboard": False} for number in range(1, 9)
    }
    assert snapshot["scenes"] == {}
    assert snapshot["shortcuts"]  # built-in shortcuts always exist


def test_an_unknown_item_reads_as_both_false(store):
    assert store.get_visibility("profiles", "nope") == {"favorite": False, "show_on_dashboard": False}
    assert store.get_visibility("presets", 99) == {"favorite": False, "show_on_dashboard": False}


def test_an_unknown_kind_is_rejected(store):
    with pytest.raises(ValueError, match="Unknown visibility kind"):
        store.get_visibility("widgets", "x")
    with pytest.raises(ValueError, match="Unknown visibility kind"):
        store.set_favorite("widgets", "x", True)


def test_profile_flags_round_trip(store, profile_manager):
    make_profile(profile_manager, "movie")

    assert store.set_favorite("profiles", "movie", True) == {"favorite": True, "show_on_dashboard": False}
    assert store.set_dashboard("profiles", "movie", True) == {"favorite": True, "show_on_dashboard": True}

    assert store.get_visibility("profiles", "movie") == {"favorite": True, "show_on_dashboard": True}
    assert profile_manager.get_profile("movie").favorite is True
    assert store.set_favorite("profiles", "movie", False)["favorite"] is False


def test_macro_flags_round_trip(store, macro_manager):
    make_macro(macro_manager, "tv_on", ["POWER_ON"])

    store.apply("macros", "tv_on", favorite=True, show_on_dashboard=True)

    assert macro_manager.get_macro("tv_on").favorite is True
    assert macro_manager.get_macro("tv_on").dashboard_visible is True
    assert store.snapshot()["macros"]["tv_on"] == {"favorite": True, "show_on_dashboard": True}


def test_shortcut_flags_round_trip(store, shortcut_manager):
    user = shortcut_manager.add_user_shortcut("Mute", "🔇", "mute_all_audio")

    store.set_favorite("shortcuts", user.key, True)
    store.set_dashboard("shortcuts", "mute_all_audio", True)

    assert store.get_visibility("shortcuts", user.key)["favorite"] is True
    assert store.get_visibility("shortcuts", "mute_all_audio")["show_on_dashboard"] is True
    assert user.key in [shortcut.key for shortcut in shortcut_manager.list_favorites()]
    assert "mute_all_audio" in [shortcut.key for shortcut in shortcut_manager.list_dashboard()]


def test_scene_flags_round_trip(store, scene_manager):
    scene = make_scene(scene_manager, SceneStep("macro", "any"))

    store.apply("scenes", scene.id, favorite=True, show_on_dashboard=True)

    assert store.get_visibility("scenes", scene.id) == {"favorite": True, "show_on_dashboard": True}
    assert [s.id for s in scene_manager.list_favorite_scenes()] == [scene.id]
    assert [s.id for s in scene_manager.list_dashboard_scenes()] == [scene.id]


def test_preset_flags_round_trip(store, preset_store):
    assert store.set_favorite("presets", 3, True) == {"favorite": True, "show_on_dashboard": False}
    assert store.set_dashboard("presets", "3", True) == {"favorite": True, "show_on_dashboard": True}

    assert store.get_visibility("presets", 3) == {"favorite": True, "show_on_dashboard": True}
    assert preset_store.get_favorite_presets() == [3]
    assert preset_store.get_dashboard_presets() == [3]
    assert store.set_favorite("presets", 3, False) == {"favorite": False, "show_on_dashboard": True}


def test_a_preset_slot_that_does_not_exist_cannot_be_changed(store, preset_store):
    assert store.set_favorite("presets", 9, True) is None
    assert preset_store.get_favorite_presets() == []


def test_setting_an_unknown_item_reports_no_such_item(store):
    assert store.set_favorite("profiles", "nope", True) is None
    assert store.set_dashboard("macros", "nope", True) is None


def test_apply_writes_both_flags_in_one_save(store, macro_manager):
    """The atomic helper: one manager write, so the two flags never disagree."""
    make_macro(macro_manager, "tv_on", ["POWER_ON"])

    with patch.object(macro_manager, "save", wraps=macro_manager.save) as save:
        store.apply("macros", "tv_on", favorite=True, show_on_dashboard=True)

    assert save.call_count == 1


def test_apply_leaves_the_flag_it_was_not_given(store, profile_manager):
    make_profile(profile_manager, "movie")
    store.set_favorite("profiles", "movie", True)

    assert store.apply("profiles", "movie", show_on_dashboard=True) == {
        "favorite": True,
        "show_on_dashboard": True,
    }


def test_apply_without_a_flag_only_reads(store, profile_manager):
    make_profile(profile_manager, "movie")

    assert store.apply("profiles", "movie") == {"favorite": False, "show_on_dashboard": False}


def test_a_store_without_sources_reads_as_empty():
    empty = VisibilityStore()

    assert empty.snapshot() == {kind: {} for kind in VISIBILITY_KINDS}
    assert empty.get_visibility("profiles", "movie") == {"favorite": False, "show_on_dashboard": False}
    assert empty.set_favorite("profiles", "movie", True) is None


def test_snapshot_follows_the_changes(store, profile_manager, macro_manager, preset_store):
    make_profile(profile_manager, "movie")
    make_macro(macro_manager, "tv_on", ["POWER_ON"])
    store.apply("profiles", "movie", favorite=True)
    store.apply("macros", "tv_on", show_on_dashboard=True)
    store.apply("presets", 1, favorite=True, show_on_dashboard=True)

    snapshot = store.snapshot()

    assert snapshot["profiles"]["movie"] == {"favorite": True, "show_on_dashboard": False}
    assert snapshot["macros"]["tv_on"] == {"favorite": False, "show_on_dashboard": True}
    assert snapshot["presets"]["1"] == {"favorite": True, "show_on_dashboard": True}


def test_visibility_store_from_runtime_binds_the_running_hub(mock_matrix, tmp_path):
    from rest_api.utils import set_macro_manager, set_profile_manager

    set_matrix_device(mock_matrix)
    set_profile_manager(ProfileManager(config_dir=str(tmp_path)))
    set_macro_manager(MacroManager(config_dir=str(tmp_path)))

    store = VisibilityStore.from_runtime()

    assert store.kinds == VISIBILITY_KINDS
    assert isinstance(store.snapshot()["presets"], dict)


# =============================================================================
# API-22: a profile's scaler / arc survive create, edit, disk and every read
# =============================================================================

# The scaler as the domain layer names it; ``scaler_mode`` is the same value.
_SCALER_ALIAS_OUTPUTS = {"1": {"input": 2, "enabled": True, "audio_mute": False, "scaler": 4, "arc": True}}
_SCALER_MODE_OUTPUTS = {"1": {"input": 2, "enabled": True, "audio_mute": False, "scaler_mode": 5, "arc": False}}


def test_scene_output_accepts_either_scaler_spelling():
    assert SceneOutput.from_dict({"input": 1, "scaler": 3}).scaler_mode == 3
    assert SceneOutput.from_dict({"input": 1, "scaler_mode": 3}).scaler == 3
    assert SceneOutput.from_dict({"input": 1}).scaler is None
    assert SceneOutput.from_dict({"input": 1, "scaler": None}).to_dict() == {
        "input": 1,
        "enabled": True,
        "audio_mute": False,
    }


def test_profile_keeps_the_scaler_alias_in_memory_and_on_disk(tmp_path):
    manager = ProfileManager(config_dir=str(tmp_path))
    manager.create_profile("movie", "Movie", dict(_SCALER_ALIAS_OUTPUTS))

    stored = manager.get_profile("movie")

    assert (stored.outputs[1].scaler, stored.outputs[1].arc) == (4, True)
    assert stored.to_dict()["outputs"] == {
        "1": {"input": 2, "enabled": True, "audio_mute": False, "scaler_mode": 4, "arc": True}
    }

    reloaded = ProfileManager(config_dir=str(tmp_path)).get_profile("movie")

    assert reloaded.to_dict()["outputs"] == stored.to_dict()["outputs"]


def test_profile_update_keeps_the_scaler_alias(tmp_path):
    manager = ProfileManager(config_dir=str(tmp_path))
    manager.create_profile("movie", "Movie", {"1": {"input": 2}})

    manager.update_profile("movie", outputs=dict(_SCALER_MODE_OUTPUTS))

    assert manager.get_profile("movie").to_dict()["outputs"]["1"]["scaler_mode"] == 5


def test_profile_list_summary_carries_the_output_settings(tmp_path):
    manager = ProfileManager(config_dir=str(tmp_path))
    manager.create_profile("movie", "Movie", dict(_SCALER_ALIAS_OUTPUTS))

    summary = manager.list_profiles()[0]

    assert summary["outputs"]["1"] == {
        "input": 2,
        "enabled": True,
        "audio_mute": False,
        "scaler_mode": 4,
        "arc": True,
    }


@pytest.fixture
async def client(aiohttp_client, mock_matrix):
    set_matrix_device(mock_matrix, {number: f"Input {number}" for number in range(1, 9)})
    return await aiohttp_client(create_rest_app())


@pytest.fixture
def data_dir() -> Path:
    """The private data directory the hub writes to in this test."""
    return Path(os.environ["MATRIX_DATA_DIR"])


async def _profile_body(client, profile_id="movie") -> dict:
    body = (await (await client.get(f"/api/profile/{profile_id}")).json())["data"]
    return body


def _saved_profile(data_dir: Path, profile_id: str) -> dict:
    saved = json.loads((data_dir / "profiles.json").read_text(encoding="utf-8"))
    return next(profile for profile in saved["profiles"] if profile["id"] == profile_id)


async def test_post_profile_round_trips_scaler_and_arc(client):
    resp = await client.post(
        "/api/profile", json={"id": "movie", "name": "Movie", "outputs": _SCALER_ALIAS_OUTPUTS}
    )

    assert resp.status == 200, await resp.text()
    outputs = (await resp.json())["data"]["outputs"]
    assert outputs["1"] == {"input": 2, "enabled": True, "audio_mute": False, "scaler_mode": 4, "arc": True}


async def test_get_profile_returns_the_saved_scaler_and_arc(client, data_dir):
    await client.post("/api/profile", json={"id": "movie", "name": "Movie", "outputs": _SCALER_ALIAS_OUTPUTS})

    body = await _profile_body(client)

    assert body["outputs"]["1"]["scaler_mode"] == 4
    assert body["outputs"]["1"]["arc"] is True
    assert _saved_profile(data_dir, "movie")["outputs"]["1"] == body["outputs"]["1"]


async def test_list_profiles_returns_the_saved_scaler_and_arc(client):
    await client.post("/api/profile", json={"id": "movie", "name": "Movie", "outputs": _SCALER_MODE_OUTPUTS})

    profiles = (await (await client.get("/api/profiles")).json())["data"]["profiles"]

    summary = next(profile for profile in profiles if profile["id"] == "movie")
    assert summary["outputs"]["1"] == {
        "input": 2,
        "enabled": True,
        "audio_mute": False,
        "scaler_mode": 5,
        "arc": False,
    }


async def test_put_profile_round_trips_scaler_and_arc(client, data_dir):
    await client.post("/api/profile", json={"id": "movie", "name": "Movie", "outputs": {"1": {"input": 2}}})

    resp = await client.put("/api/profile/movie", json={"outputs": _SCALER_ALIAS_OUTPUTS})

    assert resp.status == 200, await resp.text()
    body = await _profile_body(client)
    assert body["outputs"]["1"]["scaler_mode"] == 4
    assert body["outputs"]["1"]["arc"] is True
    assert _saved_profile(data_dir, "movie")["outputs"]["1"] == body["outputs"]["1"]


async def test_either_scaler_spelling_is_accepted(client):
    for outputs in (_SCALER_ALIAS_OUTPUTS, _SCALER_MODE_OUTPUTS):
        resp = await client.post("/api/profile", json={"id": "movie", "name": "Movie", "outputs": outputs})
        assert resp.status == 200, await resp.text()
        saved = (await resp.json())["data"]["outputs"]["1"]
        assert saved["scaler_mode"] == outputs["1"].get("scaler", outputs["1"].get("scaler_mode"))


async def test_scaler_spellings_that_agree_are_accepted(client):
    resp = await client.post(
        "/api/profile",
        json={"id": "movie", "name": "Movie", "outputs": {"1": {"input": 2, "scaler_mode": 3, "scaler": 3}}},
    )

    assert resp.status == 200, await resp.text()
    assert (await resp.json())["data"]["outputs"]["1"]["scaler_mode"] == 3


async def test_scaler_spellings_that_disagree_are_refused(client):
    resp = await client.post(
        "/api/profile",
        json={"id": "movie", "name": "Movie", "outputs": {"1": {"input": 2, "scaler_mode": 3, "scaler": 4}}},
    )

    assert resp.status == 400
    assert "disagree" in (await resp.json())["error"]


@pytest.mark.parametrize("method", ["POST", "PUT"])
@pytest.mark.parametrize(
    "setting",
    [{"scaler": 0}, {"scaler": 6}, {"scaler": "2"}, {"scaler": True}, {"scaler": 2.0},
     {"scaler_mode": 6}, {"arc": 1}, {"arc": "on"}],
)
async def test_invalid_scaler_or_arc_is_refused_and_nothing_changes(client, data_dir, method, setting):
    await client.post("/api/profile", json={"id": "movie", "name": "Movie", "outputs": _SCALER_ALIAS_OUTPUTS})
    before = await _profile_body(client)
    outputs = {"1": {"input": 2, **setting}}

    if method == "POST":
        resp = await client.post("/api/profile", json={"id": "other", "name": "Other", "outputs": outputs})
    else:
        resp = await client.put("/api/profile/movie", json={"outputs": outputs})

    assert resp.status == 400
    assert await _profile_body(client) == before
    assert _saved_profile(data_dir, "movie")["outputs"] == before["outputs"]


async def test_outputs_without_the_settings_stay_unset(client):
    resp = await client.post(
        "/api/profile",
        json={"id": "plain", "name": "Plain", "outputs": {"1": {"input": 4, "scaler": None, "arc": None}}},
    )

    assert resp.status == 200, await resp.text()
    body = await _profile_body(client, "plain")
    assert body["outputs"] == {"1": {"input": 4, "enabled": True, "audio_mute": False}}
