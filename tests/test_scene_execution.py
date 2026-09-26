"""
Unit tests for scene_execution.py (Phase 8).

Tests cover: SceneExecutor with profile/system_action/macro steps, scene
overrides, passcode verification, and error handling.

The matrix double is ``create_autospec(OreiMatrix)``: it only has the methods
the real class has, so a call to a method that does not exist fails here the
way it fails on a real matrix (API-01: the old tests mocked ``matrix.switch``,
which ``OreiMatrix`` never had). Profiles and the profile manager are the real
classes from ``config``. Effects on a device are proven in
``tests/sim/test_sim_scenes_v2.py``.
"""

from unittest.mock import AsyncMock, MagicMock, create_autospec

import pytest

from config import ProfileManager
from orei_matrix import OreiMatrix
from scene_execution import (
    ExecutionResult,
    SceneExecutor,
    StepResult,
    overridden_settings,
)
from scene_manager import (
    STEP_TYPE_MACRO,
    STEP_TYPE_PROFILE,
    STEP_TYPE_SYSTEM_ACTION,
    Scene,
    SceneManager,
    SceneStep,
)
from system_shortcuts import SystemShortcutManager


def make_matrix(result: bool = True) -> MagicMock:
    """An OreiMatrix double whose every write answers ``result``."""
    matrix = create_autospec(OreiMatrix, instance=True)
    for name in dir(OreiMatrix):
        attr = getattr(matrix, name, None)
        if isinstance(attr, AsyncMock):
            attr.return_value = result
    return matrix


@pytest.fixture
def profiles(tmp_path) -> ProfileManager:
    pm = ProfileManager(config_dir=str(tmp_path))
    pm.create_profile(
        "p1",
        "Test Profile",
        {
            1: {"input": 4, "enabled": True, "hdcp_mode": 2, "hdr_mode": 1, "audio_mute": True},
            2: {"input": 5, "enabled": True},
            3: {"input": 6, "enabled": False},
        },
    )
    return pm


@pytest.fixture
def scenes(tmp_path) -> SceneManager:
    return SceneManager(data_dir=tmp_path / "scenes")


@pytest.fixture
def executor(scenes, profiles, tmp_path) -> SceneExecutor:
    return SceneExecutor(
        scene_manager=scenes,
        profile_manager=profiles,
        system_action_manager=SystemShortcutManager(tmp_path / "shortcuts"),
    )


class TestOverriddenSettings:
    """A scene override means "leave this setting unchanged" (API-04)."""

    def test_no_overrides(self):
        assert overridden_settings(Scene(id="s1", name="Test"), "p1") == {}

    def test_only_active_overrides_count(self):
        scene = Scene(
            id="s1",
            name="Test",
            overrides={"p1": {1: {"hdcp": True, "arc": True, "input": False}, 2: {"input": False}}},
        )
        assert overridden_settings(scene, "p1") == {1: {"hdcp", "arc"}}
        assert overridden_settings(scene, "other") == {}


class TestSceneExecutorProfile:
    """Profile steps use the real OreiMatrix methods and check their answers."""

    async def test_applies_routing_and_settings_of_enabled_outputs(self, executor, scenes):
        scene, _ = scenes.create_scene(name="Test", steps=[SceneStep(type=STEP_TYPE_PROFILE, id="p1")])
        matrix = make_matrix()
        result = await executor.execute_scene(scene.id, matrix)
        assert result.success is True, result.error
        assert result.steps_completed == 1 and result.total_steps == 1
        matrix.switch_input.assert_any_await(4, 1)
        matrix.switch_input.assert_any_await(5, 2)
        assert matrix.switch_input.await_count == 2  # output 3 is disabled in the profile
        matrix.set_output_hdcp.assert_awaited_once_with(1, 2)
        matrix.set_output_hdr.assert_awaited_once_with(1, 1)  # API value; OreiMatrix maps it to the device code
        matrix.set_output_audio_mute.assert_any_await(1, True)
        matrix.set_output_audio_mute.assert_any_await(2, False)
        matrix.set_output_enable.assert_not_awaited()  # the scene executor does not change stream state

    async def test_overridden_settings_are_left_unchanged(self, executor, scenes):
        """API-04: an input override used to route Input 1; a mute override used to unmute."""
        scene, _ = scenes.create_scene(name="Test", steps=[SceneStep(type=STEP_TYPE_PROFILE, id="p1")])
        scenes.update_scene(scene.id, overrides={"p1": {1: {"input": True, "audio_mute": True, "hdr": True}}})
        matrix = make_matrix()
        result = await executor.execute_scene(scene.id, matrix)
        assert result.success is True, result.error
        assert [c.args for c in matrix.switch_input.await_args_list] == [(5, 2)]
        matrix.set_output_hdr.assert_not_awaited()
        matrix.set_output_hdcp.assert_awaited_once_with(1, 2)
        assert [c.args for c in matrix.set_output_audio_mute.await_args_list] == [(2, False)]

    async def test_a_refused_write_fails_the_step(self, executor, scenes):
        """API-08: the matrix's False answers used to be ignored."""
        scene, _ = scenes.create_scene(name="Test", steps=[SceneStep(type=STEP_TYPE_PROFILE, id="p1")])
        matrix = make_matrix()
        matrix.set_output_hdcp.return_value = False
        result = await executor.execute_scene(scene.id, matrix)
        assert result.success is False
        assert result.steps_completed == 0
        assert "output 1" in result.error and "HDCP 2" in result.error
        # the other output was still applied
        matrix.switch_input.assert_any_await(5, 2)

    async def test_a_raising_write_fails_the_step_and_the_rest_still_runs(self, executor, scenes):
        scene, _ = scenes.create_scene(name="Test", steps=[SceneStep(type=STEP_TYPE_PROFILE, id="p1")])
        matrix = make_matrix()
        matrix.switch_input.side_effect = [ConnectionError("gone"), True]
        result = await executor.execute_scene(scene.id, matrix)
        assert result.success is False
        assert "output 1" in result.error
        matrix.switch_input.assert_any_await(5, 2)

    async def test_execution_is_logged_on_the_profile_and_saved(self, executor, scenes, profiles, tmp_path):
        """API-02: ``profile_manager._save()`` does not exist."""
        scene, _ = scenes.create_scene(name="Test", steps=[SceneStep(type=STEP_TYPE_PROFILE, id="p1")])
        await executor.execute_scene(scene.id, make_matrix())
        reloaded = ProfileManager(config_dir=str(tmp_path))
        reloaded.load()
        log = reloaded.get_profile("p1").execution_log
        assert log[-1]["scene_id"] == scene.id and log[-1]["status"] == "success"

    async def test_profile_macros_run_through_the_macro_manager(self, scenes, profiles, tmp_path):
        """API-03: the old code called ``.get()`` on the MacroStep dataclass and expected ``input:3`` targets."""
        profiles.update_profile("p1", macros=["m1"])
        mm = MagicMock()
        mm.get_macro.return_value = MagicMock(steps=[])
        mm.execute_macro = AsyncMock(return_value={"success": True})
        ex = SceneExecutor(scenes, profiles, SystemShortcutManager(tmp_path / "sc"), macro_manager=mm)
        scene, _ = scenes.create_scene(name="Test", steps=[SceneStep(type=STEP_TYPE_PROFILE, id="p1")])
        result = await ex.execute_scene(scene.id, make_matrix())
        assert result.success is True, result.error
        mm.execute_macro.assert_awaited_once_with("m1")

    async def test_a_failed_profile_macro_fails_the_step(self, scenes, profiles, tmp_path):
        profiles.update_profile("p1", macros=["m1"])
        mm = MagicMock()
        mm.get_macro.return_value = MagicMock(steps=[])
        mm.execute_macro = AsyncMock(return_value={"success": False, "error": "CEC sender not configured"})
        ex = SceneExecutor(scenes, profiles, SystemShortcutManager(tmp_path / "sc"), macro_manager=mm)
        scene, _ = scenes.create_scene(name="Test", steps=[SceneStep(type=STEP_TYPE_PROFILE, id="p1")])
        result = await ex.execute_scene(scene.id, make_matrix())
        assert result.success is False
        assert "CEC sender not configured" in result.error

    async def test_unknown_profile(self, executor, scenes):
        scene, _ = scenes.create_scene(name="Test", steps=[SceneStep(type=STEP_TYPE_PROFILE, id="nope")])
        result = await executor.execute_scene(scene.id, make_matrix())
        assert result.success is False
        assert "not found" in result.error.lower()

    async def test_execute_scene_not_found(self, executor):
        result = await executor.execute_scene("nonexistent", make_matrix())
        assert result.success is False
        assert "not found" in result.error.lower()


class TestSceneExecutorSystemActions:
    async def test_route_shortcut_step_uses_switch_input(self, executor, scenes):
        """API-01: ``route_all_to_output`` called ``matrix.switch()``."""
        scene, _ = scenes.create_scene(
            name="Test",
            steps=[SceneStep(type=STEP_TYPE_SYSTEM_ACTION, id="route_all_to_output", params={"input": 6, "output": 2})],
        )
        matrix = make_matrix()
        result = await executor.execute_scene(scene.id, matrix)
        assert result.success is True, result.error
        matrix.switch_input.assert_awaited_once_with(6, 2)

    async def test_failed_shortcut_step(self, executor, scenes):
        scene, _ = scenes.create_scene(name="Test", steps=[SceneStep(type=STEP_TYPE_SYSTEM_ACTION, id="beep_off")])
        result = await executor.execute_scene(scene.id, make_matrix(result=False))
        assert result.success is False
        assert result.step_results[0].error

    async def test_unknown_shortcut_step(self, executor, scenes):
        scene, _ = scenes.create_scene(name="Test", steps=[SceneStep(type=STEP_TYPE_SYSTEM_ACTION, id="nope")])
        result = await executor.execute_scene(scene.id, make_matrix())
        assert result.success is False


class TestSceneExecutorPassword:
    """Tests for SceneExecutor password protection."""

    async def test_protected_scene_requires_passcode(self, executor, scenes):
        scene, _ = scenes.create_scene(
            name="Protected",
            steps=[SceneStep(type=STEP_TYPE_PROFILE, id="p1")],
            password_protected=True,
            passcode="1234",
        )
        matrix = make_matrix()
        result = await executor.execute_scene(scene.id, matrix)
        assert result.success is False
        assert "passcode" in result.error.lower()
        matrix.switch_input.assert_not_awaited()

    async def test_protected_scene_wrong_passcode(self, executor, scenes):
        scene, _ = scenes.create_scene(
            name="Protected",
            steps=[SceneStep(type=STEP_TYPE_PROFILE, id="p1")],
            password_protected=True,
            passcode="1234",
        )
        result = await executor.execute_scene(scene.id, make_matrix(), passcode="9999")
        assert result.success is False
        assert result.error == "invalid_passcode"

    async def test_protected_scene_correct_passcode(self, executor, scenes):
        scene, _ = scenes.create_scene(
            name="Protected",
            steps=[SceneStep(type=STEP_TYPE_PROFILE, id="p1")],
            password_protected=True,
            passcode="1234",
        )
        result = await executor.execute_scene(scene.id, make_matrix(), passcode="1234")
        assert result.success is True, result.error


class TestSceneExecutorMacroStep:
    """Tests for SceneExecutor with macro steps."""

    @pytest.fixture
    def mock_macro_manager(self):
        mm = MagicMock()
        mm.get_macro.return_value = MagicMock(steps=["step1", "step2"])
        mm.execute_macro = AsyncMock(return_value={"success": True, "detail": "Done"})
        return mm

    @pytest.fixture
    def executor_with_macros(self, scenes, profiles, mock_macro_manager, tmp_path):
        return SceneExecutor(scenes, profiles, SystemShortcutManager(tmp_path / "sc"), macro_manager=mock_macro_manager)

    async def test_macro_step_executes(self, executor_with_macros, scenes):
        scene, _ = scenes.create_scene(name="With Macro", steps=[SceneStep(type=STEP_TYPE_MACRO, id="m1")])
        result = await executor_with_macros.execute_scene(scene.id, make_matrix())
        assert result.success is True
        assert result.steps_completed == 1
        executor_with_macros.macro_manager.execute_macro.assert_awaited_once_with("m1")

    async def test_failed_macro_step_reports_the_step_errors(self, executor_with_macros, scenes):
        executor_with_macros.macro_manager.execute_macro.return_value = {
            "success": False,
            "results": [{"errors": ["Failed to send POWER_ON to output_1"]}],
        }
        scene, _ = scenes.create_scene(name="With Macro", steps=[SceneStep(type=STEP_TYPE_MACRO, id="m1")])
        result = await executor_with_macros.execute_scene(scene.id, make_matrix())
        assert result.success is False
        assert "POWER_ON to output_1" in result.error

    async def test_macro_step_without_macro_manager(self, executor, scenes):
        scene, _ = scenes.create_scene(name="Test", steps=[SceneStep(type=STEP_TYPE_MACRO, id="m1")])
        result = await executor.execute_scene(scene.id, make_matrix())
        assert result.success is False
        assert "macro manager" in result.error.lower()

    async def test_macro_not_found(self, executor_with_macros, scenes):
        executor_with_macros.macro_manager.get_macro.return_value = None
        scene, _ = scenes.create_scene(name="Test", steps=[SceneStep(type=STEP_TYPE_MACRO, id="nonexistent")])
        result = await executor_with_macros.execute_scene(scene.id, make_matrix())
        assert result.success is False
        assert "not found" in result.error.lower()


class TestStepResultDataclass:
    """Tests for StepResult dataclass."""

    def test_step_result_to_dict(self):
        r = StepResult(step_index=0, step_type="profile", step_id="p1", success=True, detail="OK")
        d = r.to_dict()
        assert d["step_index"] == 0
        assert d["type"] == "profile"
        assert d["id"] == "p1"
        assert d["success"] is True
        assert d["detail"] == "OK"


class TestExecutionResultDataclass:
    """Tests for ExecutionResult dataclass."""

    def test_execution_result_default(self):
        r = ExecutionResult(scene_id="s1", success=True, steps_completed=1, total_steps=2)
        assert r.step_results == []
        assert r.error is None
