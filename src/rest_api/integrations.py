"""
REST API handlers for integration discovery and auto-registration.
"""

import json
import logging
from pathlib import Path

from aiohttp import web

from persistence import get_data_dir

from .utils import _json_response

_LOG = logging.getLogger("rest_api.integrations")

_registered_buttons = {}
_loaded = False


def _get_flic_file_path() -> Path:
    """Return the persistent file path for registered Flic buttons."""
    return get_data_dir() / "flic_buttons.json"


def _load_buttons_if_needed():
    """Load registered buttons from persistent storage if not already loaded."""
    global _loaded, _registered_buttons
    if _loaded:
        return

    file_path = _get_flic_file_path()
    if file_path.exists():
        try:
            with open(file_path, encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict):
                    _registered_buttons = data
                elif isinstance(data, list):
                    # Convert legacy list structure to dict
                    _registered_buttons = {btn["bdaddr"]: btn for btn in data if "bdaddr" in btn}
            _LOG.info(f"Loaded {len(_registered_buttons)} registered Flic buttons from storage")
        except Exception as e:
            _LOG.warning(f"Failed to load registered Flic buttons: {e}")
    _loaded = True


def _save_buttons():
    """Save the in-memory registered buttons dict to persistent storage."""
    file_path = _get_flic_file_path()
    try:
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(_registered_buttons, f, indent=4)
    except Exception as e:
        _LOG.warning(f"Failed to save registered Flic buttons: {e}")


async def handle_register_flic_buttons(request: web.Request) -> web.Response:
    """Register Flic buttons reported by the Flic Hub SDK script."""
    try:
        _load_buttons_if_needed()
        body = await request.json()
        buttons = body.get("buttons", [])

        if not isinstance(buttons, list):
            return _json_response(False, error="Invalid buttons payload", status=400)

        updated = False
        for btn in buttons:
            if not isinstance(btn, dict) or "bdaddr" not in btn:
                continue
            bdaddr = btn["bdaddr"]
            name = btn.get("name", bdaddr)

            # Check if this button is new or its name has changed
            if bdaddr not in _registered_buttons or _registered_buttons[bdaddr].get("name") != name:
                _registered_buttons[bdaddr] = {
                    "bdaddr": bdaddr,
                    "name": name,
                    "serial": btn.get("serial", ""),
                }
                updated = True

        if updated:
            _save_buttons()
            _LOG.info(f"Registered/updated Flic buttons. Total active: {len(_registered_buttons)}")

        return _json_response(True, {"count": len(_registered_buttons)})
    except Exception as e:
        _LOG.exception(f"Error registering Flic buttons: {e}")
        return _json_response(False, error=str(e), status=500)


async def handle_get_flic_buttons(request: web.Request) -> web.Response:
    """Retrieve all registered Flic buttons."""
    try:
        _load_buttons_if_needed()
        return _json_response(True, {"buttons": list(_registered_buttons.values())})
    except Exception as e:
        _LOG.exception(f"Error retrieving Flic buttons: {e}")
        return _json_response(False, error=str(e), status=500)
