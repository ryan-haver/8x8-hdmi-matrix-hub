"""Configuration parsing for the modular Unfolded Circle Remote 3 integration."""

from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

DEFAULT_UC_PORT = 9095
DEFAULT_HUB_URL = "http://127.0.0.1:8080"
_TRUE_VALUES = frozenset({"1", "true", "yes", "on"})


def _parse_bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    stripped = value.strip().lower()
    if not stripped:
        return default
    return stripped in _TRUE_VALUES


def _first_non_empty(environ: Mapping[str, str], *keys: str) -> str | None:
    for key in keys:
        raw = environ.get(key)
        if raw is not None and raw.strip() != "":
            return raw.strip()
    return None


def _parse_port(raw: str | None, default: int) -> int:
    if raw is None:
        return default
    try:
        port = int(raw)
    except ValueError as exc:
        raise ValueError(f"Invalid UC integration port: {raw!r}") from exc
    if not (0 <= port <= 65535):
        raise ValueError(f"UC integration port out of range (0..65535): {port}")
    return port


@dataclass(frozen=True)
class UCIntegrationConfig:
    """Immutable configuration for the Unfolded Circle integration."""

    enabled: bool = False
    port: int = DEFAULT_UC_PORT
    interface: str | None = None
    disable_mdns_publish: bool = False
    config_home: Path = Path("./config")
    driver_url: str | None = None
    auth_token: str | None = None
    hub_url: str = DEFAULT_HUB_URL
    hub_api_key: str | None = None

    @property
    def http_port(self) -> int:
        """Alias matching UC_INTEGRATION_HTTP_PORT."""
        return self.port

    @property
    def disable_mdns(self) -> bool:
        """Alias matching UC_DISABLE_MDNS."""
        return self.disable_mdns_publish


def config_from_env(environ: Mapping[str, str] | None = None) -> UCIntegrationConfig:
    """Build :class:`UCIntegrationConfig` from environment variables.

    Supported variables:
    - ``UC_ENABLED`` (bool, default ``False``)
    - ``UC_INTEGRATION_HTTP_PORT`` (int, default ``9095``, alias ``UC_PORT``)
    - ``UC_INTEGRATION_INTERFACE`` (str | None)
    - ``UC_DISABLE_MDNS_PUBLISH`` (bool, default ``False``, alias ``UC_DISABLE_MDNS``)
    - ``UC_CONFIG_HOME`` (Path, default ``DATA_DIR`` or ``./config``)
    - ``UC_DRIVER_URL`` (str | None)
    - ``UC_AUTH_TOKEN`` (str | None, alias ``ADMIN_PIN``)
    - ``HUB_URL`` (str, default ``"http://127.0.0.1:8080"``)
    - ``HUB_API_KEY`` (str | None)
    """
    env: Mapping[str, str] = os.environ if environ is None else environ

    enabled = _parse_bool(env.get("UC_ENABLED"), default=False)
    port_raw = _first_non_empty(env, "UC_INTEGRATION_HTTP_PORT", "UC_PORT")
    port = _parse_port(port_raw, DEFAULT_UC_PORT)

    interface = _first_non_empty(env, "UC_INTEGRATION_INTERFACE")
    mdns_raw = _first_non_empty(env, "UC_DISABLE_MDNS_PUBLISH", "UC_DISABLE_MDNS")
    disable_mdns_publish = _parse_bool(mdns_raw, default=False)

    config_home_raw = _first_non_empty(env, "UC_CONFIG_HOME")
    if config_home_raw is not None:
        config_home = Path(config_home_raw)
    else:
        data_dir_raw = _first_non_empty(env, "DATA_DIR", "MATRIX_DATA_DIR")
        config_home = Path(data_dir_raw) if data_dir_raw is not None else Path("./config")

    driver_url = _first_non_empty(env, "UC_DRIVER_URL")
    if driver_url is not None and not driver_url.startswith(("ws://", "wss://")):
        raise ValueError(f"UC_DRIVER_URL must start with ws:// or wss://, got {driver_url!r}")

    auth_token = _first_non_empty(env, "UC_AUTH_TOKEN", "ADMIN_PIN")
    hub_url = _first_non_empty(env, "HUB_URL") or DEFAULT_HUB_URL
    hub_api_key = _first_non_empty(env, "HUB_API_KEY")

    return UCIntegrationConfig(
        enabled=enabled,
        port=port,
        interface=interface,
        disable_mdns_publish=disable_mdns_publish,
        config_home=config_home,
        driver_url=driver_url,
        auth_token=auth_token,
        hub_url=hub_url,
        hub_api_key=hub_api_key,
    )
