"""
REST API handlers for integration discovery and auto-registration.
"""

from __future__ import annotations

import logging
from pathlib import Path

from aiohttp import web

import hub.integrations.flic as _flic_mod
from _file_io import atomic_write_json
from hub.integrations.flic import (
    FlicButtonRegistry,
    FlicIntegration,
)
from persistence import get_data_dir

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


def _sync_flic_hooks() -> None:
    """Propagate any monkeypatches on rest_api.integrations into hub.integrations.flic."""
    _flic_mod.atomic_write_json = atomic_write_json
    _flic_mod.get_data_dir = get_data_dir


def _active_integration(app: web.Application | None = None) -> FlicIntegration:
    """Return active runtime FlicIntegration if present, otherwise default singleton."""
    if app is not None and "hub_runtime" in app:
        runtime = app["hub_runtime"]
        if hasattr(runtime, "loader") and "flic" in runtime.loader.integrations:
            return runtime.loader.integrations["flic"]
    from rest_api.utils import get_runtime
    runtime = get_runtime()
    if runtime is not None and hasattr(runtime, "loader") and "flic" in runtime.loader.integrations:
        return runtime.loader.integrations["flic"]
    return _default_integration


def _get_flic_file_path() -> Path:
    """Return the persistent file path for registered Flic buttons."""
    _sync_flic_hooks()
    return _default_registry.file_path


def _load_buttons_if_needed() -> None:
    """Load registered buttons from persistent storage if not already loaded."""
    global _loaded, _registered_buttons
    _sync_flic_hooks()
    _default_registry._loaded = _loaded
    _default_registry.load_if_needed()
    _registered_buttons = _default_registry._buttons
    _loaded = _default_registry._loaded


def _save_buttons() -> bool:
    """Save the in-memory registered buttons dict to persistent storage."""
    _sync_flic_hooks()
    _default_registry._buttons = _registered_buttons
    return _default_registry.save(versioned=False)


async def handle_register_flic_buttons(request: web.Request) -> web.Response:
    """Register Flic buttons reported by the Flic Hub SDK script."""
    global _registered_buttons, _loaded
    _sync_flic_hooks()
    integration = _active_integration(request.app)
    integration.registry._buttons = _registered_buttons
    integration.registry._loaded = _loaded
    response = await integration.handle_register(request)
    _registered_buttons = integration.registry._buttons
    _loaded = integration.registry._loaded
    return response


async def handle_get_flic_buttons(request: web.Request) -> web.Response:
    """Retrieve all registered Flic buttons."""
    global _registered_buttons, _loaded
    _sync_flic_hooks()
    integration = _active_integration(request.app)
    integration.registry._buttons = _registered_buttons
    integration.registry._loaded = _loaded
    response = await integration.handle_get_buttons(request)
    _registered_buttons = integration.registry._buttons
    _loaded = integration.registry._loaded
    return response

