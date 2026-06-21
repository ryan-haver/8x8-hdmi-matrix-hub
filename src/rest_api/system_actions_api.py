"""
Phase 8 System Actions REST API.

Endpoints:

  GET  /api/system-actions            — list all system actions with user prefs
  POST /api/system-actions/{key}      — update label/icon/order/enabled
  POST /api/system-actions/{key}/execute — execute a system action
"""

import json
import logging

from aiohttp import web

from system_actions import SystemActionManager
from scene_execution import execute_action
from rest_api.utils import _json_response, get_matrix_device

_LOG = logging.getLogger("rest_api.system_actions")

#: In-memory manager instance (initialized lazily)
_sam: SystemActionManager | None = None


def _get_sam() -> SystemActionManager:
    global _sam
    if _sam is None:
        from persistence import get_data_dir
        _sam = SystemActionManager(get_data_dir())
    return _sam


async def handle_list_system_actions(request: web.Request) -> web.Response:
    """GET /api/system-actions — list all system actions with user preferences."""
    try:
        sam = _get_sam()
        actions = sam.list_actions()
        return _json_response(True, {
            "actions": [a.to_dict() for a in actions],
            "count": len(actions),
        })
    except Exception as e:
        _LOG.error("Error listing system actions: %s", e)
        return _json_response(False, error=str(e), status=500)


async def handle_update_system_action(request: web.Request) -> web.Response:
    """
    PUT /api/system-actions/{key} — update editable preferences.

    Body: { "label": "...", "icon": "...", "enabled": true, "order": 5 }
    """
    try:
        key = request.match_info["key"]
        data = await request.json()
        sam = _get_sam()

        success = sam.update_prefs(
            key,
            label=data.get("label"),
            icon=data.get("icon"),
            enabled=data.get("enabled"),
            order=data.get("order"),
        )
        if not success:
            return _json_response(False, error=f"Unknown action key: {key}", status=404)

        action = sam.get_action(key)
        return _json_response(True, {"action": action.to_dict()})
    except json.JSONDecodeError:
        return _json_response(False, error="Invalid JSON body", status=400)
    except Exception as e:
        _LOG.error("Error updating system action %s: %s", key, e)
        return _json_response(False, error=str(e), status=500)


async def handle_execute_system_action(request: web.Request) -> web.Response:
    """
    POST /api/system-actions/{key}/execute — execute a system action.

    Optional body: { "params": { "output": 1 } }  — for actions that need params
    """
    try:
        key = request.match_info["key"]
        data = await request.json() if request.can_read_body else {}
        params = data.get("params", {})

        matrix = get_matrix_device()
        if matrix is None:
            return _json_response(False, error="Matrix not connected", status=503)

        sam = _get_sam()
        action = sam.get_action(key)
        if action is None:
            return _json_response(False, error=f"Unknown action key: {key}", status=404)
        if not action.enabled:
            return _json_response(False, error="System action is disabled", status=400)

        result = await execute_action(action, matrix, params)
        if not result.get("success"):
            return _json_response(False, {
                "error": "execution_failed",
                "detail": result.get("detail", "Unknown error"),
            }, status=500)

        return _json_response(True, {
            "success": True,
            "detail": result.get("detail", ""),
        })
    except json.JSONDecodeError:
        return _json_response(False, error="Invalid JSON body", status=400)
    except Exception as e:
        _LOG.error("Error executing system action %s: %s", key, e)
        return _json_response(False, error=str(e), status=500)
