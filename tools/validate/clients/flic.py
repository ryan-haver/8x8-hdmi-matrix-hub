"""Dedicated Flic replay client (WP-D1 / R6).

Provides exact-request replay and Flic Hub SDK gesture matching for validation.
Authoritative templates:
- web/js/components/integrations-drawer.js (updateFlicOutput / updateFlicSdkSnippet)
- web/js/utils/api-copy.js
- docs/FLIC_SETUP.md

Key architectural invariants:
1. Does NOT inherit from or delegate to ApiClient; owns its request builder and HTTP transport.
2. Emits exact keyless requests matching the drawer by default.
3. Explicitly distinguishes documented manual X-API-Key and ?key=/&key= variants.
4. Asserts refusal for protected profile PINs on drawer requests (no synthetic bypass).
5. Dispatches CEC commands directly to hub to assert REST 400 refusal semantics.
6. Redacts all API keys, query keys, PIN secrets, and raw exception strings in ActionResult evidence.
7. Executes real updateFlicOutput and updateFlicSdkSnippet via narrow Node driver (flic_driver.mjs).
"""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import time
import urllib.parse
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import aiohttp

from ..model import Action
from .base import ActionResult, Client, HubInfo, NotSupportedError

REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_DRAWER_PATH = REPO_ROOT / "web" / "js" / "components" / "integrations-drawer.js"
DRIVER_MJS = REPO_ROOT / "tools" / "validate" / "clients" / "flic_driver.mjs"


def get_node_version() -> str:
    """Return the installed Node.js version string, or 'unknown' if unavailable."""
    try:
        res = subprocess.run(["node", "-v"], capture_output=True, text=True, check=True)
        return res.stdout.strip()
    except Exception:
        return "unknown"


def get_drawer_sha256(source_path: Path | None = None) -> str:
    """Compute SHA-256 digest of integrations-drawer.js."""
    target = source_path or DEFAULT_DRAWER_PATH
    if target.is_file():
        return hashlib.sha256(target.read_bytes()).hexdigest()
    return "unknown"


def run_flic_driver(mode: str, payload: dict[str, Any]) -> dict[str, Any]:
    """Execute flic_driver.mjs in Node with JSON payload."""
    res = subprocess.run(
        ["node", str(DRIVER_MJS), mode],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        check=True,
    )
    return json.loads(res.stdout)


def redact_path(path: str) -> str:
    """Mask ?key=... and &key=... query strings in URLs/paths/strings."""
    return re.sub(r"([?&]key=)[^&]+", r"\1***REDACTED***", path)


def redact_headers(headers: dict[str, str]) -> dict[str, str]:
    """Mask authentication headers."""
    redacted = dict(headers)
    for k in list(redacted.keys()):
        if k.lower() in ("x-api-key", "authorization", "x-admin-pin"):
            redacted[k] = "***REDACTED***"
    return redacted


def redact_body(body: Any) -> Any:
    """Mask passwords, PINs, and secret keys in JSON payloads."""
    if isinstance(body, dict):
        out: dict[str, Any] = {}
        for k, v in body.items():
            if k.lower() in ("passcode", "pin", "password", "key", "secret", "api_key"):
                out[k] = "***REDACTED***"
            elif isinstance(v, (dict, list)):
                out[k] = redact_body(v)
            else:
                out[k] = v
        return out
    if isinstance(body, list):
        return [redact_body(item) for item in body]
    return body


@dataclass(frozen=True)
class FlicButtonInfo:
    name: str
    bdaddr: str
    serial: str = ""


@dataclass(frozen=True)
class FlicSdkEvent:
    event_name: str  # "buttonSingleOrDoubleClickOrHold" | "buttonRotate"
    bdaddr: str
    is_single_click: bool = False
    is_double_click: bool = False
    is_hold: bool = False
    button_number: int | None = None  # 0 for left, 1 for right (Duo)
    direction: int = 0  # > 0 for CW, < 0 for CCW (Twist)


def build_drawer_request(
    action: Action,
    *,
    legacy_all_output: bool = False,
    source_path: Path | None = None,
) -> tuple[str, str, Any, dict[str, str], dict[str, Any]]:
    """Build exact request matching the Drawer / SDK templates using Node bridge.

    Returns: (method, path, body, headers, metadata)
    """
    p = action.params
    metadata: dict[str, Any] = {"request_type": "generated_drawer"}
    method = "POST"
    headers: dict[str, str] = {}
    body: Any = None
    path: str = ""

    match action.intent:
        case "preset_recall":
            preset = int(p.get("preset", 1))
            driver_out = run_flic_driver(
                "--generate",
                {
                    "config": {"targetType": "preset", "presetNum": preset},
                    "sourcePath": str(source_path) if source_path else None,
                },
            )
            method = driver_out["method"]
            path = driver_out["urlPath"]
            body = driver_out["body"]

        case "profile_recall":
            profile_id = str(p.get("profile_id", ""))
            driver_out = run_flic_driver(
                "--generate",
                {
                    "config": {"targetType": "profile", "profileId": profile_id},
                    "sourcePath": str(source_path) if source_path else None,
                },
            )
            method = driver_out["method"]
            path = driver_out["urlPath"]
            # The drawer emits no body for profile recall. If a manual passcode test is explicitly
            # requested via "manual_passcode", include it and record the distinct request type.
            if p.get("manual_passcode") is not None:
                body = {"passcode": str(p["manual_passcode"])}
                headers["Content-Type"] = "application/json"
                metadata["request_type"] = "manual_passcode"
            else:
                body = driver_out["body"]

        case "route_all":
            input_num = int(p.get("input", 1))
            # Known defect: pre-fix template targeted absent route POST /api/input/{n}
            if legacy_all_output or p.get("legacy_defect", False):
                path = f"/api/input/{input_num}"
                metadata["request_type"] = "legacy_defect"
            else:
                driver_out = run_flic_driver(
                    "--generate",
                    {
                        "config": {"targetType": "switch_all", "inputNum": input_num},
                        "sourcePath": str(source_path) if source_path else None,
                    },
                )
                method = driver_out["method"]
                path = driver_out["urlPath"]
                body = driver_out["body"]
                if body is not None:
                    headers["Content-Type"] = "application/json"

        case "route":
            input_num = int(p.get("input", 1))
            output_num = int(p.get("output", 1))
            driver_out = run_flic_driver(
                "--generate",
                {
                    "config": {"targetType": "switch_output", "inputNum": input_num, "outputNum": output_num},
                    "sourcePath": str(source_path) if source_path else None,
                },
            )
            method = driver_out["method"]
            path = driver_out["urlPath"]
            body = driver_out["body"]
            if body is not None:
                headers["Content-Type"] = "application/json"

        case "cycle_input":
            cycle_dir = str(p.get("cycle_dir") or p.get("direction", "next")).lower()
            output_num = int(p.get("output", 1))
            driver_out = run_flic_driver(
                "--generate",
                {
                    "config": {"targetType": "cycle_input", "cycleDir": cycle_dir, "outputNum": output_num},
                    "sourcePath": str(source_path) if source_path else None,
                },
            )
            method = driver_out["method"]
            path = driver_out["urlPath"]
            body = driver_out["body"]

        case "volume_control":
            vol_dir = str(p.get("vol_dir") or p.get("action") or p.get("direction", "volume_up")).lower()
            output_num = int(p.get("output", 1))
            driver_out = run_flic_driver(
                "--generate",
                {
                    "config": {"targetType": "volume_control", "volDir": vol_dir, "outputNum": output_num},
                    "sourcePath": str(source_path) if source_path else None,
                },
            )
            method = driver_out["method"]
            path = driver_out["urlPath"]
            body = driver_out["body"]

        case "matrix_power":
            is_on = bool(p.get("on", True))
            driver_out = run_flic_driver(
                "--generate",
                {
                    "config": {"targetType": "power", "powerCmd": "on" if is_on else "off"},
                    "sourcePath": str(source_path) if source_path else None,
                },
            )
            method = driver_out["method"]
            path = driver_out["urlPath"]
            body = driver_out["body"]

        case "cec_input":
            input_num = int(p.get("input", 1))
            command = str(p.get("command", "power_on")).lower()
            driver_out = run_flic_driver(
                "--generate",
                {
                    "config": {
                        "targetType": "cec",
                        "cecTargetType": "input",
                        "cecTargetPort": input_num,
                        "cecCmd": command,
                    },
                    "sourcePath": str(source_path) if source_path else None,
                },
            )
            method = driver_out["method"]
            path = driver_out["urlPath"]
            body = driver_out["body"]

        case "cec_output":
            output_num = int(p.get("output", 1))
            command = str(p.get("command", "power_on")).lower()
            driver_out = run_flic_driver(
                "--generate",
                {
                    "config": {
                        "targetType": "cec",
                        "cecTargetType": "output",
                        "cecTargetPort": output_num,
                        "cecCmd": command,
                    },
                    "sourcePath": str(source_path) if source_path else None,
                },
            )
            method = driver_out["method"]
            path = driver_out["urlPath"]
            body = driver_out["body"]

        case "macro_run":
            macro_id = str(p.get("macro_id", ""))
            path = f"/api/cec/macro/{macro_id}/execute"

        case "flic_register":
            buttons = p.get("buttons", [])
            path = "/api/integrations/flic/register"
            body = {"buttons": buttons}
            headers["Content-Type"] = "application/json"

        case _:
            raise NotSupportedError(f"intent {action.intent!r} is not supported by Flic replay")

    # Documented manual API key variants
    api_key = p.get("api_key")
    if api_key is not None:
        auth_mode = str(p.get("auth_mode") or p.get("key_placement", "header")).lower()
        if auth_mode == "query" or p.get("query_key", False):
            encoded_key = urllib.parse.quote(str(api_key), safe="")
            sep = "&" if "?" in path else "?"
            path = f"{path}{sep}key={encoded_key}"
            metadata["auth_mode"] = "query"
        else:
            headers["X-API-Key"] = str(api_key)
            metadata["auth_mode"] = "header"
    else:
        metadata["auth_mode"] = "keyless"

    return method, path, body, headers, metadata


def generate_flic_sdk_snippet(
    *,
    origin: str = "http://192.168.0.100:8080",
    button_type: str = "button",
    button_identifier: str = "",
    target_type: str = "preset",
    gesture: str = "single",
    preset_num: int = 1,
    profile_id: str = "",
    input_num: int = 1,
    output_num: int = 1,
    cycle_dir: str = "next",
    vol_dir: str = "volume_up",
    power_cmd: str = "on",
    cec_target_type: str = "input",
    cec_target_port: int = 1,
    cec_cmd: str = "power_on",
    model_name: str = "HDMI Matrix",
    legacy_all_output: bool = False,
    source_path: Path | None = None,
) -> str:
    """Authoritative JavaScript snippet generator executing updateFlicSdkSnippet via Node driver."""
    config = {
        "buttonType": button_type,
        "buttonIdentifier": button_identifier,
        "targetType": target_type,
        "gesture": gesture,
        "presetNum": preset_num,
        "profileId": profile_id,
        "inputNum": input_num,
        "outputNum": output_num,
        "cycleDir": cycle_dir,
        "volDir": vol_dir,
        "powerCmd": power_cmd,
        "cecTargetType": cec_target_type,
        "cecTargetPort": cec_target_port,
        "cecCmd": cec_cmd,
    }
    payload: dict[str, Any] = {"config": config, "origin": origin}
    if source_path is not None:
        payload["sourcePath"] = str(source_path)

    out = run_flic_driver("--generate", payload)
    snippet: str = out["snippet"]

    if legacy_all_output and target_type == "switch_all":
        snippet = snippet.replace("/api/switch", f"/api/input/{input_num}")
        snippet = re.sub(
            r',\s*headers: \{"Content-Type": "application/json"\},\s*content: JSON\.stringify\(\{"input":\d+\}\)',
            "",
            snippet,
        )

    return snippet


class FlicSdkEngine:
    """Executes Flic Hub SDK scripts (startup registration & gesture matching) via Node harness."""

    def __init__(
        self,
        *,
        origin: str,
        button_type: str = "button",
        button_identifier: str = "",
        target_type: str = "preset",
        gesture: str = "single",
        preset_num: int = 1,
        profile_id: str = "",
        input_num: int = 1,
        output_num: int = 1,
        cycle_dir: str = "next",
        vol_dir: str = "volume_up",
        power_cmd: str = "on",
        cec_target_type: str = "input",
        cec_target_port: int = 1,
        cec_cmd: str = "power_on",
        legacy_all_output: bool = False,
        source_path: Path | None = None,
    ) -> None:
        self.origin = origin.rstrip("/")
        self.button_type = button_type
        self.button_identifier = button_identifier.strip()
        self.target_type = target_type
        self.gesture = gesture
        self.preset_num = preset_num
        self.profile_id = profile_id
        self.input_num = input_num
        self.output_num = output_num
        self.cycle_dir = cycle_dir
        self.vol_dir = vol_dir
        self.power_cmd = power_cmd
        self.cec_target_type = cec_target_type
        self.cec_target_port = cec_target_port
        self.cec_cmd = cec_cmd
        self.legacy_all_output = legacy_all_output
        self.source_path = source_path

        # Generate authoritative snippet for this configuration
        self.snippet = generate_flic_sdk_snippet(
            origin=self.origin,
            button_type=self.button_type,
            button_identifier=self.button_identifier,
            target_type=self.target_type,
            gesture=self.gesture,
            preset_num=self.preset_num,
            profile_id=self.profile_id,
            input_num=self.input_num,
            output_num=self.output_num,
            cycle_dir=self.cycle_dir,
            vol_dir=self.vol_dir,
            power_cmd=self.power_cmd,
            cec_target_type=self.cec_target_type,
            cec_target_port=self.cec_target_port,
            cec_cmd=self.cec_cmd,
            legacy_all_output=self.legacy_all_output,
            source_path=self.source_path,
        )

    def startup_request(self, buttons: list[FlicButtonInfo]) -> dict[str, Any]:
        """Returns the SDK startup button registration HTTP request."""
        payload = [
            {"name": b.name, "bdaddr": b.bdaddr, "serial": b.serial}
            for b in buttons
        ]
        return {
            "method": "POST",
            "url": f"{self.origin}/api/integrations/flic/register",
            "headers": {"Content-Type": "application/json"},
            "body": {"buttons": payload},
        }

    def evaluate_event(
        self,
        event: FlicSdkEvent,
        button_registry: dict[str, FlicButtonInfo],
    ) -> dict[str, Any] | None:
        """Evaluate an SDK event against the real generated script in Node harness.

        Returns the HTTP request dictionary if triggered, or None if skipped/mismatched.
        """
        evt_payload: dict[str, Any] = {
            "bdaddr": event.bdaddr,
            "isSingleClick": event.is_single_click,
            "isDoubleClick": event.is_double_click,
            "isHold": event.is_hold,
            "direction": event.direction,
        }
        if event.button_number is not None:
            evt_payload["buttonNumber"] = event.button_number

        harness_payload = {
            "script": self.snippet,
            "buttons": [
                {"name": b.name, "bdaddr": b.bdaddr, "serial": b.serial}
                for b in button_registry.values()
            ],
            "events": [
                {
                    "eventName": event.event_name,
                    "payload": evt_payload,
                }
            ],
        }

        res = run_flic_driver("--harness", harness_payload)
        event_results = res.get("eventResults", [])
        if not event_results or event_results[0].get("requestsTriggered", 0) == 0:
            return None

        req = event_results[0]["requests"][0]
        body = None
        if req.get("content"):
            try:
                body = json.loads(req["content"])
            except Exception:
                body = req["content"]

        return {
            "method": req.get("method", "POST"),
            "url": req.get("url", ""),
            "headers": req.get("headers", {}),
            "body": body,
        }


class FlicClient(Client):
    """The dedicated Flic replay client.

    Subclasses Client, owns its own request builder/transport, supports exact
    generated drawer/SDK snippet requests, and performs click/gesture evaluation.
    """

    name = "flic"
    hub_mode = "api"
    observes = False
    intents = frozenset(
        {
            "preset_recall",
            "profile_recall",
            "route",
            "route_all",
            "cycle_input",
            "volume_control",
            "matrix_power",
            "cec_input",
            "cec_output",
            "macro_run",
            "flic_register",
            "flic_sdk_event",
        }
    )

    def __init__(self) -> None:
        super().__init__()
        self._session: aiohttp.ClientSession | None = None
        self.hub: HubInfo | None = None

    def supports(self, action: Action) -> bool:
        if action.intent not in self.intents:
            return False
        return True

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

    async def observe(self, key: str) -> Any:
        raise NotSupportedError(
            f"client '{self.name}' cannot observe {key!r} (physical Flic buttons cannot observe or display matrix state)"
        )

    def environment(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "transport": "aiohttp",
            "aiohttp": aiohttp.__version__,
            "node_version": get_node_version(),
            "drawer_source_sha256": get_drawer_sha256(),
            "templates": [
                "web/js/components/integrations-drawer.js",
                "web/js/utils/api-copy.js",
                "docs/FLIC_SETUP.md",
            ],
            "node_stubs": "unobserved",
            "flic_sdk_runtime": "unobserved",
            "physical_buttons": "unobserved",
        }

    async def perform(self, action: Action) -> ActionResult:
        if not self.supports(action):
            raise NotSupportedError(f"client '{self.name}' cannot perform '{action.intent}'")

        assert self._session is not None, "client not started"
        result = ActionResult(intent=action.intent, ok=False)
        t0 = time.perf_counter()

        # Handle SDK event simulation intent
        if action.intent == "flic_sdk_event":
            p = action.params
            engine = FlicSdkEngine(
                origin=self.hub.base_url if self.hub else "http://127.0.0.1:8080",
                button_type=p.get("button_type", "button"),
                button_identifier=p.get("button_identifier", ""),
                target_type=p.get("target_type", "preset"),
                gesture=p.get("gesture", "single"),
                preset_num=int(p.get("preset_num", 1)),
                profile_id=str(p.get("profile_id", "")),
                input_num=int(p.get("input_num", 1)),
                output_num=int(p.get("output_num", 1)),
                cycle_dir=str(p.get("cycle_dir", "next")),
                vol_dir=str(p.get("vol_dir", "volume_up")),
                power_cmd=str(p.get("power_cmd", "on")),
                cec_target_type=str(p.get("cec_target_type", "input")),
                cec_target_port=int(p.get("cec_target_port", 1)),
                cec_cmd=str(p.get("cec_cmd", "power_on")),
                legacy_all_output=bool(p.get("legacy_all_output", False)),
            )

            # Optional startup registration phase
            if p.get("run_startup_registration"):
                buttons_raw = p.get("buttons", [])
                buttons = [FlicButtonInfo(b["name"], b["bdaddr"], b.get("serial", "")) for b in buttons_raw]
                reg_req = engine.startup_request(buttons)
                reg_record = {
                    "method": reg_req["method"],
                    "path": "/api/integrations/flic/register",
                    "headers": reg_req["headers"],
                    "body": redact_body(reg_req["body"]),
                }
                async with self._session.request(
                    reg_req["method"], "/api/integrations/flic/register", json=reg_req["body"], headers=reg_req["headers"]
                ) as resp:
                    parsed: Any = None
                    try:
                        parsed = await resp.json(content_type=None)
                    except ValueError:
                        parsed = await resp.text()
                    reg_record["status"] = resp.status
                    reg_record["response"] = parsed
                    result.requests.append(reg_record)

            # Event dispatch
            evt_data = p.get("event", {})
            evt = FlicSdkEvent(
                event_name=evt_data.get("event_name", "buttonSingleOrDoubleClickOrHold"),
                bdaddr=evt_data.get("bdaddr", ""),
                is_single_click=bool(evt_data.get("is_single_click", False)),
                is_double_click=bool(evt_data.get("is_double_click", False)),
                is_hold=bool(evt_data.get("is_hold", False)),
                button_number=evt_data.get("button_number"),
                direction=int(evt_data.get("direction", 0)),
            )
            raw_reg = p.get("button_registry", {})
            reg = {k: FlicButtonInfo(v["name"], v["bdaddr"], v.get("serial", "")) for k, v in raw_reg.items()}

            req_spec = engine.evaluate_event(evt, reg)
            if req_spec is None:
                # Event did not match trigger or filter: zero requests triggered
                result.ok = True
                result.status = 200
                result.steps.append(f"SDK event {evt.event_name} ignored (no matching trigger or button filter)")
                result.elapsed_ms = round((time.perf_counter() - t0) * 1000, 1)
                return result

            # Matching event: make the single triggered HTTP request
            target_path = req_spec["url"].replace(engine.origin, "", 1)
            method = req_spec["method"]
            body = req_spec["body"]
            headers = req_spec["headers"]
            metadata = {"request_type": "flic_sdk_event"}
        else:
            method, target_path, body, headers, metadata = build_drawer_request(action)

        req_headers: dict[str, str] = {}
        forwarded = self.context.get("forwarded_for")
        if forwarded:
            req_headers["X-Forwarded-For"] = forwarded
        if headers:
            req_headers.update(headers)

        record: dict[str, Any] = {
            "method": method,
            "path": redact_path(target_path),
            "headers": redact_headers(req_headers),
            "body": redact_body(body),
            "metadata": metadata,
        }

        try:
            req_kwargs: dict[str, Any] = {"headers": req_headers}
            if body is not None:
                req_kwargs["json"] = body

            async with self._session.request(method, target_path, **req_kwargs) as resp:
                text = await resp.text()
                try:
                    parsed_resp: Any = await resp.json(content_type=None) if text else None
                except ValueError:
                    parsed_resp = text[:2000]

                record["status"] = resp.status
                record["response"] = parsed_resp
                record["elapsed_ms"] = round((time.perf_counter() - t0) * 1000, 1)
                result.requests.append(record)
                result.status = resp.status
                result.body = parsed_resp

                # Check HTTP envelope and partial effects
                is_http_ok = 200 <= resp.status < 300
                is_multi_status_207 = resp.status == 207
                is_payload_success = True
                if isinstance(parsed_resp, dict):
                    if parsed_resp.get("success") is False:
                        is_payload_success = False

                result.ok = is_http_ok and not is_multi_status_207 and is_payload_success
                result.steps.append(
                    f"{method} {redact_path(target_path)}"
                    + (f" {redact_body(body)}" if body is not None else "")
                    + f" -> HTTP {resp.status}"
                )
        except (aiohttp.ClientError, TimeoutError) as exc:
            raw_err = f"{type(exc).__name__}: {exc}"
            result.error = redact_path(raw_err)
            result.steps.append(f"{method} {redact_path(target_path)} -> {result.error}")

        result.elapsed_ms = round((time.perf_counter() - t0) * 1000, 1)
        return result
