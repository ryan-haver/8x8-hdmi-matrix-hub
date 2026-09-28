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
from typing import Any

from aiohttp import web

from scene_manager import (
    STEP_TYPE_PROFILE,
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


def _get_executor():
    from persistence import get_data_dir
    from rest_api.utils import get_macro_manager, get_system_shortcut_manager
    from scene_execution import SceneExecutor
    from system_shortcuts import SystemShortcutManager as SystemActionManager

    # The hub's shortcut manager (the one the shortcut routes edit); a private
    # instance only when the REST layer was not set up with one.
    sam = get_system_shortcut_manager() or SystemActionManager(get_data_dir())
    return SceneExecutor(
        scene_manager=_get_scene_manager(),
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
        return await _json_response(
            True,
            {
                "scenes": [s.to_dict() for s in scenes],
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

        # Password inheritance check: scene containing protected profile must itself be protected
        if not bool(data.get("password_protected", False)) and mgr.steps_reference_protected_profile(
            steps, _profile_map(steps)
        ):
            return await _json_response(
                False,
                error="Scene contains a password-protected Profile; the Scene must also be password-protected",
                status=400,
            )

        scene, err = mgr.create_scene(
            name=data.get("name", "Unnamed Scene"),
            icon=data.get("icon", "🎬"),
            steps=steps,
            password_protected=bool(data.get("password_protected", False)),
            passcode=data.get("passcode"),
        )
        if err:
            return await _json_response(False, error=err, status=400)

        return await _json_response(True, {"scene": scene.to_dict()}, status=201)
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
        return await _json_response(True, {"scene": scene.to_dict()})
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
        if mgr.get_scene(scene_id) is None:
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

        # Password inheritance check
        password_protected = data.get("password_protected")
        if steps is not None and not password_protected:
            profile_map = _profile_map(steps)
            existing = mgr.get_scene(scene_id)
            scene_is_protected = (
                password_protected
                if password_protected is not None
                else (existing.password_protected if existing else False)
            )
            if not scene_is_protected and mgr.steps_reference_protected_profile(steps, profile_map):
                return await _json_response(
                    False,
                    error="Scene contains a password-protected Profile; the Scene must also be password-protected",
                    status=400,
                )

        scene, err = mgr.update_scene(
            scene_id,
            name=data.get("name"),
            icon=data.get("icon"),
            steps=steps,
            overrides=overrides,
            favorite=data.get("favorite"),
            dashboard_visible=data.get("dashboard_visible"),
            dashboard_order=data.get("dashboard_order"),
            password_protected=password_protected,
            passcode=data.get("passcode"),
        )
        if err:
            return await _json_response(False, error=err, status=400)

        return await _json_response(True, {"scene": scene.to_dict()})
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
        if not mgr.delete_scene(scene_id):
            return await _json_response(False, error="Scene not found", status=404)
        return await _json_response(True, {"deleted": scene_id})
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
        data = await request.json() if request.can_read_body else {}
        passcode = data.get("passcode") if isinstance(data, dict) else None

        from rest_api.utils import get_matrix_device

        matrix = get_matrix_device()
        if matrix is None:
            return await _json_response(False, error="Matrix not connected", status=503)

        if _get_scene_manager().get_scene(scene_id) is None:
            return await _json_response(False, error="Scene not found", status=404)

        executor = _get_executor()
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
