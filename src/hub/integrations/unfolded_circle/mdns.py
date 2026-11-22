"""Direct mDNS publisher and clean unregistration for the Unfolded Circle integration (UC-11, UC-02)."""

from __future__ import annotations

import asyncio
import contextlib
import logging
import socket
from typing import Any

from zeroconf import IPVersion
from zeroconf.asyncio import AsyncServiceInfo, AsyncZeroconf

from hub import __version__

from .config import UCIntegrationConfig

_LOG = logging.getLogger("uc.mdns")

UC_MDNS_SERVICE_TYPE = "_uc-integration._tcp.local."


def _detect_local_ip(preferred: str | None) -> str:
    """Return a routable IPv4 address for mDNS, never advertising ``0.0.0.0`` (`UC-11`)."""
    if preferred and preferred.strip() and preferred.strip() != "0.0.0.0":
        return preferred.strip()
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.connect(("192.0.2.1", 80))
            ip = sock.getsockname()[0]
            if ip and ip != "0.0.0.0":
                return ip
    except OSError:
        pass
    return "127.0.0.1"


class UCMdnsPublisher:
    """Publishes and cleanly unregisters ``_uc-integration._tcp.local.`` mDNS records (`UC-11`, `UC-02`)."""

    def __init__(
        self,
        config: UCIntegrationConfig | None = None,
        *,
        driver_id: str = "hdmi_matrix",
        name: str = "HDMI Matrix",
        version: str = __version__,
        developer: str = "Ryan Haver",
        port: int | None = None,
        interface: str | None = None,
        auth_token: str | None = None,
        disable_mdns: bool | None = None,
        zeroconf: Any = None,
    ) -> None:
        self.driver_id = driver_id
        self.name = name
        self.version = version
        self.developer = developer
        self.port = port if port is not None else (config.port if config else 9095)
        self.interface = interface if interface is not None else (config.interface if config else None)
        self.auth_token = auth_token if auth_token is not None else (config.auth_token if config else None)
        self.disable_mdns = (
            disable_mdns
            if disable_mdns is not None
            else (config.disable_mdns_publish if config else False)
        )
        self._zeroconf = zeroconf
        self._owns_zeroconf = False
        self._registered_info: Any = None
        self.published: bool = False

    def txt_properties(self) -> dict[str, str]:
        """Build the mDNS TXT record dictionary (`ver`, `developer`, and optional `pwd` per `UC-02`)."""
        props: dict[str, str] = {
            "name": self.name,
            "ver": self.version,
            "developer": self.developer,
        }
        if self.auth_token and self.auth_token.strip():
            props["pwd"] = "true"
        return props

    def build_service_info(self) -> dict[str, Any]:
        """Construct the `_uc-integration._tcp.local.` service descriptor."""
        ip_addr = _detect_local_ip(self.interface)
        hostname = socket.gethostname().split(".")[0] or "hdmi-matrix-hub"
        props = self.txt_properties()
        try:
            packed_ip = socket.inet_aton(ip_addr)
        except OSError:
            packed_ip = socket.inet_aton("127.0.0.1")

        return {
            "type": UC_MDNS_SERVICE_TYPE,
            "name": f"{self.driver_id}.{UC_MDNS_SERVICE_TYPE}",
            "server": f"{hostname}.local.",
            "port": self.port,
            "address": ip_addr,
            "addresses": [packed_ip],
            "properties": dict(props),
            "txt": dict(props),
        }

    def _build_zeroconf_service_info(self, info: dict[str, Any]) -> AsyncServiceInfo:
        return AsyncServiceInfo(
            info["type"],
            info["name"],
            addresses=info["addresses"],
            port=info["port"],
            properties=info["properties"],
            server=info["server"],
        )

    async def start(self) -> bool:
        """Publish the mDNS service unless disabled or already published."""
        if self.disable_mdns:
            _LOG.info("UC mDNS advertisement disabled (UC_DISABLE_MDNS_PUBLISH=true)")
            return False
        if self.published:
            return True

        info = self.build_service_info()
        created_zc: AsyncZeroconf | None = None
        try:
            if self._zeroconf is None:
                created_zc = AsyncZeroconf(ip_version=IPVersion.V4Only)
                self._zeroconf = created_zc
                self._owns_zeroconf = True
                zc_info = self._build_zeroconf_service_info(info)
                await self._register_with_backend(self._zeroconf, zc_info)
                self._registered_info = zc_info
            else:
                await self._register_with_backend(self._zeroconf, info)
                self._registered_info = info
        except BaseException:
            self._registered_info = None
            if created_zc is not None:
                self._zeroconf = None
                self._owns_zeroconf = False
                with contextlib.suppress(Exception):
                    await created_zc.async_close()
            raise

        self.published = True
        _LOG.info(
            "Published %s on %s:%d (pwd=%s)",
            info["name"],
            info["address"],
            info["port"],
            "pwd" in info["properties"],
        )
        return True

    async def stop(self) -> None:
        """Unregister the mDNS service cleanly (`UC-11`)."""
        if not self.published and not self._owns_zeroconf:
            return

        info = self._registered_info
        self._registered_info = None
        was_published = self.published
        self.published = False

        try:
            if was_published and self._zeroconf is not None and info is not None:
                await self._unregister_with_backend(self._zeroconf, info)
        finally:
            if self._owns_zeroconf and self._zeroconf is not None:
                zc = self._zeroconf
                self._zeroconf = None
                self._owns_zeroconf = False
                close_fn = getattr(zc, "async_close", None) or getattr(zc, "close", None)
                if close_fn is not None:
                    res = close_fn()
                    if asyncio.iscoroutine(res):
                        await res

        if was_published:
            _LOG.info("Unregistered UC mDNS service")

    @staticmethod
    async def _register_with_backend(zc: Any, info: Any) -> None:
        reg = getattr(zc, "async_register_service", None) or getattr(zc, "register_service", None)
        if reg is not None:
            res = reg(info)
            if asyncio.iscoroutine(res):
                await res

    @staticmethod
    async def _unregister_with_backend(zc: Any, info: Any) -> None:
        unreg = getattr(zc, "async_unregister_service", None) or getattr(zc, "unregister_service", None)
        if unreg is not None:
            res = unreg(info)
            if asyncio.iscoroutine(res):
                await res
