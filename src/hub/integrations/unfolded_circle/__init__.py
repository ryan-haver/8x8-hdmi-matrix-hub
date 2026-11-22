"""Modular Unfolded Circle Remote 3 integration package (Phase 4 / WP-C3 / R3)."""

from __future__ import annotations

import asyncio
from collections import deque
from collections.abc import Callable
from pathlib import Path
from typing import Any

from hub.integrations.base import Integration

from .bridge import UCBridge
from .config import UCIntegrationConfig, config_from_env
from .entities import (
    APPROVED_GOLDEN_ENTITY_IDS,
    CEC_COMMAND_ALIASES,
    INPUT_CEC_SIMPLE_COMMANDS,
    OUTPUT_CEC_COMMAND_SET,
    OUTPUT_CEC_SIMPLE_COMMANDS,
    STANDARD_CEC_COMMANDS,
    SURVIVING_GOLDEN_ENTITY_IDS,
    build_compatible_entities,
    build_entities,
    build_ucapi_entities,
    to_ucapi_entity,
)
from .handlers import UCCommandDispatcher
from .mdns import UC_MDNS_SERVICE_TYPE, UCMdnsPublisher
from .migration import load_config_state, migrate_legacy_config_state, save_config_state
from .setup import PendingSetup, UCSetupHandler, login_page, probe_address
from .state import EntityStateProjector

__all__ = [
    "APPROVED_GOLDEN_ENTITY_IDS",
    "CEC_COMMAND_ALIASES",
    "EntityStateProjector",
    "INPUT_CEC_SIMPLE_COMMANDS",
    "OUTPUT_CEC_COMMAND_SET",
    "OUTPUT_CEC_SIMPLE_COMMANDS",
    "PendingSetup",
    "STANDARD_CEC_COMMANDS",
    "SURVIVING_GOLDEN_ENTITY_IDS",
    "UCBridge",
    "UCCommandDispatcher",
    "UCIntegrationConfig",
    "UCMdnsPublisher",
    "UCSetupHandler",
    "UC_MDNS_SERVICE_TYPE",
    "UnfoldedCircleIntegration",
    "build_compatible_entities",
    "build_entities",
    "build_ucapi_entities",
    "config_from_env",
    "load_config_state",
    "login_page",
    "migrate_legacy_config_state",
    "probe_address",
    "save_config_state",
    "to_ucapi_entity",
]


class UnfoldedCircleIntegration(Integration):
    """Modular Unfolded Circle Remote 3 integration driven by ``HubClientLocal``."""

    name: str = "unfolded_circle"
    env_flag: str = "UC_ENABLED"
    config_from_env = staticmethod(config_from_env)

    def __init__(
        self,
        config: UCIntegrationConfig | None = None,
        *,
        mdns_publisher: UCMdnsPublisher | None = None,
        api_factory: Callable[[asyncio.AbstractEventLoop], Any] | None = None,
        driver_metadata: str | Path | dict[str, Any] | None = None,
        probe_fn: Callable[[str, int], Any] | None = None,
        compatible: bool = True,
        include_select: bool = False,
        include_legacy_sensors: bool = True,
    ) -> None:
        self.config: UCIntegrationConfig = config if config is not None else config_from_env()
        self.projector: EntityStateProjector = EntityStateProjector(
            include_select=include_select,
            include_legacy_sensors=include_legacy_sensors,
            compatible=compatible,
        )
        self.mdns: UCMdnsPublisher = (
            mdns_publisher if mdns_publisher is not None else UCMdnsPublisher(self.config)
        )
        self.bridge: UCBridge = UCBridge(
            self.config,
            self.projector,
            self.mdns,
            api_factory=api_factory,
            driver_metadata=driver_metadata,
            probe_fn=probe_fn,
        )

    def bind_runtime(
        self,
        *,
        reconfigure: Callable[..., Any] | None = None,
        current_address: Callable[[], Any] | None = None,
        driver_metadata: str | Path | dict[str, Any] | None = None,
    ) -> None:
        """Bind runtime hooks for matrix address inspection and live reconfiguration."""
        self.bridge.bind_runtime(
            reconfigure=reconfigure,
            current_address=current_address,
            driver_metadata=driver_metadata,
        )

    def routes(self) -> list[Any]:
        """UC uses its own `ucapi` WebSocket server on `config.port`, not aiohttp routes."""
        return []

    @property
    def running(self) -> bool:
        return self.bridge.running

    @property
    def standby(self) -> bool:
        return self.projector.standby

    @property
    def hub_client(self) -> Any:
        return self.bridge.hub_client

    @property
    def api(self) -> Any:
        return self.bridge.api

    @property
    def dispatcher(self) -> UCCommandDispatcher | None:
        return self.bridge.dispatcher

    @property
    def setup_handler(self) -> UCSetupHandler | None:
        return self.bridge.setup_handler

    @property
    def entities(self) -> list[dict[str, Any]]:
        return self.bridge.entities

    @property
    def migrated_config(self) -> dict[str, Any] | None:
        return self.bridge.migrated_config

    @property
    def pushed_updates(self) -> deque[dict[str, dict[str, Any]]]:
        return self.bridge.pushed_updates

    async def start(self, hub_client: Any) -> None:
        """Start the integration against ``hub_client``."""
        await self.bridge.start(hub_client)

    async def stop(self) -> None:
        """Stop the integration, close the UC server, unsubscribe from hub events, and unregister mDNS."""
        await self.bridge.stop()

    async def on_enter_standby(self) -> None:
        """Pause entity/device pushes while the Remote sleeps without disconnecting the matrix (`UC-06`, `UC-17`)."""
        await self.bridge.on_enter_standby()

    async def on_exit_standby(self) -> dict[str, dict[str, Any]]:
        """Resume pushes on wake and resync state from the hub (`UC-06`, `UC-17`)."""
        return await self.bridge.on_exit_standby()

    def health(self) -> dict[str, Any]:
        """Return structured health information for `/api/health`."""
        if not self.running:
            status = "stopped"
        elif self.projector.connected:
            status = "ok"
        else:
            status = "degraded"

        return {
            "name": self.name,
            "enabled": self.config.enabled,
            "running": self.running,
            "status": status,
            "connected": self.projector.connected,
            "device_state": self.projector.device_state,
            "standby": self.projector.standby,
            "entity_count": len(self.entities),
            "configured_entity_count": len(self.projector.configured_entities),
            "port": self.config.port,
            "mdns_published": self.mdns.published,
        }
