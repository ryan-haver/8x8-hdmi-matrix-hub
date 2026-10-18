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
5. Asserts refusal for invalid CEC target/command combinations.
6. Redacts all API keys, query keys, and PIN secrets in ActionResult.requests and evidence.
7. Exercises actual Flic Hub SDK callback patterns with stubbed button/http managers.
"""

from __future__ import annotations

import json
import re
import time
from dataclasses import dataclass
from typing import Any

import aiohttp

from ..model import Action
from .base import ActionResult, Client, HubInfo, NotSupportedError

VALID_CEC_INPUT_COMMANDS = frozenset({"power_on", "power_off", "play", "pause"})
VALID_CEC_OUTPUT_COMMANDS = frozenset(
    {"power_on", "power_off", "play", "pause", "mute", "volume_up", "volume_down"}
)


def redact_path(path: str) -> str:
    """Mask ?key=... and &key=... query strings in URLs/paths."""
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
) -> tuple[str, str, Any, dict[str, str], dict[str, Any]]:
    """Build exact request matching the Drawer / SDK templates.

    Returns: (method, path, body, headers, metadata)
    """
    p = action.params
    metadata: dict[str, Any] = {"request_type": "generated_drawer"}
    method = "POST"
    headers: dict[str, str] = {}
    body: Any = None

    match action.intent:
        case "preset_recall":
            preset = int(p.get("preset", 1))
            path = f"/api/preset/{preset}"

        case "profile_recall":
            profile_id = str(p.get("profile_id", ""))
            path = f"/api/profile/{profile_id}/recall"
            # The drawer emits no body for profile recall. If a manual passcode test is explicitly
            # requested via "manual_passcode", include it and record the distinct request type.
            if p.get("manual_passcode") is not None:
                body = {"passcode": str(p["manual_passcode"])}
                headers["Content-Type"] = "application/json"
                metadata["request_type"] = "manual_passcode"

        case "route_all":
            input_num = int(p.get("input", 1))
            # Known defect: pre-fix template targeted absent route POST /api/input/{n}
            if legacy_all_output or p.get("legacy_defect", False):
                path = f"/api/input/{input_num}"
                metadata["request_type"] = "legacy_defect"
            else:
                path = "/api/switch"
                body = {"input": input_num}
                headers["Content-Type"] = "application/json"

        case "route":
            input_num = int(p.get("input", 1))
            output_num = int(p.get("output", 1))
            path = f"/api/output/{output_num}/source"
            body = {"input": input_num}
            headers["Content-Type"] = "application/json"

        case "cycle_input":
            cycle_dir = str(p.get("cycle_dir") or p.get("direction", "next")).lower()
            output_num = int(p.get("output", 1))
            path = f"/api/input/{cycle_dir}?output={output_num}"

        case "volume_control":
            vol_dir = str(p.get("vol_dir") or p.get("action") or p.get("direction", "volume_up")).lower()
            output_num = int(p.get("output", 1))
            path = f"/api/cec/output/{output_num}/{vol_dir}"

        case "matrix_power":
            is_on = bool(p.get("on", True))
            path = f"/api/power/{'on' if is_on else 'off'}"

        case "cec_input":
            input_num = int(p.get("input", 1))
            command = str(p.get("command", "power_on")).lower()
            if command not in VALID_CEC_INPUT_COMMANDS:
                raise NotSupportedError(
                    f"unsupported CEC input command {command!r}; Flic only supports {sorted(VALID_CEC_INPUT_COMMANDS)}"
                )
            path = f"/api/cec/input/{input_num}/{command}"

        case "cec_output":
            output_num = int(p.get("output", 1))
            command = str(p.get("command", "power_on")).lower()
            if command not in VALID_CEC_OUTPUT_COMMANDS:
                raise NotSupportedError(
                    f"unsupported CEC output command {command!r}; Flic only supports {sorted(VALID_CEC_OUTPUT_COMMANDS)}"
                )
            path = f"/api/cec/output/{output_num}/{command}"

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
            sep = "&" if "?" in path else "?"
            path = f"{path}{sep}key={api_key}"
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
) -> str:
    """Exact JavaScript snippet generator matching updateFlicSdkSnippet in integrations-drawer.js."""
    url_path = ""
    body_obj: dict[str, Any] | None = None
    method = "POST"

    match target_type:
        case "preset":
            url_path = f"/api/preset/{preset_num}"
        case "profile":
            url_path = f"/api/profile/{profile_id}/recall"
        case "switch_all":
            if legacy_all_output:
                url_path = f"/api/input/{input_num}"
            else:
                url_path = "/api/switch"
                body_obj = {"input": input_num}
        case "switch_output":
            url_path = f"/api/output/{output_num}/source"
            body_obj = {"input": input_num}
        case "cycle_input":
            url_path = f"/api/input/{cycle_dir}?output={output_num}"
        case "volume_control":
            url_path = f"/api/cec/output/{output_num}/{vol_dir}"
        case "power":
            url_path = f"/api/power/{power_cmd}"
        case "cec":
            url_path = f"/api/cec/{cec_target_type}/{cec_target_port}/{cec_cmd}"

    if gesture == "left_single":
        trigger_condition = "obj.buttonNumber === 0 && obj.isSingleClick"
        event_name = "buttonSingleOrDoubleClickOrHold"
    elif gesture == "left_double":
        trigger_condition = "obj.buttonNumber === 0 && obj.isDoubleClick"
        event_name = "buttonSingleOrDoubleClickOrHold"
    elif gesture == "left_hold":
        trigger_condition = "obj.buttonNumber === 0 && obj.isHold"
        event_name = "buttonSingleOrDoubleClickOrHold"
    elif gesture == "right_single":
        trigger_condition = "obj.buttonNumber === 1 && obj.isSingleClick"
        event_name = "buttonSingleOrDoubleClickOrHold"
    elif gesture == "right_double":
        trigger_condition = "obj.buttonNumber === 1 && obj.isDoubleClick"
        event_name = "buttonSingleOrDoubleClickOrHold"
    elif gesture == "right_hold":
        trigger_condition = "obj.buttonNumber === 1 && obj.isHold"
        event_name = "buttonSingleOrDoubleClickOrHold"
    elif gesture == "single":
        trigger_condition = "obj.isSingleClick"
        event_name = "buttonSingleOrDoubleClickOrHold"
    elif gesture == "double":
        trigger_condition = "obj.isDoubleClick"
        event_name = "buttonSingleOrDoubleClickOrHold"
    elif gesture == "hold":
        trigger_condition = "obj.isHold"
        event_name = "buttonSingleOrDoubleClickOrHold"
    elif gesture == "rotate_cw":
        trigger_condition = "obj.direction > 0"
        event_name = "buttonRotate"
    elif gesture == "rotate_ccw":
        trigger_condition = "obj.direction < 0"
        event_name = "buttonRotate"
    else:
        trigger_condition = "obj.isSingleClick"
        event_name = "buttonSingleOrDoubleClickOrHold"

    body_clause = ""
    if body_obj is not None:
        body_clause = f',\n            headers: {{"Content-Type": "application/json"}},\n            content: JSON.stringify({json.dumps(body_obj)})'

    action_code = (
        f'        http.makeRequest({{\n'
        f'            url: API_BASE + "{url_path}",\n'
        f'            method: "{method}"{body_clause}\n'
        f'        }}, function(err, res) {{\n'
        f'            console.log(err ? "Request failed" : "Matrix updated successfully!");\n'
        f'        }});'
    )

    identifier = button_identifier.strip()
    if identifier:
        handler_body = (
            f'    var button = buttonManager.getButton(obj.bdaddr);\n'
            f'    if (button && (button.name === "{identifier}" || obj.bdaddr === "{identifier}")) {{\n'
            f'        if ({trigger_condition}) {{\n'
            f'            console.log("Flic Button trigger detected - updating {model_name}");\n'
            f'{action_code}\n'
            f'        }}\n'
            f'    }}'
        )
    else:
        handler_body = (
            f'    if ({trigger_condition}) {{\n'
            f'        console.log("Flic Button trigger detected - updating {model_name}");\n'
            f'{action_code}\n'
            f'    }}'
        )

    return (
        f'// {model_name} Hub - Flic Hub SDK Integration Script\n'
        f'// Paste this in the Flic Hub IDE (https://hubsdk.flic.io/)\n\n'
        f'var buttonManager = require("buttons");\n'
        f'var http = require("http");\n\n'
        f'var API_BASE = "{origin}";\n\n'
        f'// Automatically register all paired buttons with the {model_name} Hub server on startup\n'
        f'try {{\n'
        f'    var buttons = buttonManager.getButtons().map(function(btn) {{\n'
        f'        return {{ name: btn.name, bdaddr: btn.bdaddr, serial: btn.serialNumber || "" }};\n'
        f'    }});\n'
        f'    http.makeRequest({{\n'
        f'        url: API_BASE + "/api/integrations/flic/register",\n'
        f'        method: "POST",\n'
        f'        headers: {{"Content-Type": "application/json"}},\n'
        f'        content: JSON.stringify({{buttons: buttons}})\n'
        f'    }}, function(err, res) {{\n'
        f'        console.log(err ? "Failed to register buttons with {model_name} Hub" : "Buttons registered successfully!");\n'
        f'    }});\n'
        f'}} catch (e) {{\n'
        f'    console.log("Startup registration failed: " + e);\n'
        f'}}\n\n'
        f'buttonManager.on("{event_name}", function(obj) {{\n'
        f'{handler_body}\n'
        f'}});\n\n'
        f'console.log("{model_name} Control script loaded successfully!");\n'
    )


class FlicSdkEngine:
    """Simulates Flic Hub SDK execution (startup registration & gesture matching)."""

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
        """Evaluate an SDK event against configured gesture and button filter.

        Returns the HTTP request dictionary if triggered, or None if skipped/mismatched.
        """
        # 1. Button identifier filter check
        if self.button_identifier:
            btn = button_registry.get(event.bdaddr)
            if not btn:
                return None
            if btn.name != self.button_identifier and event.bdaddr != self.button_identifier:
                return None

        # 2. Gesture condition check
        matched = False
        match self.gesture:
            case "single":
                matched = (
                    event.event_name == "buttonSingleOrDoubleClickOrHold"
                    and event.is_single_click
                    and (event.button_number is None or event.button_number == 0)
                )
            case "double":
                matched = (
                    event.event_name == "buttonSingleOrDoubleClickOrHold"
                    and event.is_double_click
                    and (event.button_number is None or event.button_number == 0)
                )
            case "hold":
                matched = (
                    event.event_name == "buttonSingleOrDoubleClickOrHold"
                    and event.is_hold
                    and (event.button_number is None or event.button_number == 0)
                )
            case "left_single":
                matched = (
                    event.event_name == "buttonSingleOrDoubleClickOrHold"
                    and event.button_number == 0
                    and event.is_single_click
                )
            case "left_double":
                matched = (
                    event.event_name == "buttonSingleOrDoubleClickOrHold"
                    and event.button_number == 0
                    and event.is_double_click
                )
            case "left_hold":
                matched = (
                    event.event_name == "buttonSingleOrDoubleClickOrHold"
                    and event.button_number == 0
                    and event.is_hold
                )
            case "right_single":
                matched = (
                    event.event_name == "buttonSingleOrDoubleClickOrHold"
                    and event.button_number == 1
                    and event.is_single_click
                )
            case "right_double":
                matched = (
                    event.event_name == "buttonSingleOrDoubleClickOrHold"
                    and event.button_number == 1
                    and event.is_double_click
                )
            case "right_hold":
                matched = (
                    event.event_name == "buttonSingleOrDoubleClickOrHold"
                    and event.button_number == 1
                    and event.is_hold
                )
            case "rotate_cw":
                matched = event.event_name == "buttonRotate" and event.direction > 0
            case "rotate_ccw":
                matched = event.event_name == "buttonRotate" and event.direction < 0

        if not matched:
            return None

        # 3. Build action HTTP request
        url_path = ""
        body_obj: dict[str, Any] | None = None
        headers: dict[str, str] = {}

        match self.target_type:
            case "preset":
                url_path = f"/api/preset/{self.preset_num}"
            case "profile":
                url_path = f"/api/profile/{self.profile_id}/recall"
            case "switch_all":
                if self.legacy_all_output:
                    url_path = f"/api/input/{self.input_num}"
                else:
                    url_path = "/api/switch"
                    body_obj = {"input": self.input_num}
                    headers["Content-Type"] = "application/json"
            case "switch_output":
                url_path = f"/api/output/{self.output_num}/source"
                body_obj = {"input": self.input_num}
                headers["Content-Type"] = "application/json"
            case "cycle_input":
                url_path = f"/api/input/{self.cycle_dir}?output={self.output_num}"
            case "volume_control":
                url_path = f"/api/cec/output/{self.output_num}/{self.vol_dir}"
            case "power":
                url_path = f"/api/power/{self.power_cmd}"
            case "cec":
                url_path = f"/api/cec/{self.cec_target_type}/{self.cec_target_port}/{self.cec_cmd}"

        return {
            "method": "POST",
            "url": f"{self.origin}{url_path}",
            "headers": headers,
            "body": body_obj,
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
        if action.intent == "cec_input":
            cmd = str(action.params.get("command", "power_on")).lower()
            if cmd not in VALID_CEC_INPUT_COMMANDS:
                return False
        if action.intent == "cec_output":
            cmd = str(action.params.get("command", "power_on")).lower()
            if cmd not in VALID_CEC_OUTPUT_COMMANDS:
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
            "templates": [
                "web/js/components/integrations-drawer.js",
                "web/js/utils/api-copy.js",
                "docs/FLIC_SETUP.md",
            ],
            "sdk_version": "1.0.0",
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
                result.ok = 200 <= resp.status < 300
                result.steps.append(
                    f"{method} {redact_path(target_path)}"
                    + (f" {redact_body(body)}" if body is not None else "")
                    + f" -> HTTP {resp.status}"
                )
        except (aiohttp.ClientError, TimeoutError) as exc:
            result.error = f"{type(exc).__name__}: {exc}"
            result.steps.append(f"{method} {redact_path(target_path)} -> {result.error}")

        result.elapsed_ms = round((time.perf_counter() - t0) * 1000, 1)
        return result
