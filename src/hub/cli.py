#!/usr/bin/env python3
"""
8x8 HDMI Matrix Hub - the one runtime entry point (Docker image, local runs, tests).

The core (matrix control, REST API, web UI at /ui, kiosk at /kiosk) always runs.
Integrations are opt-in through environment variables (docs/REMEDIATION_PLAN.md D4,
D11); a disabled integration is never imported and opens no port.

Usage:
    python run.py                     # core only (UC_ENABLED defaults to false)
    UC_ENABLED=true python run.py     # core + Unfolded Circle Remote integration (port 9095)
    python run.py healthcheck         # exit 0 when /api/health answers (Docker HEALTHCHECK)

Environment variables (docs/DOCKER.md has the full table):
    MATRIX_HOST               matrix IP / host name (UC off; with UC on the Remote's setup sets it)
    MATRIX_PORT               matrix HTTPS port (default 443)
    API_PORT                  REST API + web UI port (default 8080)
    DATA_DIR                  persistent data directory (image: /data)
    LOG_LEVEL                 DEBUG | INFO | WARNING | ERROR (default INFO)
    UC_ENABLED                start the Remote 3 integration (default false)
    UC_INTEGRATION_HTTP_PORT  integration WebSocket port (default 9095, from driver.json)
    UC_INTEGRATION_INTERFACE  bind address, also the address published by mDNS
    UC_DISABLE_MDNS_PUBLISH   true = do not announce the integration by mDNS (bridge networking)
    UC_DRIVER_URL             ws://host:port the Remote should use (bridge networking)
    UC_CONFIG_HOME            integration state directory (default: DATA_DIR)

Deprecated names are still read, with one warning at start-up: OREI_HOST, OREI_PORT,
REST_API_PORT, OREI_API_PORT, MATRIX_DATA_DIR, UC_PORT, UC_DISABLE_MDNS. USE_MODULAR
and WEBUI_ENABLED are ignored: the mode follows UC_ENABLED and the web UI is part
of the core.

Both UC modes use one asynchronous runtime and the same matrix owner.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import signal
import sys
import tempfile
from collections.abc import Callable, Mapping, MutableMapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from hub.runtime_paths import SOURCE_ROOT, driver_metadata_path

PROJECT_ROOT = SOURCE_ROOT
DRIVER_JSON = driver_metadata_path()

DEFAULT_MATRIX_HOST = "192.168.0.100"
DEFAULT_MATRIX_PORT = 443
DEFAULT_API_PORT = 8080

#: Canonical name -> deprecated names still accepted (first one set wins).
ENV_ALIASES: dict[str, tuple[str, ...]] = {
    "MATRIX_HOST": ("OREI_HOST",),
    "MATRIX_PORT": ("OREI_PORT",),
    "API_PORT": ("REST_API_PORT", "OREI_API_PORT"),
    "DATA_DIR": ("MATRIX_DATA_DIR",),
    "UC_INTEGRATION_HTTP_PORT": ("UC_PORT",),
    "UC_DISABLE_MDNS_PUBLISH": ("UC_DISABLE_MDNS",),
}

#: Variables that no longer change anything, with the reason logged when they are set.
RETIRED_ENV: dict[str, str] = {
    "USE_MODULAR": "the mode follows UC_ENABLED",
    "WEBUI_ENABLED": "the web UI and kiosk are part of the core and always served",
}

_TRUE = ("1", "true", "yes", "on")

_LOG = logging.getLogger("run")


class ConfigError(Exception):
    """The environment cannot be used as given; the message says what to change."""


def env_bool(value: str | None, default: bool = False) -> bool:
    if value is None or value.strip() == "":
        return default
    return value.strip().lower() in _TRUE


def resolve_env(environ: Mapping[str, str]) -> tuple[dict[str, str], list[str]]:
    """Canonical values for every aliased name, and the deprecation notes to log.

    A canonical name always wins over its aliases. Only non-empty values count.
    """
    values: dict[str, str] = {}
    notes: list[str] = []
    for canonical, aliases in ENV_ALIASES.items():
        value = environ.get(canonical, "").strip()
        for alias in aliases:
            alias_value = environ.get(alias, "").strip()
            if not alias_value:
                continue
            if not value:
                value = alias_value
                notes.append(f"{alias} -> use {canonical}")
            elif alias_value != value:
                notes.append(f"{alias} ignored ({canonical} is set)")
        if value:
            values[canonical] = value
    for name, reason in RETIRED_ENV.items():
        if environ.get(name, "").strip():
            notes.append(f"{name} is ignored ({reason})")
    if environ.get("REST_API_ENABLED", "").strip() and not env_bool(environ["REST_API_ENABLED"], True):
        notes.append("REST_API_ENABLED=false is ignored (the REST API is the core and always runs)")
    return values, notes


def _port(name: str, value: str | None, default: int) -> int:
    if value is None:
        return default
    try:
        port = int(value)
    except ValueError:
        raise ConfigError(f"{name}={value!r} is not a port number") from None
    if not 1 <= port <= 65535:
        raise ConfigError(f"{name}={port} is outside 1-65535")
    return port


@dataclass(frozen=True)
class Settings:
    """The resolved runtime configuration."""

    matrix_host: str | None  #: None: not set (API-only mode falls back to a saved Remote setup)
    matrix_port: int
    api_port: int
    data_dir: Path | None  #: None: not set (local development defaults of the modules apply)
    log_level: str
    uc_enabled: bool
    uc_config_home: Path | None
    uc_port: int | None
    uc_interface: str | None
    uc_disable_mdns: bool
    uc_driver_url: str | None
    notes: tuple[str, ...] = ()


def load_settings(environ: Mapping[str, str]) -> Settings:
    values, notes = resolve_env(environ)
    data_dir = Path(values["DATA_DIR"]) if "DATA_DIR" in values else None
    if SOURCE_ROOT is None and data_dir is None:
        raise ConfigError("Installed runtime requires an explicit writable DATA_DIR (or MATRIX_DATA_DIR)")
    uc_home_raw = environ.get("UC_CONFIG_HOME", "").strip()
    uc_config_home = Path(uc_home_raw) if uc_home_raw else data_dir
    driver_url = environ.get("UC_DRIVER_URL", "").strip() or None
    if driver_url and not driver_url.startswith(("ws://", "wss://")):
        raise ConfigError(f"UC_DRIVER_URL={driver_url!r} must start with ws:// or wss:// (e.g. ws://192.168.1.20:9095)")
    uc_port_raw = values.get("UC_INTEGRATION_HTTP_PORT")
    log_level = environ.get("LOG_LEVEL", "INFO").strip().upper() or "INFO"
    if log_level not in ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"):
        notes.append(f"LOG_LEVEL={log_level} is not a level; using INFO")
        log_level = "INFO"
    return Settings(
        matrix_host=values.get("MATRIX_HOST"),
        matrix_port=_port("MATRIX_PORT", values.get("MATRIX_PORT"), DEFAULT_MATRIX_PORT),
        api_port=_port("API_PORT", values.get("API_PORT"), DEFAULT_API_PORT),
        data_dir=data_dir,
        log_level=log_level,
        uc_enabled=env_bool(environ.get("UC_ENABLED")),
        uc_config_home=uc_config_home,
        uc_port=_port("UC_INTEGRATION_HTTP_PORT", uc_port_raw, 0) if uc_port_raw else None,
        uc_interface=environ.get("UC_INTEGRATION_INTERFACE", "").strip() or None,
        uc_disable_mdns=env_bool(values.get("UC_DISABLE_MDNS_PUBLISH")),
        uc_driver_url=driver_url,
        notes=tuple(notes),
    )


def export_env(settings: Settings, environ: MutableMapping[str, str]) -> None:
    """Hand the canonical values to the modules under the names they read today.

    persistence.py reads MATRIX_DATA_DIR; the config managers, driver.py and ucapi
    read UC_CONFIG_HOME; driver.py reads REST_API_PORT and REST_API_ENABLED; ucapi
    reads the UC_* names. Phase 4 moves these reads into one config module.
    """
    environ["API_PORT"] = str(settings.api_port)
    environ["REST_API_PORT"] = str(settings.api_port)
    environ["REST_API_ENABLED"] = "true"
    environ["MATRIX_PORT"] = str(settings.matrix_port)
    if settings.matrix_host:
        environ["MATRIX_HOST"] = settings.matrix_host
    if settings.data_dir is not None:
        environ["DATA_DIR"] = str(settings.data_dir)
        environ["MATRIX_DATA_DIR"] = str(settings.data_dir)
    if settings.uc_config_home is not None:
        environ["UC_CONFIG_HOME"] = str(settings.uc_config_home)
    if settings.uc_port is not None:
        environ["UC_INTEGRATION_HTTP_PORT"] = str(settings.uc_port)
    if settings.uc_interface:
        environ["UC_INTEGRATION_INTERFACE"] = settings.uc_interface
    else:
        # ucapi treats an empty value as a bind address; unset means all interfaces.
        environ.pop("UC_INTEGRATION_INTERFACE", None)
    environ["UC_DISABLE_MDNS_PUBLISH"] = "true" if settings.uc_disable_mdns else "false"
    environ["UC_ENABLED"] = "true" if settings.uc_enabled else "false"


def check_writable(directory: Path) -> None:
    """Fail early with a useful message when the data directory cannot be written."""
    try:
        directory.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(dir=directory, prefix=".write-test-"):
            pass
    except OSError as exc:
        uid = os.getuid() if hasattr(os, "getuid") else "?"
        gid = os.getgid() if hasattr(os, "getgid") else "?"
        raise ConfigError(
            f"data directory {directory} is not writable by uid {uid} gid {gid} ({exc.strerror or exc}). "
            f"On the host: sudo chown -R {uid}:{gid} <your data folder> (docs/DOCKER.md, Persistent storage)"
        ) from None


def saved_matrix_address(config_home: Path | None) -> tuple[str, int] | None:
    """The matrix address a Remote integration setup saved (``config_state.json``), if any."""
    if config_home is None:
        return None
    try:
        data = json.loads((config_home / "config_state.json").read_text(encoding="utf-8"))
        host = str(data.get("host") or "").strip()
        if host:
            return host, int(data.get("port") or DEFAULT_MATRIX_PORT)
    except (OSError, ValueError, TypeError, AttributeError):
        pass
    return None


def saved_telnet_port(config_home: Path | None) -> int | None:
    """The matrix Telnet port a saved setup carries (``config_state.json`` ``telnet_port``), if any (BE-32).

    ``None`` leaves the default to the matrix client: ``OREI_TELNET_PORT``, else 23.
    """
    if config_home is None:
        return None
    try:
        data = json.loads((config_home / "config_state.json").read_text(encoding="utf-8"))
        port = int(data["telnet_port"])
    except (OSError, ValueError, TypeError, KeyError, AttributeError):
        return None
    return port if 1 <= port <= 65535 else None


def configure_logging(level: str) -> None:
    logging.basicConfig(
        level=getattr(logging, level, logging.INFO),
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    )


# ---------------------------------------------------------------------------
# Shared runtime (both UC modes)
# ---------------------------------------------------------------------------


async def run_core(settings: Settings) -> None:
    """Run both integration modes through the shared composition root."""
    from hub.runtime.composition import build_runtime

    stop = asyncio.Event()
    loop = asyncio.get_running_loop()
    installed: list[tuple[signal.Signals, Callable[..., Any] | int | None]] = []
    for sig in (signal.SIGTERM, signal.SIGINT):
        try:
            loop.add_signal_handler(sig, stop.set)
            installed.append((sig, None))
        except (NotImplementedError, RuntimeError, ValueError):
            try:
                previous = signal.getsignal(sig)
                signal.signal(sig, lambda *_: loop.call_soon_threadsafe(stop.set))
                installed.append((sig, previous))
            except (OSError, ValueError):
                pass
    runtime = startup = stopped = None
    try:
        runtime = build_runtime(settings, environ=dict(os.environ))
        startup = asyncio.create_task(runtime.start(), name="hub_startup")
        stopped = asyncio.create_task(stop.wait(), name="hub_stop_signal")
        done, _ = await asyncio.wait({startup, stopped}, return_when=asyncio.FIRST_COMPLETED)
        if startup in done:
            await startup
            _LOG.info("Hub running; ucapi imported: %s", "ucapi" in sys.modules)
            await stopped
    finally:
        try:
            if startup is not None and not startup.done():
                startup.cancel()
            if runtime is not None:
                await runtime.stop()
            if stopped is not None:
                stopped.cancel()
            await asyncio.gather(*(task for task in (startup, stopped) if task is not None), return_exceptions=True)
        finally:
            for sig, previous in installed:
                if previous is None:
                    loop.remove_signal_handler(sig)
                else:
                    signal.signal(sig, previous)


# ---------------------------------------------------------------------------
# Metadata compatibility helpers (the runtime passes metadata directly to UC)
# ---------------------------------------------------------------------------


def write_driver_metadata(driver_url: str, source: Path = DRIVER_JSON) -> Path:
    """A copy of driver.json with ``driver_url`` set, in a temporary file."""
    metadata: dict[str, Any] = json.loads(source.read_text(encoding="utf-8"))
    metadata["driver_url"] = driver_url
    fd, path = tempfile.mkstemp(prefix="hdmi-matrix-driver-", suffix=".json")
    with os.fdopen(fd, "w", encoding="utf-8") as fh:
        json.dump(metadata, fh, indent=2)
    return Path(path)


def use_driver_metadata(metadata_path: Path) -> Callable[[], None]:
    """Make ``IntegrationAPI.init`` load ``metadata_path`` instead of the driver.json it is given.

    driver.py passes a fixed "driver.json"; this keeps the driver untouched while the
    advertised URL comes from UC_DRIVER_URL (UC-03). Returns a function that undoes it.
    ``init(driver_path, setup_handler)`` is ucapi's public signature (0.5.1 through 0.7.x).
    """
    import ucapi

    original = ucapi.IntegrationAPI.init

    async def init(self: Any, driver_path: str, setup_handler: Any = None) -> Any:
        _LOG.debug("Loading driver metadata from %s instead of %s", metadata_path, driver_path)
        return await original(self, str(metadata_path), setup_handler)

    ucapi.IntegrationAPI.init = init  # type: ignore[method-assign]

    def restore() -> None:
        ucapi.IntegrationAPI.init = original  # type: ignore[method-assign]

    return restore


def run_uc_driver(settings: Settings) -> None:
    """Compatibility entry for callers; UC uses the same runtime as core mode."""
    asyncio.run(run_core(settings))


# ---------------------------------------------------------------------------


def healthcheck(environ: Mapping[str, str]) -> int:
    """Docker HEALTHCHECK: 0 when /api/health answers 200 on the configured API port."""
    import urllib.request

    try:
        port = load_settings(environ).api_port
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/api/health", timeout=5) as resp:  # noqa: S310
            return 0 if resp.status == 200 else 1
    except Exception as exc:  # noqa: BLE001
        print(f"unhealthy: {exc}", file=sys.stderr)
        return 1


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if argv[:1] == ["healthcheck"]:
        return healthcheck(os.environ)

    try:
        settings = load_settings(os.environ)
    except ConfigError as exc:
        configure_logging("INFO")
        _LOG.error("Configuration error: %s", exc)
        return 2
    configure_logging(settings.log_level)
    if settings.notes:
        _LOG.warning("Deprecated or ignored environment variables: %s (docs/DOCKER.md)", "; ".join(settings.notes))

    _LOG.info("=" * 60)
    _LOG.info("8x8 HDMI Matrix Hub")
    _LOG.info("=" * 60)
    try:
        for directory in dict.fromkeys(d for d in (settings.data_dir, settings.uc_config_home) if d is not None):
            check_writable(directory)
        export_env(settings, os.environ)
        asyncio.run(run_core(settings))
    except ConfigError as exc:
        _LOG.error("Configuration error: %s", exc)
        return 2
    except KeyboardInterrupt:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
