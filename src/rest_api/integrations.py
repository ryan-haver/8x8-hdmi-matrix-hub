"""
REST API handlers for integration discovery and auto-registration.
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

from aiohttp import web

from _file_io import atomic_write_json
from persistence import get_data_dir

# Ensure local hub package directories are discoverable even if hub was imported
# from the parent editable install.
_src_dir = Path(__file__).resolve().parent.parent
if str(_src_dir) not in sys.path:
    sys.path.insert(0, str(_src_dir))
try:
    import hub

    _local_hub_dir = str(_src_dir / "hub")
    if _local_hub_dir not in hub.__path__:
        hub.__path__.append(_local_hub_dir)
except ImportError:
    pass

try:
    from hub.integrations.flic import (
        FlicButtonRegistry,
        FlicIntegration,
    )
except ImportError:
    from src.hub.integrations.flic import (
        FlicButtonRegistry,
        FlicIntegration,
    )

_LOG = logging.getLogger("rest_api.integrations")

_default_registry = FlicButtonRegistry()
_default_integration = FlicIntegration(registry=_default_registry)

# Backward-compatibility exports and state
_registered_buttons: dict[str, dict] = _default_registry._buttons
_loaded = False

__all__ = [
    "_default_integration",
    "_default_registry",
    "_get_flic_file_path",
    "_load_buttons_if_needed",
    "_loaded",
    "_registered_buttons",
    "_save_buttons",
    "atomic_write_json",
    "get_data_dir",
    "handle_get_flic_buttons",
    "handle_register_flic_buttons",
]


def _get_flic_file_path() -> Path:
    """Return the persistent file path for registered Flic buttons."""
    return _default_registry.file_path


def _load_buttons_if_needed() -> None:
    """Load registered buttons from persistent storage if not already loaded."""
    global _loaded, _registered_buttons
    _default_registry._loaded = _loaded
    _default_registry.load_if_needed()
    _registered_buttons = _default_registry._buttons
    _loaded = _default_registry._loaded


def _save_buttons() -> bool:
    """Save the in-memory registered buttons dict to persistent storage."""
    _default_registry._buttons = _registered_buttons
    return _default_registry.save()


async def handle_register_flic_buttons(request: web.Request) -> web.Response:
    """Register Flic buttons reported by the Flic Hub SDK script."""
    global _registered_buttons, _loaded
    _default_registry._buttons = _registered_buttons
    _default_registry._loaded = _loaded
    response = await _default_integration.handle_register(request)
    _registered_buttons = _default_registry._buttons
    _loaded = _default_registry._loaded
    return response


async def handle_get_flic_buttons(request: web.Request) -> web.Response:
    """Retrieve all registered Flic buttons."""
    global _registered_buttons, _loaded
    _default_registry._buttons = _registered_buttons
    _default_registry._loaded = _loaded
    response = await _default_integration.handle_get_buttons(request)
    _registered_buttons = _default_registry._buttons
    _loaded = _default_registry._loaded
    return response
