"""
Scene execution engine — applies Profiles, System Actions and CEC macros in order.

This module is responsible for:
1. Leaving the settings a scene overrides unchanged when it applies a Profile
2. Executing each step in a Scene in order, checking every matrix answer
3. Logging execution results to Profile.execution_log and Scene.execution_history
4. Emitting WebSocket events on errors
"""

import logging
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from typing import Any

from config import Profile, ProfileManager
from scene_manager import STEP_TYPE_MACRO, STEP_TYPE_PROFILE, STEP_TYPE_SYSTEM_ACTION, Scene, SceneManager
from system_shortcuts import (
    SystemShortcutManager as SystemActionManager,
)
from system_shortcuts import (
    execute_shortcut as execute_action,
)

_LOG = logging.getLogger("scene_execution")


@dataclass
class StepResult:
    """Result of executing a single step."""

    step_index: int
    step_type: str
    step_id: str
    success: bool
    detail: str = ""
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "step_index": self.step_index,
            "type": self.step_type,
            "id": self.step_id,
            "success": self.success,
            "detail": self.detail,
            "error": self.error,
        }


@dataclass
class ExecutionResult:
    """Result of executing an entire scene."""

    scene_id: str
    success: bool
    steps_completed: int
    total_steps: int
    step_results: list[StepResult] = field(default_factory=list)
    error: str | None = None  # Overall error if success=False

    def to_dict(self) -> dict[str, Any]:
        return {
            "scene_id": self.scene_id,
            "success": self.success,
            "steps_completed": self.steps_completed,
            "total_steps": self.total_steps,
            "step_results": [r.to_dict() for r in self.step_results],
            "error": self.error,
        }


# =============================================================================
# Overrides
# =============================================================================


def overridden_settings(scene: Scene, profile_id: str) -> dict[int, set[str]]:
    """
    The output settings a scene leaves unchanged when it runs ``profile_id``.

    A per-scene override means "leave this setting as it is on the matrix"
    (docs/PHASE_8_SPEC.md: apply each output setting *unless* it is overridden
    for this scene). Only keys whose override value is true count; an override
    stored as ``False`` is not active. API-04: overrides used to reset the
    setting to a default instead, so an ``input`` override routed Input 1.

    ``enabled`` can be overridden too, but the scene executor never changes an
    output's stream state, so there is nothing to leave unchanged for it.

    :returns: ``{output_num: {"input", "hdcp", ...}}``
    """
    skipped: dict[int, set[str]] = {}
    for output_num, settings in scene.get_overrides_for_profile(profile_id).items():
        keys = {key for key, disabled in settings.items() if disabled}
        if keys:
            skipped[output_num] = keys
    return skipped


# =============================================================================
# Profile execution helpers
# =============================================================================


async def _apply_output(matrix_device, output_num: int, output_cfg: Any, skip: set[str]) -> list[str]:
    """Apply one output of a profile; returns what the matrix did not accept (empty = all applied).

    Uses the real ``OreiMatrix`` methods and checks their result (API-01,
    API-08). HDR and scaler values are the hub's 1-based API values;
    ``OreiMatrix`` maps them to the device codes (``device_codes``).
    """
    failed: list[str] = []

    async def apply(what: str, call: Any) -> None:
        try:
            ok = await call
        except Exception as exc:  # noqa: BLE001 - one failed write must not stop the other outputs
            _LOG.error("Output %d %s failed: %s", output_num, what, exc)
            ok = False
        if not ok:
            failed.append(what)

    if "input" not in skip:
        await apply(f"route input {output_cfg.input}", matrix_device.switch_input(output_cfg.input, output_num))
    hdcp = getattr(output_cfg, "hdcp_mode", None)
    if hdcp is not None and "hdcp" not in skip:
        await apply(f"HDCP {hdcp}", matrix_device.set_output_hdcp(output_num, hdcp))
    hdr = getattr(output_cfg, "hdr_mode", None)
    if hdr is not None and "hdr" not in skip:
        await apply(f"HDR {hdr}", matrix_device.set_output_hdr(output_num, hdr))
    # Profiles do not store scaler/ARC yet (API-22); applied when present.
    scaler = getattr(output_cfg, "scaler_mode", None)
    if scaler is not None and "scaler" not in skip:
        await apply(f"scaler {scaler}", matrix_device.set_output_scaler(output_num, scaler))
    arc = getattr(output_cfg, "arc", None)
    if arc is not None and "arc" not in skip:
        await apply(f"ARC {'on' if arc else 'off'}", matrix_device.set_output_arc(output_num, bool(arc)))
    mute = getattr(output_cfg, "audio_mute", None)
    if mute is not None and "audio_mute" not in skip:
        await apply("mute" if mute else "unmute", matrix_device.set_output_audio_mute(output_num, bool(mute)))
    return failed


def _macro_error(outcome: dict[str, Any]) -> str:
    """A one-line reason from a ``MacroManager.execute_macro`` result."""
    if outcome.get("error"):
        return str(outcome["error"])
    errors = [err for step in outcome.get("results", []) for err in step.get("errors", [])]
    return "; ".join(errors) or "macro execution failed"


async def _execute_profile(
    profile: Profile,
    matrix_device,
    skip: dict[int, set[str]] | None = None,
    macro_manager: Any | None = None,
) -> StepResult:
    """
    Execute a single Profile against the matrix.

    Applies routing and per-output settings of every enabled output (outputs a
    profile marks disabled are not touched), then runs the profile's macros in
    order through the ``MacroManager`` (docs/PHASE_8_SPEC.md "Execute each
    macro in order"). Every matrix answer is checked: the step fails if
    anything was not applied, and the error names the output and the setting.

    :param profile: Profile to execute
    :param matrix_device: OreiMatrix instance
    :param skip: settings to leave unchanged per output (scene overrides, :func:`overridden_settings`)
    :param macro_manager: MacroManager that runs the profile's macros
    """
    skip = skip or {}
    problems: list[str] = []
    applied = 0
    try:
        for output_num in sorted(profile.outputs):
            output_cfg = profile.outputs[output_num]
            if not output_cfg.enabled:
                continue
            failed = await _apply_output(matrix_device, output_num, output_cfg, skip.get(output_num, set()))
            if failed:
                problems.append(f"output {output_num}: {', '.join(failed)} not applied")
            else:
                applied += 1

        # API-03: macros run through the MacroManager (targets like "output_1"),
        # which sends each step with the configured CEC sender (VAL-02).
        for macro_id in profile.macros:
            if macro_manager is None:
                problems.append(f"macro {macro_id}: macro manager not available")
                continue
            if macro_manager.get_macro(macro_id) is None:
                problems.append(f"macro {macro_id}: not found")
                continue
            outcome = await macro_manager.execute_macro(macro_id)
            if not outcome.get("success"):
                problems.append(f"macro {macro_id}: {_macro_error(outcome)}")
    except Exception as exc:  # noqa: BLE001 - reported as a failed step; the scene continues
        _LOG.error("Profile %s execution failed: %s", profile.id, exc)
        problems.append(str(exc))

    if problems:
        return StepResult(
            step_index=0,
            step_type=STEP_TYPE_PROFILE,
            step_id=profile.id,
            success=False,
            detail=f"Profile '{profile.name}': {applied} output(s) applied",
            error="; ".join(problems),
        )
    return StepResult(
        step_index=0,  # Will be overwritten by caller
        step_type=STEP_TYPE_PROFILE,
        step_id=profile.id,
        success=True,
        detail=f"Profile '{profile.name}' executed",
    )


# =============================================================================
# Scene executor
# =============================================================================


class SceneExecutor:
    """
    Executes Scenes with override handling, per-step results, error handling,
    and execution history logging.
    """

    def __init__(
        self,
        scene_manager: SceneManager,
        profile_manager: ProfileManager,
        system_action_manager: SystemActionManager,
        macro_manager: Any | None = None,
    ):
        self.scene_manager = scene_manager
        self.profile_manager = profile_manager
        self.system_action_manager = system_action_manager
        # MacroManager is optional — macro steps and profile macros fail without it
        self.macro_manager = macro_manager

    async def execute_scene(
        self,
        scene_id: str,
        matrix_device,
        passcode: str | None = None,
    ) -> ExecutionResult:
        """
        Execute a scene by ID.

        :param scene_id: Scene to execute
        :param matrix_device: OreiMatrix instance
        :param passcode: Plaintext passcode if the scene is password-protected
        :returns: ExecutionResult with per-step results
        """
        scene = self.scene_manager.get_scene(scene_id)
        if scene is None:
            return ExecutionResult(
                scene_id=scene_id,
                success=False,
                steps_completed=0,
                total_steps=0,
                error="Scene not found",
            )

        # Passcode check
        if scene.password_protected:
            if not passcode:
                return ExecutionResult(
                    scene_id=scene_id,
                    success=False,
                    steps_completed=0,
                    total_steps=len(scene.steps),
                    error="passcode_required",
                )
            if not self.scene_manager.verify_passcode(scene_id, passcode):
                return ExecutionResult(
                    scene_id=scene_id,
                    success=False,
                    steps_completed=0,
                    total_steps=len(scene.steps),
                    error="invalid_passcode",
                )

        step_results: list[StepResult] = []
        steps_completed = 0

        for i, step in enumerate(scene.steps):
            if step.type == STEP_TYPE_PROFILE:
                result = await self._execute_profile_step(step, matrix_device, scene)
            elif step.type == STEP_TYPE_SYSTEM_ACTION:
                result = await self._execute_system_action_step(step, matrix_device)
            elif step.type == STEP_TYPE_MACRO:
                result = await self._execute_macro_step(step, matrix_device)
            else:
                result = StepResult(
                    step_index=i,
                    step_type=step.type,
                    step_id=step.id,
                    success=False,
                    error=f"Unknown step type: {step.type}",
                )

            result.step_index = i
            step_results.append(result)
            if result.success:
                steps_completed += 1
            # Continue on error — do not abort

        # Determine overall success
        success = all(r.success for r in step_results)
        overall_error: str | None = None
        if not success:
            failed = [r for r in step_results if not r.success]
            overall_error = "; ".join(f"{r.step_id}: {r.error}" for r in failed)

        # Record in scene history
        scene.record_execution(
            status="success" if success else "error",
            steps_completed=steps_completed,
            error=overall_error,
        )
        self.scene_manager._save()

        # Emit WebSocket event on error
        if not success:
            await self._emit_error_event(scene, step_results, overall_error)

        return ExecutionResult(
            scene_id=scene_id,
            success=success,
            steps_completed=steps_completed,
            total_steps=len(scene.steps),
            step_results=step_results,
            error=overall_error,
        )

    async def _execute_profile_step(
        self,
        step: Any,  # SceneStep
        matrix_device,
        scene: Scene,
    ) -> StepResult:
        """Execute a single profile step, leaving the scene's overridden settings unchanged."""
        profile = self.profile_manager.get_profile(step.id)
        if profile is None:
            return StepResult(
                step_index=0,
                step_type=STEP_TYPE_PROFILE,
                step_id=step.id,
                success=False,
                error="Profile not found",
            )

        result = await _execute_profile(
            profile,
            matrix_device,
            skip=overridden_settings(scene, profile.id),
            macro_manager=self.macro_manager,
        )

        # Log to profile's execution history (API-02: persisted with the manager's save())
        now = datetime.now(UTC).isoformat()
        log_entry = {
            "timestamp": now,
            "scene_id": scene.id,
            "scene_name": scene.name,
            "status": "success" if result.success else "error",
            "error": result.error,
        }
        profile.execution_log.append(log_entry)
        profile.execution_log = _prune_profile_log(profile.execution_log)
        if not self.profile_manager.save():
            _LOG.warning("Could not save the execution log of profile %s", profile.id)

        return result

    async def _execute_system_action_step(
        self,
        step: Any,  # SceneStep
        matrix_device,
    ) -> StepResult:
        """Execute a single system action step."""
        action = self.system_action_manager.get_action(step.id)
        if action is None:
            return StepResult(
                step_index=0,
                step_type=STEP_TYPE_SYSTEM_ACTION,
                step_id=step.id,
                success=False,
                error=f"Unknown system action: {step.id}",
            )
        if not action.enabled:
            return StepResult(
                step_index=0,
                step_type=STEP_TYPE_SYSTEM_ACTION,
                step_id=step.id,
                success=False,
                error="System action is disabled",
            )

        result = await execute_action(action, matrix_device, step.params)
        return StepResult(
            step_index=0,
            step_type=STEP_TYPE_SYSTEM_ACTION,
            step_id=step.id,
            success=result.get("success", False),
            detail=result.get("detail", ""),
            error=None if result.get("success") else result.get("detail"),
        )

    async def _execute_macro_step(
        self,
        step: Any,  # SceneStep
        matrix_device,
    ) -> StepResult:
        """Execute a single CEC macro step."""
        if self.macro_manager is None:
            return StepResult(
                step_index=0,
                step_type=STEP_TYPE_MACRO,
                step_id=step.id,
                success=False,
                error="Macro manager not available",
            )

        # Check if macro exists
        macro = self.macro_manager.get_macro(step.id)
        if macro is None:
            return StepResult(
                step_index=0,
                step_type=STEP_TYPE_MACRO,
                step_id=step.id,
                success=False,
                error=f"Macro not found: {step.id}",
            )

        # Execute the macro
        result = await self.macro_manager.execute_macro(step.id)
        success = bool(result.get("success", False))
        return StepResult(
            step_index=0,
            step_type=STEP_TYPE_MACRO,
            step_id=step.id,
            success=success,
            detail=result.get("detail", f"Executed {len(macro.steps)} step(s)"),
            error=None if success else _macro_error(result),
        )

    async def _emit_error_event(
        self,
        scene: Scene,
        step_results: list[StepResult],
        overall_error: str | None,
    ) -> None:
        """Emit a WebSocket error event for scene execution failure."""
        try:
            from rest_api.websocket import broadcast_status_update

            await broadcast_status_update(
                "scene_execution_error",
                {
                    "scene_id": scene.id,
                    "scene_name": scene.name,
                    "steps_completed": sum(1 for r in step_results if r.success),
                    "total_steps": len(step_results),
                    "error": overall_error,
                },
            )
        except Exception as e:
            _LOG.error("Failed to emit scene execution error event: %s", e)


def _prune_profile_log(log: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Prune profile execution log to last 7 days."""
    cutoff_str = (datetime.now(UTC) - timedelta(days=7)).isoformat()
    return [e for e in log if e.get("timestamp", "") >= cutoff_str]
