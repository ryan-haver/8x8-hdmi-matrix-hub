"""Home Assistant Zeroconf discovery integration for the 8x8 HDMI Matrix Hub."""

from __future__ import annotations

import asyncio
import inspect
import logging
import os
import socket
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from hub import __version__

_LOG = logging.getLogger("hub.integrations.homeassistant")

SERVICE_TYPE = "_orei-hdmi-matrix._tcp.local."

from hub.integrations.base import Integration, _await_cleanup


def _enabled(val: str) -> bool:
    return val.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class HomeAssistantDiscoveryConfig:
    """Configuration for Home Assistant mDNS/Zeroconf discovery."""

    enabled: bool = False
    api_port: int = 8080
    host_ip: str | None = None
    service_name: str = "OREI HDMI Matrix Hub"

    @classmethod
    def config_from_env(
        cls, environ: Mapping[str, str] | None = None
    ) -> HomeAssistantDiscoveryConfig:
        """Parse configuration from environment mapping."""
        if environ is None:
            environ = os.environ

        enabled = _enabled(environ.get("HA_DISCOVERY_ENABLED", ""))

        raw_port = environ.get("API_PORT") or environ.get("REST_API_PORT") or "8080"
        try:
            api_port = int(raw_port)
        except (ValueError, TypeError):
            api_port = 8080

        host_ip = environ.get("HOST_IP") or environ.get("API_HOST") or None
        service_name = environ.get("HA_DISCOVERY_SERVICE_NAME", "OREI HDMI Matrix Hub")

        return cls(
            enabled=enabled,
            api_port=api_port,
            host_ip=host_ip,
            service_name=service_name,
        )


class HomeAssistantDiscoveryIntegration(Integration):
    """Advertises hub on local network via Zeroconf for Home Assistant auto-discovery."""

    name: str = "homeassistant"
    env_flag: str = "HA_DISCOVERY_ENABLED"

    def __init__(
        self,
        config: HomeAssistantDiscoveryConfig | None = None,
        zeroconf: Any = None,
    ) -> None:
        self.config = config or self.config_from_env({})
        self.hub_client: Any = None
        self._zeroconf: Any = zeroconf
        self._owns_zeroconf: bool = zeroconf is None
        self._service_info: Any = None
        self._registered: bool = False
        self._started: bool = False
        self._error: str | None = None
        self._cleanup_task: asyncio.Task[None] | None = None

    @classmethod
    def config_from_env(cls, environ: Mapping[str, str]) -> HomeAssistantDiscoveryConfig:
        """Construct HomeAssistantDiscoveryConfig from environment mapping."""
        return HomeAssistantDiscoveryConfig.config_from_env(environ)

    def build_zeroconf_properties(self, snapshot: Any = None) -> dict[str, str]:
        """Build dictionary of properties advertised in the Zeroconf TXT record."""
        props: dict[str, str] = {
            "version": __version__,
            "service": "orei_hdmi_matrix",
            "api_port": str(self.config.api_port),
            "path": "/api",
        }

        if snapshot is not None:
            if hasattr(snapshot, "connected"):
                props["connected"] = "true" if snapshot.connected else "false"
            elif isinstance(snapshot, dict) and "connected" in snapshot:
                props["connected"] = "true" if snapshot["connected"] else "false"

            if hasattr(snapshot, "power"):
                props["power"] = "true" if snapshot.power else "false"
            elif isinstance(snapshot, dict) and "power" in snapshot:
                props["power"] = "true" if snapshot["power"] else "false"

            if hasattr(snapshot, "mac"):
                props["mac"] = str(snapshot.mac)
            elif isinstance(snapshot, dict) and "mac" in snapshot:
                props["mac"] = str(snapshot["mac"])

        return props

    async def start(self, hub_client: Any) -> None:
        """Start discovery and advertise service via AsyncZeroconf."""
        if self._started:
            return
        if self._service_info is not None or (self._zeroconf is not None and self._owns_zeroconf):
            await self.stop()
        self.hub_client = hub_client
        self._started = True

        if not self.config.enabled:
            _LOG.info("Home Assistant discovery is disabled (HA_DISCOVERY_ENABLED not set)")
            return

        try:
            from zeroconf import ServiceInfo
            from zeroconf.asyncio import AsyncZeroconf
        except ImportError as e:
            _LOG.warning("zeroconf library not available; discovery disabled: %s", e)
            self._error = "zeroconf library not available"
            self._registered = False
            return

        try:
            addresses: list[str] = []
            if self.config.host_ip:
                addresses.append(self.config.host_ip)

            props = self.build_zeroconf_properties()
            service_type = SERVICE_TYPE
            service_name = self.config.service_name
            full_name = f"{service_name}.{service_type}"
            server = f"{socket.gethostname().split('.')[0]}.local."

            info = ServiceInfo(
                type_=service_type,
                name=full_name,
                port=self.config.api_port,
                properties=props,
                server=server,
                parsed_addresses=addresses if addresses else None,
            )

            if self._zeroconf is None:
                self._zeroconf = AsyncZeroconf()
                self._owns_zeroconf = True

            # Registration can acquire the service before it returns or raises.
            # Retain its identity so rollback also withdraws a partial service.
            self._service_info = info
            # Preserve the established HA service type, whose service label is
            # longer than strict RFC 6763's 15-character limit.
            announcement = await self._zeroconf.async_register_service(info, strict=False)
            if inspect.isawaitable(announcement):
                await announcement
            self._registered = True
            self._error = None
            _LOG.info("Advertised Home Assistant discovery service: %s", full_name)
        except BaseException as e:
            try:
                await self.stop()
            except BaseException as cleanup_error:
                # Startup cancellation/failure remains authoritative. Failed
                # cleanup retains its resource for loader rollback or retry.
                if isinstance(e, Exception) and not isinstance(cleanup_error, Exception):
                    raise
            finally:
                self._error = "Failed to register discovery service"
            if not isinstance(e, Exception):
                raise
            _LOG.warning("Failed to register Home Assistant zeroconf discovery (%s)", type(e).__name__)

    async def stop(self) -> None:
        """Stop discovery and cleanly unregister zeroconf service."""
        if self._cleanup_task is None or self._cleanup_task.done():
            self._cleanup_task = asyncio.create_task(self._stop_resources(), name="ha-discovery-cleanup")
        await _await_cleanup(self._cleanup_task)

    async def _stop_resources(self) -> None:
        failures: list[Exception] = []
        if self._zeroconf is not None and self._service_info is not None:
            try:
                async with asyncio.timeout(2.0):
                    goodbye = await self._zeroconf.async_unregister_service(self._service_info)
                    if inspect.isawaitable(goodbye):
                        await goodbye
                _LOG.info("Unregistered Home Assistant discovery service: %s", self._service_info.name)
            except Exception as e:
                failures.append(e)
                _LOG.warning("Error unregistering Home Assistant zeroconf service (%s)", type(e).__name__)
            else:
                self._service_info = None
                self._registered = False

        if self._zeroconf is not None and self._owns_zeroconf:
            try:
                async with asyncio.timeout(2.0):
                    await self._zeroconf.async_close()
            except Exception as e:
                failures.append(e)
                _LOG.warning("Error closing AsyncZeroconf instance (%s)", type(e).__name__)
            else:
                self._zeroconf = None
                self._owns_zeroconf = False
                self._service_info = None
                self._registered = False

        self._started = False
        self.hub_client = None
        self._error = None
        if failures:
            self._error = "Failed to stop discovery service"
            raise ExceptionGroup("Home Assistant discovery shutdown failed", failures)

    def health(self) -> dict[str, Any]:
        """Report discovery integration health."""
        if not self.config.enabled:
            status = "disabled"
        elif self._error:
            status = "error"
        elif self._registered:
            status = "ok"
        else:
            status = "error"

        result = {
            "status": status,
            "enabled": self.config.enabled,
            "registered": self._registered,
            "service_name": self.config.service_name,
            "port": self.config.api_port,
        }
        if self._error:
            result["error"] = self._error
        return result

