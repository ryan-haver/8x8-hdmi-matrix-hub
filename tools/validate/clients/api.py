"""The ``api`` client: drives the hub's REST API the way HA, Flic and scripts do."""

from __future__ import annotations

import time
from typing import Any

import aiohttp

from ..model import Action
from .base import ActionResult, Client, HubInfo, NotSupportedError


def rest_call(action: Action) -> tuple[str, str, Any]:
    """Map an intent to ``(method, path, json_body)``; the REST contract in one place."""
    p = action.params
    match action.intent:
        case "route":
            return "POST", "/api/switch", {"input": p["input"], "output": p["output"]}
        case "route_all":
            return "POST", "/api/switch", {"input": p["input"]}
        case "preset_recall":
            return "POST", f"/api/preset/{p['preset']}", None
        case "preset_save":
            return "POST", f"/api/preset/{p['preset']}/save", {}
        case "preset_rename":
            return "POST", f"/api/device-settings/preset/{p['preset']}/name", {"name": p["name"]}
        case "matrix_power":
            return "POST", "/api/power/on" if p["on"] else "/api/power/off", None
        case "output_mute":
            return "POST", f"/api/output/{p['output']}/mute", {"muted": p["muted"]}
        case "output_setting":
            return "POST", f"/api/output/{p['output']}/{p['setting']}", p.get("body", {})
        case "cec_input":
            return "POST", f"/api/cec/input/{p['input']}/{p['command']}", None
        case "cec_output":
            return "POST", f"/api/cec/output/{p['output']}/{p['command']}", None
        case "profile_recall":
            body = {"passcode": p["passcode"]} if p.get("passcode") else None
            return "POST", f"/api/profile/{p['profile_id']}/recall", body
        case "request":
            return p.get("method", "GET").upper(), p["path"], p.get("json")
    raise NotSupportedError(action.intent)


class ApiClient(Client):
    name = "api"
    intents = frozenset(
        {
            "route", "route_all", "preset_recall", "preset_save", "preset_rename", "matrix_power",
            "output_mute", "output_setting", "cec_input", "cec_output", "profile_recall", "request",
        }
    )

    def __init__(self) -> None:
        super().__init__()
        self._session: aiohttp.ClientSession | None = None
        self.hub: HubInfo | None = None

    async def start(self, hub: HubInfo) -> None:
        self.hub = hub
        self._session = aiohttp.ClientSession(
            base_url=hub.base_url,
            timeout=aiohttp.ClientTimeout(total=30),
            headers={"X-Forwarded-For": hub.forwarded_for},
        )

    async def stop(self) -> None:
        if self._session:
            await self._session.close()
            self._session = None

    async def request(self, method: str, path: str, body: Any = None) -> tuple[int, Any, dict[str, Any]]:
        """One HTTP exchange; returns ``(status, parsed body, record)``."""
        assert self._session is not None, "client not started"
        t0 = time.perf_counter()
        kwargs: dict[str, Any] = {} if body is None else {"json": body}
        async with self._session.request(method, path, **kwargs) as resp:
            text = await resp.text()
            try:
                parsed: Any = await resp.json(content_type=None) if text else None
            except ValueError:
                parsed = text[:2000]
            record = {
                "method": method,
                "path": path,
                "body": body,
                "status": resp.status,
                "response": parsed,
                "elapsed_ms": round((time.perf_counter() - t0) * 1000, 1),
            }
            return resp.status, parsed, record

    async def perform(self, action: Action) -> ActionResult:
        method, path, body = rest_call(action)
        result = ActionResult(intent=action.intent, ok=False)
        t0 = time.perf_counter()
        try:
            status, parsed, record = await self.request(method, path, body)
            result.requests.append(record)
            result.status, result.body = status, parsed
            result.ok = 200 <= status < 300
            result.steps.append(f"{method} {path}" + (f" {body}" if body is not None else "") + f" -> HTTP {status}")
        except (aiohttp.ClientError, TimeoutError) as exc:
            result.error = f"{type(exc).__name__}: {exc}"
            result.steps.append(f"{method} {path} -> {result.error}")
        result.elapsed_ms = round((time.perf_counter() - t0) * 1000, 1)
        return result

    def environment(self) -> dict[str, Any]:
        return {"name": self.name, "aiohttp": aiohttp.__version__}
