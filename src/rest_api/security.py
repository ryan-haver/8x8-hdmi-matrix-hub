"""Access levels and browser request guards for the REST API."""

from __future__ import annotations

import asyncio
import hashlib
import hmac
import ipaddress
import json
import os
import re
import secrets
import time
from pathlib import Path
from urllib.parse import urlsplit

from aiohttp import web

from _file_io import atomic_write_json
from password import PasswordError, hash_passcode, verify_passcode

SESSION_COOKIE = "orei_session"
DEVICE_COOKIE = "orei_device_token"
SESSION_IDLE = 30 * 60
DEVICE_LIFETIME = 365 * 24 * 60 * 60


def _digest(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def _host_name(host: str) -> str | None:
    """Parse one Host value, including bracketed IPv6 and an optional port."""
    if not host or "," in host or "@" in host or "/" in host or "\\" in host:
        return None
    if host.startswith("["):
        match = re.fullmatch(r"\[([^]]+)\](?::\d{1,5})?", host)
        if not match:
            return None
        try:
            ipaddress.IPv6Address(match.group(1))
        except ValueError:
            return None
        return match.group(1)
    match = re.fullmatch(r"([^:]+)(?::\d{1,5})?", host)
    return match.group(1).lower() if match else None


def allowed_host(host: str) -> bool:
    name = _host_name(host)
    if name is None:
        return False
    try:
        ipaddress.ip_address(name)
        return True
    except ValueError:
        pass
    if name in ("localhost", "host.docker.internal") or name.endswith(".local"):
        return True
    configured = {item.strip().lower() for item in os.environ.get("ALLOWED_HOSTS", "").split(",")}
    return name in configured or host.lower() in configured


def allowed_origin(request: web.Request, origin: str) -> bool:
    try:
        parsed = urlsplit(origin)
        if parsed.scheme not in ("http", "https") or not parsed.netloc or parsed.path or parsed.query or parsed.fragment:
            return False
        same = parsed.scheme == request.scheme and parsed.netloc.lower() == request.headers.get("Host", "").lower()
    except ValueError:
        return False
    configured = {item.strip() for item in os.environ.get("CORS_ALLOWED_ORIGINS", "").split(",")}
    return same or "*" in configured or origin in configured


def request_origin(request: web.Request) -> str | None:
    origin = request.headers.get("Origin")
    if origin:
        return origin
    referer = request.headers.get("Referer")
    if referer:
        try:
            parsed = urlsplit(referer)
            return f"{parsed.scheme}://{parsed.netloc}"
        except ValueError:
            return referer
    return None


def route_level(method: str, path: str) -> str | None:
    if path.startswith("/api/auth/"):
        if path in ("/api/auth/status", "/api/auth/unlock", "/api/auth/lock", "/api/auth/pin"):
            return None
        return "admin"
    if method not in ("POST", "PUT", "DELETE", "PATCH"):
        return None
    parts = path.strip("/").split("/")
    if len(parts) < 2 or parts[0] != "api":
        return None
    section = parts[1]
    suffix = parts[-1]
    if section in ("settings", "themes", "dashboard", "device-settings") or path == "/api/ui/preferences":
        return "admin"
    if section == "integrations" and path == "/api/integrations/flic/register":
        return "admin"
    if section == "system" and suffix in ("reboot", "panel_lock"):
        return "admin"
    if section == "input" and suffix in ("edid", "name"):
        return "admin"
    if section == "output" and suffix in ("name", "hdcp", "hdr", "scaler"):
        return "admin"
    if section in ("profile", "profiles"):
        return "control" if suffix == "recall" else "admin"
    if section in ("scene", "scenes"):
        return "control" if suffix in ("recall", "execute") else "admin"
    if section == "v2" and len(parts) > 2 and parts[2] == "scenes":
        return "control" if suffix == "execute" else None if suffix in ("validate", "history") else "admin"
    if section == "cec" and len(parts) > 2 and parts[2] in ("macro", "macros"):
        return "control" if suffix in ("execute", "test") else "admin"
    if section in ("shortcuts", "system-shortcuts"):
        return "control" if suffix == "execute" else "admin"
    if section == "preset" and suffix == "save":
        return "admin"
    if section in ("switch", "preset", "power", "cec", "ext-audio"):
        return "control"
    if section == "input" and suffix in ("next", "previous"):
        return "control"
    if section == "output" and suffix in ("source", "enable", "arc", "mute"):
        return "control"
    if section == "system" and suffix in ("beep", "lcd"):
        return "control"
    return None


class SecurityManager:
    """Per-application persistent credentials and ephemeral sessions."""

    def __init__(self, data_dir: Path):
        self.path = data_dir / "security.json"
        try:
            self.state = json.loads(self.path.read_text()) if self.path.exists() else {}
        except (OSError, ValueError):
            self.state = {}
        self.state.setdefault("devices", {})
        self.state.setdefault("api_keys", {})
        if os.environ.get("ADMIN_PIN_RESET", "").lower() == "true":
            self.state.pop("admin_pin", None)
            self._save()
        self.sessions: dict[str, tuple[str, float]] = {}
        self.failures: dict[str, tuple[int, float]] = {}
        self._lock = asyncio.Lock()
        self._env_ready = False

    def _save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        atomic_write_json(self.path, self.state)

    async def ready(self) -> None:
        if self._env_ready:
            return
        async with self._lock:
            if self._env_ready:
                return
            for level in ("admin", "control"):
                pin = os.environ.get(f"{level.upper()}_PIN")
                if pin and not (level == "admin" and os.environ.get("ADMIN_PIN_RESET", "").lower() == "true"):
                    self.state[f"{level}_pin"] = await asyncio.get_running_loop().run_in_executor(None, hash_passcode, pin)
            self._env_ready = True
            self._save()

    def pin_set(self, level: str) -> bool:
        return bool(self.state.get(f"{level}_pin"))

    async def verify_pin(self, level: str, pin: str, peer: str = "unknown") -> bool:
        key = f"{level}:{peer}"
        failures, until = self.failures.get(key, (0, 0))
        if time.monotonic() < until:
            raise web.HTTPTooManyRequests(text="PIN temporarily locked")
        stored = self.state.get(f"{level}_pin")
        try:
            valid = bool(stored and await asyncio.get_running_loop().run_in_executor(None, verify_passcode, pin, stored))
        except (PasswordError, TypeError):
            valid = False
        if valid:
            self.failures.pop(key, None)
            return True
        failures += 1
        self.failures[key] = (failures, time.monotonic() + min(3600, 2 ** (failures - 5)) if failures >= 5 else 0)
        if failures >= 5:
            raise web.HTTPTooManyRequests(text="PIN temporarily locked")
        return False

    def session_level(self, request: web.Request) -> str:
        token = request.cookies.get(SESSION_COOKIE, "")
        item = self.sessions.get(_digest(token)) if token else None
        if not item:
            return "none"
        level, last_seen = item
        if time.monotonic() - last_seen > SESSION_IDLE:
            self.sessions.pop(_digest(token), None)
            return "none"
        self.sessions[_digest(token)] = (level, time.monotonic())
        return level

    def remembered(self, request: web.Request) -> bool:
        token = request.cookies.get(DEVICE_COOKIE, "")
        return bool(token and any(hmac.compare_digest(item.get("hash", ""), _digest(token)) for item in self.state["devices"].values()))

    def api_key_valid(self, request: web.Request) -> bool:
        token = request.headers.get("X-API-Key") or request.query.get("key", "")
        if not token:
            return False
        if any(hmac.compare_digest(item.get("hash", ""), _digest(token)) for item in self.state["api_keys"].values()):
            return True
        return any(hmac.compare_digest(token, os.environ.get(name, "")) for name in ("API_KEY", "CONTROL_API_KEY") if os.environ.get(name))

    def access_level(self, request: web.Request) -> str:
        session = self.session_level(request)
        if session == "admin":
            return "admin"
        if session == "control" or self.remembered(request) or self.api_key_valid(request):
            return "control"
        return "none"

    def new_session(self, response: web.Response, level: str) -> None:
        token = secrets.token_urlsafe(32)
        self.sessions[_digest(token)] = (level, time.monotonic())
        response.set_cookie(SESSION_COOKIE, token, httponly=True, samesite="Strict", max_age=SESSION_IDLE)

    def remember_device(self, response: web.Response, name: str) -> None:
        token = secrets.token_urlsafe(32)
        self.state["devices"][secrets.token_hex(8)] = {"name": name[:80], "hash": _digest(token), "created": int(time.time())}
        self._save()
        response.set_cookie(DEVICE_COOKIE, token, httponly=True, samesite="Strict", max_age=DEVICE_LIFETIME)


def manager(request: web.Request) -> SecurityManager:
    return request.app["security_manager"]


@web.middleware
async def security_middleware(request: web.Request, handler):
    if not allowed_host(request.headers.get("Host", "")):
        raise web.HTTPMisdirectedRequest(text="Unrecognized Host; add it to ALLOWED_HOSTS")
    origin = request_origin(request)
    if request.path.startswith("/api/") and request.method in ("POST", "PUT", "DELETE", "PATCH"):
        if origin and not allowed_origin(request, origin):
            raise web.HTTPForbidden(text="Cross-origin mutation denied")
        if (request.content_length or request.headers.get("Transfer-Encoding")) and not request.content_type.startswith("application/json"):
            raise web.HTTPUnsupportedMediaType(text="JSON Content-Type required")
    security = manager(request)
    await security.ready()
    level = route_level(request.method, request.path)
    if level == "admin" and security.pin_set("admin") and security.session_level(request) != "admin":
        pin = request.headers.get("X-Admin-PIN", "")
        if not pin or not await security.verify_pin("admin", pin, request.remote or "unknown"):
            raise web.HTTPUnauthorized(text="Admin unlock required")
    if level == "control" and security.pin_set("control") and security.access_level(request) == "none":
        raise web.HTTPUnauthorized(text="Control unlock or API key required")
    response = await handler(request)
    token = request.cookies.get(SESSION_COOKIE)
    if token and security.session_level(request) != "none":
        response.set_cookie(SESSION_COOKIE, token, httponly=True, samesite="Strict", max_age=SESSION_IDLE)
    return response


async def auth_status(request: web.Request) -> web.Response:
    security = manager(request)
    return web.json_response({"admin_pin_set": security.pin_set("admin"), "control_pin_set": security.pin_set("control"), "session_level": security.access_level(request), "device_remembered": security.remembered(request)})


async def auth_unlock(request: web.Request) -> web.Response:
    security = manager(request)
    body = await request.json()
    level = body.get("level", "admin")
    if level not in ("admin", "control"):
        raise web.HTTPBadRequest(text="Invalid level")
    if not await security.verify_pin(level, body.get("pin"), request.remote or "unknown"):
        raise web.HTTPUnauthorized(text="Incorrect PIN")
    response = web.json_response({"level": level})
    security.new_session(response, level)
    if level == "control" and body.get("remember_device"):
        security.remember_device(response, str(body.get("device_name") or "Device"))
    return response


async def auth_lock(request: web.Request) -> web.Response:
    security = manager(request)
    token = request.cookies.get(SESSION_COOKIE)
    if token:
        security.sessions.pop(_digest(token), None)
    response = web.json_response({"locked": True})
    response.del_cookie(SESSION_COOKIE)
    return response


async def auth_pin(request: web.Request) -> web.Response:
    security = manager(request)
    body = await request.json()
    level = body.get("level", "admin")
    if level not in ("admin", "control"):
        raise web.HTTPBadRequest(text="Invalid level")
    if security.pin_set("admin") and security.session_level(request) != "admin":
        if not await security.verify_pin("admin", body.get("current_pin"), request.remote or "unknown"):
            raise web.HTTPUnauthorized(text="Current Admin PIN required")
    pin = body.get("pin")
    try:
        stored = await asyncio.get_running_loop().run_in_executor(None, hash_passcode, pin) if pin else None
    except PasswordError as exc:
        raise web.HTTPBadRequest(text=str(exc)) from exc
    if stored:
        security.state[f"{level}_pin"] = stored
    else:
        security.state.pop(f"{level}_pin", None)
    security._save()
    return web.json_response({"admin_pin_set": security.pin_set("admin"), "control_pin_set": security.pin_set("control")})


async def auth_devices(request: web.Request) -> web.Response:
    security = manager(request)
    if request.method == "GET":
        return web.json_response([{"id": key, "name": item["name"], "created": item["created"]} for key, item in security.state["devices"].items()])
    security.state["devices"].pop(request.match_info["device_id"], None)
    security._save()
    return web.json_response({"deleted": True})


async def auth_api_keys(request: web.Request) -> web.Response:
    security = manager(request)
    if request.method == "GET":
        return web.json_response([{"id": key, "name": item["name"], "created": item["created"]} for key, item in security.state["api_keys"].items()])
    if request.method == "DELETE":
        security.state["api_keys"].pop(request.match_info["key_id"], None)
        security._save()
        return web.json_response({"deleted": True})
    body = await request.json()
    key = secrets.token_urlsafe(32)
    key_id = secrets.token_hex(8)
    security.state["api_keys"][key_id] = {"name": str(body.get("name") or "API key")[:80], "hash": _digest(key), "created": int(time.time())}
    security._save()
    return web.json_response({"id": key_id, "key": key}, status=201)
