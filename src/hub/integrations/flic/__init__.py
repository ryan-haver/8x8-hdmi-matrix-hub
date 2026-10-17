"""Flic button modular integration for the 8x8 HDMI Matrix Hub."""

from __future__ import annotations

import json
import logging
import os
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from aiohttp import web

from _file_io import atomic_write_json
from persistence import get_data_dir

_LOG = logging.getLogger("hub.integrations.flic")

# Base class fallback if integration framework base is not yet merged
try:
    from hub.integrations.base import Integration
except ImportError:
    try:
        from src.hub.integrations.base import Integration  # type: ignore[no-redef]
    except ImportError:
        class Integration:  # type: ignore[no-redef]
            """Fallback base class when integration framework base is not present."""

            name: str
            env_flag: str

            def routes(self) -> list[Any]:
                return []


@dataclass(frozen=True)
class FlicIntegrationConfig:
    """Configuration for the Flic button integration."""

    enabled: bool = True
    data_dir: Path | None = None

    @classmethod
    def config_from_env(cls, environ: Mapping[str, str] | None = None) -> FlicIntegrationConfig:
        """Parse configuration from environment mapping.

        Note: FLIC_ENABLED defaults to True unless explicitly set to
        "false" / "0" / "no" / "off" so existing /api/integrations/flic/*
        routes continue working by default while supporting opt-out.
        """
        if environ is None:
            environ = os.environ

        raw_enabled = environ.get("FLIC_ENABLED", "")
        if raw_enabled:
            enabled = raw_enabled.strip().lower() not in {"0", "false", "no", "off"}
        else:
            enabled = True

        data_dir_raw = environ.get("MATRIX_DATA_DIR")
        if data_dir_raw:
            data_dir = Path(data_dir_raw)
        elif "UC_CONFIG_HOME" in environ:
            data_dir = Path(environ["UC_CONFIG_HOME"]) / "data"
        else:
            data_dir = None

        return cls(enabled=enabled, data_dir=data_dir)


class FlicButtonRegistry:
    """Manages persistent registration of Flic buttons."""

    def __init__(self, data_dir: Path | None = None, file_path: Path | None = None) -> None:
        self._data_dir = data_dir
        self._file_path = file_path
        self._buttons: dict[str, dict[str, Any]] = {}
        self._loaded: bool = False

    @property
    def file_path(self) -> Path:
        """Return the persistent file path for registered Flic buttons."""
        if self._file_path is not None:
            return self._file_path
        base = self._data_dir if self._data_dir is not None else get_data_dir()
        return base / "flic_buttons.json"

    def load_if_needed(self, force: bool = False) -> None:
        """Load registered buttons from persistent storage if not already loaded."""
        if self._loaded and not force:
            return

        target_file = self.file_path
        if target_file.exists():
            try:
                with open(target_file, encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        self._buttons = data
                    elif isinstance(data, list):
                        # Convert legacy list structure to dict
                        self._buttons = {
                            btn["bdaddr"]: btn
                            for btn in data
                            if isinstance(btn, dict) and "bdaddr" in btn
                        }
                _LOG.info("Loaded %d registered Flic buttons from storage", len(self._buttons))
            except Exception as e:
                _LOG.warning("Failed to load registered Flic buttons: %s", e)
        self._loaded = True

    def save(self) -> bool:
        """Save the in-memory registered buttons dict to persistent storage."""
        try:
            atomic_write_json(self.file_path, self._buttons, indent=4)
            return True
        except Exception as e:
            _LOG.warning("Failed to save registered Flic buttons: %s", e)
            return False

    def register_buttons(self, buttons: list[dict[str, Any]]) -> int:
        """Register buttons reported by Flic hub or API client.

        Returns total count of registered buttons.
        """
        self.load_if_needed()
        if not isinstance(buttons, list):
            raise ValueError("Buttons payload must be a list")

        previous = self._buttons.copy()
        updated = False
        for btn in buttons:
            if not isinstance(btn, dict) or "bdaddr" not in btn:
                continue
            bdaddr = btn["bdaddr"]
            name = btn.get("name", bdaddr)

            if bdaddr not in self._buttons or self._buttons[bdaddr].get("name") != name:
                self._buttons[bdaddr] = {
                    "bdaddr": bdaddr,
                    "name": name,
                    "serial": btn.get("serial", ""),
                }
                updated = True

        if updated:
            if not self.save():
                self._buttons = previous
                raise RuntimeError("Failed to save registered Flic buttons")
            _LOG.info("Registered/updated Flic buttons. Total active: %d", len(self._buttons))

        return len(self._buttons)

    def list_buttons(self) -> list[dict[str, Any]]:
        """Return list of all registered buttons."""
        self.load_if_needed()
        return list(self._buttons.values())

    def __len__(self) -> int:
        self.load_if_needed()
        return len(self._buttons)


class FlicIntegration(Integration):
    """Modular integration for Flic smart buttons."""

    name: str = "flic"
    env_flag: str = "FLIC_ENABLED"

    def __init__(
        self,
        config: FlicIntegrationConfig | None = None,
        registry: FlicButtonRegistry | None = None,
    ) -> None:
        self.config = config or self.config_from_env({})
        self.registry = registry or FlicButtonRegistry(data_dir=self.config.data_dir)
        self.hub_client: Any = None
        self._started: bool = False

    @classmethod
    def config_from_env(cls, environ: Mapping[str, str]) -> FlicIntegrationConfig:
        """Construct FlicIntegrationConfig from environment mapping."""
        return FlicIntegrationConfig.config_from_env(environ)

    async def start(self, hub_client: Any) -> None:
        """Start the Flic integration and load persisted buttons."""
        self.hub_client = hub_client
        if self.config.enabled:
            self.registry.load_if_needed()
        self._started = True

    async def stop(self) -> None:
        """Stop the Flic integration."""
        self._started = False
        self.hub_client = None

    def health(self) -> dict[str, Any]:
        """Report integration health and registered button count."""
        return {
            "status": "ok" if self.config.enabled else "disabled",
            "enabled": self.config.enabled,
            "registered_buttons_count": len(self.registry) if self.config.enabled else 0,
        }

    async def handle_register(self, request: web.Request) -> web.Response:
        """Handle POST /api/integrations/flic/register."""
        try:
            from rest_api.utils import _json_response, safe_error_message
            from rest_api.validation import BadRequestError, parse_json_object
        except ImportError:
            from src.rest_api.utils import _json_response, safe_error_message
            from src.rest_api.validation import BadRequestError, parse_json_object

        try:
            body = await parse_json_object(request)
            buttons = body.get("buttons", [])
            if not isinstance(buttons, list):
                return _json_response(False, error="Invalid buttons payload", status=400)
            count = self.registry.register_buttons(buttons)
            return _json_response(True, {"count": count})
        except BadRequestError as e:
            return _json_response(False, error=str(e), status=400)
        except RuntimeError as e:
            return _json_response(False, error=str(e), status=500)
        except Exception as e:
            return _json_response(
                False, error=safe_error_message(e, "registering Flic buttons"), status=500
            )

    async def handle_get_buttons(self, request: web.Request) -> web.Response:
        """Handle GET /api/integrations/flic/buttons."""
        try:
            from rest_api.utils import _json_response, safe_error_message
        except ImportError:
            from src.rest_api.utils import _json_response, safe_error_message

        try:
            buttons = self.registry.list_buttons()
            return _json_response(True, {"buttons": buttons})
        except Exception as e:
            return _json_response(
                False, error=safe_error_message(e, "retrieving Flic buttons"), status=500
            )

    def routes(self) -> list[tuple[str, str, Callable]]:
        """Return integration routes."""
        return [
            ("POST", "/api/integrations/flic/register", self.handle_register),
            ("GET", "/api/integrations/flic/buttons", self.handle_get_buttons),
        ]
