"""Address resolution shared by REST and Remote setup."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from hub.runtime_paths import default_config_dir

if TYPE_CHECKING:
    from hub.cli import Settings


@dataclass(frozen=True)
class MatrixAddress:
    host: str
    port: int = 443
    telnet_port: int | None = None
    user: str | None = None
    password: str | None = field(default=None, repr=False)


@dataclass(frozen=True)
class ReconfigureResult:
    success: bool
    error_kind: str | None = None
    connected: bool = False


def resolve_matrix_address(settings: Settings) -> MatrixAddress | None:
    """Keep credentials bound to the saved UC address and preserve core precedence."""
    saved = None
    home = settings.uc_config_home or default_config_dir(data_dir=settings.data_dir)
    primary = home / "config_state.json"
    source = primary if primary.exists() else home / "config_state.json.migrated"
    try:
        data = json.loads(source.read_text(encoding="utf-8"))
        host = data.get("host")
        port = int(data.get("port") or 443)
        telnet = data.get("telnet_port")
        telnet = int(telnet) if telnet is not None else None
        if isinstance(host, str) and host.strip() and 1 <= port <= 65535 and (telnet is None or 1 <= telnet <= 65535):
            saved = MatrixAddress(
                host.strip(),
                port,
                telnet,
                data.get("user") if settings.uc_enabled else None,
                data.get("password") if settings.uc_enabled else None,
            )
    except (OSError, ValueError, TypeError, AttributeError):
        pass
    if settings.uc_enabled and saved:
        return saved
    if settings.matrix_host:
        return MatrixAddress(settings.matrix_host, settings.matrix_port)
    if saved:
        return saved
    return None if settings.uc_enabled else MatrixAddress("192.168.0.100", settings.matrix_port)
