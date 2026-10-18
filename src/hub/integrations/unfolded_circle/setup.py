"""Unfolded Circle Remote setup, authorization, login page, and reconfigure flow (UC-02, UC-05, BE-02, BE-10)."""

from __future__ import annotations

import asyncio
import hmac
import logging
import os
import re
import socket
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from typing import Any

import ucapi

from .config import UCIntegrationConfig

_LOG = logging.getLogger("uc.setup")

HOST_PATTERN = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9.-]{0,251}[A-Za-z0-9])?$")


@dataclass(frozen=True)
class _FallbackMatrixAddress:
    """Structural equivalent of ``hub.runtime.config.MatrixAddress`` when R1 is not imported."""

    host: str
    port: int = 443
    telnet_port: int | None = None
    user: str | None = None
    password: str | None = field(default=None, repr=False)


@dataclass(frozen=True)
class _ResolvedCurrentAddress:
    """Internal normalized view of the current matrix address and credential state."""

    host: str
    port: int = 443
    telnet_port: int | None = 23
    user: str | None = None
    password: str | None = field(default=None, repr=False)
    effective_password: str = field(default="admin", repr=False)
    has_own_credentials: bool = False
    configured: bool = False
    address_cls: type[Any] | None = None


@dataclass(frozen=True)
class PendingSetup:
    """Matrix address verified by the first setup page, awaiting its login page response."""

    host: str
    port: int


def _build_runtime_address(
    *,
    host: str,
    port: int,
    telnet_port: int | None,
    user: str | None,
    password: str | None,
    preferred_cls: type[Any] | None = None,
) -> Any:
    """Construct a `MatrixAddress` instance matching R1's frozen 5-field signature."""
    cls = preferred_cls
    if cls is None:
        try:
            from hub.runtime.config import MatrixAddress as _R1MatrixAddress

            cls = _R1MatrixAddress
        except ImportError:
            cls = _FallbackMatrixAddress
    try:
        return cls(
            host=host,
            port=port,
            telnet_port=telnet_port,
            user=user,
            password=password,
        )
    except TypeError:
        return _FallbackMatrixAddress(
            host=host,
            port=port,
            telnet_port=telnet_port,
            user=user,
            password=password,
        )


def map_error_kind(error_kind: str | None) -> ucapi.IntegrationSetupError:
    """Map runtime ``ReconfigureResult.error_kind`` to ``ucapi.IntegrationSetupError``."""
    if not error_kind:
        return ucapi.IntegrationSetupError.OTHER
    norm = str(error_kind).strip().lower()
    if norm in ("auth", "authorization", "authorization_error", "unauthorized"):
        return ucapi.IntegrationSetupError.AUTHORIZATION_ERROR
    if norm in ("timeout", "timed_out"):
        return ucapi.IntegrationSetupError.TIMEOUT
    if norm in ("not_found", "dns", "invalid", "notfound"):
        return ucapi.IntegrationSetupError.NOT_FOUND
    if norm in ("refused", "connection_refused"):
        return ucapi.IntegrationSetupError.CONNECTION_REFUSED
    return ucapi.IntegrationSetupError.OTHER


async def probe_address(
    host: str,
    port: int,
    *,
    timeout: float = 5.0,
) -> ucapi.IntegrationSetupError | None:
    """Check that ``host:port`` resolves and accepts a TCP connection without sending credentials (`UC-05`)."""
    if host.rstrip(".").lower().endswith(".invalid"):
        return ucapi.IntegrationSetupError.NOT_FOUND
    try:
        _, writer = await asyncio.wait_for(asyncio.open_connection(host, port), timeout=timeout)
        writer.close()
        try:
            await writer.wait_closed()
        except Exception:
            pass
        return None
    except TimeoutError:
        return ucapi.IntegrationSetupError.TIMEOUT
    except socket.gaierror:
        return ucapi.IntegrationSetupError.NOT_FOUND
    except ConnectionRefusedError:
        return ucapi.IntegrationSetupError.CONNECTION_REFUSED
    except OSError:
        return ucapi.IntegrationSetupError.OTHER


def login_page(host: str, port: int) -> ucapi.RequestUserInput:
    """Build the second setup page asking for the matrix's login (`UC-05`)."""
    return ucapi.RequestUserInput(
        {"en": "Matrix Login"},
        [
            {
                "id": "info",
                "label": {"en": f"Sign in to {host}:{port}"},
                "field": {
                    "label": {
                        "value": {
                            "en": (
                                "Enter the web interface login for this OREI matrix. "
                                "The default login is Admin / admin."
                            )
                        }
                    }
                },
            },
            {
                "id": "user",
                "label": {"en": "Username"},
                "field": {"text": {"value": "Admin"}},
            },
            {
                "id": "password",
                "label": {"en": "Password"},
                "field": {"password": {}},
            },
        ],
    )


class UCSetupHandler:
    """Handles UC Remote ``DriverSetupRequest``, ``UserDataResponse``, and ``AbortDriverSetup``."""

    def __init__(
        self,
        config: UCIntegrationConfig,
        *,
        hub_getter: Callable[[], Any],
        reconfigure_getter: Callable[[], Callable[..., Any] | None],
        current_address_getter: Callable[[], Callable[[], Any] | None],
        saved_config_getter: Callable[[], dict[str, Any] | None],
        on_setup_complete: Callable[[Any, bool], Any],
        probe_fn: Callable[[str, int], Any] | None = None,
    ) -> None:
        self.config = config
        self._hub_getter = hub_getter
        self._reconfigure_getter = reconfigure_getter
        self._current_address_getter = current_address_getter
        self._saved_config_getter = saved_config_getter
        self._on_setup_complete = on_setup_complete
        self._probe_fn = probe_fn if probe_fn is not None else probe_address
        self._pending_setup: PendingSetup | None = None

    @property
    def pending_setup(self) -> PendingSetup | None:
        return self._pending_setup

    def _effective_auth_token(self) -> str | None:
        if self.config.auth_token:
            return self.config.auth_token
        env_tok = os.environ.get("UC_AUTH_TOKEN", "").strip() or os.environ.get("ADMIN_PIN", "").strip()
        return env_tok or None

    def _resolve_current_address(self) -> _ResolvedCurrentAddress:
        saved = self._saved_config_getter() or {}
        default_telnet_raw = os.environ.get("OREI_TELNET_PORT") or os.environ.get("MATRIX_TELNET_PORT") or "23"
        try:
            default_telnet = int(default_telnet_raw)
        except ValueError:
            default_telnet = 23
        default_password = os.environ.get("OREI_PASSWORD", "admin") or "admin"
        saved_pw = str(saved.get("password") or "") or None
        saved_user = str(saved.get("user") or "") or None

        cur_fn = self._current_address_getter()
        if cur_fn is not None:
            raw = cur_fn()
            if raw is None:
                return _ResolvedCurrentAddress(
                    host="",
                    port=443,
                    telnet_port=default_telnet,
                    user=None,
                    password=None,
                    effective_password=saved_pw or default_password,
                    has_own_credentials=False,
                    configured=False,
                )
            if isinstance(raw, Mapping):
                host = str(raw.get("host") or "").strip()
                port = int(raw.get("port", 443))
                t_port = raw.get("telnet_port", default_telnet)
                u = raw.get("user")
                p = raw.get("password")
                has_creds = bool(raw.get("has_own_credentials", bool(u and p)))
                configured = bool(raw.get("configured", bool(host))) and bool(host)
                return _ResolvedCurrentAddress(
                    host=host,
                    port=port,
                    telnet_port=int(t_port) if t_port is not None else default_telnet,
                    user=str(u) if u else (saved_user if has_creds else None),
                    password=str(p) if p else (saved_pw if has_creds else None),
                    effective_password=str(p or saved_pw or default_password),
                    has_own_credentials=has_creds,
                    configured=configured,
                )

            host = str(getattr(raw, "host", "") or "").strip()
            port = int(getattr(raw, "port", 443))
            t_port = getattr(raw, "telnet_port", default_telnet)
            u = getattr(raw, "user", None)
            p = getattr(raw, "password", None)
            explicit_has_creds = getattr(raw, "has_own_credentials", None)
            has_creds = bool(u and p) if explicit_has_creds is None else bool(explicit_has_creds)
            explicit_cfg = getattr(raw, "configured", None)
            configured = bool(host) if explicit_cfg is None else (bool(explicit_cfg) and bool(host))
            return _ResolvedCurrentAddress(
                host=host,
                port=port,
                telnet_port=int(t_port) if t_port is not None else default_telnet,
                user=str(u) if u else (saved_user if has_creds else None),
                password=str(p) if p else (saved_pw if has_creds else None),
                effective_password=str(p or saved_pw or default_password),
                has_own_credentials=has_creds,
                configured=configured,
                address_cls=type(raw),
            )

        if saved and isinstance(saved.get("host"), str) and saved["host"].strip():
            has_creds = bool(saved_user and saved_pw)
            return _ResolvedCurrentAddress(
                host=saved["host"].strip(),
                port=int(saved.get("port", 443)),
                telnet_port=int(saved.get("telnet_port", default_telnet)),
                user=saved_user if has_creds else None,
                password=saved_pw if has_creds else None,
                effective_password=saved_pw or default_password,
                has_own_credentials=has_creds,
                configured=True,
            )

        env_host = os.environ.get("MATRIX_HOST", "").strip()
        if env_host:
            env_port = int(os.environ.get("MATRIX_PORT", "443"))
            return _ResolvedCurrentAddress(
                host=env_host,
                port=env_port,
                telnet_port=default_telnet,
                user=None,
                password=None,
                effective_password=default_password,
                has_own_credentials=False,
                configured=True,
            )

        return _ResolvedCurrentAddress(
            host="",
            port=443,
            telnet_port=default_telnet,
            user=None,
            password=None,
            effective_password=default_password,
            has_own_credentials=False,
            configured=False,
        )

    def _is_hub_connected(self) -> bool:
        hub = self._hub_getter()
        if hub is None:
            return False
        return bool(getattr(hub, "connected", False))

    async def _invoke_reconfigure(
        self,
        address: Any,
    ) -> tuple[bool, ucapi.IntegrationSetupError | None, Any]:
        reconfigure_fn = self._reconfigure_getter()
        if reconfigure_fn is None:
            return True, None, address
        try:
            res = reconfigure_fn(address, persist=True)
        except TypeError:
            res = reconfigure_fn(address)
        out = await res if asyncio.iscoroutine(res) else res
        if isinstance(out, bool):
            return (True, None, address) if out else (False, ucapi.IntegrationSetupError.OTHER, address)
        if isinstance(out, Mapping):
            ok = bool(out.get("success", False))
            err_kind = out.get("error_kind") or out.get("error")
            return (ok, None if ok else map_error_kind(err_kind), address)
        ok = bool(getattr(out, "success", False))
        err_kind = getattr(out, "error_kind", None)
        res_addr = getattr(out, "address", None)
        effective_addr = res_addr if res_addr is not None and hasattr(res_addr, "host") else address
        return (ok, None if ok else map_error_kind(err_kind), effective_addr)

    async def __call__(self, msg: ucapi.SetupDriver) -> ucapi.SetupAction:
        return await self.handle(msg)

    async def handle(self, msg: ucapi.SetupDriver) -> ucapi.SetupAction:
        """Process a setup lifecycle request from ``ucapi.IntegrationAPI``."""
        if isinstance(msg, ucapi.DriverSetupRequest):
            return await self._handle_setup_request(msg)
        if isinstance(msg, ucapi.UserDataResponse):
            return await self._handle_user_data(msg)
        if isinstance(msg, ucapi.AbortDriverSetup):
            self._pending_setup = None
            _LOG.info("Setup aborted by Remote (%s)", msg.error)
            return ucapi.SetupError()
        return ucapi.SetupError()

    async def _handle_setup_request(self, msg: ucapi.DriverSetupRequest) -> ucapi.SetupAction:
        self._pending_setup = None
        setup_data = msg.setup_data or {}
        host = str(setup_data.get("host", "")).strip()
        try:
            port = int(setup_data.get("port", 443))
        except (TypeError, ValueError):
            port = -1

        if not host or not HOST_PATTERN.match(host) or not (1 <= port <= 65535):
            _LOG.error("Setup: invalid matrix address %r:%r", host, setup_data.get("port"))
            return ucapi.SetupError(error_type=ucapi.IntegrationSetupError.NOT_FOUND)

        token = self._effective_auth_token()
        if token:
            provided = str(
                setup_data.get("auth_token") or setup_data.get("token") or setup_data.get("pin") or ""
            )
            if not provided or not hmac.compare_digest(provided, token):
                _LOG.warning("Setup rejected: invalid or missing UC_AUTH_TOKEN")
                return ucapi.SetupError(error_type=ucapi.IntegrationSetupError.AUTHORIZATION_ERROR)

        cur = self._resolve_current_address()
        if not token and cur.configured and (cur.host, cur.port) != (host, port):
            provided_pw = str(setup_data.get("current_password") or "")
            if not provided_pw or not hmac.compare_digest(provided_pw, cur.effective_password):
                _LOG.warning("Setup rejected: current matrix password required to change matrix address")
                return ucapi.SetupError(error_type=ucapi.IntegrationSetupError.AUTHORIZATION_ERROR)

        _LOG.info("Setup requested for matrix at %s:%d (reconfigure=%s)", host, port, msg.reconfigure)

        if cur.configured and (cur.host, cur.port) == (host, port):
            same_addr = _build_runtime_address(
                host=host,
                port=port,
                telnet_port=cur.telnet_port,
                user=cur.user if cur.has_own_credentials else None,
                password=cur.password if cur.has_own_credentials else None,
                preferred_cls=cur.address_cls,
            )
            if self._is_hub_connected():
                ok, err, effective_addr = await self._invoke_reconfigure(same_addr)
                if not ok:
                    return ucapi.SetupError(error_type=err or ucapi.IntegrationSetupError.OTHER)
                res = self._on_setup_complete(effective_addr, cur.has_own_credentials)
                if asyncio.iscoroutine(res):
                    await res
                return ucapi.SetupComplete()

            reconfigure_fn = self._reconfigure_getter()
            if reconfigure_fn is not None:
                ok, err, effective_addr = await self._invoke_reconfigure(same_addr)
                if ok:
                    res = self._on_setup_complete(effective_addr, cur.has_own_credentials)
                    if asyncio.iscoroutine(res):
                        await res
                    return ucapi.SetupComplete()
                if err != ucapi.IntegrationSetupError.AUTHORIZATION_ERROR:
                    return ucapi.SetupError(error_type=err or ucapi.IntegrationSetupError.OTHER)

        probe_res = self._probe_fn(host, port)
        err = await probe_res if asyncio.iscoroutine(probe_res) else probe_res
        if err is not None:
            _LOG.error("Setup: matrix unreachable at %s:%d (%s)", host, port, err)
            return ucapi.SetupError(error_type=err)

        self._pending_setup = PendingSetup(host=host, port=port)
        _LOG.info("Setup: %s:%d reachable, requesting matrix login", host, port)
        return login_page(host, port)

    async def _handle_user_data(self, msg: ucapi.UserDataResponse) -> ucapi.SetupAction:
        pending, self._pending_setup = self._pending_setup, None
        if pending is None:
            _LOG.warning("Setup: user data received with no pending address")
            return ucapi.SetupError(error_type=ucapi.IntegrationSetupError.OTHER)

        inputs = msg.input_values or {}
        user = str(inputs.get("user") or "").strip() or "Admin"
        password = str(inputs.get("password") or "")
        _LOG.info("Setup: login received for %s:%d", pending.host, pending.port)
        if not password:
            return ucapi.SetupError(error_type=ucapi.IntegrationSetupError.AUTHORIZATION_ERROR)

        cur = self._resolve_current_address()
        new_addr = _build_runtime_address(
            host=pending.host,
            port=pending.port,
            telnet_port=cur.telnet_port,
            user=user,
            password=password,
            preferred_cls=cur.address_cls,
        )
        ok, err, effective_addr = await self._invoke_reconfigure(new_addr)
        if not ok:
            _LOG.error("Setup: login/connect failed for %s:%d (%s)", pending.host, pending.port, err)
            return ucapi.SetupError(error_type=err or ucapi.IntegrationSetupError.OTHER)

        res = self._on_setup_complete(effective_addr, True)
        if asyncio.iscoroutine(res):
            await res
        return ucapi.SetupComplete()
