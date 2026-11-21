"""Small client for the hub's REST API.

Every request uses Home Assistant's shared aiohttp session, a timeout, and
``async with`` so the response is always released (HA-01, HA-08). The hub
answers ``{"success": bool, "data": ..., "error": str | None}``; anything else
(connection error, timeout, non-2xx, ``success: false``, unparseable body)
raises a :class:`HubError` subclass so callers never mistake a failure for
success.
"""

from __future__ import annotations

from typing import Any

import aiohttp

from .const import REQUEST_TIMEOUT


class HubError(Exception):
    """The hub did not do what was asked."""


class HubConnectionError(HubError):
    """The hub could not be reached (network error or timeout)."""


class HubResponseError(HubError):
    """The hub answered with an error (non-2xx or ``success: false``)."""

    def __init__(self, path: str, status: int, error: str | None) -> None:
        self.path = path
        self.status = status
        self.error = error or f"HTTP {status}"
        super().__init__(f"{path}: {self.error} (HTTP {status})")


def _validate_auth_status(auth: Any) -> dict[str, Any]:
    """Require a well-formed ``/api/auth/status`` payload so malformed answers fail closed."""
    if not isinstance(auth, dict):
        raise HubResponseError("/api/auth/status", 200, "the hub returned a malformed auth status")
    control_pin_set = auth.get("control_pin_set")
    session_level = auth.get("session_level")
    if (
        not isinstance(control_pin_set, bool)
        or not isinstance(session_level, str)
        or session_level not in ("none", "control", "admin")
        or ("admin_pin_set" in auth and not isinstance(auth["admin_pin_set"], bool))
        or ("device_remembered" in auth and not isinstance(auth["device_remembered"], bool))
    ):
        raise HubResponseError("/api/auth/status", 200, "the hub returned a malformed auth status")
    return auth


class HubClient:
    """The hub at ``http://host:port``."""

    def __init__(self, session: aiohttp.ClientSession, host: str, port: int, api_key: str | None = None) -> None:
        self._session = session
        self.host = host
        self.port = port
        self.api_key = api_key
        # An IPv6 literal needs brackets in a URL (found by the ha validation client on Docker Desktop).
        url_host = f"[{host}]" if ":" in host and not host.startswith("[") else host
        self.base_url = f"http://{url_host}:{port}"
        self._timeout = aiohttp.ClientTimeout(total=REQUEST_TIMEOUT)

    async def _request(
        self, method: str, path: str, payload: dict[str, Any] | None = None, *, envelope: bool = True
    ) -> Any:
        """One request; returns the ``data`` member of a successful answer.

        With ``envelope=False`` (the ``/api/auth/*`` routes, which answer a bare
        JSON object) a 2xx answer is returned whole.
        """
        kwargs: dict[str, Any] = {"timeout": self._timeout}
        if self.api_key:
            kwargs["headers"] = {"X-API-Key": self.api_key}
        if payload is not None:
            kwargs["json"] = payload
        try:
            async with self._session.request(method, f"{self.base_url}{path}", **kwargs) as resp:
                try:
                    body = await resp.json(content_type=None)
                except ValueError:
                    body = None
                status = resp.status
        except (TimeoutError, aiohttp.ClientError) as err:
            raise HubConnectionError(f"{method} {path}: {err or type(err).__name__}") from err
        if not isinstance(body, dict):
            raise HubResponseError(path, status, "the hub sent no JSON answer")
        if not envelope:
            if not 200 <= status < 300:
                raise HubResponseError(path, status, body.get("error"))
            return body
        if not 200 <= status < 300 or body.get("success") is not True:
            raise HubResponseError(path, status, body.get("error"))
        return body.get("data")

    async def get(self, path: str) -> Any:
        return await self._request("GET", path)

    async def post(self, path: str, payload: dict[str, Any] | None = None) -> Any:
        return await self._request("POST", path, payload)

    # ------------------------------------------------------------ reads

    async def health(self) -> dict[str, Any]:
        """``/api/health``: answers while the hub runs, even if the matrix is offline."""
        data = await self.get("/api/health")
        return data if isinstance(data, dict) else {}

    async def status(self) -> dict[str, Any]:
        """``/api/status``: routing (``{"1": 2, ...}``), names, power."""
        data = await self.get("/api/status")
        if not isinstance(data, dict):
            raise HubResponseError("/api/status", 200, "the hub returned null status data")
        return data

    async def outputs(self) -> list[dict[str, Any]]:
        data = await self.get("/api/status/outputs")
        return list((data or {}).get("outputs") or [])

    async def inputs(self) -> list[dict[str, Any]]:
        data = await self.get("/api/status/inputs")
        return list((data or {}).get("inputs") or [])

    async def device(self) -> dict[str, Any]:
        """``/api/status/device``: model, firmware version, MAC (needs the matrix online)."""
        data = await self.get("/api/status/device")
        return dict((data or {}).get("device") or {})

    async def auth_status(self) -> dict[str, Any]:
        """``/api/auth/status``: which locks are set and what this client may do.

        ``control_pin_set`` says whether control commands need a key at all;
        ``session_level`` is ``"control"`` when the hub accepts this client's
        API key and ``"none"`` when it does not. Reading it changes nothing on
        the hub and counts no PIN attempt. Missing or mistyped fields raise
        :class:`HubResponseError` so callers fail closed.
        """
        return _validate_auth_status(await self._request("GET", "/api/auth/status", envelope=False))

    async def control_allowed(self) -> bool:
        """Whether the hub will accept this client's control commands (routing, power, CEC)."""
        auth = _validate_auth_status(await self.auth_status())
        return (not auth["control_pin_set"]) or auth["session_level"] in ("control", "admin")

    # ------------------------------------------------------------ writes

    async def route(self, output: int, input_num: int) -> None:
        await self.post(f"/api/output/{output}/source", {"input": input_num})

    async def recall_preset(self, preset: int) -> None:
        await self.post(f"/api/preset/{preset}")

    async def set_power(self, on: bool) -> None:
        await self.post("/api/power/on" if on else "/api/power/off")

    async def set_mute(self, output: int, muted: bool) -> None:
        await self.post(f"/api/output/{output}/mute", {"muted": muted})

    async def set_stream(self, output: int, enabled: bool) -> None:
        await self.post(f"/api/output/{output}/enable", {"enabled": enabled})

    async def reboot(self) -> None:
        await self.post("/api/system/reboot")

    async def send_cec(self, port_type: str, port: int, command: str) -> None:
        await self.post(f"/api/cec/{port_type}/{port}/{command}")
