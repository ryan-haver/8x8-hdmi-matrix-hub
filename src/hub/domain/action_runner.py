"""One executor for every action the hub can run (API-19, WP-C3).

Recall, scene runs, macro runs, shortcut runs and hardware preset recalls each
had their own path from the REST layer down to the matrix, and each reported
what happened differently: a status code here, an ``applied`` list there, a
free-text error string everywhere else. :class:`ActionRunner` is the one place
an action is run and normalised, so every surface (REST, WebSocket, the
Unfolded Circle integration) answers with the same structure.

A run always returns an :class:`ActionRunResult`, whose ``status_code`` says
what happened:

===========  ========  ==================================================
outcome      status    meaning
===========  ========  ==================================================
full success  200       every step was applied
partial       207       some steps were, ``success`` is False
nothing       500       no step was applied
refused       403       ``passcode_required`` / ``invalid_passcode``
locked out    429       too many wrong passcodes (SEC-06)
unknown       404       no such profile / scene / macro / shortcut / preset
bad request   400       unknown kind, or a shortcut that is disabled
not ready     503       the manager or matrix this kind needs is absent
===========  ========  ==================================================

Each kind is executed by the manager that already owns it, so this class owns
no matrix logic of its own: the profile path is the shared ``apply_profile_state``
writer (DI-11), the scene path is :class:`scene_execution.SceneExecutor`, macros
are run by ``MacroManager``, shortcuts by ``execute_shortcut`` and presets by
the matrix. A kind can also be handed its own runner with ``register()``.
"""

from __future__ import annotations

import inspect
import logging
import math
from collections.abc import Awaitable, Callable, Mapping
from dataclasses import dataclass, field
from typing import Any

from hub.core.errors import safe_action_error
from hub.core.matrix_service import MatrixService
from password import attempt_pin, check_pin_lockout, verify_passcode_async
from profile_execution import apply_profile_state
from system_shortcuts import execute_shortcut

_LOG = logging.getLogger(__name__)

#: The kinds of action ActionRunner executes.
ACTION_KINDS: tuple[str, ...] = ("profile", "scene", "macro", "shortcut", "preset")

STATUS_OK = 200
STATUS_PARTIAL = 207
STATUS_BAD_REQUEST = 400
STATUS_FORBIDDEN = 403
STATUS_NOT_FOUND = 404
STATUS_FAILED = 500
STATUS_LOCKED = 429
STATUS_UNAVAILABLE = 503

# The refusal codes the REST layer already publishes (SEC-04 / SEC-05 / SEC-06).
PASSCODE_REQUIRED = "passcode_required"
INVALID_PASSCODE = "invalid_passcode"
PASSCODE_LOCKED = "passcode_locked"

#: The matrix has eight hardware preset slots; anything else does not exist.
PRESET_SLOTS = 8

#: ``SceneExecutor`` refuses a run with one of these in its ``error``.
_PASSCODE_ERRORS = (PASSCODE_REQUIRED, INVALID_PASSCODE)


@dataclass
class StepResult:
    """One step of an action run: what it was, and whether the hub applied it."""

    step_index: int
    action: str
    success: bool
    error: str | None = None
    data: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        """The step as a client sees it."""
        return {
            "step_index": self.step_index,
            "action": self.action,
            "success": self.success,
            "error": self.error,
            "data": self.data,
        }


@dataclass
class ActionRunResult:
    """
    The normalised outcome of running one action.

    ``steps_completed`` of ``total_steps`` says how much of the action the
    matrix accepted, ``partial`` says whether that is worth retrying by hand
    (207) or whether nothing happened at all (500).
    """

    kind: str
    action_id: str
    success: bool
    partial: bool
    status_code: int
    steps_completed: int = 0
    total_steps: int = 0
    step_results: list[StepResult] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    data: dict[str, Any] = field(default_factory=dict)

    @property
    def error(self) -> str | None:
        """The one-line reason of a failed run, or None when it succeeded."""
        return "; ".join(self.errors) if self.errors else None

    @property
    def code(self) -> str | None:
        """The machine-readable reason of a refusal (``passcode_required``, ...)."""
        value = self.data.get("code")
        return str(value) if value else None

    def to_response_dict(self) -> dict[str, Any]:
        """The hub's response envelope (``{"success", "data", "error"}``) for this run."""
        return {
            "success": self.success,
            "data": {
                "kind": self.kind,
                "id": self.action_id,
                "partial": self.partial,
                "status_code": self.status_code,
                "steps_completed": self.steps_completed,
                "total_steps": self.total_steps,
                "step_results": [step.to_dict() for step in self.step_results],
                "errors": list(self.errors),
                "result": dict(self.data),
            },
            "error": self.error,
        }


# =============================================================================
# Result helpers
# =============================================================================


def _status(success: bool, steps_completed: int) -> int:
    """API-08: 200 everything applied, 207 some of it, 500 none of it."""
    if success:
        return STATUS_OK
    return STATUS_PARTIAL if steps_completed > 0 else STATUS_FAILED


def _result(
    kind: str,
    action_id: str,
    *,
    success: bool,
    partial: bool,
    status_code: int,
    step_results: list[StepResult] | None = None,
    errors: list[str] | None = None,
    data: dict[str, Any] | None = None,
) -> ActionRunResult:
    """Build a result and count its steps, so the counts never disagree."""
    steps = list(step_results or [])
    completed = sum(1 for step in steps if step.success)
    return ActionRunResult(
        kind=kind,
        action_id=action_id,
        success=success,
        partial=partial,
        status_code=status_code,
        steps_completed=completed,
        total_steps=len(steps),
        step_results=steps,
        errors=list(errors or []),
        data=dict(data or {}),
    )


def _from_steps(
    kind: str,
    action_id: str,
    steps: list[StepResult],
    errors: list[str],
    data: dict[str, Any] | None = None,
) -> ActionRunResult:
    """A result built from its steps: any error means not successful."""
    completed = sum(1 for step in steps if step.success)
    success = not errors
    return _result(
        kind,
        action_id,
        success=success,
        partial=not success and completed > 0,
        status_code=_status(success, completed),
        step_results=steps,
        errors=errors,
        data=data,
    )


def _not_found(kind: str, action_id: str) -> ActionRunResult:
    """404: the hub has no such action."""
    return _result(
        kind,
        action_id,
        success=False,
        partial=False,
        status_code=STATUS_NOT_FOUND,
        errors=[f"{kind.capitalize()} '{action_id}' not found"],
        data={"code": "not_found", "id": action_id},
    )


def _bad_request(kind: str, action_id: str, message: str, code: str = "bad_request") -> ActionRunResult:
    """400: the request itself cannot be run."""
    return _result(
        kind,
        action_id,
        success=False,
        partial=False,
        status_code=STATUS_BAD_REQUEST,
        errors=[message],
        data={"code": code, "id": action_id},
    )


def _unavailable(kind: str, action_id: str, message: str) -> ActionRunResult:
    """503: this kind needs a manager or a matrix that is not there."""
    return _result(
        kind,
        action_id,
        success=False,
        partial=False,
        status_code=STATUS_UNAVAILABLE,
        errors=[message],
        data={"code": "not_configured", "id": action_id},
    )


def _refused(kind: str, action_id: str, code: str) -> ActionRunResult:
    """403: a protected action without the right passcode (SEC-04 / SEC-05)."""
    return _result(
        kind,
        action_id,
        success=False,
        partial=False,
        status_code=STATUS_FORBIDDEN,
        errors=[code],
        data={"code": code, "id": action_id, "requires_passcode": True},
    )


def _locked(kind: str, action_id: str, retry_after: float) -> ActionRunResult:
    """429: too many wrong passcodes for this action (SEC-06 / F-SEC-007)."""
    seconds = max(1, math.ceil(retry_after))
    return _result(
        kind,
        action_id,
        success=False,
        partial=False,
        status_code=STATUS_LOCKED,
        errors=[PASSCODE_LOCKED],
        data={"code": PASSCODE_LOCKED, "id": action_id, "retry_after": seconds},
    )


def _coerce(kind: str, action_id: str, raw: Any) -> ActionRunResult:
    """Normalise what a registered executor returned into an ActionRunResult.

    Executors may return an :class:`ActionRunResult` or a mapping with the same
    fields; anything else is a bug in the executor and becomes a 500.
    """
    if isinstance(raw, ActionRunResult):
        return raw
    if not isinstance(raw, Mapping):
        raise TypeError(f"{kind} executor returned {type(raw).__name__}, not an ActionRunResult")
    steps = []
    for step in raw.get("step_results") or []:
        steps.append(step if isinstance(step, StepResult) else StepResult(**_only_fields(step, StepResult)))
    errors = [str(error) for error in raw.get("errors") or []]
    success = bool(raw.get("success", not errors))
    completed = raw.get("steps_completed")
    completed = sum(1 for step in steps if step.success) if completed is None else int(completed)
    partial = bool(raw.get("partial", not success and completed > 0))
    status = raw.get("status_code")
    return ActionRunResult(
        kind=str(raw.get("kind") or kind),
        action_id=str(raw.get("action_id") or action_id),
        success=success,
        partial=partial,
        status_code=int(status) if status else _status(success, completed),
        steps_completed=completed,
        total_steps=int(raw.get("total_steps", len(steps))),
        step_results=steps,
        errors=errors,
        data=dict(raw.get("data") or {}),
    )


def _only_fields(mapping: Mapping[str, Any], cls: type) -> dict[str, Any]:
    """The dataclass fields of ``cls`` present in ``mapping``."""
    names = getattr(cls, "__dataclass_fields__", {})
    return {name: mapping[name] for name in names if name in mapping}


async def _resolve(value: Any) -> Any:
    """Await ``value`` when the call it came from was async; a runner may be either."""
    return await value if inspect.isawaitable(value) else value


# =============================================================================
# Passcodes (SEC-06)
# =============================================================================


def _pin_key(kind: str, action_id: str) -> str:
    """The attempt-limiter key of an action; the same one the REST layer uses."""
    return f"{kind}:{action_id}"


async def _passcode_refusal(
    kind: str,
    action_id: str,
    passcode: Any,
    verify: Callable[[], Awaitable[bool]],
) -> ActionRunResult | None:
    """
    Check a passcode under the attempt limiter, PBKDF2 off the event loop.

    Returns None when the action may run, else the 403/429 to answer with.
    """
    key = _pin_key(kind, action_id)
    retry_after = check_pin_lockout(key)
    if retry_after > 0:
        return _locked(kind, action_id, retry_after)
    if passcode in (None, ""):
        return _refused(kind, action_id, PASSCODE_REQUIRED)
    attempt = await attempt_pin(key, verify)
    if attempt.locked:
        return _locked(kind, action_id, attempt.retry_after)
    if not attempt.ok:
        _LOG.warning("Wrong passcode for %s '%s'", kind, action_id)
        return _refused(kind, action_id, INVALID_PASSCODE)
    return None


def _macro_errors(outcome: Mapping[str, Any]) -> list[str]:
    """The reasons a ``MacroManager.execute_macro`` outcome failed."""
    if outcome.get("error"):
        return [str(outcome["error"])]
    errors = [str(error) for step in outcome.get("results") or [] for error in step.get("errors") or []]
    if errors:
        return errors
    halted = outcome.get("halted_at_step")
    return [f"Macro execution halted at step {halted}"] if halted else ["Macro execution failed"]


def _output_error(errors: list[str], output_num: int) -> str | None:
    """The ``apply_profile_state`` error of one output (``output 3: ...``)."""
    prefix = f"output {output_num}:"
    return next((error for error in errors if error.startswith(prefix)), None)


# =============================================================================
# ActionRunner
# =============================================================================


class ActionRunner:
    """
    The single executor for profiles, scenes, macros, shortcuts and presets.

    The managers are the ones the hub already owns; anything left out is only
    needed by the kinds that use it, so a runner without a macro manager can
    still recall profiles that have no power-on macro. ``from_runtime()``
    builds one from the running hub's managers.
    """

    def __init__(
        self,
        matrix_device: Any = None,
        *,
        profile_manager: Any = None,
        scene_manager: Any = None,
        macro_manager: Any = None,
        shortcut_manager: Any = None,
        profile_executor: Any = None,
        scene_executor: Any = None,
        macro_executor: Any = None,
        shortcut_executor: Any = None,
        preset_executor: Any = None,
    ) -> None:
        """
        :param matrix_device: the ``OreiMatrix`` instance actions are applied to
        :param profile_manager: ``ProfileManager`` (profiles)
        :param scene_manager: ``SceneManager`` (scenes)
        :param macro_manager: ``MacroManager`` (macros, profile power-on macros)
        :param shortcut_manager: ``SystemShortcutManager`` (shortcuts, scene steps)
        :param preset_executor: recalls presets; the matrix device by default
        :param profile_executor: a runner for the ``profile`` kind (see ``register``)
        :param scene_executor: a runner for the ``scene`` kind
        :param macro_executor: a runner for the ``macro`` kind
        :param shortcut_executor: a runner for the ``shortcut`` kind
        """
        self.matrix_device = matrix_device
        self.profile_manager = profile_manager
        self.scene_manager = scene_manager
        self.macro_manager = macro_manager
        self.shortcut_manager = shortcut_manager
        self.preset_executor = preset_executor
        self._executors: dict[str, Any] = {
            "profile": profile_executor,
            "scene": scene_executor,
            "macro": macro_executor,
            "shortcut": shortcut_executor,
        }

    @classmethod
    def from_runtime(cls, matrix_device: Any = None) -> ActionRunner:
        """A runner bound to the managers the running hub already holds."""
        from rest_api.scenes_v2 import _phase8_scene_manager
        from rest_api.utils import (
            get_macro_manager,
            get_matrix_device,
            get_profile_manager,
            get_system_shortcut_manager,
        )

        return cls(
            matrix_device if matrix_device is not None else get_matrix_device(),
            profile_manager=get_profile_manager(),
            scene_manager=_phase8_scene_manager,
            macro_manager=get_macro_manager(),
            shortcut_manager=get_system_shortcut_manager(),
        )

    @property
    def kinds(self) -> tuple[str, ...]:
        """The action kinds this runner can execute."""
        return ACTION_KINDS

    def register(self, kind: str, executor: Any) -> None:
        """
        Hand one kind to its own runner (a callable, or an object with
        ``run_action``), called as ``executor(action_id, passcode=...,
        params=...)`` and awaited when it returns an awaitable. It returns an
        :class:`ActionRunResult` (or a mapping with the same fields).
        """
        normalized = _normalize_kind(kind)
        if normalized not in ACTION_KINDS:
            raise ValueError(f"Unknown action kind: {kind!r}")
        self._executors[normalized] = executor

    async def run(
        self,
        kind: str,
        action_id: str,
        *,
        passcode: str | None = None,
        params: dict[str, Any] | None = None,
    ) -> ActionRunResult:
        """
        Run one action and report what happened, never raising.

        :param kind: ``profile``, ``scene``, ``macro``, ``shortcut`` or ``preset``
        :param action_id: the id, key or preset number to run
        :param passcode: plaintext passcode of a protected profile or scene
        :param params: extra arguments of the action (macro timeout, shortcut
                       routing parameters, ...)
        """
        normalized = _normalize_kind(kind)
        action_id = str(action_id)
        if normalized is None or normalized not in ACTION_KINDS:
            _LOG.warning("Refusing to run unknown action kind '%s'", kind)
            return _bad_request(str(kind), action_id, f"Unsupported action kind: {kind}", code="unknown_kind")

        executor = self._executors.get(normalized)
        if executor is not None:
            return await self._delegate(normalized, action_id, executor, passcode=passcode, params=params or {})

        try:
            return await _RUNNERS[normalized](self, action_id, passcode, params or {})
        except Exception as exc:
            # One place catches what an action did wrong, so no surface has to.
            message, error_id = safe_action_error(exc, f"{normalized} '{action_id}' failed", logger=_LOG)
            return _result(
                normalized,
                action_id,
                success=False,
                partial=False,
                status_code=STATUS_FAILED,
                errors=[message],
                data={"code": "execution_error", "id": action_id, "error_id": error_id},
            )

    async def _delegate(
        self,
        kind: str,
        action_id: str,
        executor: Any,
        *,
        passcode: str | None,
        params: dict[str, Any],
    ) -> ActionRunResult:
        """Run one kind through its registered executor."""
        try:
            call = getattr(executor, "run_action", executor)
            return _coerce(kind, action_id, await _resolve(call(action_id, passcode=passcode, params=params)))
        except Exception as exc:
            message, error_id = safe_action_error(exc, f"{kind} executor failed for '{action_id}'", logger=_LOG)
            return _result(
                kind,
                action_id,
                success=False,
                partial=False,
                status_code=STATUS_FAILED,
                errors=[message],
                data={"code": "execution_error", "id": action_id, "error_id": error_id},
            )

    # ---- profiles -----------------------------------------------------------

    async def _run_profile(
        self, action_id: str, passcode: str | None, params: dict[str, Any]
    ) -> ActionRunResult:
        """Recall a profile: its power-on macro, then the shared state writer (DI-11)."""
        manager = self.profile_manager
        if manager is None:
            return _unavailable("profile", action_id, "Profile manager not initialized")

        profile = manager.get_profile(action_id)
        if profile is None:
            return _not_found("profile", action_id)

        if profile.is_password_protected():
            denied = await _passcode_refusal(
                "profile",
                action_id,
                passcode,
                lambda: verify_passcode_async(passcode, profile.passcode_hash),
            )
            if denied is not None:
                return denied

        matrix = self.matrix_device
        if matrix is None:
            return _unavailable("profile", action_id, "Matrix device not configured")

        steps: list[StepResult] = []
        errors: list[str] = []
        power_on_macro: dict[str, Any] | None = None

        if profile.power_on_macro:
            step, power_on_macro, macro_errors = await self._run_power_on_macro(profile.power_on_macro)
            steps.append(step)
            errors.extend(macro_errors)

        state = await apply_profile_state(profile, matrix)
        errors.extend(state.errors)
        failed_outputs = set(state.failed_outputs)
        for output_num, config in sorted(profile.outputs.items()):
            applied = output_num not in failed_outputs
            steps.append(
                StepResult(
                    step_index=len(steps),
                    action=f"output:{output_num}",
                    success=applied,
                    error=None if applied else _output_error(state.errors, output_num),
                    data={"output": output_num, "input": config.input, "enabled": config.enabled},
                )
            )

        return _from_steps(
            "profile",
            action_id,
            steps,
            errors,
            {
                "profile": profile.name,
                "applied": state.applied,
                "failed_outputs": state.failed_outputs,
                "power_on_macro": power_on_macro,
            },
        )

    async def _run_power_on_macro(self, macro_id: str) -> tuple[StepResult, dict[str, Any] | None, list[str]]:
        """A profile's power-on macro as one step, with the reason it failed."""
        manager = self.macro_manager
        if manager is None or manager.get_macro(macro_id) is None:
            outcome = {"success": False, "error": f"Macro not found: {macro_id}"}
        else:
            try:
                outcome = await manager.execute_macro(macro_id)
            except Exception as exc:
                message, error_id = safe_action_error(exc, f"Power-on macro '{macro_id}' failed", logger=_LOG)
                outcome = {"success": False, "error": message, "error_id": error_id}
        success = bool(outcome.get("success"))
        reasons = [] if success else _macro_errors(outcome)
        step = StepResult(
            step_index=0,
            action=f"macro:{macro_id}",
            success=success,
            error="; ".join(reasons) or None,
            data={"macro_id": macro_id, "steps_executed": outcome.get("steps_executed")},
        )
        errors = [] if success else [f"Power-on macro '{macro_id}': {outcome.get('error') or 'failed'}"]
        return step, outcome, errors

    # ---- scenes -------------------------------------------------------------

    async def _run_scene(
        self, action_id: str, passcode: str | None, params: dict[str, Any]
    ) -> ActionRunResult:
        """Run a scene through the shared executor, so recall and steps stay in step."""
        manager = self.scene_manager
        if manager is None:
            return _unavailable("scene", action_id, "Scene manager not initialized")
        if manager.get_scene(action_id) is None:
            return _not_found("scene", action_id)
        if self.matrix_device is None:
            return _unavailable("scene", action_id, "Matrix device not configured")

        profiles_map = self.profile_manager.get_profiles_map() if self.profile_manager else {}
        if manager.is_scene_password_protected(action_id, profiles_map):
            denied = await _passcode_refusal(
                "scene",
                action_id,
                passcode,
                lambda: manager.verify_scene_passcode_async(action_id, passcode, profiles_map),
            )
            if denied is not None:
                return denied

        from scene_execution import SceneExecutor, _PasscodeCheckedSceneManager

        executor = SceneExecutor(
            scene_manager=_PasscodeCheckedSceneManager(manager, action_id),
            profile_manager=self.profile_manager,
            system_action_manager=self.shortcut_manager,
            macro_manager=self.macro_manager,
        )
        result = await executor.execute_scene(action_id, self.matrix_device, passcode=passcode)
        return _from_scene_result(action_id, result)

    # ---- macros -------------------------------------------------------------

    async def _run_macro(
        self, action_id: str, passcode: str | None, params: dict[str, Any]
    ) -> ActionRunResult:
        """Run a CEC macro; ``timeout_s`` and ``continue_on_error`` are optional overrides."""
        manager = self.macro_manager
        if manager is None:
            return _unavailable("macro", action_id, "Macro manager not initialized")

        macro = manager.get_macro(action_id)
        if macro is None:
            return _not_found("macro", action_id)

        kwargs: dict[str, Any] = {}
        if "timeout_s" in params:
            timeout = params["timeout_s"]
            if isinstance(timeout, bool) or not isinstance(timeout, (int, float)) or timeout <= 0:
                return _bad_request("macro", action_id, "timeout_s must be a positive number")
            kwargs["timeout_s"] = float(timeout)
        if "continue_on_error" in params:
            if not isinstance(params["continue_on_error"], bool):
                return _bad_request("macro", action_id, "continue_on_error must be true or false")
            kwargs["continue_on_error"] = params["continue_on_error"]

        outcome = await manager.execute_macro(action_id, **kwargs)
        steps = [
            StepResult(
                step_index=index,
                action=str(step.get("command", "step")),
                success=bool(step.get("success")),
                error="; ".join(str(error) for error in step.get("errors") or []) or None,
                data={"step": step.get("step"), "targets": step.get("targets")},
            )
            for index, step in enumerate(outcome.get("results") or [])
        ]
        errors = [] if outcome.get("success") else _macro_errors(outcome)
        return _from_steps("macro", action_id, steps, errors, outcome)

    # ---- shortcuts ----------------------------------------------------------

    async def _run_shortcut(
        self, action_id: str, passcode: str | None, params: dict[str, Any]
    ) -> ActionRunResult:
        """
        Run a system shortcut.

        A shortcut is one action, so a refusal is not a partial run: like
        ``POST /api/shortcuts/{key}/execute`` it is answered with 500, and the
        detail of a per-output failure is in the step's data.
        """
        manager = self.shortcut_manager
        if manager is None:
            return _unavailable("shortcut", action_id, "System shortcut manager not initialized")

        shortcut = manager.get(action_id)
        if shortcut is None:
            return _not_found("shortcut", action_id)
        if not shortcut.enabled:
            return _bad_request("shortcut", action_id, f"Shortcut '{action_id}' is disabled", code="disabled")
        if self.matrix_device is None:
            return _unavailable("shortcut", action_id, "Matrix device not configured")

        outcome = await execute_shortcut(shortcut, self.matrix_device, params)
        success = bool(outcome.get("success"))
        detail = outcome.get("detail")
        steps = [
            StepResult(
                step_index=0,
                action=str(shortcut.type or "shortcut"),
                success=success,
                error=None if success else str(detail or "shortcut failed"),
                data=outcome,
            )
        ]
        return _from_steps("shortcut", action_id, steps, [] if success else [str(detail or "shortcut failed")], outcome)

    # ---- presets ------------------------------------------------------------

    async def _run_preset(
        self, action_id: str, passcode: str | None, params: dict[str, Any]
    ) -> ActionRunResult:
        """Recall a hardware preset slot (1-8)."""
        executor = self.preset_executor or self.matrix_device
        recaller = getattr(executor, "recall_preset", None)
        if recaller is None and not callable(executor):
            return _unavailable("preset", action_id, "Matrix device not configured")
        recaller = recaller or executor

        try:
            number = int(str(action_id).strip())
        except (TypeError, ValueError):
            return _not_found("preset", action_id)
        if not 1 <= number <= PRESET_SLOTS:
            return _not_found("preset", action_id)

        try:
            if isinstance(executor, MatrixService):
                recalled = await executor.recall_preset(number, propagate_errors=True)
            else:
                recalled = bool(await _resolve(recaller(number)))
        except Exception as exc:
            message, error_id = safe_action_error(exc, "recalling preset", logger=_LOG)
            return _result(
                "preset",
                action_id,
                success=False,
                partial=False,
                status_code=STATUS_FAILED,
                step_results=[
                    StepResult(
                        step_index=0,
                        action=f"preset:{number}",
                        success=False,
                        error=message,
                        data={"preset": number, "error_id": error_id},
                    )
                ],
                errors=[message],
                data={
                    "code": "execution_error",
                    "id": action_id,
                    "preset": number,
                    "name": f"Preset {number}",
                    "error_id": error_id,
                },
            )

        steps = [
            StepResult(
                step_index=0,
                action=f"preset:{number}",
                success=recalled,
                error=None if recalled else f"Failed to recall preset {number}",
                data={"preset": number},
            )
        ]
        return _from_steps(
            "preset",
            action_id,
            steps,
            [] if recalled else [f"Failed to recall preset {number}"],
            {"preset": number, "name": f"Preset {number}"},
        )


_RUNNERS: dict[str, Callable[[ActionRunner, str, str | None, dict[str, Any]], Awaitable[ActionRunResult]]] = {
    "profile": ActionRunner._run_profile,
    "scene": ActionRunner._run_scene,
    "macro": ActionRunner._run_macro,
    "shortcut": ActionRunner._run_shortcut,
    "preset": ActionRunner._run_preset,
}


def _normalize_kind(kind: str) -> str | None:
    """The canonical name of an action kind, or None if it is not one."""
    return str(kind).strip().lower() if kind is not None else None


def _from_scene_result(action_id: str, result: Any) -> ActionRunResult:
    """A scene run's ``ExecutionResult`` as an ActionRunResult."""
    if not result.success and result.error in _PASSCODE_ERRORS:
        return _refused("scene", action_id, result.error)

    steps = [
        StepResult(
            step_index=step.step_index,
            action=step.step_type,
            success=step.success,
            error=step.error,
            data={"id": step.step_id, "detail": step.detail},
        )
        for step in result.step_results
    ]
    errors = [] if result.success else [result.error or "Scene execution failed"]
    return _from_steps("scene", action_id, steps, errors, result.to_dict())
