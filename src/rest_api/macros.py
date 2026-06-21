"""
CEC Macro management endpoints.

Handles macro CRUD, execution, and testing.
"""

import json
import logging

from aiohttp import web

from .utils import _json_response, get_macro_manager

_LOG = logging.getLogger("rest_api.macros")


async def handle_list_macros(request: web.Request) -> web.Response:
    """List all saved CEC macros."""
    macro_manager = get_macro_manager()

    if macro_manager is None:
        return _json_response(False, error="Macro manager not initialized", status=503)

    try:
        macros = macro_manager.list_macros()
        return _json_response(True, {"macros": macros})
    except Exception as e:
        _LOG.error(f"Error listing macros: {e}")
        return _json_response(False, error=str(e), status=500)


async def handle_get_macro(request: web.Request) -> web.Response:
    """Get details of a specific macro."""
    macro_manager = get_macro_manager()

    if macro_manager is None:
        return _json_response(False, error="Macro manager not initialized", status=503)

    try:
        macro_id = request.match_info.get("macro_id", "")
        if not macro_id:
            return _json_response(False, error="Macro ID required", status=400)

        macro = macro_manager.get_macro(macro_id)
        if macro is None:
            return _json_response(False, error=f"Macro '{macro_id}' not found", status=404)

        return _json_response(True, macro.to_dict())
    except Exception as e:
        _LOG.error(f"Error getting macro: {e}")
        return _json_response(False, error=str(e), status=500)


async def handle_create_macro(request: web.Request) -> web.Response:
    """Create a new CEC macro."""
    macro_manager = get_macro_manager()

    if macro_manager is None:
        return _json_response(False, error="Macro manager not initialized", status=503)

    try:
        data = await request.json()

        name = data.get("name")
        steps = data.get("steps", [])
        icon = data.get("icon", "⚡")
        description = data.get("description", "")
        macro_id = data.get("id")

        if not name:
            return _json_response(False, error="Missing 'name' parameter", status=400)

        if not steps:
            return _json_response(False, error="Missing 'steps' parameter", status=400)

        # Validate steps structure
        for i, step in enumerate(steps):
            if "command" not in step:
                return _json_response(False, error=f"Step {i + 1} missing 'command'", status=400)
            if "targets" not in step or not step["targets"]:
                return _json_response(False, error=f"Step {i + 1} missing 'targets'", status=400)

        macro = macro_manager.create_macro(
            name=name,
            steps=steps,
            icon=icon,
            description=description,
            macro_id=macro_id,
        )
        _LOG.info(f"Macro '{name}' ({macro.id}) created")

        return _json_response(True, macro.to_dict())
    except json.JSONDecodeError:
        return _json_response(False, error="Invalid JSON", status=400)
    except Exception as e:
        _LOG.error(f"Error creating macro: {e}")
        return _json_response(False, error=str(e), status=500)


async def handle_update_macro(request: web.Request) -> web.Response:
    """Update an existing CEC macro."""
    macro_manager = get_macro_manager()

    if macro_manager is None:
        return _json_response(False, error="Macro manager not initialized", status=503)

    try:
        macro_id = request.match_info.get("macro_id", "")
        if not macro_id:
            return _json_response(False, error="Macro ID required", status=400)

        data = await request.json()

        name = data.get("name")
        steps = data.get("steps")
        icon = data.get("icon")
        description = data.get("description")

        # Validate steps if provided
        if steps is not None:
            for i, step in enumerate(steps):
                if "command" not in step:
                    return _json_response(False, error=f"Step {i + 1} missing 'command'", status=400)
                if "targets" not in step or not step["targets"]:
                    return _json_response(False, error=f"Step {i + 1} missing 'targets'", status=400)

        macro = macro_manager.update_macro(
            macro_id=macro_id,
            name=name,
            steps=steps,
            icon=icon,
            description=description,
        )

        if macro is None:
            return _json_response(False, error=f"Macro '{macro_id}' not found", status=404)

        _LOG.info(f"Macro '{macro_id}' updated")
        return _json_response(True, macro.to_dict())
    except json.JSONDecodeError:
        return _json_response(False, error="Invalid JSON", status=400)
    except Exception as e:
        _LOG.error(f"Error updating macro: {e}")
        return _json_response(False, error=str(e), status=500)


async def handle_delete_macro(request: web.Request) -> web.Response:
    """Delete a CEC macro."""
    macro_manager = get_macro_manager()

    if macro_manager is None:
        return _json_response(False, error="Macro manager not initialized", status=503)

    try:
        macro_id = request.match_info.get("macro_id", "")
        if not macro_id:
            return _json_response(False, error="Macro ID required", status=400)

        if macro_manager.delete_macro(macro_id):
            _LOG.info(f"Macro '{macro_id}' deleted")
            return _json_response(True, {"deleted": macro_id})
        else:
            return _json_response(False, error=f"Macro '{macro_id}' not found", status=404)
    except Exception as e:
        _LOG.error(f"Error deleting macro: {e}")
        return _json_response(False, error=str(e), status=500)


async def handle_execute_macro(request: web.Request) -> web.Response:
    """Execute a CEC macro."""
    macro_manager = get_macro_manager()

    if macro_manager is None:
        return _json_response(False, error="Macro manager not initialized", status=503)

    try:
        macro_id = request.match_info.get("macro_id", "")
        if not macro_id:
            return _json_response(False, error="Macro ID required", status=400)

        if not macro_manager.get_macro(macro_id):
            return _json_response(False, error=f"Macro '{macro_id}' not found", status=404)

        result = await macro_manager.execute_macro(macro_id)

        if result.get("success"):
            return _json_response(True, result)
        else:
            return _json_response(False, error=result.get("error", "Execution failed"), status=500)
    except Exception as e:
        _LOG.error(f"Error executing macro: {e}")
        return _json_response(False, error=str(e), status=500)


async def handle_test_macro(request: web.Request) -> web.Response:
    """Test/validate a CEC macro without executing (dry run)."""
    macro_manager = get_macro_manager()

    if macro_manager is None:
        return _json_response(False, error="Macro manager not initialized", status=503)

    try:
        macro_id = request.match_info.get("macro_id", "")
        if not macro_id:
            return _json_response(False, error="Macro ID required", status=400)

        if not macro_manager.get_macro(macro_id):
            return _json_response(False, error=f"Macro '{macro_id}' not found", status=404)

        result = await macro_manager.test_macro(macro_id)

        return _json_response(True, result)
    except Exception as e:
        _LOG.error(f"Error testing macro: {e}")
        return _json_response(False, error=str(e), status=500)


# =============================================================================
# Phase 7: Macro surface-visibility endpoints (favorite + dashboard)
# =============================================================================


async def handle_list_favorite_macros(request: web.Request) -> web.Response:
    """GET /api/cec/macros/favorites — list macros marked as favorites."""
    macro_manager = get_macro_manager()
    if macro_manager is None:
        return _json_response(False, error="Macro manager not initialized", status=503)
    try:
        macros = macro_manager.list_favorites()
        return _json_response(
            True,
            {
                "macros": [m.to_dict() for m in macros],
            },
        )
    except Exception as e:
        _LOG.error(f"Error listing favorite macros: {e}")
        return _json_response(False, error=str(e), status=500)


async def handle_toggle_macro_favorite(request: web.Request) -> web.Response:
    """POST /api/cec/macro/{id}/favorite — toggle favorite flag."""
    macro_manager = get_macro_manager()
    if macro_manager is None:
        return _json_response(False, error="Macro manager not initialized", status=503)
    try:
        macro_id = request.match_info.get("macro_id", "")
        if not macro_id:
            return _json_response(False, error="Macro ID required", status=400)
        macro = macro_manager.toggle_favorite(macro_id)
        if macro is None:
            return _json_response(False, error=f"Macro '{macro_id}' not found", status=404)
        return _json_response(
            True,
            {
                "id": macro.id,
                "favorite": macro.favorite,
            },
        )
    except Exception as e:
        _LOG.error(f"Error toggling macro favorite: {e}")
        return _json_response(False, error=str(e), status=500)


async def handle_toggle_macro_dashboard(request: web.Request) -> web.Response:
    """POST /api/cec/macro/{id}/dashboard — toggle dashboard-visible flag."""
    macro_manager = get_macro_manager()
    if macro_manager is None:
        return _json_response(False, error="Macro manager not initialized", status=503)
    try:
        macro_id = request.match_info.get("macro_id", "")
        if not macro_id:
            return _json_response(False, error="Macro ID required", status=400)
        macro = macro_manager.toggle_dashboard_visible(macro_id)
        if macro is None:
            return _json_response(False, error=f"Macro '{macro_id}' not found", status=404)
        return _json_response(
            True,
            {
                "id": macro.id,
                "dashboard_visible": macro.dashboard_visible,
            },
        )
    except Exception as e:
        _LOG.error(f"Error toggling macro dashboard flag: {e}")
        return _json_response(False, error=str(e), status=500)
