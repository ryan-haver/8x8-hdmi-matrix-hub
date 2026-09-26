"""The ``ha`` client: a real Home Assistant in Docker, with ``custom_components/hdmi_matrix`` installed (WP-D1).

VALIDATION_PLAN §4 "Real clients for V3": a real ``homeassistant/home-assistant``
container, the custom component installed and configured through Home
Assistant's own API, service calls and entity states checked against the
device.

``start()``:

1. creates a container from the pinned image (``VALIDATE_HA_IMAGE`` overrides
   it), copies a minimal ``configuration.yaml`` and ``custom_components/hdmi_matrix``
   into ``/config`` (``docker cp``: nothing is bind-mounted, so the container
   never writes into the repository), publishes port 8123 on a free local port
   and maps ``host.docker.internal`` to the Docker host (``host-gateway``),
   where the hub under test listens;
2. onboards Home Assistant through its HTTP API (owner user, auth code ->
   token, core config, analytics, integration step) and creates a long-lived
   token over the WebSocket API.

The entry itself is added by the ``ha_config_flow`` intent (scenario
``ha.config_flow``), through ``/api/config/config_entries/flow`` exactly as the
UI does; other intents add it on first use when a run starts elsewhere.

Intents become what a Home Assistant user does: ``route`` -> ``select.select_option``
on the output's source select (option = the input's name as HA lists it),
``preset_recall`` -> ``button.press``, ``matrix_power`` / ``output_mute`` /
``output_setting`` (``enable``) -> ``switch.turn_on/off``, ``cec_input`` /
``cec_output`` -> ``hdmi_matrix.send_cec_command``, ``ha_service`` -> any
service (``target="entry"|"device"`` adds the entry or device id). Service
calls go over the WebSocket API, as the frontend sends them; the result is
mapped to an HTTP-like status (200 ok, 400 validation error, 404 not found,
500 Home Assistant error) for ``Response`` checks.

``observe(key)`` (``ClientState`` checks) reads what Home Assistant shows:
``<platform>.<unique-id suffix>`` (``select.output_1_source``; ``@attr`` for an
attribute), ``device.<field>``, ``entry.<field>``, ``log.errors`` (integration
errors in the Home Assistant log).
"""

from __future__ import annotations

import asyncio
import json
import os
import secrets
import shutil
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

import aiohttp

from ..model import Action
from ..stack import free_port
from .base import ActionResult, Client, HubInfo, NotSupportedError

ROOT = Path(__file__).resolve().parents[3]
COMPONENT = ROOT / "custom_components" / "hdmi_matrix"
DOMAIN = "hdmi_matrix"

#: Pinned so evidence is reproducible; the newest stable release when WP-D1 ran.
#: ``VALIDATE_HA_IMAGE=homeassistant/home-assistant:2025.1.4`` checks the minimum version (D8).
DEFAULT_IMAGE = "homeassistant/home-assistant:2026.9.3"
#: How the container reaches the Docker host (``--add-host ...:host-gateway``).
HOST_ALIAS = "host.docker.internal"

CONFIGURATION_YAML = """\
# Minimal Home Assistant configuration for the validation run (tools/validate/clients/ha.py).
homeassistant:
  name: Validation
  unit_system: metric
  time_zone: UTC
  country: US
  latitude: 0
  longitude: 0
  elevation: 0

frontend:
config:

logger:
  default: warning
  logs:
    custom_components.hdmi_matrix: debug
    homeassistant.components.hdmi_matrix: debug
"""

#: Service-call error codes (WebSocket API) -> HTTP-like status for ``Response`` checks.
_ERROR_STATUS = {
    "service_validation_error": 400,
    "invalid_format": 400,
    "not_found": 404,
    "home_assistant_error": 500,
    "unknown_error": 500,
}


def _docker(*args: str, check: bool = True, timeout: float = 600) -> subprocess.CompletedProcess[str]:
    return subprocess.run(  # noqa: S603 - fixed docker argv
        ["docker", *args], capture_output=True, text=True, encoding="utf-8", errors="replace",
        check=check, timeout=timeout,
    )


class HomeAssistantClient(Client):
    name = "ha"
    observes = True
    intents = frozenset(
        {
            "route", "preset_recall", "matrix_power", "output_mute", "output_setting", "cec_input", "cec_output",
            "ha_service", "ha_config_flow", "ha_reconfigure",
        }
    )

    def __init__(self) -> None:
        super().__init__()
        self.image = os.environ.get("VALIDATE_HA_IMAGE", DEFAULT_IMAGE)
        self.hub: HubInfo | None = None
        self.container: str | None = None
        self.port = 0
        self.url = ""
        self.token = ""
        self.version = ""
        self.image_digest: str | None = None
        self.hub_host = HOST_ALIAS
        self.hub_port = 0
        self.entry_id: str | None = None
        self.log_dir: Path | None = None
        self._session: aiohttp.ClientSession | None = None
        self._ws: aiohttp.ClientWebSocketResponse | None = None
        self._ws_id = 0
        self._ws_lock = asyncio.Lock()
        self._registry: dict[str, dict[str, Any]] = {}
        self.setup_steps: list[str] = []

    # ------------------------------------------------------------ lifecycle

    async def start(self, hub: HubInfo) -> None:
        if shutil.which("docker") is None:
            raise RuntimeError("the 'ha' client needs Docker (a real Home Assistant container); docker not found")
        self.hub = hub
        parts = urlsplit(hub.base_url)
        self.hub_port = parts.port or 80
        # A hub on this machine is the Docker host as seen from the container.
        self.hub_host = HOST_ALIAS if parts.hostname in ("127.0.0.1", "localhost", "0.0.0.0") else (parts.hostname or "")
        if hub.artifacts_dir is not None:
            self.log_dir = Path(hub.artifacts_dir).parent / "logs"
        await asyncio.to_thread(self._start_container)
        self._session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=60))
        try:
            await self._wait_ready()
            await self._onboard()
        except Exception:
            await self.stop()
            raise

    def _start_container(self) -> None:
        try:
            _docker("version", "--format", "{{.Server.Version}}", timeout=30)
        except (subprocess.SubprocessError, OSError) as exc:
            raise RuntimeError(f"the 'ha' client needs a running Docker engine: {exc}") from exc
        if _docker("image", "inspect", self.image, check=False, timeout=60).returncode != 0:
            self.setup_steps.append(f"docker pull {self.image}")
            _docker("pull", "-q", self.image, timeout=1200)
        inspect = json.loads(_docker("image", "inspect", self.image, timeout=60).stdout)[0]
        self.image_digest = (inspect.get("RepoDigests") or [inspect.get("Id")])[0]
        self.port = free_port()
        name = f"hdmi-matrix-validate-ha-{secrets.token_hex(3)}"
        self.container = _docker(
            "create", "--name", name,
            "--add-host", f"{HOST_ALIAS}:host-gateway",
            "-p", f"127.0.0.1:{self.port}:8123",
            "-e", "TZ=UTC",
            self.image,
        ).stdout.strip()
        with tempfile.TemporaryDirectory(prefix="ha-validate-config-") as tmp:
            cfg = Path(tmp)
            (cfg / "configuration.yaml").write_text(CONFIGURATION_YAML, encoding="utf-8")
            shutil.copytree(COMPONENT, cfg / "custom_components" / DOMAIN,
                            ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
            _docker("cp", f"{cfg}{os.sep}.", f"{self.container}:/config")
        _docker("start", self.container)
        self.url = f"http://127.0.0.1:{self.port}"
        self.setup_steps.append(f"docker run {self.image} as {name} (config + custom_components/{DOMAIN} copied in; "
                                f"{HOST_ALIAS} -> host-gateway; 8123 -> 127.0.0.1:{self.port})")

    async def _wait_ready(self, timeout: float = 300) -> None:
        assert self._session is not None
        deadline = time.monotonic() + timeout
        while True:
            try:
                async with self._session.get(f"{self.url}/api/onboarding") as resp:
                    if resp.status == 200:
                        return
            except (aiohttp.ClientError, TimeoutError):
                pass
            if time.monotonic() > deadline:
                raise RuntimeError(f"Home Assistant did not start within {timeout:.0f} s:\n{self._log_tail()}")
            state = _docker("inspect", "-f", "{{.State.Running}}", self.container or "", check=False).stdout.strip()
            if state == "false":
                raise RuntimeError(f"the Home Assistant container exited:\n{self._log_tail()}")
            await asyncio.sleep(2)

    async def _onboard(self) -> None:
        """Owner user -> token -> the remaining onboarding steps -> a long-lived token (HA's onboarding API)."""
        assert self._session is not None
        client_id = f"{self.url}/"
        password = secrets.token_urlsafe(16)
        user = await self._http("POST", "/api/onboarding/users", {
            "client_id": client_id, "name": "Validation", "username": "validate", "password": password,
            "language": "en",
        }, auth=False)
        async with self._session.post(f"{self.url}/auth/token", data={
            "grant_type": "authorization_code", "code": user["auth_code"], "client_id": client_id,
        }) as resp:
            tokens = await resp.json()
            if resp.status != 200:
                raise RuntimeError(f"token exchange failed: HTTP {resp.status} {tokens}")
        self.token = tokens["access_token"]
        await self._http("POST", "/api/onboarding/core_config", {})
        await self._http("POST", "/api/onboarding/analytics", {})
        await self._http("POST", "/api/onboarding/integration",
                         {"client_id": client_id, "redirect_uri": f"{client_id}?auth_callback=1"})
        await self._ws_connect()
        self.token = await self._ws_call("auth/long_lived_access_token", client_name="validate", lifespan=1)
        await self._ws_close()
        await self._ws_connect()
        self.version = (await self._http("GET", "/api/config")).get("version", "")
        self.setup_steps.append(f"onboarded Home Assistant {self.version} through /api/onboarding")

    async def stop(self) -> None:
        await self._ws_close()
        if self._session is not None:
            await self._session.close()
            self._session = None
        if self.container:
            if self.log_dir is not None:
                self.log_dir.mkdir(parents=True, exist_ok=True)
                logs = _docker("logs", self.container, check=False, timeout=60)
                (self.log_dir / "home-assistant.log").write_text(logs.stdout + logs.stderr, encoding="utf-8")
            _docker("rm", "-f", self.container, check=False, timeout=120)
            self.container = None

    def _log_tail(self, lines: int = 40) -> str:
        if not self.container:
            return "(no container)"
        out = _docker("logs", "--tail", str(lines), self.container, check=False, timeout=60)
        return out.stdout + out.stderr

    # ------------------------------------------------------------ HTTP / WebSocket API

    async def _http(self, method: str, path: str, body: Any = None, *, auth: bool = True,
                    record: list[dict[str, Any]] | None = None) -> Any:
        assert self._session is not None
        headers = {"Authorization": f"Bearer {self.token}"} if auth else {}
        t0 = time.perf_counter()
        async with self._session.request(method, f"{self.url}{path}", json=body, headers=headers) as resp:
            text = await resp.text()
            try:
                parsed: Any = json.loads(text) if text else None
            except ValueError:
                parsed = text[:500]
            if record is not None:
                record.append({"method": method, "path": path, "body": body, "status": resp.status,
                               "response": parsed, "via": "home assistant http api",
                               "elapsed_ms": round((time.perf_counter() - t0) * 1000, 1)})
            if resp.status >= 400:
                raise RuntimeError(f"{method} {path}: HTTP {resp.status} {text[:300]}")
            return parsed

    async def _ws_connect(self) -> None:
        assert self._session is not None
        self._ws = await self._session.ws_connect(f"{self.url}/api/websocket", heartbeat=30)
        hello = await self._ws.receive_json()
        if hello.get("type") != "auth_required":
            raise RuntimeError(f"unexpected WebSocket greeting {hello}")
        await self._ws.send_json({"type": "auth", "access_token": self.token})
        answer = await self._ws.receive_json()
        if answer.get("type") != "auth_ok":
            raise RuntimeError(f"WebSocket authentication failed: {answer}")

    async def _ws_close(self) -> None:
        if self._ws is not None:
            await self._ws.close()
            self._ws = None

    async def _ws_message(self, msg_type: str, **payload: Any) -> dict[str, Any]:
        """Send one command and return its ``result`` message (success or error)."""
        async with self._ws_lock:
            if self._ws is None or self._ws.closed:
                await self._ws_connect()
            assert self._ws is not None
            self._ws_id += 1
            msg_id = self._ws_id
            await self._ws.send_json({"id": msg_id, "type": msg_type, **payload})
            while True:
                msg = await asyncio.wait_for(self._ws.receive_json(), 60)
                if msg.get("id") == msg_id and msg.get("type") == "result":
                    return msg

    async def _ws_call(self, msg_type: str, **payload: Any) -> Any:
        msg = await self._ws_message(msg_type, **payload)
        if not msg.get("success"):
            raise RuntimeError(f"{msg_type} failed: {msg.get('error')}")
        return msg.get("result")

    # ------------------------------------------------------------ the config entry

    async def _entries(self) -> list[dict[str, Any]]:
        return list(await self._http("GET", f"/api/config/config_entries/entry?domain={DOMAIN}") or [])

    async def _config_flow(self, record: list[dict[str, Any]], options: dict[str, Any] | None) -> int:
        """Add the hub the way a user does in Settings -> Devices & services. Returns an HTTP-like status."""
        for entry in await self._entries():  # a clean slate: remove earlier entries
            await self._http("DELETE", f"/api/config/config_entries/entry/{entry['entry_id']}", record=record)
        self.entry_id = None
        self._registry.clear()
        flow = await self._http("POST", "/api/config/config_entries/flow",
                                {"handler": DOMAIN, "show_advanced_options": False}, record=record)
        if flow.get("type") != "form" or flow.get("step_id") != "user":
            return 500
        result = await self._http("POST", f"/api/config/config_entries/flow/{flow['flow_id']}",
                                  {"host": self.hub_host, "port": self.hub_port}, record=record)
        if result.get("type") != "create_entry":
            return 400
        entry = result.get("result")
        self.entry_id = entry.get("entry_id") if isinstance(entry, dict) else str(entry)
        await self._wait_loaded()
        if options:
            flow = await self._http("POST", "/api/config/config_entries/options/flow",
                                    {"handler": self.entry_id}, record=record)
            done = await self._http("POST", f"/api/config/config_entries/options/flow/{flow['flow_id']}",
                                    options, record=record)
            if done.get("type") != "create_entry":
                return 400
            await asyncio.sleep(1)  # the options update reloads the entry
            await self._wait_loaded()
        return 200

    async def _wait_loaded(self, timeout: float = 60) -> None:
        deadline = time.monotonic() + timeout
        while True:
            state = await self.observe("entry.state")
            if state == "loaded":
                self._registry.clear()
                return
            if time.monotonic() > deadline:
                raise RuntimeError(f"the {DOMAIN} entry did not load (state {state!r}):\n{self._log_tail()}")
            await asyncio.sleep(1)

    async def _ensure_entry(self) -> None:
        if self.entry_id is not None:
            return
        loaded = [e for e in await self._entries() if e.get("state") == "loaded"]
        if loaded:
            self.entry_id = loaded[0]["entry_id"]
            return
        if await self._config_flow([], {"scan_interval": 5}) != 200:
            raise RuntimeError("could not add the hub in Home Assistant")

    async def _entity_id(self, key: str) -> str:
        """``select.output_1_source`` -> the entity id Home Assistant gave that unique id."""
        platform, _, suffix = key.partition(".")
        for attempt in range(2):
            if not self._registry or attempt:
                entries = await self._ws_call("config/entity_registry/list")
                self._registry = {e["unique_id"]: e for e in entries
                                  if e.get("platform") == DOMAIN and e.get("config_entry_id") == self.entry_id}
            for unique_id, e in self._registry.items():
                if unique_id.endswith(f"_{suffix}") and e["entity_id"].startswith(f"{platform}."):
                    return str(e["entity_id"])
        raise NotSupportedError(f"no {platform} entity with unique id suffix {suffix!r}")

    async def _state(self, entity_id: str) -> dict[str, Any]:
        return dict(await self._http("GET", f"/api/states/{entity_id}") or {})

    # ------------------------------------------------------------ observe

    async def observe(self, key: str) -> Any:
        if key.startswith("entry."):
            field = key.split(".", 1)[1]
            for entry in await self._entries():
                if self.entry_id is None or entry.get("entry_id") == self.entry_id:
                    return entry.get(field)
            return None
        if key == "log.errors":
            logs = _docker("logs", self.container or "", check=False, timeout=60)
            text = logs.stdout + logs.stderr
            return sum(1 for line in text.splitlines() if " ERROR " in line and DOMAIN in line)
        await self._ensure_entry()
        if key.startswith("device."):
            field = key.split(".", 1)[1]
            devices = await self._ws_call("config/device_registry/list")
            mine = [d for d in devices if self.entry_id in (d.get("config_entries") or [])]
            return mine[0].get(field) if len(mine) == 1 else f"<{len(mine)} devices>"
        entity_key, _, attr = key.partition("@")
        state = await self._state(await self._entity_id(entity_key))
        if attr:
            return state.get("attributes", {}).get(attr)
        return state.get("state")

    # ------------------------------------------------------------ perform

    async def _service(self, domain: str, service: str, data: dict[str, Any],
                       result: ActionResult) -> None:
        t0 = time.perf_counter()
        msg = await self._ws_message("call_service", domain=domain, service=service, service_data=data)
        error = msg.get("error") or {}
        result.status = 200 if msg.get("success") else _ERROR_STATUS.get(str(error.get("code")), 500)
        result.ok = result.status == 200
        if error:
            result.error = f"{error.get('code')}: {error.get('message')}"
        result.requests.append({
            "method": "call_service", "path": f"{domain}.{service}", "body": data, "status": result.status,
            "response": {"success": msg.get("success"), "error": error or None},
            "via": "home assistant websocket api", "elapsed_ms": round((time.perf_counter() - t0) * 1000, 1),
        })
        result.steps.append(f"call_service {domain}.{service} {data} -> "
                            + ("ok" if result.ok else f"{error.get('code')}: {error.get('message')}"))

    async def _service_call(self, action: Action) -> tuple[str, str, dict[str, Any]]:
        """``(domain, service, service_data)`` for an intent."""
        p = action.params
        match action.intent:
            case "route":
                entity = await self._entity_id(f"select.output_{p['output']}_source")
                options = (await self._state(entity)).get("attributes", {}).get("options") or []
                if not 1 <= p["input"] <= len(options):
                    raise NotSupportedError(f"input {p['input']} is not among the select options {options}")
                return "select", "select_option", {"entity_id": entity, "option": options[p["input"] - 1]}
            case "preset_recall":
                return "button", "press", {"entity_id": await self._entity_id(f"button.preset_{p['preset']}")}
            case "matrix_power":
                return "switch", "turn_on" if p["on"] else "turn_off", {"entity_id": await self._entity_id("switch.power")}
            case "output_mute":
                entity = await self._entity_id(f"switch.output_{p['output']}_mute")
                return "switch", "turn_on" if p["muted"] else "turn_off", {"entity_id": entity}
            case "output_setting":
                if p["setting"] != "enable":
                    raise NotSupportedError(f"Home Assistant has no entity for output {p['setting']}")
                entity = await self._entity_id(f"switch.output_{p['output']}_stream")
                on = bool(p.get("body", {}).get("enabled", True))
                return "switch", "turn_on" if on else "turn_off", {"entity_id": entity}
            case "cec_input" | "cec_output":
                port_type = "input" if action.intent == "cec_input" else "output"
                return DOMAIN, "send_cec_command", {"port_type": port_type, "port_num": p[port_type],
                                                    "command": p["command"]}
            case "ha_service":
                data = dict(p.get("data") or {})
                if p.get("entity"):  # e.g. "button.reboot" -> that entity's id
                    data["entity_id"] = await self._entity_id(p["entity"])
                if p.get("target") == "entry":
                    data["config_entry_id"] = self.entry_id
                elif p.get("target") == "device":
                    devices = await self._ws_call("config/device_registry/list")
                    data["device_id"] = next(d["id"] for d in devices if self.entry_id in (d.get("config_entries") or []))
                return p["domain"], p["service"], data
        raise NotSupportedError(action.intent)

    async def perform(self, action: Action) -> ActionResult:
        if action.intent not in self.intents:
            raise NotSupportedError(action.intent)
        result = ActionResult(intent=action.intent, ok=False)
        t0 = time.perf_counter()
        if action.intent == "ha_config_flow":
            result.status = await self._config_flow(result.requests, action.params.get("options"))
            result.ok = result.status == 200
            result.steps.extend(f"{r['method']} {r['path']} {r['body'] or ''} -> HTTP {r['status']} "
                                f"{(r['response'] or {}).get('type', '') if isinstance(r['response'], dict) else ''}"
                                for r in result.requests)
        elif action.intent == "ha_reconfigure":
            await self._ensure_entry()
            result.status = await self._reconfigure(result, action.params)
            result.ok = result.status == 200
        else:
            await self._ensure_entry()
            domain, service, data = await self._service_call(action)
            await self._service(domain, service, data, result)
        result.body = {"home_assistant": self.version, "entry_id": self.entry_id}
        result.elapsed_ms = round((time.perf_counter() - t0) * 1000, 1)
        return result

    async def _reconfigure(self, result: ActionResult, params: dict[str, Any]) -> int:
        """The entry's Reconfigure dialog: point it at the hub by another address (``host="ip"``: the host's IP)."""
        host = params.get("host", self.hub_host)
        if host == "ip":  # the Docker host's IPv4 address as the container resolves it
            out = _docker("exec", self.container or "", "getent", "ahostsv4", HOST_ALIAS, check=False, timeout=60)
            host = out.stdout.split()[0] if out.stdout.split() else self.hub_host
        flow = await self._http("POST", "/api/config/config_entries/flow",
                                {"handler": DOMAIN, "entry_id": self.entry_id},
                                record=result.requests)
        done = await self._http("POST", f"/api/config/config_entries/flow/{flow['flow_id']}",
                                {"host": host, "port": params.get("port", self.hub_port)}, record=result.requests)
        result.steps.extend(f"{r['method']} {r['path']} {r['body'] or ''} -> HTTP {r['status']}"
                            for r in result.requests)
        result.steps.append(f"flow result: {done.get('type')} {done.get('reason') or done.get('errors') or ''}")
        if done.get("type") != "abort" or done.get("reason") != "reconfigure_successful":
            return 400
        self.hub_host = host
        await asyncio.sleep(1)
        await self._wait_loaded()
        return 200

    def environment(self) -> dict[str, Any]:
        manifest = json.loads((COMPONENT / "manifest.json").read_text(encoding="utf-8"))
        return {
            "name": self.name,
            "client": "real Home Assistant container (tools/validate/clients/ha.py)",
            "home_assistant": self.version,
            "image": self.image,
            "image_digest": self.image_digest,
            "component": f"custom_components/{DOMAIN} {manifest.get('version')}",
            "hub_url_from_home_assistant": f"http://{self.hub_host}:{self.hub_port}",
            "setup": self.setup_steps,
            "aiohttp": aiohttp.__version__,
        }
