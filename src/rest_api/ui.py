"""
UI preferences endpoints for managing layouts, tab pinning, and custom sorting order.
"""

import json
import logging
from pathlib import Path

from aiohttp import web

from .utils import _json_response

_LOG = logging.getLogger("rest_api.ui")

# UI Preferences file location (within persistent /data volume)
UI_PREFS_FILE = Path(__file__).parent.parent.parent / "data" / "ui_preferences.json"

# Default tab layout settings
DEFAULT_PREFS = {
    "pinnedTabs": ["matrix", "dashboard", "inputs", "outputs", "profiles"],
    "tabOrder": ["matrix", "dashboard", "inputs", "outputs", "profiles"]
}


def _ensure_data_dir():
    """Ensure the data directory exists."""
    UI_PREFS_FILE.parent.mkdir(parents=True, exist_ok=True)


def _load_preferences() -> dict:
    """Load UI preferences from file, or return defaults."""
    try:
        if UI_PREFS_FILE.exists():
            with open(UI_PREFS_FILE, encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        _LOG.warning(f"Failed to load UI preferences: {e}")

    return DEFAULT_PREFS.copy()


def _save_preferences(data: dict) -> bool:
    """Save UI preferences to file."""
    try:
        _ensure_data_dir()
        with open(UI_PREFS_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        _LOG.error(f"Failed to save UI preferences: {e}")
        return False


async def handle_get_ui_preferences(request: web.Request) -> web.Response:
    """Get current UI preferences (pinned tabs and sorting order)."""
    prefs = _load_preferences()
    return _json_response(True, prefs)


async def handle_set_ui_preferences(request: web.Request) -> web.Response:
    """Update UI preferences persistently."""
    try:
        body = await request.json()

        pinned_tabs = body.get("pinnedTabs")
        tab_order = body.get("tabOrder")

        # Basic validations
        if not isinstance(pinned_tabs, list):
            return _json_response(False, error="pinnedTabs must be a list", status=400)
        if not isinstance(tab_order, list):
            return _json_response(False, error="tabOrder must be a list", status=400)

        # Enforce content types to be strings
        pinned_tabs = [str(t) for t in pinned_tabs]
        tab_order = [str(t) for t in tab_order]

        prefs_data = {
            "pinnedTabs": pinned_tabs,
            "tabOrder": tab_order
        }

        if _save_preferences(prefs_data):
            _LOG.info("UI preferences saved successfully")
            return _json_response(True, prefs_data)
        else:
            return _json_response(False, error="Failed to save UI preferences", status=500)

    except json.JSONDecodeError:
        return _json_response(False, error="Invalid JSON body", status=400)
    except Exception as e:
        _LOG.error(f"Error updating UI preferences: {e}")
        return _json_response(False, error=str(e), status=500)
