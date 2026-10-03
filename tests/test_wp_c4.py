"""Regressions for DI-11/12 and VAL-07..10; effects are also validated at V3."""

from unittest.mock import AsyncMock, MagicMock, create_autospec

import pytest

from cec_macros import MacroManager
from config import ProfileManager
from orei_matrix import OreiMatrix
from scene_execution import SceneExecutor
from scene_manager import Scene, SceneManager, SceneStep, detect_conflicts
from system_shortcuts import SystemShortcutManager


async def test_scene_applies_disabled_stream_without_running_any_profile_macros(tmp_path):
    pm = ProfileManager(config_dir=str(tmp_path / "profiles"))
    pm.create_profile("p", "State", {1: {"input": 4, "enabled": False, "audio_mute": True}},
                      macros=["quick"], power_on_macro="on", power_off_macro="off")
    sm = SceneManager(data_dir=tmp_path / "scenes")
    scene, err = sm.create_scene("State", steps=[SceneStep("profile", "p")])
    assert err is None
    mm = MagicMock()
    mm.execute_macro = AsyncMock(return_value={"success": True})
    matrix = create_autospec(OreiMatrix, instance=True)
    result = await SceneExecutor(sm, pm, SystemShortcutManager(tmp_path / "sc"), mm).execute_scene(scene.id, matrix)
    assert result.success
    matrix.switch_input.assert_awaited_once_with(4, 1)
    matrix.set_output_enable.assert_awaited_once_with(1, False)
    matrix.set_output_audio_mute.assert_awaited_once_with(1, True)
    mm.execute_macro.assert_not_awaited()


async def test_wait_runs_between_actions_and_is_cancellable(tmp_path, monkeypatch):
    import asyncio

    sm = SceneManager(data_dir=tmp_path / "scenes")
    scene, err = sm.create_scene("Wait", steps=[SceneStep("wait", "", {"seconds": 0.5})])
    assert err is None
    sleeper = AsyncMock(side_effect=asyncio.CancelledError)
    monkeypatch.setattr("scene_execution.asyncio.sleep", sleeper)
    executor = SceneExecutor(sm, ProfileManager(config_dir=str(tmp_path / "p")),
                             SystemShortcutManager(tmp_path / "sc"))
    with pytest.raises(asyncio.CancelledError):
        await executor.execute_scene(scene.id, create_autospec(OreiMatrix, instance=True))
    sleeper.assert_awaited_once_with(0.5)
    assert scene.execution_history == []


@pytest.mark.parametrize("seconds", [0.5, 1, 30])
def test_wait_accepts_bounded_duration(seconds):
    step = SceneStep("wait", "", {"seconds": seconds})
    assert step.validate() is None
    assert SceneStep.from_dict(step.to_dict()) == step


@pytest.mark.parametrize("seconds", [None, True, "1", 0, 0.49, 30.1, float("nan"), float("inf"), 10**1000])
def test_wait_rejects_invalid_duration(seconds):
    assert SceneStep("wait", "", {"seconds": seconds}).validate() is not None


async def test_macro_uses_its_saved_continue_policy_and_explicit_override(tmp_path):
    mm = MacroManager(config_dir=str(tmp_path))
    macro = mm.create_macro("Continue", macro_id="m", steps=[
        {"command": "POWER_OFF", "targets": ["output_1"]},
        {"command": "POWER_OFF", "targets": ["output_2"]},
    ])
    macro.continue_on_error = True
    mm.save()
    mm = MacroManager(config_dir=str(tmp_path))
    sender = AsyncMock(side_effect=[False, True])
    mm.set_cec_sender(sender)
    outcome = await mm.execute_macro("m")
    assert outcome["success"] is False
    assert outcome["steps_executed"] == 2
    assert sender.await_count == 2
    sender.reset_mock(side_effect=True)
    sender.side_effect = [False, True]
    outcome = await mm.execute_macro("m", continue_on_error=False)
    assert outcome["halted_at_step"] == 1
    assert sender.await_count == 1


def test_conflicts_report_every_applied_value_including_defaults_and_disabled_outputs(tmp_path):
    pm = ProfileManager(config_dir=str(tmp_path))
    first = pm.create_profile("a", "First", {1: {"input": 4, "enabled": False, "hdr_mode": 1}})
    second = pm.create_profile("b", "Second", {1: {"input": 1, "enabled": True, "hdr_mode": 3}})
    scene = Scene("s", "Conflicts", steps=[SceneStep("profile", "a"), SceneStep("profile", "b")])
    conflicts = {c.setting_key: c.to_dict() for c in detect_conflicts(scene, {"a": first, "b": second})}
    assert set(conflicts) == {"input", "enabled", "hdr"}
    assert conflicts["input"]["profiles"] == [
        {"id": "a", "name": "First", "value": 4}, {"id": "b", "name": "Second", "value": 1},
    ]
    scene.overrides = {"a": {1: {"input": True, "enabled": True, "hdr": True}}}
    assert detect_conflicts(scene, {"a": first, "b": second}) == []
