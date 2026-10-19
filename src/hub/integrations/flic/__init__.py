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
from hub.persistence import (
    MigrationError,
    SchemaVersionError,
    block_reason,
    flat_map_records,
    is_write_blocked,
    load_versioned_json,
    save_versioned_json,
)
from hub.persistence.migrations import assert_writable
from persistence import get_data_dir

_LOG = logging.getLogger("hub.integrations.flic")

from hub.integrations.base import Integration


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
        self._metadata: dict[str, Any] = {}
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
                raw = load_versioned_json(target_file, default=None)
                if raw is not None:
                    if isinstance(raw, Mapping):
                        records = flat_map_records("flic_buttons.json", raw)
                        if not records:
                            records = {
                                k: dict(v)
                                for k, v in raw.items()
                                if k != "schema_version" and isinstance(v, Mapping) and "bdaddr" in v
                            }
                        self._buttons.clear()
                        self._buttons.update(records)
                        self._metadata = {k: v for k, v in raw.items() if k not in self._buttons}
                    elif isinstance(raw, list):
                        records = {
                            (btn.get("bdaddr") or btn.get("address")): dict(btn)
                            for btn in raw
                            if isinstance(btn, Mapping) and (btn.get("bdaddr") or btn.get("address"))
                        }
                        self._buttons.clear()
                        self._buttons.update(records)
                        self._metadata = {}
                    else:
                        self._buttons.clear()
                        self._metadata = {}
                else:
                    self._buttons.clear()
                    self._metadata = {}
                _LOG.info("Loaded %d registered Flic buttons from storage", len(self._buttons))
            except (MigrationError, SchemaVersionError) as e:
                _LOG.warning("Failed to load registered Flic buttons: %s", e)
                self._buttons.clear()
                self._metadata = {}
            except Exception as e:
                _LOG.warning("Failed to load registered Flic buttons: %s", e)
                self._buttons.clear()
                self._metadata = {}
        else:
            self._buttons.clear()
            self._metadata = {}
        self._loaded = True

    def save(self, *, versioned: bool = True) -> bool:
        """Save the in-memory registered buttons dict to persistent storage."""
        if is_write_blocked(self.file_path):
            _LOG.error("Refusing to save %s: %s", self.file_path.name, block_reason(self.file_path))
            return False
        try:
            if versioned:
                payload = dict(self._metadata)
                payload.update(self._buttons)
                return save_versioned_json(self.file_path, payload, indent=4)
            else:
                assert_writable(self.file_path)
                payload = dict(self._metadata)
                payload.update(self._buttons)
                atomic_write_json(self.file_path, payload, indent=4)
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

        previous = {k: dict(v) for k, v in self._buttons.items()}
        updated = False
        for btn in buttons:
            if not isinstance(btn, dict) or "bdaddr" not in btn:
                continue
            bdaddr = btn["bdaddr"]
            name = btn.get("name", bdaddr)
            serial = btn.get("serial", "")

            existing = self._buttons.get(bdaddr)
            if existing is None or existing.get("name") != name or existing.get("serial") != serial:
                new_btn = dict(existing) if existing else {"bdaddr": bdaddr}
                new_btn["bdaddr"] = bdaddr
                new_btn["name"] = name
                new_btn["serial"] = serial
                self._buttons[bdaddr] = new_btn
                updated = True

        if updated:
            if not self.save():
                self._buttons.clear()
                self._buttons.update(previous)
                raise RuntimeError("Failed to save registered Flic buttons")
            _LOG.info("Registered/updated Flic buttons. Total active: %d", len(self._buttons))

        return len(self._buttons)

    def list_buttons(self) -> list[dict[str, Any]]:
        """Return list of all registered buttons with only established public fields."""
        self.load_if_needed()
        return [
            {
                "bdaddr": b.get("bdaddr", k),
                "name": b.get("name", b.get("bdaddr", k)),
                "serial": b.get("serial", ""),
            }
            for k, b in self._buttons.items()
        ]

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
        self.config = config if config is not None else self.config_from_env({})
        self.registry = (
            registry
            if registry is not None
            else FlicButtonRegistry(data_dir=self.config.data_dir)
        )
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
        from rest_api.utils import _json_response, safe_error_message
        from rest_api.validation import BadRequestError, parse_json_object

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
        from rest_api.utils import _json_response, safe_error_message

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
