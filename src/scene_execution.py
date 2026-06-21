"""
Scene execution engine — applies Profiles and System Actions in order.

This module is responsible for:
1. Applying per-scene overrides to a Profile before execution
2. Executing each step in a Scene in order
3. Logging execution results to Profile.execution_log and Scene.execution_history
4. Emitting WebSocket events on errors
"""

import logging
from dataclasses import dataclass, field
from datetime import UTC, datetime, timezone
from typing import Any

from config import Profile, ProfileManager
from scene_manager import STEP_TYPE_MACRO, STEP_TYPE_PROFILE, STEP_TYPE_SYSTEM_ACTION, Scene, SceneManager
from system_shortcuts import (
    SystemShortcut as SystemAction,
)
from system_shortcuts import (
    SystemShortcutManager as SystemActionManager,
)
from system_shortcuts import (
    execute_shortcut as execute_action,
)

_LOG = logging.getLogger("scene_execution")


# Default output settings (must match OreiMatrix / Profile defaults)
_DEFAULT_OUTPUT_SETTINGS = {
    "input": 1,
    "enabled": True,
    "hdcp": 3,
    "hdr": 3,
    "scaler": 0,
    "arc": False,
    "audio_mute": False,
}


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
# Override application
# =============================================================================


def apply_overrides_to_profile(
    profile: Profile,
    scene: Scene,
) -> Profile:
    """
    Return a copy of the profile with per-scene overrides applied.

    The original profile object is never modified.
    Overrides are applied by setting overridden settings to their defaults
    (so the matrix is left unchanged for those settings).
    """
    import copy

    overrides = scene.get_overrides_for_profile(profile.id)
    if not overrides:
        return profile

    # Deep copy the profile so we can mutate it
    overridden_profile: Profile = copy.deepcopy(profile)

    for output_num, disabled_settings in overrides.items():
        if output_num not in overridden_profile.outputs:
            continue
        output_cfg = overridden_profile.outputs[output_num]
        for setting_key in disabled_settings:
            # Set to default so the matrix command skips it
            if setting_key == "input":
                output_cfg.input = _DEFAULT_OUTPUT_SETTINGS["input"]
            elif setting_key == "enabled":
                output_cfg.enabled = _DEFAULT_OUTPUT_SETTINGS["enabled"]
            elif setting_key == "hdcp":
                output_cfg.hdcp_mode = _DEFAULT_OUTPUT_SETTINGS["hdcp"]
            elif setting_key == "hdr":
                output_cfg.hdr_mode = _DEFAULT_OUTPUT_SETTINGS["hdr"]
            elif setting_key == "scaler":
                output_cfg.scaler_mode = _DEFAULT_OUTPUT_SETTINGS["scaler"]
            elif setting_key == "arc":
                output_cfg.arc = _DEFAULT_OUTPUT_SETTINGS["arc"]
            elif setting_key == "audio_mute":
                output_cfg.audio_mute = _DEFAULT_OUTPUT_SETTINGS["audio_mute"]

    return overridden_profile


# =============================================================================
# Profile execution helpers
# =============================================================================


async def _execute_profile(
    profile: Profile,
    matrix_device,
    scene: Scene | None = None,
) -> StepResult:
    """
    Execute a single Profile against the matrix.

    Applies routing, per-output settings, then macro sequence.

    :param profile: Profile to execute
    :param matrix_device: OreiMatrix instance
    :param scene: Scene this profile is being executed within (for logging)
    """
    try:
        # Step 1: Apply routing for each output
        for output_num, output_cfg in profile.outputs.items():
            if not output_cfg.enabled:
                continue
            # Route input to output
            await matrix_device.switch(output_cfg.input, output_num)

        # Step 2: Apply per-output settings
        for output_num, output_cfg in profile.outputs.items():
            if not output_cfg.enabled:
                continue
            # HDCP
            if getattr(output_cfg, "hdcp_mode", None) is not None:
                await matrix_device.set_output_hdcp(output_num, output_cfg.hdcp_mode)
            # HDR
            if getattr(output_cfg, "hdr_mode", None) is not None:
                await matrix_device.set_output_hdr(output_num, output_cfg.hdr_mode)
            # Scaler
            if getattr(output_cfg, "scaler_mode", None) is not None:
                await matrix_device.set_output_scaler(output_num, output_cfg.scaler_mode)
            # ARC
            if hasattr(output_cfg, "arc") and output_cfg.arc is not None:
                await matrix_device.set_output_arc(output_num, output_cfg.arc)
            # Audio mute
            if hasattr(output_cfg, "audio_mute") and output_cfg.audio_mute is not None:
                await matrix_device.set_output_audio_mute(output_num, output_cfg.audio_mute)

        # Step 3: Execute CEC macros (CEC commands)
        # Note: macros is a list of macro IDs — look up and execute each
        # For now, we handle direct CEC commands embedded in the profile
        # (the profile.macros field contains macro_id strings)
        # We look up via macro_manager if available
        from rest_api.utils import get_macro_manager

        macro_mgr = get_macro_manager()
        for macro_id in profile.macros:
            if macro_mgr is not None:
                macro = macro_mgr.get_macro(macro_id)
                if macro is not None:
                    for step in macro.steps:
                        # Execute each macro step via the matrix
                        cmd = step.get("command", "")
                        params = step.get("params", {})
                        cec_target = params.get("target")
                        if cmd and cec_target:
                            await _send_cec_command(matrix_device, cmd, cec_target, params)

        detail = f"Profile '{profile.name}' executed"
        return StepResult(
            step_index=0,  # Will be overwritten by caller
            step_type=STEP_TYPE_PROFILE,
            step_id=profile.id,
            success=True,
            detail=detail,
        )

    except Exception as exc:
        _LOG.error("Profile %s execution failed: %s", profile.id, exc)
        return StepResult(
            step_index=0,
            step_type=STEP_TYPE_PROFILE,
            step_id=profile.id,
            success=False,
            error=str(exc),
        )


async def _send_cec_command(matrix_device, command: str, target: str, params: dict[str, Any]) -> bool:
    """Send a single CEC command to the matrix."""
    try:
        # Parse target: "input:3", "output:1", "all_inputs"
        if target.startswith("input:"):
            port = int(target.split(":")[1])
            cec_method = _get_input_cec_method(matrix_device, command)
            if cec_method:
                return await cec_method(port)
        elif target.startswith("output:"):
            port = int(target.split(":")[1])
            cec_method = _get_output_cec_method(matrix_device, command)
            if cec_method:
                return await cec_method(port)
        elif target == "all_inputs":
            for n in range(1, 9):
                cec_method = _get_input_cec_method(matrix_device, command)
                if cec_method:
                    await cec_method(n)
        elif target == "all_outputs":
            for n in range(1, 9):
                cec_method = _get_output_cec_method(matrix_device, command)
                if cec_method:
                    await cec_method(n)
        return True
    except Exception as e:
        _LOG.error("CEC command %s to %s failed: %s", command, target, e)
        return False


def _get_input_cec_method(matrix_device, command: str):
    """Return the appropriate input CEC method for a command."""
    mapping = {
        "power_on": "cec_input_power_on",
        "power_off": "cec_input_power_off",
        "up": "cec_input_up",
        "down": "cec_input_down",
        "left": "cec_input_left",
        "right": "cec_input_right",
        "select": "cec_input_select",
        "menu": "cec_input_menu",
        "back": "cec_input_back",
        "play": "cec_input_play",
        "pause": "cec_input_pause",
        "stop": "cec_input_stop",
        "previous": "cec_input_previous",
        "next": "cec_input_next",
        "rewind": "cec_input_rewind",
        "fast_forward": "cec_input_fast_forward",
        "volume_up": "cec_input_volume_up",
        "volume_down": "cec_input_volume_down",
        "mute": "cec_input_mute",
    }
    method_name = mapping.get(command.lower())
    if method_name:
        return getattr(matrix_device, method_name, None)
    return None


def _get_output_cec_method(matrix_device, command: str):
    """Return the appropriate output CEC method for a command."""
    mapping = {
        "power_on": "cec_output_power_on",
        "power_off": "cec_output_power_off",
        "volume_up": "cec_output_volume_up",
        "volume_down": "cec_output_volume_down",
        "mute": "cec_output_mute",
    }
    method_name = mapping.get(command.lower())
    if method_name:
        return getattr(matrix_device, method_name, None)
    return None


# =============================================================================
# Scene executor
# =============================================================================


class SceneExecutor:
    """
    Executes Scenes with full override application, conflict resolution,
    error handling, and execution history logging.
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
        # MacroManager is optional — scene can include macro steps only if provided
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
            result: StepResult | None = None

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

            if result:
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
        """Execute a single profile step with overrides applied."""
        profile = self.profile_manager.get_profile(step.id)
        if profile is None:
            return StepResult(
                step_index=0,
                step_type=STEP_TYPE_PROFILE,
                step_id=step.id,
                success=False,
                error="Profile not found",
            )

        # Apply per-scene overrides
        overridden_profile = apply_overrides_to_profile(profile, scene)

        # Execute
        result = await _execute_profile(overridden_profile, matrix_device, scene)

        # Log to profile's execution history
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
        self.profile_manager._save()

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
        success = result.get("success", False)
        return StepResult(
            step_index=0,
            step_type=STEP_TYPE_MACRO,
            step_id=step.id,
            success=success,
            detail=result.get("detail", f"Executed {len(macro.steps)} step(s)"),
            error=None if success else result.get("error", "Macro execution failed"),
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
    cutoff = datetime.now(UTC) - __import__("datetime").timedelta(days=7)
    cutoff_str = cutoff.isoformat()
    return [e for e in log if e.get("timestamp", "") >= cutoff_str]
