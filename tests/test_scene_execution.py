"""
Unit tests for scene_execution.py (Phase 8).

Tests cover: SceneExecutor with profile/system_action/macro steps,
override application, passcode verification, and error handling.
"""

import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest

from scene_execution import (
    ExecutionResult,
    SceneExecutor,
    StepResult,
    apply_overrides_to_profile,
)
from scene_manager import (
    STEP_TYPE_MACRO,
    STEP_TYPE_PROFILE,
    STEP_TYPE_SYSTEM_ACTION,
    Scene,
    SceneManager,
    SceneStep,
)


class TestApplyOverridesToProfile:
    """Tests for apply_overrides_to_profile() function."""

    def test_no_overrides_returns_profile_unchanged(self):
        """Scene with no overrides returns the profile as-is."""
        profile = MagicMock()
        profile.outputs = {}
        profile.id = "p1"
        scene = Scene(id="s1", name="Test")

        result = apply_overrides_to_profile(profile, scene)
        assert result is profile

    def test_overrides_reset_to_defaults(self):
        """Overridden settings are reset to defaults in the returned profile."""
        import copy

        # Create a real-ish profile mock with mutable outputs
        profile = MagicMock()
        profile.id = "p1"
        profile.outputs = {
            1: MagicMock(input=5, enabled=True, hdcp_mode=2, hdr_mode=1, scaler_mode=0, arc=True, audio_mute=True),
        }
        scene = Scene(
            id="s1",
            name="Test",
            steps=[SceneStep(type=STEP_TYPE_PROFILE, id="p1")],
            overrides={"p1": {1: {"hdcp": True, "arc": True}}},
        )

        result = apply_overrides_to_profile(profile, scene)
        # Overridden settings should be reset to defaults
        assert result.outputs[1].hdcp_mode == 3  # default
        assert result.outputs[1].arc is False  # default
        # Non-overridden settings preserved
        assert result.outputs[1].input == 5


class _FakeOutputCfg:
    """Plain object with attributes — avoids MagicMock await issues."""
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


class TestSceneExecutorProfile:
    """Tests for SceneExecutor with profile steps."""

    @pytest.fixture
    def temp_dir(self):
        with tempfile.TemporaryDirectory() as d:
            yield Path(d)

    @pytest.fixture
    def mock_profile_manager(self):
        pm = MagicMock()
        profile = MagicMock()
        profile.id = "p1"
        profile.name = "Test Profile"
        profile.outputs = {
            1: _FakeOutputCfg(input=1, enabled=True, hdcp_mode=3, hdr_mode=3,
                              scaler_mode=0, arc=False, audio_mute=False),
        }
        profile.macros = []
        profile.power_on_macro = None
        profile.power_off_macro = None
        profile.execution_log = []
        pm.get_profile.return_value = profile
        pm._save = MagicMock()
        pm.list_profiles.return_value = [profile]
        return pm

    @pytest.fixture
    def mock_system_action_manager(self):
        sam = MagicMock()
        sam.get_action.return_value = None
        return sam

    @pytest.fixture
    def executor(self, temp_dir, mock_profile_manager, mock_system_action_manager):
        scene_manager = SceneManager(data_dir=temp_dir)
        return SceneExecutor(
            scene_manager=scene_manager,
            profile_manager=mock_profile_manager,
            system_action_manager=mock_system_action_manager,
        ), scene_manager

    @pytest.mark.asyncio
    async def test_execute_scene_with_profile(self, executor):
        """Scene with profile step executes successfully."""
        ex, scene_manager = executor
        scene, _ = scene_manager.create_scene(
            name="Test",
            steps=[SceneStep(type=STEP_TYPE_PROFILE, id="p1")],
        )

        matrix = MagicMock()
        matrix.switch = AsyncMock(return_value=None)
        matrix.set_output_hdcp = AsyncMock(return_value=None)
        matrix.set_output_hdr = AsyncMock(return_value=None)
        matrix.set_output_scaler = AsyncMock(return_value=None)
        matrix.set_output_arc = AsyncMock(return_value=None)
        matrix.set_output_audio_mute = AsyncMock(return_value=None)

        result = await ex.execute_scene(scene.id, matrix)
        assert result.success is True
        assert result.steps_completed == 1
        assert result.total_steps == 1

    @pytest.mark.asyncio
    async def test_execute_scene_not_found(self, executor):
        """Executing nonexistent scene returns failure."""
        ex, _ = executor
        matrix = MagicMock()
        result = await ex.execute_scene("nonexistent", matrix)
        assert result.success is False
        assert "not found" in result.error.lower()


class TestSceneExecutorPassword:
    """Tests for SceneExecutor password protection."""

    @pytest.fixture
    def temp_dir(self):
        with tempfile.TemporaryDirectory() as d:
            yield Path(d)

    @pytest.fixture
    def executor(self, temp_dir):
        scene_manager = SceneManager(data_dir=temp_dir)
        pm = MagicMock()
        profile = MagicMock()
        profile.id = "p1"
        profile.outputs = {1: _FakeOutputCfg(input=1, enabled=True, hdcp_mode=3, hdr_mode=3, scaler_mode=0, arc=False, audio_mute=False)}
        profile.macros = []
        profile.execution_log = []
        pm.get_profile.return_value = profile
        pm._save = MagicMock()
        pm.list_profiles.return_value = [profile]
        sam = MagicMock()
        return SceneExecutor(
            scene_manager=scene_manager,
            profile_manager=pm,
            system_action_manager=sam,
        ), scene_manager

    @pytest.mark.asyncio
    async def test_protected_scene_requires_passcode(self, executor):
        """Protected scene without passcode returns passcode_required."""
        ex, scene_manager = executor
        scene, _ = scene_manager.create_scene(
            name="Protected",
            steps=[SceneStep(type=STEP_TYPE_PROFILE, id="p1")],
            password_protected=True,
            passcode="1234",
        )
        result = await ex.execute_scene(scene.id, MagicMock())
        assert result.success is False
        assert "passcode" in result.error.lower()

    @pytest.mark.asyncio
    async def test_protected_scene_wrong_passcode(self, executor):
        """Protected scene with wrong passcode returns invalid_passcode."""
        ex, scene_manager = executor
        scene, _ = scene_manager.create_scene(
            name="Protected",
            steps=[SceneStep(type=STEP_TYPE_PROFILE, id="p1")],
            password_protected=True,
            passcode="1234",
        )
        result = await ex.execute_scene(scene.id, MagicMock(), passcode="9999")
        assert result.success is False
        assert "passcode" in result.error.lower() or "invalid" in result.error.lower()

    @pytest.mark.asyncio
    async def test_protected_scene_correct_passcode(self, executor):
        """Protected scene with correct passcode executes."""
        ex, scene_manager = executor
        scene, _ = scene_manager.create_scene(
            name="Protected",
            steps=[SceneStep(type=STEP_TYPE_PROFILE, id="p1")],
            password_protected=True,
            passcode="1234",
        )
        matrix = MagicMock()
        matrix.switch = AsyncMock(return_value=None)
        matrix.set_output_hdcp = AsyncMock(return_value=None)
        matrix.set_output_hdr = AsyncMock(return_value=None)
        matrix.set_output_scaler = AsyncMock(return_value=None)
        matrix.set_output_arc = AsyncMock(return_value=None)
        matrix.set_output_audio_mute = AsyncMock(return_value=None)
        result = await ex.execute_scene(scene.id, matrix, passcode="1234")
        assert result.success is True

    @pytest.mark.asyncio
    async def test_unprotected_scene_no_passcode_needed(self, executor):
        """Unprotected scene executes without passcode."""
        ex, scene_manager = executor
        scene, _ = scene_manager.create_scene(
            name="Open",
            steps=[SceneStep(type=STEP_TYPE_PROFILE, id="p1")],
        )
        matrix = MagicMock()
        matrix.switch = AsyncMock(return_value=None)
        matrix.set_output_hdcp = AsyncMock(return_value=None)
        matrix.set_output_hdr = AsyncMock(return_value=None)
        matrix.set_output_scaler = AsyncMock(return_value=None)
        matrix.set_output_arc = AsyncMock(return_value=None)
        matrix.set_output_audio_mute = AsyncMock(return_value=None)
        result = await ex.execute_scene(scene.id, matrix)
        assert result.success is True


class TestSceneExecutorMacroStep:
    """Tests for SceneExecutor with macro steps."""

    @pytest.fixture
    def temp_dir(self):
        with tempfile.TemporaryDirectory() as d:
            yield Path(d)

    @pytest.fixture
    def mock_macro_manager(self):
        mm = MagicMock()
        macro = MagicMock()
        macro.steps = ["step1", "step2"]
        mm.get_macro.return_value = macro
        mm.execute_macro = AsyncMock(return_value={"success": True, "detail": "Done"})
        return mm

    @pytest.fixture
    def executor_with_macros(self, temp_dir, mock_macro_manager):
        scene_manager = SceneManager(data_dir=temp_dir)
        pm = MagicMock()
        profile = MagicMock()
        profile.id = "p1"
        profile.outputs = {1: MagicMock(input=1, enabled=True)}
        profile.macros = []
        profile.execution_log = []
        pm.get_profile.return_value = profile
        pm._save = MagicMock()
        pm.list_profiles.return_value = [profile]
        sam = MagicMock()
        sam.get_action.return_value = None
        executor = SceneExecutor(
            scene_manager=scene_manager,
            profile_manager=pm,
            system_action_manager=sam,
            macro_manager=mock_macro_manager,
        )
        return executor, scene_manager

    @pytest.mark.asyncio
    async def test_macro_step_executes(self, executor_with_macros):
        """Macro step is executed via macro_manager."""
        executor, scene_manager = executor_with_macros
        scene, _ = scene_manager.create_scene(
            name="With Macro",
            steps=[SceneStep(type=STEP_TYPE_MACRO, id="m1")],
        )
        result = await executor.execute_scene(scene.id, MagicMock())
        assert result.success is True
        assert result.steps_completed == 1

    @pytest.mark.asyncio
    async def test_macro_step_without_macro_manager(self, temp_dir):
        """Macro step without macro_manager returns failure."""
        scene_manager = SceneManager(data_dir=temp_dir)
        pm = MagicMock()
        pm.get_profile.return_value = None
        pm._save = MagicMock()
        sam = MagicMock()
        executor = SceneExecutor(
            scene_manager=scene_manager,
            profile_manager=pm,
            system_action_manager=sam,
            macro_manager=None,
        )
        scene, _ = scene_manager.create_scene(
            name="Test",
            steps=[SceneStep(type=STEP_TYPE_MACRO, id="m1")],
        )
        result = await executor.execute_scene(scene.id, MagicMock())
        assert result.success is False
        assert "macro manager" in result.error.lower()

    @pytest.mark.asyncio
    async def test_macro_not_found(self, executor_with_macros):
        """Macro step for nonexistent macro returns failure."""
        executor, scene_manager = executor_with_macros
        # Override get_macro to return None
        executor.macro_manager.get_macro.return_value = None
        scene, _ = scene_manager.create_scene(
            name="Test",
            steps=[SceneStep(type=STEP_TYPE_MACRO, id="nonexistent")],
        )
        result = await executor.execute_scene(scene.id, MagicMock())
        assert result.success is False
        assert "not found" in result.error.lower()


class TestStepResultDataclass:
    """Tests for StepResult dataclass."""

    def test_step_result_to_dict(self):
        """StepResult serializes to dict."""
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
        """ExecutionResult has sensible defaults."""
        r = ExecutionResult(
            scene_id="s1",
            success=True,
            steps_completed=1,
            total_steps=2,
        )
        assert r.step_results == []
        assert r.error is None