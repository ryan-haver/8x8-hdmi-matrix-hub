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

from aiohttp import web

from scene_manager import (
    STEP_TYPE_PROFILE,
    STEP_TYPE_SYSTEM_ACTION,
    SceneManager,
    SceneStep,
    detect_conflicts,
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
    from rest_api.utils import get_macro_manager
    from scene_execution import SceneExecutor
    from system_shortcuts import SystemShortcutManager as SystemActionManager

    sam = SystemActionManager(get_data_dir())
    return SceneExecutor(
        scene_manager=_get_scene_manager(),
        profile_manager=_get_profile_manager(),
        system_action_manager=sam,
        macro_manager=get_macro_manager(),
    )


def _get_profile_manager():
    from config import ProfileManager
    from rest_api.utils import get_profile_manager

    mgr = get_profile_manager()
    if mgr is None:
        raise RuntimeError("ProfileManager not initialized")
    return mgr  # type: ignore


async def _json_response(success: bool, data: dict = None, error: str = None, status: int = 200) -> web.Response:
    """Helper to build a standard JSON response."""
    body = {"success": success}
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
        mgr = _get_scene_manager()

        # Parse steps
        steps = []
        for step_data in data.get("steps", []):
            steps.append(SceneStep.from_dict(step_data))

        # Password inheritance check: scene containing protected profile must itself be protected
        pm = _get_profile_manager()
        profile_map = {p.id: p for p in pm.list_profiles()} if pm else None
        if not bool(data.get("password_protected", False)) and mgr.steps_reference_protected_profile(
            steps, profile_map
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
        mgr = _get_scene_manager()

        # Parse steps if provided
        steps = None
        if "steps" in data:
            steps = [SceneStep.from_dict(s) for s in data["steps"]]

        # Parse overrides if provided
        overrides = None
        if "overrides" in data:
            overrides = {}
            for pid, outers in data["overrides"].items():
                overrides[pid] = {}
                for out_str, settings in outers.items():
                    overrides[pid][int(out_str)] = settings

        # Password inheritance check
        password_protected = data.get("password_protected")
        if steps is not None and not password_protected:
            pm = _get_profile_manager()
            profile_map = {p.id: p for p in pm.list_profiles()} if pm else None
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
        passcode = data.get("passcode")

        from rest_api.utils import get_matrix_device

        matrix = get_matrix_device()
        if matrix is None:
            return await _json_response(False, error="Matrix not connected", status=503)

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

        return await _json_response(True, result.to_dict())
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

        # Build profile map for conflict detection
        pm = _get_profile_manager()
        profile_map = {p.id: p for p in (pm._profiles.values() if hasattr(pm, "_profiles") else [])}

        conflicts = detect_conflicts(scene, profile_map)
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

        step = SceneStep.from_dict(data)
        err = step.validate()
        if err:
            return await _json_response(False, error=err, status=400)

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
