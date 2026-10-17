"""
Phase 8 Scene REST API — unified grouping of Profiles and System Actions.

Endpoints:

Scenes:
  GET    /api/v2/scenes                     — list all scenes
  POST   /api/v2/scenes                     — create scene
  GET    /api/v2/scenes/{scene_id}         — get scene
  PUT    /api/v2/scenes/{scene_id}         — update scene
  DELETE /api/v2/scenes/{scene_id}          — delete scene
  POST   /api/v2/scenes/{scene_id}/execute — execute scene (optional passcode in body)
  GET    /api/v2/scenes/{scene_id}/history  — execution history
  POST   /api/v2/scenes/{scene_id}/validate — detect conflicts
  PUT    /api/v2/scenes/{scene_id}/override — set/clear override
  POST   /api/v2/scenes/{scene_id}/steps   — add step
  DELETE /api/v2/scenes/{scene_id}/steps/{index} — remove step

System Actions:
  GET    /api/system-actions                — list all system actions with user prefs
  PUT    /api/system-actions/{key}         — update label/icon/order/enabled
  POST   /api/system-actions/{key}/execute — execute a system action
"""

import json
import logging
import math
from typing import Any

from aiohttp import web

from password import (
    PIN_CLEAR,
    PIN_SET,
    attempt_pin,
    check_pin_lockout,
    hash_passcode_async,
    requested_pin_change,
    reset_pin_lockout,
)
from scene_manager import (
    STEP_TYPE_PROFILE,
    Scene,
    SceneManager,
    SceneStep,
    detect_conflicts,
    validate_overrides,
)

_LOG = logging.getLogger("rest_api.scenes_v2")

# Phase 8 manager — set by app.py at startup
_phase8_scene_manager: "SceneManager | None" = None


def set_phase8_scene_manager(mgr: "SceneManager") -> None:
    """Called by app.py to inject the Phase 8 SceneManager."""
    global _phase8_scene_manager
    _phase8_scene_manager = mgr


def _get_scene_manager() -> "SceneManager":
    if _phase8_scene_manager is None:
        raise RuntimeError("Phase8 SceneManager not initialized")
    return _phase8_scene_manager


class _PasscodeCheckedSceneManager:
    """
    The SceneManager as the executor sees it once the REST layer has checked
    the passcode of ``scene_id`` (with the attempt limiter, off the event
    loop): the executor's own synchronous re-check would run PBKDF2 on the
    event loop again (SEC-06), so it is answered from that result.
    """

    def __init__(self, manager: SceneManager, scene_id: str):
        self._manager = manager
        self._scene_id = scene_id

    def verify_passcode(self, scene_id: str, passcode: str) -> bool:
        if scene_id == self._scene_id:
            return True
        return self._manager.verify_passcode(scene_id, passcode)

    def __getattr__(self, name: str) -> Any:
        return getattr(self._manager, name)


def _get_executor(passcode_checked_scene: str | None = None):
    from persistence import get_data_dir
    from rest_api.utils import get_macro_manager, get_system_shortcut_manager
    from scene_execution import SceneExecutor
    from system_shortcuts import SystemShortcutManager as SystemActionManager

    # The hub's shortcut manager (the one the shortcut routes edit); a private
    # instance only when the REST layer was not set up with one.
    sam = get_system_shortcut_manager() or SystemActionManager(get_data_dir())
    scene_manager: Any = _get_scene_manager()
    if passcode_checked_scene is not None:
        scene_manager = _PasscodeCheckedSceneManager(scene_manager, passcode_checked_scene)
    return SceneExecutor(
        scene_manager=scene_manager,
        profile_manager=_get_profile_manager(),
        system_action_manager=sam,
        macro_manager=get_macro_manager(),
    )


def _get_profile_manager():
    from rest_api.utils import get_profile_manager

    mgr = get_profile_manager()
    if mgr is None:
        raise RuntimeError("ProfileManager not initialized")
    return mgr  # type: ignore


def _profile_map(steps: list[SceneStep]) -> dict[str, Any]:
    """``{profile_id: Profile}`` for the profiles the steps reference (unknown ids left out).

    API-05: this used ``{p.id: p for p in pm.list_profiles()}``, but
    ``list_profiles()`` returns summary dicts, so every create/update with
    profiles on the hub failed with 500.
    """
    pm = _get_profile_manager()
    found: dict[str, Any] = {}
    for step in steps:
        if step.type == STEP_TYPE_PROFILE and step.id not in found:
            profile = pm.get_profile(step.id)
            if profile is not None:
                found[step.id] = profile
    return found


def _all_profiles_map() -> dict[str, Any]:
    """``{profile_id: Profile}`` for every profile, for PIN inheritance (SEC-04 / SEC-05)."""
    from rest_api.utils import get_profile_manager

    pm = get_profile_manager()
    return pm.get_profiles_map() if pm is not None else {}


def _scene_dict(mgr: SceneManager, scene: Scene, profiles_map: dict[str, Any]) -> dict[str, Any]:
    """
    A scene as clients see it: never ``passcode_hash`` (F-SEC-005), and
    ``password_protected`` true when a PIN is needed to run it, its own or
    inherited from a protected Profile (``passcode_inherited``).
    """
    result = scene.to_dict()
    result["password_protected"] = mgr.is_scene_password_protected(scene.id, profiles_map)
    result["passcode_inherited"] = mgr.is_passcode_inherited(scene.id, profiles_map)
    return result


def _pin_key(scene_id: str) -> str:
    """Attempt-limiter key of a scene (SEC-06)."""
    return f"scene:{scene_id}"


async def _optional_json(request: web.Request) -> dict[str, Any]:
    """The JSON object body of a request that may have none (raises JSONDecodeError if malformed)."""
    if not request.can_read_body:
        return {}
    data = await request.json()
    return data if isinstance(data, dict) else {}


def _supplied_pin(request: web.Request, data: dict[str, Any], *fields: str) -> Any:
    """The passcode a request supplies: the first non-empty body field, else the X-Passcode header."""
    for name in fields:
        value = data.get(name)
        if value not in (None, ""):
            return value
    return request.headers.get("X-Passcode") or None


async def _pin_locked_response(scene_id: str, retry_after: float) -> web.Response:
    """429 for a scene locked out after too many wrong passcodes (F-SEC-007)."""
    seconds = max(1, math.ceil(retry_after))
    response = await _json_response(
        False,
        {"error": "passcode_locked", "scene_id": scene_id, "retry_after": seconds, "requires_scene_passcode": True},
        error=f"Too many wrong passcodes; try again in {seconds} s",
        status=429,
    )
    response.headers["Retry-After"] = str(seconds)
    return response


async def _check_scene_pin(
    mgr: SceneManager, scene_id: str, passcode: Any, profiles_map: dict[str, Any]
) -> web.Response | None:
    """
    Check ``passcode`` for a protected scene (own or inherited PIN) under the
    attempt limiter. Returns None if it matches, else the response to send:
    429 while locked out, 403 ``passcode_required`` / ``invalid_passcode``.
    """
    key = _pin_key(scene_id)
    retry_after = check_pin_lockout(key)
    if retry_after > 0:
        return await _pin_locked_response(scene_id, retry_after)
    if passcode in (None, ""):
        error = "passcode_required"
    else:
        attempt = await attempt_pin(key, lambda: mgr.verify_scene_passcode_async(scene_id, passcode, profiles_map))
        if attempt.locked:
            return await _pin_locked_response(scene_id, attempt.retry_after)
        if attempt.ok:
            return None
        _LOG.warning("Wrong passcode for scene '%s'", scene_id)
        error = "invalid_passcode"
    return await _json_response(
        False,
        {"error": error, "scene_id": scene_id, "requires_scene_passcode": True},
        status=403,
    )


def _parse_steps(raw: Any) -> list[SceneStep]:
    """Steps from a request body; raises ValueError with a client-facing message."""
    if not isinstance(raw, list):
        raise ValueError("steps must be a list")
    steps = []
    for i, item in enumerate(raw):
        if not isinstance(item, dict):
            raise ValueError(f"step {i} must be an object")
        steps.append(SceneStep.from_dict(item))
    return steps


def _parse_overrides(raw: Any) -> dict[str, dict[int, dict[str, bool]]]:
    """Overrides from a request body (output keys are strings in JSON); raises ValueError."""
    if not isinstance(raw, dict):
        raise ValueError("overrides must be an object")
    overrides: dict[str, dict[int, dict[str, bool]]] = {}
    for pid, outputs in raw.items():
        if not isinstance(outputs, dict):
            raise ValueError(f"overrides for {pid!r} must be an object")
        overrides[pid] = {}
        for out_str, settings in outputs.items():
            try:
                out_num = int(out_str)
            except (TypeError, ValueError):
                raise ValueError(f"override output {out_str!r} must be a number") from None
            overrides[pid][out_num] = settings
    err = validate_overrides(overrides)
    if err:
        raise ValueError(err)
    return overrides


def _execution_status(result: Any) -> int:
    """HTTP status of a scene run (API-08): 200 all steps succeeded, 207 some did, 500 none did."""
    if result.success:
        return 200
    return 207 if result.steps_completed > 0 else 500


async def _json_response(success: bool, data: dict = None, error: str = None, status: int = 200) -> web.Response:
    """Helper to build a standard JSON response."""
    body: dict[str, Any] = {"success": success}
    if data is not None:
        body["data"] = data
    if error is not None:
        body["error"] = error
    return web.json_response(body, status=status)


# =============================================================================
# Scenes CRUD
# =============================================================================


async def handle_list_scenes(request: web.Request) -> web.Response:
    """GET /api/v2/scenes — list all scenes."""
    try:
        mgr = _get_scene_manager()
        scenes = mgr.list_scenes()
        profiles_map = _all_profiles_map()
        return await _json_response(
            True,
            {
                "scenes": [_scene_dict(mgr, s, profiles_map) for s in scenes],
                "count": len(scenes),
            },
        )
    except Exception as e:
        _LOG.error("Error listing scenes: %s", e)
        return await _json_response(False, error=str(e), status=500)


async def handle_create_scene(request: web.Request) -> web.Response:
    """POST /api/v2/scenes — create a new scene."""
    try:
        data = await request.json()
        if not isinstance(data, dict):
            return await _json_response(False, error="Body must be a JSON object", status=400)
        mgr = _get_scene_manager()

        try:
            steps = _parse_steps(data.get("steps", []))
        except ValueError as exc:
            return await _json_response(False, error=str(exc), status=400)
        for i, step in enumerate(steps):
            err = step.validate()
            if err:
                return await _json_response(False, error=f"Step {i}: {err}", status=400)

        action, new_pin, pin_error = requested_pin_change(data, has_own_pin=False)
        if pin_error:
            return await _json_response(False, error=pin_error, status=400)

        # The manager enforces PIN inheritance (a scene containing a protected
        # profile must itself be protected) with the profile map (SEC-05).
        profiles_map = _all_profiles_map()
        scene, err = mgr.create_scene(
            name=data.get("name", "Unnamed Scene"),
            icon=data.get("icon", "🎬"),
            steps=steps,
            password_protected=action == PIN_SET,
            passcode_hash=await hash_passcode_async(new_pin) if action == PIN_SET else None,
            profiles_map=profiles_map,
        )
        if err:
            return await _json_response(False, error=err, status=400)

        return await _json_response(True, {"scene": _scene_dict(mgr, scene, profiles_map)}, status=201)
    except json.JSONDecodeError:
        return await _json_response(False, error="Invalid JSON body", status=400)
    except Exception as e:
        _LOG.error("Error creating scene: %s", e)
        return await _json_response(False, error=str(e), status=500)


async def handle_get_scene(request: web.Request) -> web.Response:
    """GET /api/v2/scenes/{scene_id} — get a scene by ID."""
    try:
        scene_id = request.match_info["scene_id"]
        mgr = _get_scene_manager()
        scene = mgr.get_scene(scene_id)
        if scene is None:
            return await _json_response(False, error="Scene not found", status=404)
        return await _json_response(True, {"scene": _scene_dict(mgr, scene, _all_profiles_map())})
    except Exception as e:
        _LOG.error("Error getting scene %s: %s", scene_id, e)
        return await _json_response(False, error=str(e), status=500)


async def handle_update_scene(request: web.Request) -> web.Response:
    """PUT /api/v2/scenes/{scene_id} — update a scene."""
    try:
        scene_id = request.match_info["scene_id"]
        data = await request.json()
        if not isinstance(data, dict):
            return await _json_response(False, error="Body must be a JSON object", status=400)
        mgr = _get_scene_manager()
        existing = mgr.get_scene(scene_id)
        if existing is None:
            return await _json_response(False, error="Scene not found", status=404)

        # Parse (and validate) everything before anything is changed (API-13)
        steps = None
        overrides: dict[str, dict[int, dict[str, bool]]] | None = None
        try:
            if "steps" in data:
                steps = _parse_steps(data["steps"])
            if "overrides" in data:
                overrides = _parse_overrides(data["overrides"])
        except ValueError as exc:
            return await _json_response(False, error=str(exc), status=400)

        # PIN (SEC-05): setting, changing or removing the PIN of a protected
        # scene (own PIN or one inherited from a protected profile) needs the
        # current passcode ("current_passcode" or the X-Passcode header).
        profiles_map = _all_profiles_map()
        protected_now = mgr.is_scene_password_protected(scene_id, profiles_map)
        action, new_pin, pin_error = requested_pin_change(
            data, has_own_pin=existing.is_password_protected(), protected=protected_now
        )
        if pin_error:
            return await _json_response(False, error=pin_error, status=400)
        if action is not None and protected_now:
            denied = await _check_scene_pin(
                mgr, scene_id, _supplied_pin(request, data, "current_passcode"), profiles_map
            )
            if denied is not None:
                return denied
        pin_kwargs: dict[str, Any] = {}
        if action == PIN_SET:
            pin_kwargs = {"password_protected": True, "passcode_hash": await hash_passcode_async(new_pin)}
        elif action == PIN_CLEAR:
            pin_kwargs = {"password_protected": False}

        # The manager enforces PIN inheritance with the profile map
        scene, err = mgr.update_scene(
            scene_id,
            name=data.get("name"),
            icon=data.get("icon"),
            steps=steps,
            overrides=overrides,
            favorite=data.get("favorite"),
            dashboard_visible=data.get("dashboard_visible"),
            dashboard_order=data.get("dashboard_order"),
            profiles_map=profiles_map,
            **pin_kwargs,
        )
        if err:
            return await _json_response(False, error=err, status=400)

        return await _json_response(True, {"scene": _scene_dict(mgr, scene, profiles_map)})
    except json.JSONDecodeError:
        return await _json_response(False, error="Invalid JSON body", status=400)
    except Exception as e:
        _LOG.error("Error updating scene %s: %s", scene_id, e)
        return await _json_response(False, error=str(e), status=500)


async def handle_delete_scene(request: web.Request) -> web.Response:
    """DELETE /api/v2/scenes/{scene_id} — delete a scene."""
    try:
        scene_id = request.match_info["scene_id"]
        mgr = _get_scene_manager()
        if mgr.get_scene(scene_id) is None:
            return await _json_response(False, error="Scene not found", status=404)

        # Deleting a protected scene needs its passcode (SEC-05): body
        # "current_passcode"/"passcode" or the X-Passcode header.
        profiles_map = _all_profiles_map()
        if mgr.is_scene_password_protected(scene_id, profiles_map):
            data = await _optional_json(request)
            denied = await _check_scene_pin(
                mgr, scene_id, _supplied_pin(request, data, "current_passcode", "passcode"), profiles_map
            )
            if denied is not None:
                return denied

        if not mgr.delete_scene(scene_id):
            return await _json_response(False, error="Scene not found", status=404)
        reset_pin_lockout(_pin_key(scene_id))
        return await _json_response(True, {"deleted": scene_id})
    except json.JSONDecodeError:
        return await _json_response(False, error="Invalid JSON body", status=400)
    except Exception as e:
        _LOG.error("Error deleting scene %s: %s", scene_id, e)
        return await _json_response(False, error=str(e), status=500)


# =============================================================================
# Scene execution
# =============================================================================


async def handle_execute_scene(request: web.Request) -> web.Response:
    """POST /api/v2/scenes/{scene_id}/execute — execute a scene."""
    try:
        scene_id = request.match_info["scene_id"]
        data = await _optional_json(request)
        passcode = data.get("passcode")

        from rest_api.utils import get_matrix_device

        matrix = get_matrix_device()
        if matrix is None:
            return await _json_response(False, error="Matrix not connected", status=503)

        mgr = _get_scene_manager()
        if mgr.get_scene(scene_id) is None:
            return await _json_response(False, error="Scene not found", status=404)

        # Own or inherited PIN, checked under the attempt limiter with PBKDF2
        # off the event loop (SEC-04, SEC-06 / F-SEC-007)
        passcode_checked = None
        profiles_map = _all_profiles_map()
        if mgr.is_scene_password_protected(scene_id, profiles_map):
            denied = await _check_scene_pin(mgr, scene_id, passcode, profiles_map)
            if denied is not None:
                return denied
            passcode_checked = scene_id

        executor = _get_executor(passcode_checked)
        result = await executor.execute_scene(scene_id, matrix, passcode=passcode)

        if not result.success and result.error in ("passcode_required", "invalid_passcode"):
            return await _json_response(
                False,
                {
                    "error": result.error,
                    "scene_id": scene_id,
                    "requires_scene_passcode": True,
                },
                status=403,
            )

        # API-08: the answer says what happened - 200 every step succeeded,
        # 207 some did (per-step results in data.step_results), 500 none did.
        return await _json_response(result.success, result.to_dict(), status=_execution_status(result))
    except json.JSONDecodeError:
        return await _json_response(False, error="Invalid JSON body", status=400)
    except Exception as e:
        _LOG.error("Error executing scene %s: %s", scene_id, e)
        return await _json_response(False, error=str(e), status=500)


async def handle_scene_history(request: web.Request) -> web.Response:
    """GET /api/v2/scenes/{scene_id}/history — get execution history."""
    try:
        scene_id = request.match_info["scene_id"]
        mgr = _get_scene_manager()
        scene = mgr.get_scene(scene_id)
        if scene is None:
            return await _json_response(False, error="Scene not found", status=404)
        return await _json_response(
            True,
            {
                "scene_id": scene_id,
                "last_executed": scene.last_executed,
                "execution_history": [e.to_dict() for e in scene.execution_history],
            },
        )
    except Exception as e:
        _LOG.error("Error getting scene history %s: %s", scene_id, e)
        return await _json_response(False, error=str(e), status=500)


# =============================================================================
# Conflict detection
# =============================================================================


async def handle_validate_scene(request: web.Request) -> web.Response:
    """POST /api/v2/scenes/{scene_id}/validate — detect conflicts in scene steps."""
    try:
        scene_id = request.match_info["scene_id"]
        mgr = _get_scene_manager()
        scene = mgr.get_scene(scene_id)
        if scene is None:
            return await _json_response(False, error="Scene not found", status=404)

        conflicts = detect_conflicts(scene, _profile_map(scene.steps))
        return await _json_response(
            True,
            {
                "scene_id": scene_id,
                "conflicts": [c.to_dict() for c in conflicts],
                "has_conflicts": len(conflicts) > 0,
            },
        )
    except Exception as e:
        _LOG.error("Error validating scene %s: %s", scene_id, e)
        return await _json_response(False, error=str(e), status=500)


# =============================================================================
# Override management
# =============================================================================


async def handle_set_override(request: web.Request) -> web.Response:
    """
    PUT /api/v2/scenes/{scene_id}/override — set a per-profile output override.

    Body: { "profile_id": "...", "output_num": 1, "setting_key": "hdcp", "disabled": true }
    """
    try:
        scene_id = request.match_info["scene_id"]
        data = await request.json()
        mgr = _get_scene_manager()

        scene, err = mgr.set_override(
            scene_id,
            profile_id=data["profile_id"],
            output_num=int(data["output_num"]),
            setting_key=data["setting_key"],
            disabled=bool(data.get("disabled", True)),
        )
        if err:
            return await _json_response(False, error=err, status=400)

        return await _json_response(True, {"scene": scene.to_dict()})
    except json.JSONDecodeError:
        return await _json_response(False, error="Invalid JSON body", status=400)
    except KeyError as e:
        return await _json_response(False, error=f"Missing field: {e}", status=400)
    except Exception as e:
        _LOG.error("Error setting override: %s", e)
        return await _json_response(False, error=str(e), status=500)


async def handle_clear_override(request: web.Request) -> web.Response:
    """
    DELETE /api/v2/scenes/{scene_id}/override — remove an override.

    Body: { "profile_id": "...", "output_num": 1, "setting_key": "hdcp" }
    """
    try:
        scene_id = request.match_info["scene_id"]
        data = await request.json()
        mgr = _get_scene_manager()

        scene, err = mgr.clear_override(
            scene_id,
            profile_id=data["profile_id"],
            output_num=int(data["output_num"]),
            setting_key=data["setting_key"],
        )
        if err:
            return await _json_response(False, error=err, status=400)

        return await _json_response(True, {"scene": scene.to_dict()})
    except json.JSONDecodeError:
        return await _json_response(False, error="Invalid JSON body", status=400)
    except KeyError as e:
        return await _json_response(False, error=f"Missing field: {e}", status=400)
    except Exception as e:
        _LOG.error("Error clearing override: %s", e)
        return await _json_response(False, error=str(e), status=500)


# =============================================================================
# Scene step management
# =============================================================================


async def handle_add_step(request: web.Request) -> web.Response:
    """
    POST /api/v2/scenes/{scene_id}/steps — add a step to a scene.

    Body: { "type": "profile", "id": "profile_abc" }
          or { "type": "system_action", "id": "mute_all_audio", "params": {} }
    """
    try:
        scene_id = request.match_info["scene_id"]
        data = await request.json()
        mgr = _get_scene_manager()

        if not isinstance(data, dict):
            return await _json_response(False, error="Body must be a JSON object", status=400)
        step = SceneStep.from_dict(data)
        err = step.validate()
        if err:
            return await _json_response(False, error=err, status=400)

        existing = mgr.get_scene(scene_id)
        if existing is None:
            return await _json_response(False, error="Scene not found", status=404)
        if not existing.password_protected and mgr.steps_reference_protected_profile([step], _profile_map([step])):
            return await _json_response(
                False,
                error="Cannot add a step referencing a password-protected Profile to an unprotected Scene",
                status=400,
            )

        scene, err = mgr.add_step(scene_id, step)
        if err:
            return await _json_response(False, error=err, status=400)

        return await _json_response(True, {"scene": scene.to_dict()})
    except json.JSONDecodeError:
        return await _json_response(False, error="Invalid JSON body", status=400)
    except Exception as e:
        _LOG.error("Error adding step: %s", e)
        return await _json_response(False, error=str(e), status=500)


async def handle_remove_step(request: web.Request) -> web.Response:
    """
    DELETE /api/v2/scenes/{scene_id}/steps/{index} — remove step at index.
    """
    try:
        scene_id = request.match_info["scene_id"]
        index = int(request.match_info["index"])
        mgr = _get_scene_manager()

        scene, err = mgr.remove_step(scene_id, index)
        if err:
            return await _json_response(False, error=err, status=400)

        return await _json_response(True, {"scene": scene.to_dict()})
    except (ValueError, KeyError) as e:
        return await _json_response(False, error=f"Invalid index: {e}", status=400)
    except Exception as e:
        _LOG.error("Error removing step: %s", e)
        return await _json_response(False, error=str(e), status=500)
