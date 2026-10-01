"""
Scene execution engine — applies Profiles, System Actions and CEC macros in order.

This module is responsible for:
1. Leaving the settings a scene overrides unchanged when it applies a Profile
2. Executing each step in a Scene in order, checking every matrix answer
3. Logging execution results to Profile.execution_log and Scene.execution_history
4. Emitting WebSocket events on errors
"""

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from typing import Any

from config import Profile, ProfileManager
from profile_execution import apply_profile_state
from scene_manager import (
    STEP_TYPE_MACRO,
    STEP_TYPE_PROFILE,
    STEP_TYPE_SYSTEM_ACTION,
    STEP_TYPE_WAIT,
    Scene,
    SceneManager,
)
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
) -> StepResult:
    """Apply recall's exact state with scene overrides, without any macros (DI-11)."""
    outcome = await apply_profile_state(profile, matrix_device, skip)
    return StepResult(
        step_index=0,
        step_type=STEP_TYPE_PROFILE,
        step_id=profile.id,
        success=not outcome.errors,
        detail=f"Profile '{profile.name}': {len(outcome.applied)} output(s) applied",
        error="; ".join(outcome.errors) if outcome.errors else None,
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
        # MacroManager is optional — scene macro steps fail without it
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
            elif step.type == STEP_TYPE_WAIT:
                error = step.validate()
                if error is None:
                    await asyncio.sleep(step.params["seconds"])
                result = StepResult(
                    step_index=i, step_type=STEP_TYPE_WAIT, step_id=step.id,
                    success=error is None, detail=f"Waited {step.params.get('seconds')} seconds" if error is None else "",
                    error=error,
                )
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
