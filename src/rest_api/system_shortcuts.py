"""
Unified System Shortcuts REST API.

Exposes `/api/shortcuts` endpoints mapping to the consolidated SystemShortcut manager.
"""

import logging

from aiohttp import web

from hub.runtime.actions import catalog_changes, run_rest_action

from .utils import (
    _json_response,
    get_matrix_device,
    get_system_shortcut_manager,
    safe_error_message,
)
from .validation import (
    ICON_MAX_LENGTH,
    NAME_MAX_LENGTH,
    BadRequestError,
    optional_bool,
    optional_string,
    parse_json_object,
    validate_int,
    validate_list,
    validate_string,
)

_LOG = logging.getLogger("rest_api.system_shortcuts")


def _params_from(body: dict) -> dict:
    """The body's ``params`` object (``{}`` when absent); anything other than an object is a 400."""
    params = body.get("params")
    if params is None:
        return {}
    if not isinstance(params, dict):
        raise BadRequestError("'params' must be an object")
    return params


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
        return _json_response(False, error=safe_error_message(exc, "listing system shortcuts"), status=500)


async def handle_list_favorite_shortcuts(request: web.Request) -> web.Response:
    """GET /api/shortcuts/favorites — list favorite shortcuts only."""
    manager = get_system_shortcut_manager()
    if manager is None:
        return _json_response(False, error="System shortcut manager not initialized", status=503)
    try:
        shortcuts = manager.list_favorites()
        return _json_response(True, {"shortcuts": [s.to_dict() for s in shortcuts], "count": len(shortcuts)})
    except Exception as exc:
        return _json_response(False, error=safe_error_message(exc, "listing favorite shortcuts"), status=500)


async def handle_list_dashboard_shortcuts(request: web.Request) -> web.Response:
    """GET /api/shortcuts/dashboard — list dashboard-visible shortcuts only."""
    manager = get_system_shortcut_manager()
    if manager is None:
        return _json_response(False, error="System shortcut manager not initialized", status=503)
    try:
        shortcuts = manager.list_dashboard()
        return _json_response(True, {"shortcuts": [s.to_dict() for s in shortcuts], "count": len(shortcuts)})
    except Exception as exc:
        return _json_response(False, error=safe_error_message(exc, "listing dashboard shortcuts"), status=500)


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
        return _json_response(False, error=safe_error_message(exc, "getting shortcut"), status=500)


# =============================================================================
# Mutation Endpoints
# =============================================================================


@catalog_changes
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

        body = await parse_json_object(request)
        label = body.get("label") or body.get("name")
        order = body.get("order")

        success = manager.update_prefs(
            key,
            label=None if label is None else validate_string(label, "label", max_length=NAME_MAX_LENGTH),
            icon=optional_string(body, "icon", max_length=ICON_MAX_LENGTH),
            enabled=optional_bool(body, "enabled"),
            order=None if order is None else validate_int(order, "order", minimum=0, maximum=10_000),
            favorite=optional_bool(body, "favorite"),
            dashboard_visible=optional_bool(body, "dashboard_visible"),
        )
        if not success:
            return _json_response(False, error="Failed to update shortcut preferences", status=500)

        updated_sc = manager.get(key)
        return _json_response(True, updated_sc.to_dict())
    except BadRequestError as exc:
        return exc.response()
    except Exception as exc:
        return _json_response(False, error=safe_error_message(exc, "updating shortcut"), status=500)


@catalog_changes
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
        return _json_response(False, error=safe_error_message(exc, "toggling shortcut favorite"), status=500)


@catalog_changes
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
        return _json_response(False, error=safe_error_message(exc, "toggling shortcut dashboard flag"), status=500)


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

        params = _params_from(await parse_json_object(request, allow_empty=True))

        run = await run_rest_action("shortcut", key, params=params)
        result = run.data
        if not result:
            return _json_response(False, error=run.error, status=run.status_code)
        status = 200 if result.get("success") else 500
        return _json_response(result.get("success", False), result, status=status)
    except BadRequestError as exc:
        return exc.response()
    except Exception as exc:
        return _json_response(False, error=safe_error_message(exc, "executing shortcut"), status=500)


@catalog_changes
async def handle_reorder_shortcuts(request: web.Request) -> web.Response:
    """PUT /api/shortcuts/reorder — bulk reorder shortcuts by key list."""
    manager = get_system_shortcut_manager()
    if manager is None:
        return _json_response(False, error="System shortcut manager not initialized", status=503)
    try:
        body = await parse_json_object(request)
        ordered_ids = body.get("ordered_ids") or body.get("ordered_keys", [])
        if not isinstance(ordered_ids, list):
            return _json_response(False, error="ordered_ids must be a list", status=400)
        validate_list(ordered_ids, "ordered_ids")
        if not all(isinstance(key, str) for key in ordered_ids):
            return _json_response(False, error="ordered_ids must be a list of strings", status=400)
        if not manager.reorder(ordered_ids):
            return _json_response(False, error="Failed to reorder shortcuts", status=500)
        return _json_response(True, {"reordered": True, "count": len(ordered_ids)})
    except BadRequestError as exc:
        return exc.response()
    except Exception as exc:
        return _json_response(False, error=safe_error_message(exc, "reordering shortcuts"), status=500)


@catalog_changes
async def handle_create_shortcut(request: web.Request) -> web.Response:
    """POST /api/shortcuts — create a user-defined shortcut."""
    manager = get_system_shortcut_manager()
    if manager is None:
        return _json_response(False, error="System shortcut manager not initialized", status=503)
    try:
        body = await parse_json_object(request)
        name = body.get("name") or body.get("label")
        icon = optional_string(body, "icon", max_length=ICON_MAX_LENGTH) or "⚡"
        type = body.get("type")
        params = _params_from(body)

        if not name or not type:
            return _json_response(False, error="name and type are required fields", status=400)

        name = validate_string(name, "name", max_length=NAME_MAX_LENGTH)

        if not isinstance(type, str) or not type.strip():
            return _json_response(False, error="type must be a non-empty string", status=400)

        sc = manager.add_user_shortcut(name, icon, type, params)
        if sc is None:
            return _json_response(False, error="Failed to create shortcut. Ensure type is valid.", status=400)

        return _json_response(True, sc.to_dict(), status=201)
    except BadRequestError as exc:
        return exc.response()
    except Exception as exc:
        return _json_response(False, error=safe_error_message(exc, "creating user shortcut"), status=500)


@catalog_changes
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
        return _json_response(False, error=safe_error_message(exc, "deleting shortcut"), status=500)
