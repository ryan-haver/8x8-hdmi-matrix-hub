"""
Unified System Shortcuts REST API.

Exposes `/api/shortcuts` endpoints mapping to the consolidated SystemShortcut manager.
"""

import json
import logging

from aiohttp import web

from system_shortcuts import SystemShortcut, execute_shortcut

from .utils import (
    _json_response,
    get_matrix_device,
    get_system_shortcut_manager,
)

_LOG = logging.getLogger("rest_api.system_shortcuts")


# =============================================================================
# Query Endpoints
# =============================================================================


async def handle_list_shortcuts(request: web.Request) -> web.Response:
    """GET /api/shortcuts — list all shortcuts (with custom name/icon/order/flags)."""
    manager = get_system_shortcut_manager()
    if manager is None:
        return _json_response(False, error="System shortcut manager not initialized", status=503)
    try:
        enabled_only = request.query.get("enabled_only", "").lower() == "true"
        shortcuts = manager.list_shortcuts(enabled_only=enabled_only)
        return _json_response(True, {"shortcuts": [s.to_dict() for s in shortcuts], "count": len(shortcuts)})
    except Exception as exc:
        _LOG.error("Error listing system shortcuts: %s", exc)
        return _json_response(False, error=str(exc), status=500)


async def handle_list_favorite_shortcuts(request: web.Request) -> web.Response:
    """GET /api/shortcuts/favorites — list favorite shortcuts only."""
    manager = get_system_shortcut_manager()
    if manager is None:
        return _json_response(False, error="System shortcut manager not initialized", status=503)
    try:
        shortcuts = manager.list_favorites()
        return _json_response(True, {"shortcuts": [s.to_dict() for s in shortcuts], "count": len(shortcuts)})
    except Exception as exc:
        _LOG.error("Error listing favorite shortcuts: %s", exc)
        return _json_response(False, error=str(exc), status=500)


async def handle_list_dashboard_shortcuts(request: web.Request) -> web.Response:
    """GET /api/shortcuts/dashboard — list dashboard-visible shortcuts only."""
    manager = get_system_shortcut_manager()
    if manager is None:
        return _json_response(False, error="System shortcut manager not initialized", status=503)
    try:
        shortcuts = manager.list_dashboard()
        return _json_response(True, {"shortcuts": [s.to_dict() for s in shortcuts], "count": len(shortcuts)})
    except Exception as exc:
        _LOG.error("Error listing dashboard shortcuts: %s", exc)
        return _json_response(False, error=str(exc), status=500)


async def handle_get_shortcut(request: web.Request) -> web.Response:
    """GET /api/shortcuts/{key} — get a single shortcut."""
    manager = get_system_shortcut_manager()
    if manager is None:
        return _json_response(False, error="System shortcut manager not initialized", status=503)
    try:
        key = request.match_info.get("id") or request.match_info.get("key", "")
        if not key:
            return _json_response(False, error="Shortcut key required", status=400)
        sc = manager.get(key)
        if sc is None:
            return _json_response(False, error=f"Shortcut '{key}' not found", status=404)
        return _json_response(True, sc.to_dict())
    except Exception as exc:
        _LOG.error("Error getting shortcut: %s", exc)
        return _json_response(False, error=str(exc), status=500)


# =============================================================================
# Mutation Endpoints
# =============================================================================


async def handle_update_shortcut(request: web.Request) -> web.Response:
    """PUT /api/shortcuts/{key} — update label, icon, enabled, order, favorite, and dashboard flags."""
    manager = get_system_shortcut_manager()
    if manager is None:
        return _json_response(False, error="System shortcut manager not initialized", status=503)
    try:
        key = request.match_info.get("id") or request.match_info.get("key", "")
        if not key:
            return _json_response(False, error="Shortcut key required", status=400)
        sc = manager.get(key)
        if sc is None:
            return _json_response(False, error=f"Shortcut '{key}' not found", status=404)

        body = await request.json()

        success = manager.update_prefs(
            key,
            label=body.get("label") or body.get("name"),
            icon=body.get("icon"),
            enabled=body.get("enabled"),
            order=body.get("order"),
            favorite=body.get("favorite"),
            dashboard_visible=body.get("dashboard_visible"),
        )
        if not success:
            return _json_response(False, error="Failed to update shortcut preferences", status=500)

        updated_sc = manager.get(key)
        return _json_response(True, updated_sc.to_dict())
    except json.JSONDecodeError:
        return _json_response(False, error="Invalid JSON body", status=400)
    except Exception as exc:
        _LOG.error("Error updating shortcut %s: %s", key, exc)
        return _json_response(False, error=str(exc), status=500)


async def handle_toggle_favorite(request: web.Request) -> web.Response:
    """POST /api/shortcuts/{key}/favorite — toggle the favorite flag."""
    manager = get_system_shortcut_manager()
    if manager is None:
        return _json_response(False, error="System shortcut manager not initialized", status=503)
    try:
        key = request.match_info.get("id") or request.match_info.get("key", "")
        sc = manager.get(key)
        if sc is None:
            return _json_response(False, error=f"Shortcut '{key}' not found", status=404)
        new_state = manager.toggle_favorite(key)
        return _json_response(True, {"id": key, "key": key, "favorite": new_state})
    except Exception as exc:
        _LOG.error("Error toggling shortcut favorite: %s", exc)
        return _json_response(False, error=str(exc), status=500)


async def handle_toggle_dashboard(request: web.Request) -> web.Response:
    """POST /api/shortcuts/{key}/dashboard — toggle the dashboard_visible flag."""
    manager = get_system_shortcut_manager()
    if manager is None:
        return _json_response(False, error="System shortcut manager not initialized", status=503)
    try:
        key = request.match_info.get("id") or request.match_info.get("key", "")
        sc = manager.get(key)
        if sc is None:
            return _json_response(False, error=f"Shortcut '{key}' not found", status=404)
        new_state = manager.toggle_dashboard_visible(key)
        return _json_response(True, {"id": key, "key": key, "dashboard_visible": new_state})
    except Exception as exc:
        _LOG.error("Error toggling shortcut dashboard flag: %s", exc)
        return _json_response(False, error=str(exc), status=500)


async def handle_execute_shortcut(request: web.Request) -> web.Response:
    """POST /api/shortcuts/{key}/execute — execute the shortcut against the matrix."""
    manager = get_system_shortcut_manager()
    if manager is None:
        return _json_response(False, error="System shortcut manager not initialized", status=503)
    try:
        key = request.match_info.get("id") or request.match_info.get("key", "")
        sc = manager.get(key)
        if sc is None:
            return _json_response(False, error=f"Shortcut '{key}' not found", status=404)
        if not sc.enabled:
            return _json_response(False, error=f"Shortcut '{key}' is disabled", status=400)

        matrix = get_matrix_device()
        if matrix is None:
            return _json_response(False, error="Matrix device not connected", status=503)

        data = await request.json() if request.can_read_body else {}
        params = data.get("params", {})

        result = await execute_shortcut(sc, matrix, params)
        status = 200 if result.get("success") else 500
        return _json_response(result.get("success", False), result, status=status)
    except Exception as exc:
        _LOG.error("Error executing shortcut %s: %s", key, exc)
        return _json_response(False, error=str(exc), status=500)


async def handle_reorder_shortcuts(request: web.Request) -> web.Response:
    """PUT /api/shortcuts/reorder — bulk reorder shortcuts by key list."""
    manager = get_system_shortcut_manager()
    if manager is None:
        return _json_response(False, error="System shortcut manager not initialized", status=503)
    try:
        body = await request.json()
        ordered_ids = body.get("ordered_ids") or body.get("ordered_keys", [])
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


async def handle_create_shortcut(request: web.Request) -> web.Response:
    """POST /api/shortcuts — create a user-defined shortcut."""
    manager = get_system_shortcut_manager()
    if manager is None:
        return _json_response(False, error="System shortcut manager not initialized", status=503)
    try:
        body = await request.json()
        name = body.get("name") or body.get("label")
        icon = body.get("icon", "⚡")
        type = body.get("type")
        params = body.get("params", {})

        if not name or not type:
            return _json_response(False, error="name and type are required fields", status=400)

        sc = manager.add_user_shortcut(name, icon, type, params)
        if sc is None:
            return _json_response(False, error="Failed to create shortcut. Ensure type is valid.", status=400)

        return _json_response(True, sc.to_dict(), status=201)
    except json.JSONDecodeError:
        return _json_response(False, error="Invalid JSON body", status=400)
    except Exception as exc:
        _LOG.error("Error creating user shortcut: %s", exc)
        return _json_response(False, error=str(exc), status=500)


async def handle_delete_shortcut(request: web.Request) -> web.Response:
    """DELETE /api/shortcuts/{key} — delete a user-defined shortcut."""
    manager = get_system_shortcut_manager()
    if manager is None:
        return _json_response(False, error="System shortcut manager not initialized", status=503)
    try:
        key = request.match_info.get("id") or request.match_info.get("key", "")
        if not key:
            return _json_response(False, error="Shortcut key required", status=400)

        sc = manager.get(key)
        if sc is None:
            return _json_response(False, error=f"Shortcut '{key}' not found", status=404)

        if sc.builtin:
            return _json_response(False, error="Built-in shortcuts cannot be deleted", status=400)

        success = manager.delete(key)
        if not success:
            return _json_response(False, error="Failed to delete shortcut", status=500)

        return _json_response(True, {"deleted": True, "id": key, "key": key})
    except Exception as exc:
        _LOG.error("Error deleting shortcut %s: %s", key, exc)
        return _json_response(False, error=str(exc), status=500)
