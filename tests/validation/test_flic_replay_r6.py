"""Unit and mock integration tests for the dedicated Flic replay client (R6)."""

from __future__ import annotations

import pytest
from aiohttp import web

from tools.validate.clients import FlicClient, NotSupportedError, make_client
from tools.validate.clients.base import HubInfo
from tools.validate.clients.flic import (
    FlicButtonInfo,
    FlicSdkEngine,
    FlicSdkEvent,
    build_drawer_request,
    generate_flic_sdk_snippet,
    redact_body,
    redact_headers,
    redact_path,
)
from tools.validate.model import act


def test_flic_client_registration():
    client = make_client("flic")
    assert isinstance(client, FlicClient)
    assert client.name == "flic"
    assert client.hub_mode == "api"
    assert client.observes is False


def test_flic_client_intents_and_unsupported_intents():
    client = FlicClient()
    supported = {
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
    assert client.intents == supported
    assert client.supports(act("preset_recall", preset=1)) is True
    assert client.supports(act("route", input=2, output=1)) is True
    assert client.supports(act("route_all", input=3)) is True

    # Physical button client cannot observe state or perform UI/editor intents
    assert client.supports(act("scene_wait_edit", scene_id="s", seconds=1.0)) is False
    assert client.supports(act("preset_save", preset=1)) is False
    assert client.supports(act("port_rename", kind="input", port=1, name="TV")) is False
    assert client.supports(act("device_change")) is False


@pytest.mark.asyncio
async def test_observe_raises_not_supported():
    client = FlicClient()
    with pytest.raises(NotSupportedError, match="cannot observe"):
        await client.observe("outputs[0].source")


def test_environment_evidence():
    client = FlicClient()
    env = client.environment()
    assert env["name"] == "flic"
    assert env["transport"] == "aiohttp"
    assert "web/js/components/integrations-drawer.js" in env["templates"]
    assert "docs/FLIC_SETUP.md" in env["templates"]


def test_build_drawer_request_exact_base_requests():
    # 1. Hardware preset
    m, p, b, h, meta = build_drawer_request(act("preset_recall", preset=2))
    assert (m, p, b, h) == ("POST", "/api/preset/2", None, {})
    assert meta["request_type"] == "generated_drawer"

    # 2. Profile (generated drawer emits absent body)
    m, p, b, h, meta = build_drawer_request(act("profile_recall", profile_id="movie_night"))
    assert (m, p, b, h) == ("POST", "/api/profile/movie_night/recall", None, {})
    assert meta["request_type"] == "generated_drawer"

    # 3. Output source routing
    m, p, b, h, meta = build_drawer_request(act("route", input=3, output=2))
    assert (m, p, b, h) == ("POST", "/api/output/2/source", {"input": 3}, {"Content-Type": "application/json"})

    # 4. Corrected route_all (post-fix drawer generator)
    m, p, b, h, meta = build_drawer_request(act("route_all", input=4))
    assert (m, p, b, h) == ("POST", "/api/switch", {"input": 4}, {"Content-Type": "application/json"})

    # 5. Pre-fix route_all (defect reproduction)
    m, p, b, h, meta = build_drawer_request(act("route_all", input=4, legacy_defect=True))
    assert (m, p, b, h) == ("POST", "/api/input/4", None, {})
    assert meta["request_type"] == "legacy_defect"

    # 6. Cycle input
    m, p, b, h, _ = build_drawer_request(act("cycle_input", cycle_dir="next", output=1))
    assert (m, p, b, h) == ("POST", "/api/input/next?output=1", None, {})
    m, p, b, h, _ = build_drawer_request(act("cycle_input", cycle_dir="previous", output=3))
    assert (m, p, b, h) == ("POST", "/api/input/previous?output=3", None, {})

    # 7. Volume control
    m, p, b, h, _ = build_drawer_request(act("volume_control", vol_dir="volume_up", output=2))
    assert (m, p, b, h) == ("POST", "/api/cec/output/2/volume_up", None, {})
    m, p, b, h, _ = build_drawer_request(act("volume_control", vol_dir="mute", output=1))
    assert (m, p, b, h) == ("POST", "/api/cec/output/1/mute", None, {})

    # 8. Matrix power
    m, p, b, h, _ = build_drawer_request(act("matrix_power", on=True))
    assert (m, p, b, h) == ("POST", "/api/power/on", None, {})
    m, p, b, h, _ = build_drawer_request(act("matrix_power", on=False))
    assert (m, p, b, h) == ("POST", "/api/power/off", None, {})

    # 9. CEC input / output
    m, p, b, h, _ = build_drawer_request(act("cec_input", input=2, command="play"))
    assert (m, p, b, h) == ("POST", "/api/cec/input/2/play", None, {})
    m, p, b, h, _ = build_drawer_request(act("cec_output", output=1, command="power_off"))
    assert (m, p, b, h) == ("POST", "/api/cec/output/1/power_off", None, {})

    # 10. Macro run
    m, p, b, h, _ = build_drawer_request(act("macro_run", macro_id="all_off"))
    assert (m, p, b, h) == ("POST", "/api/cec/macro/all_off/execute", None, {})

    # 11. SDK registration
    buttons = [{"name": "Den", "bdaddr": "AA:BB:CC", "serial": "123"}]
    m, p, b, h, _ = build_drawer_request(act("flic_register", buttons=buttons))
    assert (m, p, b, h) == ("POST", "/api/integrations/flic/register", {"buttons": buttons}, {"Content-Type": "application/json"})


def test_auth_variants_header_and_query():
    # Keyless by default
    _, _, _, h, meta = build_drawer_request(act("preset_recall", preset=1))
    assert "X-API-Key" not in h
    assert meta["auth_mode"] == "keyless"

    # Header variant: X-API-Key
    _, _, _, h, meta = build_drawer_request(act("preset_recall", preset=1, api_key="secret-key-123"))
    assert h["X-API-Key"] == "secret-key-123"
    assert meta["auth_mode"] == "header"

    # Query variant without existing query param: ?key=
    _, p, _, h, meta = build_drawer_request(act("preset_recall", preset=1, api_key="secret-key-123", auth_mode="query"))
    assert p == "/api/preset/1?key=secret-key-123"
    assert "X-API-Key" not in h
    assert meta["auth_mode"] == "query"

    # Query variant WITH existing query param: &key= (cycle input)
    _, p, _, h, meta = build_drawer_request(
        act("cycle_input", cycle_dir="next", output=2, api_key="secret-key-123", auth_mode="query")
    )
    assert p == "/api/input/next?output=2&key=secret-key-123"
    assert "X-API-Key" not in h


def test_profile_pin_refusal_vs_manual_passcode_distinction():
    # Drawer generated profile recall has NO body/passcode
    _, _, body, _, meta = build_drawer_request(act("profile_recall", profile_id="locked_room", passcode="9999"))
    assert body is None
    assert meta["request_type"] == "generated_drawer"

    # Explicit manual passcode test is distinctly labeled
    _, _, body, headers, meta = build_drawer_request(
        act("profile_recall", profile_id="locked_room", manual_passcode="9999")
    )
    assert body == {"passcode": "9999"}
    assert headers["Content-Type"] == "application/json"
    assert meta["request_type"] == "manual_passcode"


def test_redaction_helpers():
    # Redact query keys
    assert redact_path("/api/preset/1?key=secret_123") == "/api/preset/1?key=***REDACTED***"
    assert redact_path("/api/input/next?output=1&key=secret_123") == "/api/input/next?output=1&key=***REDACTED***"
    assert redact_path("/api/status") == "/api/status"

    # Redact headers
    headers = {"Content-Type": "application/json", "X-API-Key": "my-secret-key", "Authorization": "Bearer xyz"}
    redacted_h = redact_headers(headers)
    assert redacted_h["Content-Type"] == "application/json"
    assert redacted_h["X-API-Key"] == "***REDACTED***"
    assert redacted_h["Authorization"] == "***REDACTED***"

    # Redact body
    body = {"passcode": "1234", "input": 2, "nested": {"pin": "5678", "label": "test"}}
    redacted_b = redact_body(body)
    assert redacted_b["passcode"] == "***REDACTED***"
    assert redacted_b["input"] == 2
    assert redacted_b["nested"]["pin"] == "***REDACTED***"
    assert redacted_b["nested"]["label"] == "test"


def test_sdk_engine_gesture_matching_and_filtering():
    engine = FlicSdkEngine(
        origin="http://192.168.0.100:8080",
        button_type="button",
        button_identifier="Living Room",
        target_type="switch_output",
        gesture="double",
        output_num=2,
        input_num=3,
    )
    buttons = {
        "AA:BB:CC": FlicButtonInfo(name="Living Room", bdaddr="AA:BB:CC"),
        "11:22:33": FlicButtonInfo(name="Bedroom", bdaddr="11:22:33"),
    }

    # 1. Matching button, matching double click -> produces request
    evt_match = FlicSdkEvent(event_name="buttonSingleOrDoubleClickOrHold", bdaddr="AA:BB:CC", is_double_click=True)
    req = engine.evaluate_event(evt_match, buttons)
    assert req is not None
    assert req["url"] == "http://192.168.0.100:8080/api/output/2/source"
    assert req["body"] == {"input": 3}

    # 2. Matching button, non-matching single click -> 0 requests
    evt_single = FlicSdkEvent(event_name="buttonSingleOrDoubleClickOrHold", bdaddr="AA:BB:CC", is_single_click=True)
    assert engine.evaluate_event(evt_single, buttons) is None

    # 3. Matching gesture, non-matching button -> 0 requests
    evt_wrong_btn = FlicSdkEvent(event_name="buttonSingleOrDoubleClickOrHold", bdaddr="11:22:33", is_double_click=True)
    assert engine.evaluate_event(evt_wrong_btn, buttons) is None

    # 4. Unknown button -> 0 requests
    evt_unknown = FlicSdkEvent(event_name="buttonSingleOrDoubleClickOrHold", bdaddr="99:99:99", is_double_click=True)
    assert engine.evaluate_event(evt_unknown, buttons) is None


def test_sdk_engine_duo_and_twist_gestures():
    # Duo left single click
    duo_engine = FlicSdkEngine(
        origin="http://192.168.0.100:8080",
        button_type="duo",
        gesture="left_single",
        target_type="preset",
        preset_num=1,
    )
    evt_left = FlicSdkEvent(event_name="buttonSingleOrDoubleClickOrHold", bdaddr="AA:BB", is_single_click=True, button_number=0)
    evt_right = FlicSdkEvent(event_name="buttonSingleOrDoubleClickOrHold", bdaddr="AA:BB", is_single_click=True, button_number=1)
    assert duo_engine.evaluate_event(evt_left, {}) is not None
    assert duo_engine.evaluate_event(evt_right, {}) is None

    # Twist rotate clockwise
    twist_engine = FlicSdkEngine(
        origin="http://192.168.0.100:8080",
        button_type="twist",
        gesture="rotate_cw",
        target_type="cycle_input",
        output_num=1,
        cycle_dir="next",
    )
    evt_cw = FlicSdkEvent(event_name="buttonRotate", bdaddr="AA:BB", direction=1)
    evt_ccw = FlicSdkEvent(event_name="buttonRotate", bdaddr="AA:BB", direction=-1)
    assert twist_engine.evaluate_event(evt_cw, {}) is not None
    assert twist_engine.evaluate_event(evt_ccw, {}) is None


def test_generate_sdk_snippet_contains_startup_and_handler():
    snippet = generate_flic_sdk_snippet(
        origin="http://192.168.1.50:8080",
        button_type="button",
        button_identifier="Kitchen",
        target_type="switch_output",
        gesture="single",
        output_num=1,
        input_num=2,
    )
    assert 'var API_BASE = "http://192.168.1.50:8080";' in snippet
    assert 'url: API_BASE + "/api/integrations/flic/register"' in snippet
    assert 'button.name === "Kitchen"' in snippet
    assert 'obj.isSingleClick' in snippet
    assert 'url: API_BASE + "/api/output/1/source"' in snippet
    assert 'JSON.stringify({"input": 2})' in snippet


@pytest.mark.asyncio
async def test_flic_client_perform_flow_against_mock_server(aiohttp_server):
    received_requests = []

    async def handler(request: web.Request) -> web.Response:
        received_requests.append(
            {
                "method": request.method,
                "path": request.rel_url.raw_path,
                "query": dict(request.query),
                "headers": dict(request.headers),
                "body": await request.json() if request.content_type == "application/json" else None,
            }
        )
        if request.path == "/api/auth-test" and "X-API-Key" not in request.headers and "key" not in request.query:
            return web.json_response({"error": "Control unlock or API key required"}, status=401)
        return web.json_response({"success": True, "path": request.path}, status=200)

    app = web.Application()
    app.router.add_post("/api/preset/{preset}", handler)
    app.router.add_post("/api/output/{output}/source", handler)
    app.router.add_post("/api/switch", handler)
    app.router.add_post("/api/integrations/flic/register", handler)

    server = await aiohttp_server(app)
    client = FlicClient()
    await client.start(HubInfo(f"http://{server.host}:{server.port}"))

    try:
        # Perform preset recall
        res = await client.perform(act("preset_recall", preset=3))
        assert res.ok is True
        assert res.status == 200
        assert len(res.requests) == 1
        assert res.requests[0]["path"] == "/api/preset/3"

        # Perform route with query key (and check redaction)
        res_query = await client.perform(
            act("route", input=2, output=1, api_key="secret-token-abc", auth_mode="query")
        )
        assert res_query.ok is True
        assert res_query.requests[0]["path"] == "/api/output/1/source?key=***REDACTED***"
        assert res_query.requests[0]["body"] == {"input": 2}

        # Perform route_all
        res_all = await client.perform(act("route_all", input=4))
        assert res_all.ok is True
        assert res_all.requests[0]["path"] == "/api/switch"
        assert res_all.requests[0]["body"] == {"input": 4}

    finally:
        await client.stop()
