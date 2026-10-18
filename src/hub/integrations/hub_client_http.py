"""REST and reconnecting WebSocket implementation of the hub contract."""

import asyncio
import contextlib
import json
import logging
from copy import deepcopy
from typing import Any
from urllib.parse import quote

import aiohttp

from .hub_client import EventPublisher, HubClient, HubEvent, HubSnapshot, apply_status, port_map

_LOG = logging.getLogger(__name__)


class HubClientError(RuntimeError):
    """A hub request failed, including an actionable authentication error."""

    def __init__(self, message: str, response: dict[str, Any] | None = None, status: int = 0) -> None:
        super().__init__(message)
        self.response = response or {"success": False, "data": None, "error": message}
        self.status = status


class HubClientHttp(EventPublisher, HubClient):
    def __init__(
        self,
        base_url: str = "http://localhost:8080",
        api_key: str | None = None,
        *,
        timeout: float = 15,
        reconnect_delay: float = 1,
        reconnect_max_delay: float = 30,
    ) -> None:
        super().__init__()
        self.base_url = base_url.rstrip("/")
        self.ws_url = self.base_url.replace("https://", "wss://", 1).replace("http://", "ws://", 1) + "/ws"
        self.api_key = api_key
        self.timeout = timeout
        self.reconnect_delay = reconnect_delay
        self.reconnect_max_delay = reconnect_max_delay
        self._session: aiohttp.ClientSession | None = None
        self._ws: aiohttp.ClientWebSocketResponse | None = None
        self._ws_ready = False
        self._ws_task: asyncio.Task[None] | None = None
        self._snapshot_lock = asyncio.Lock()

    async def _ensure_session(self) -> aiohttp.ClientSession:
        if self._closed:
            raise RuntimeError("Hub client is closed")
        if self._session is None:
            self._session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout))
        return self._session

    @property
    def _headers(self) -> dict[str, str]:
        return {"X-API-Key": self.api_key} if self.api_key else {}

    async def _request(self, method: str, path: str, body: dict[str, Any] | None = None) -> dict[str, Any]:
        session = await self._ensure_session()
        try:
            async with session.request(method, self.base_url + path, json=body, headers=self._headers) as response:
                try:
                    payload = await response.json()
                except (ValueError, aiohttp.ContentTypeError) as exc:
                    if response.status in (401, 403):
                        raise HubClientError(
                            "Hub denied access; check HUB_API_KEY / CONTROL_PIN", status=response.status
                        ) from exc
                    raise HubClientError(
                        f"Hub returned invalid JSON (HTTP {response.status})", status=response.status
                    ) from exc
                if not isinstance(payload, dict) or "success" not in payload:
                    raise HubClientError("Hub returned an invalid response envelope", status=response.status)
                if response.status >= 400 or payload.get("success") is not True:
                    message = str(payload.get("error") or f"HTTP {response.status}")
                    if response.status in (401, 403):
                        message = "Hub denied access; check HUB_API_KEY / CONTROL_PIN: " + message
                    raise HubClientError(message, payload, response.status)
                return payload
        except (aiohttp.ClientError, TimeoutError) as exc:
            raise HubClientError("Unable to reach the hub") from exc

    async def _get(self, path: str) -> dict[str, Any]:
        payload = await self._request("GET", path)
        data = payload.get("data")
        if not isinstance(data, dict):
            raise HubClientError(f"Expected an object in {path} data")
        return data

    async def _post(self, path: str, json: dict[str, Any] | None = None) -> dict[str, Any]:
        """Command results retain success/data/error, including passcode errors."""
        try:
            return await self._request("POST", path, json)
        except HubClientError as exc:
            return exc.response

    async def _delete(self, path: str) -> dict[str, Any]:
        return await self._request("DELETE", path)

    async def snapshot(self) -> HubSnapshot:
        """Read the real endpoints; keep last-known state during a matrix outage."""
        async with self._snapshot_lock:
            paths = [
                "/api/health",
                "/api/status",
                "/api/status/full",
                "/api/presets",
                "/api/inputs",
                "/api/outputs",
                "/api/profiles",
                "/api/scenes",
                "/api/shortcuts",
                "/api/cec/macros",
                "/api/status/cables",
                "/api/device-settings/favorite-presets",
            ]
            results = await asyncio.gather(*(self._get(path) for path in paths), return_exceptions=True)
            data: dict[str, dict[str, Any]] = {}
            for path, result in zip(paths, results, strict=True):
                if isinstance(result, BaseException):
                    if isinstance(result, HubClientError) and result.status == 503 and path != "/api/health":
                        continue  # Hub is up but the matrix or an optional manager is down.
                    raise result
                data[path] = result
            state = deepcopy(self._snapshot)
            health = data["/api/health"]
            state.connected = health.get("matrix", {}).get("connected", False) is True
            full = data.get("/api/status/full", {})
            apply_status(state, full)
            # Names endpoints contain metadata only. Signals belong to status/full.
            apply_status(state, data.get("/api/inputs", {}))
            outputs = data.get("/api/outputs", {}).get("outputs", [])
            if isinstance(outputs, list):
                for row in outputs:
                    if isinstance(row, dict) and "name" in row:
                        state.output_names[int(row["number"])] = row["name"]
            apply_status(state, data.get("/api/status", {}), legacy_routing=True)
            cables = data.get("/api/status/cables", {}).get("inputs")
            if isinstance(cables, dict):
                state.input_cables = {
                    port: bool(value) for port, value in port_map(cables).items() if value is not None
                }
            elif isinstance(cables, list):
                state.input_cables = {
                    int(row["number"]): bool(row["cableConnected"])
                    for row in cables
                    if isinstance(row, dict) and row.get("cableConnected") is not None
                }
            presets = data.get("/api/presets", {}).get("presets")
            if presets is not None:
                state.preset_names = {int(row["number"]): row["name"] for row in presets}
            favorites = data.get("/api/device-settings/favorite-presets", {})
            if "favorite_presets" in favorites:
                state.favorite_presets = [int(value) for value in favorites["favorite_presets"]]
            for field, path in (
                ("profiles", "/api/profiles"),
                ("scenes", "/api/scenes"),
                ("shortcuts", "/api/shortcuts"),
                ("macros", "/api/cec/macros"),
            ):
                if path in data:
                    setattr(state, field, data[path].get(field, []))
            self._snapshot = deepcopy(state)
            return state

    async def switch(self, input_num: int, output_num: int | None = None) -> bool:
        body = {"input": input_num}
        if output_num is not None:
            body["output"] = output_num
        return (await self._post("/api/switch", body)).get("success") is True

    async def cycle_input(self, direction: str, output_num: int = 1, *, cycle: bool = True) -> bool:
        if direction not in {"next", "previous"}:
            raise ValueError("direction must be next or previous")
        query = f"?output={output_num}" + ("&cycle=false" if not cycle else "")
        return (await self._post(f"/api/input/{direction}{query}")).get("success") is True

    async def recall_preset(self, preset: int) -> bool:
        return (await self._post(f"/api/preset/{preset}")).get("success") is True

    async def save_preset(self, preset: int) -> bool:
        return (await self._post(f"/api/preset/{preset}/save")).get("success") is True

    async def power(self, on: bool) -> bool:
        return (await self._post("/api/power/" + ("on" if on else "off"))).get("success") is True

    async def send_cec(self, target_kind: str, port: int, command: str) -> bool:
        if target_kind not in {"input", "output"}:
            raise ValueError("target_kind must be input or output")
        return (await self._post(f"/api/cec/{target_kind}/{port}/{quote(command, safe='')}")).get("success") is True

    async def run_action(self, kind: str, action_id: str, *, passcode: str | None = None) -> dict[str, Any]:
        paths = {
            "profile": "/api/profile/{}/recall",
            "scene": "/api/scene/{}/recall",
            "shortcut": "/api/shortcuts/{}/execute",
            "macro": "/api/cec/macro/{}/execute",
        }
        if kind not in paths:
            raise ValueError(f"Unknown action kind: {kind}")
        return await self._post(
            paths[kind].format(quote(action_id, safe="")), {"passcode": passcode} if passcode is not None else None
        )

    @property
    def websocket_connected(self) -> bool:
        return self._ws_ready and self._ws is not None and not self._ws.closed

    async def _start_events(self) -> None:
        await self.connect_websocket()

    async def connect_websocket(self) -> bool:
        """Start a single reconnect supervisor; return the first attempt's result."""
        await self._ensure_session()
        if self._ws_task is not None and not self._ws_task.done():
            return self.websocket_connected
        first: asyncio.Future[bool] = asyncio.get_running_loop().create_future()
        self._ws_task = asyncio.create_task(self._ws_loop(first), name="hub_client_ws")
        return await asyncio.shield(first)

    async def _ws_loop(self, first: asyncio.Future[bool]) -> None:
        delay = self.reconnect_delay
        try:
            while not self._closed:
                try:
                    session = await self._ensure_session()
                    async with session.ws_connect(self.ws_url, headers=self._headers, heartbeat=30) as ws:
                        self._ws = ws
                        old = deepcopy(self._snapshot)
                        state = await self.snapshot()  # Full catalog and state resync, every reconnect.
                        self._snapshot = old
                        await self._publish_snapshot(state)
                        self._ws_ready = True
                        if not first.done():
                            first.set_result(True)
                        delay = self.reconnect_delay
                        async for message in ws:
                            if message.type == aiohttp.WSMsgType.TEXT:
                                try:
                                    payload = json.loads(message.data)
                                    if isinstance(payload, dict):
                                        await self._handle_ws(payload)
                                except (ValueError, TypeError, KeyError):
                                    _LOG.warning("Ignoring malformed hub WebSocket message")
                            elif message.type == aiohttp.WSMsgType.ERROR:
                                break
                except (aiohttp.ClientError, HubClientError, TimeoutError):
                    _LOG.warning("Hub WebSocket unavailable; reconnecting")
                finally:
                    self._ws_ready = False
                    self._ws = None
                    if not first.done():
                        first.set_result(False)
                state = deepcopy(self._snapshot)
                state.connected = False
                await self._publish_snapshot(state)
                await asyncio.sleep(delay)
                delay = min(delay * 2, self.reconnect_max_delay)
        finally:
            if not first.done():
                first.set_result(False)

    async def _handle_ws(self, payload: dict[str, Any]) -> None:
        event = payload.get("event", payload.get("type"))
        data = payload.get("data", {})
        if not isinstance(data, dict):
            return
        state = deepcopy(self._snapshot)
        if event in {"status", "status_update"}:
            apply_status(state, data, legacy_routing=True)
        elif event == "routing_change":
            state.routing[int(data["output"])] = int(data["input"])
        elif event == "signal_change":
            state.input_signals[int(data["input"])] = bool(data["has_signal"])
        elif event == "connection_change" and "output" in data:
            state.output_displays[int(data["output"])] = bool(data["connected"])
        elif event == "cable_change" and data.get("type") == "input":
            state.input_cables[int(data["port"])] = bool(data["connected"])
        elif event == "cable_change" and data.get("type") == "output":
            await self._emit(
                HubEvent(
                    "cable",
                    {
                        "type": "output",
                        "port": int(data["port"]),
                        "connected": bool(data["connected"]),
                    },
                )
            )
            return
        elif event in {"matrix_connection", "connection_change", "connected"}:
            state.connected = data.get("matrix", data).get("connected", state.connected) is True
        elif event == "power_change":
            apply_status(state, data)
        elif event in {"input_name_change", "output_name_change"}:
            kind = "input" if event == "input_name_change" else "output"
            getattr(state, kind + "_names")[int(data[kind])] = data["name"]
        elif event in {"names_change", "presets_change", "device_settings", "device_settings_full"}:
            previous = deepcopy(self._snapshot)
            state = await self.snapshot()
            self._snapshot = previous
            # Explicit values also support events sent before REST caches update.
            apply_status(state, data)
        else:
            return
        await self._publish_snapshot(state)

    async def disconnect_websocket(self) -> None:
        task, self._ws_task = self._ws_task, None
        if task is not None:
            task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await task
        if self._ws is not None:
            await self._ws.close()
            self._ws = None

    async def close(self) -> None:
        await self.disconnect_websocket()
        await self._close_events()
        if self._session is not None:
            await self._session.close()
            self._session = None
