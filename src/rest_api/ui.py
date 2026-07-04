"""
UI preferences endpoints for managing layouts, tab pinning, and custom sorting order.

The storage location is resolved from the persistent data directory, which is
controlled by the ``MATRIX_DATA_DIR`` or ``UC_CONFIG_HOME`` environment
variables. See :mod:`persistence` for resolution details.
"""

import json
import logging
from pathlib import Path

from aiohttp import web

from persistence import ensure_data_dir, get_data_dir, migrate_legacy_file

from .utils import _json_response

_LOG = logging.getLogger("rest_api.ui")

# UI Preferences file (resolved from persistent data dir at init time)
_UI_PREFS_FILE = "ui_preferences.json"
_ui_prefs_path: Path | None = None

# Default tab layout settings
DEFAULT_PREFS = {
    "pinnedTabs": ["matrix", "dashboard", "inputs", "outputs", "profiles"],
    "tabOrder": ["matrix", "dashboard", "inputs", "outputs", "profiles"],
}


def init_ui_preferences(data_dir: Path | None = None):
    """Initialize UI preferences storage with the persistent data directory.

    :param data_dir: Explicit data directory (defaults to
                     ``persistence.get_data_dir()`` which honors
                     ``MATRIX_DATA_DIR`` and ``UC_CONFIG_HOME`` env vars).
    """
    global _ui_prefs_path

    if data_dir is None:
        data_dir = get_data_dir()

    ensure_data_dir(data_dir)
    target = data_dir / _UI_PREFS_FILE
    migrate_legacy_file(target, _UI_PREFS_FILE)

    _ui_prefs_path = target
    _LOG.info(f"UI preferences storage initialized at {_ui_prefs_path}")


def _resolve_ui_prefs_path() -> Path:
    """Return the current UI prefs path, lazily resolving it if not initialized."""
    global _ui_prefs_path
    if _ui_prefs_path is None:
        init_ui_preferences()
    assert _ui_prefs_path is not None
    return _ui_prefs_path


def _load_preferences() -> dict:
    """Load UI preferences from file, or return defaults."""
    path = _resolve_ui_prefs_path()
    try:
        if path.exists():
            with open(path, encoding="utf-8") as f:
                return json.load(f)
    except Exception as e:
        _LOG.warning(f"Failed to load UI preferences: {e}")

    return DEFAULT_PREFS.copy()


def _save_preferences(data: dict) -> bool:
    """Save UI preferences to file."""
    path = _resolve_ui_prefs_path()
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        from _file_io import atomic_write_json
        atomic_write_json(path, data)
        return True
    except Exception as e:
        _LOG.exception(f"Failed to save UI preferences: {e}")
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

        prefs_data = {"pinnedTabs": pinned_tabs, "tabOrder": tab_order}

        if _save_preferences(prefs_data):
            _LOG.info("UI preferences saved successfully")
            return _json_response(True, prefs_data)
        else:
            return _json_response(False, error="Failed to save UI preferences", status=500)

    except json.JSONDecodeError:
        return _json_response(False, error="Invalid JSON body", status=400)
    except Exception as e:
        _LOG.exception(f"Error updating UI preferences: {e}")
        return _json_response(False, error=str(e), status=500)
