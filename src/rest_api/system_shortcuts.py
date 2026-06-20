"""
System Shortcuts REST API.

Endpoints for managing built-in quick-routing shortcuts (Phase 7).

Each shortcut carries the same surface-visibility flags as profiles and
CEC macros (``favorite``, ``dashboard_visible``) plus an ``enabled`` flag.
Built-ins cannot be deleted (only disabled); user-added shortcuts can be
freely renamed, enabled/disabled, and deleted.

Routes (registered in app.py):

- GET    /api/system-shortcuts              — list all (filterable via query params)
- GET    /api/system-shortcuts/favorites   — list favorite shortcuts only
- GET    /api/system-shortcuts/dashboard   — list dashboard-visible shortcuts only
- GET    /api/system-shortcuts/{id}        — get a single shortcut
- PUT    /api/system-shortcuts/{id}        — rename / enable / disable / set favorite / set dashboard
- POST   /api/system-shortcuts/{id}/favorite      — toggle favorite flag
- POST   /api/system-shortcuts/{id}/dashboard     — toggle dashboard-visible flag
- POST   /api/system-shortcuts/{id}/execute       — execute the shortcut
- POST   /api/system-shortcuts              — create a new user shortcut
- DELETE /api/system-shortcuts/{id}        — delete a user shortcut
- PUT    /api/system-shortcuts/reorder     — bulk reorder by id list
"""

import json
import logging

from aiohttp import web

from system_shortcuts import SystemShortcut, VALID_TYPES, execute_shortcut

from .utils import (
    _json_response,
    get_matrix_device,
    get_system_shortcut_manager,
)

_LOG = logging.getLogger("rest_api.system_shortcuts")


# =============================================================================
# Query endpoints
# =============================================================================


async def handle_list_shortcuts(request: web.Request) -> web.Response:
    """GET /api/system-shortcuts — list all shortcuts."""
    manager = get_system_shortcut_manager()
    if manager is None:
        return _json_response(False, error="System shortcut manager not initialized", status=503)
    try:
        enabled_only = request.query.get("enabled_only", "").lower() == "true"
        include_builtin = request.query.get("include_builtin", "true").lower() != "false"
        shortcuts = manager.list_shortcuts(enabled_only=enabled_only, include_builtin=include_builtin)
        return _json_response(True, {
            "shortcuts": [s.to_dict() for s in shortcuts],
        })
    except Exception as exc:
        _LOG.error("Error listing system shortcuts: %s", exc)
        return _json_response(False, error=str(exc), status=500)


async def handle_list_favorite_shortcuts(request: web.Request) -> web.Response:
    """GET /api/system-shortcuts/favorites — list favorites only."""
    manager = get_system_shortcut_manager()
    if manager is None:
        return _json_response(False, error="System shortcut manager not initialized", status=503)
    try:
        shortcuts = manager.list_favorites()
        return _json_response(True, {
            "shortcuts": [s.to_dict() for s in shortcuts],
        })
    except Exception as exc:
        _LOG.error("Error listing favorite shortcuts: %s", exc)
        return _json_response(False, error=str(exc), status=500)


async def handle_list_dashboard_shortcuts(request: web.Request) -> web.Response:
    """GET /api/system-shortcuts/dashboard — list dashboard-visible only."""
    manager = get_system_shortcut_manager()
    if manager is None:
        return _json_response(False, error="System shortcut manager not initialized", status=503)
    try:
        shortcuts = manager.list_dashboard()
        return _json_response(True, {
            "shortcuts": [s.to_dict() for s in shortcuts],
        })
    except Exception as exc:
        _LOG.error("Error listing dashboard shortcuts: %s", exc)
        return _json_response(False, error=str(exc), status=500)


async def handle_get_shortcut(request: web.Request) -> web.Response:
    """GET /api/system-shortcuts/{id} — get one shortcut."""
    manager = get_system_shortcut_manager()
    if manager is None:
        return _json_response(False, error="System shortcut manager not initialized", status=503)
    try:
        shortcut_id = request.match_info.get("id", "")
        if not shortcut_id:
            return _json_response(False, error="Shortcut id required", status=400)
        sc = manager.get(shortcut_id)
        if sc is None:
            return _json_response(False, error=f"Shortcut '{shortcut_id}' not found", status=404)
        return _json_response(True, sc.to_dict())
    except Exception as exc:
        _LOG.error("Error getting shortcut: %s", exc)
        return _json_response(False, error=str(exc), status=500)


# =============================================================================
# Mutation endpoints
# =============================================================================


async def handle_update_shortcut(request: web.Request) -> web.Response:
    """PUT /api/system-shortcuts/{id} — rename / set enabled / set flags."""
    manager = get_system_shortcut_manager()
    if manager is None:
        return _json_response(False, error="System shortcut manager not initialized", status=503)
    try:
        shortcut_id = request.match_info.get("id", "")
        if not shortcut_id:
            return _json_response(False, error="Shortcut id required", status=400)
        sc = manager.get(shortcut_id)
        if sc is None:
            return _json_response(False, error=f"Shortcut '{shortcut_id}' not found", status=404)

        body = await request.json()

        if "name" in body and isinstance(body["name"], str):
            if not manager.rename(shortcut_id, body["name"]):
                return _json_response(False, error="Failed to rename shortcut", status=400)
        if "enabled" in body:
            if not manager.set_enabled(shortcut_id, bool(body["enabled"])):
                return _json_response(False, error="Failed to update enabled flag", status=500)
        if "favorite" in body:
            target = bool(body["favorite"])
            current = sc.favorite
            if target != current:
                manager.toggle_favorite(shortcut_id)
        if "dashboard_visible" in body:
            target = bool(body["dashboard_visible"])
            current = sc.dashboard_visible
            if target != current:
                manager.toggle_dashboard_visible(shortcut_id)
        if "order" in body:
            try:
                sc.order = int(body["order"])
                # Persist via reorder (single-id list is fine)
                manager.reorder([shortcut_id])
            except (TypeError, ValueError):
                return _json_response(False, error="order must be an integer", status=400)

        return _json_response(True, sc.to_dict())
    except json.JSONDecodeError:
        return _json_response(False, error="Invalid JSON body", status=400)
    except Exception as exc:
        _LOG.error("Error updating shortcut: %s", exc)
        return _json_response(False, error=str(exc), status=500)


async def handle_toggle_favorite(request: web.Request) -> web.Response:
    """POST /api/system-shortcuts/{id}/favorite — toggle the favorite flag."""
    manager = get_system_shortcut_manager()
    if manager is None:
        return _json_response(False, error="System shortcut manager not initialized", status=503)
    try:
        shortcut_id = request.match_info.get("id", "")
        sc = manager.get(shortcut_id)
        if sc is None:
            return _json_response(False, error=f"Shortcut '{shortcut_id}' not found", status=404)
        new_state = manager.toggle_favorite(shortcut_id)
        return _json_response(True, {"id": shortcut_id, "favorite": new_state})
    except Exception as exc:
        _LOG.error("Error toggling shortcut favorite: %s", exc)
        return _json_response(False, error=str(exc), status=500)


async def handle_toggle_dashboard(request: web.Request) -> web.Response:
    """POST /api/system-shortcuts/{id}/dashboard — toggle dashboard-visible flag."""
    manager = get_system_shortcut_manager()
    if manager is None:
        return _json_response(False, error="System shortcut manager not initialized", status=503)
    try:
        shortcut_id = request.match_info.get("id", "")
        sc = manager.get(shortcut_id)
        if sc is None:
            return _json_response(False, error=f"Shortcut '{shortcut_id}' not found", status=404)
        new_state = manager.toggle_dashboard_visible(shortcut_id)
        return _json_response(True, {"id": shortcut_id, "dashboard_visible": new_state})
    except Exception as exc:
        _LOG.error("Error toggling shortcut dashboard flag: %s", exc)
        return _json_response(False, error=str(exc), status=500)


async def handle_execute_shortcut(request: web.Request) -> web.Response:
    """POST /api/system-shortcuts/{id}/execute — run the shortcut against the matrix."""
    manager = get_system_shortcut_manager()
    if manager is None:
        return _json_response(False, error="System shortcut manager not initialized", status=503)
    try:
        shortcut_id = request.match_info.get("id", "")
        sc = manager.get(shortcut_id)
        if sc is None:
            return _json_response(False, error=f"Shortcut '{shortcut_id}' not found", status=404)
        if not sc.enabled:
            return _json_response(False, error=f"Shortcut '{shortcut_id}' is disabled", status=400)

        matrix_device = get_matrix_device()
        if matrix_device is None:
            return _json_response(False, error="Matrix device not available", status=503)

        result = execute_shortcut(sc, matrix_device)
        status = 200 if result.get("success") else 500
        return _json_response(result.get("success", False), result, status=status)
    except Exception as exc:
        _LOG.error("Error executing shortcut: %s", exc)
        return _json_response(False, error=str(exc), status=500)


async def handle_create_shortcut(request: web.Request) -> web.Response:
    """POST /api/system-shortcuts — create a new user shortcut."""
    manager = get_system_shortcut_manager()
    if manager is None:
        return _json_response(False, error="System shortcut manager not initialized", status=503)
    try:
        body = await request.json()
        name = body.get("name", "")
        icon = body.get("icon", "⚡")
        type_value = body.get("type", "")
        params = body.get("params", {})

        if type_value not in VALID_TYPES:
            return _json_response(
                False,
                error=f"Invalid type. Must be one of: {sorted(VALID_TYPES)}",
                status=400,
            )
        sc = manager.add_user_shortcut(name=name, icon=icon, type=type_value, params=params)
        if sc is None:
            return _json_response(False, error="Failed to create shortcut", status=400)
        return _json_response(True, sc.to_dict(), status=201)
    except json.JSONDecodeError:
        return _json_response(False, error="Invalid JSON body", status=400)
    except Exception as exc:
        _LOG.error("Error creating shortcut: %s", exc)
        return _json_response(False, error=str(exc), status=500)


async def handle_delete_shortcut(request: web.Request) -> web.Response:
    """DELETE /api/system-shortcuts/{id} — delete a user shortcut (built-ins cannot)."""
    manager = get_system_shortcut_manager()
    if manager is None:
        return _json_response(False, error="System shortcut manager not initialized", status=503)
    try:
        shortcut_id = request.match_info.get("id", "")
        sc = manager.get(shortcut_id)
        if sc is None:
            return _json_response(False, error=f"Shortcut '{shortcut_id}' not found", status=404)
        if sc.builtin:
            return _json_response(
                False,
                error="Built-in shortcuts cannot be deleted. Use PUT to disable instead.",
                status=400,
            )
        if not manager.delete(shortcut_id):
            return _json_response(False, error="Failed to delete shortcut", status=500)
        return _json_response(True, {"id": shortcut_id, "deleted": True})
    except Exception as exc:
        _LOG.error("Error deleting shortcut: %s", exc)
        return _json_response(False, error=str(exc), status=500)


async def handle_reorder_shortcuts(request: web.Request) -> web.Response:
    """PUT /api/system-shortcuts/reorder — bulk reorder by id list."""
    manager = get_system_shortcut_manager()
    if manager is None:
        return _json_response(False, error="System shortcut manager not initialized", status=503)
    try:
        body = await request.json()
        ordered_ids = body.get("ordered_ids", [])
        if not isinstance(ordered_ids, list):
            return _json_response(False, error="ordered_ids must be a list", status=400)
        if not manager.reorder(ordered_ids):
            return _json_response(False, error="Failed to reorder shortcuts", status=500)
        return _json_response(True, {"reordered": True, "count": len(ordered_ids)})
    except json.JSONDecodeError:
        return _json_response(False, error="Invalid JSON body", status=400)
    except Exception as exc:
        _LOG.error("Error reordering shortcuts: %s", exc)
        return _json_response(False, error=str(exc), status=500)