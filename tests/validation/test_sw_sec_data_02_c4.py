"""C4 display-only privacy controls; loopback HTTP is not live HA acceptance."""

import asyncio
import copy
import json
import logging
from types import SimpleNamespace
from unittest.mock import AsyncMock

import aiohttp
import pytest
from aiohttp import web

from tools.validate.clients.api import ApiClient
from tools.validate.clients.base import HubInfo
from tools.validate.clients.ha import HomeAssistantClient
from tools.validate.evidence import redact, write_record
from tools.validate.model import ClientState, Hub, Response, Scenario, act
from tools.validate.runner import Outcome, Runner, RunOptions, WsObserver

MARKERS = tuple(f"c4-private-synthetic-{n}" for n in range(20))


@pytest.fixture
async def bounded_http(aiohttp_client):
    """Explicitly close every test-owned HTTP server/session before fixture teardown."""
    clients = []

    async def create(app):
        client = await asyncio.wait_for(aiohttp_client(app), 3)
        clients.append(client)
        return client

    try:
        yield create
    finally:
        await asyncio.wait_for(asyncio.gather(*(client.close() for client in clients)), 3)


def assert_safe(raw):
    assert not any(marker.encode() in raw for marker in MARKERS)


def scenario(action, expect=(), **kwargs):
    return Scenario(id="synthetic.cfour", title="C4 synthetic diagnostic boundaries", features=("F-SEC-014",),
                    action=action, expect=expect, covers=("tools/validate/evidence.py",), **kwargs)


def runner_at(url, tmp_path, monkeypatch):
    runner = Runner(RunOptions(out_dir=tmp_path, hub_url=url))
    runner.hub = SimpleNamespace(base_url=url, external_url=url, entry=url, mode="api", uc_url=None)
    runner.device = SimpleNamespace(state=AsyncMock(return_value={"routing": [1], "output": 1}))
    monkeypatch.setattr(runner, "_wait_hub_telnet", AsyncMock())
    monkeypatch.setattr(WsObserver, "start", AsyncMock())
    monkeypatch.setattr(WsObserver, "sync", AsyncMock(return_value=True))
    monkeypatch.setattr(WsObserver, "stop", AsyncMock())
    return runner


def persist_and_scan(runner, outcome, tmp_path, capsys, caplog, extra=()):
    runner.outcomes.append(outcome)
    runner._write_summary()
    records = list((tmp_path / "evidence").rglob("*.json"))
    assert len(records) == 1
    record = json.loads(records[0].read_bytes())
    captured = capsys.readouterr()
    # Retain the full streams/logs scanned, including ordinary empty captures.
    streams = {"stdout.log": captured.out, "stderr.log": captured.err, "captured.log": caplog.text}
    for name, text in streams.items():
        (tmp_path / name).write_text(text, encoding="utf-8")
    blobs = [p.read_bytes() for p in records] + [(tmp_path / "run-summary.json").read_bytes(), outcome.reason.encode()]
    blobs += [text.encode() for text in streams.values()] + [text.encode() for text in extra]
    (tmp_path / "scan.json").write_text(json.dumps({"blobs": len(blobs), "bytes": sum(map(len, blobs)),
                                                  "safe": not any(m.encode() in b for m in MARKERS for b in blobs)}))
    for blob in blobs:
        assert_safe(blob)
    return record


@pytest.mark.parametrize("case", (str.lower, str.upper, str.swapcase))
def test_fields_pairs_json_queries_and_exact_header_controls(case, tmp_path):
    credentials = ("current_pin", "current_passcode", "passcode", "pin", "api_key", "Authorization",
                   "token", "orei_session", "orei_device_token")
    headers = [(case(name), MARKERS[i]) for i, name in enumerate((
        "X-Passcode", "X-Admin-PIN", "X-API-Key", "Authorization", "Cookie", "Set-Cookie", "X-Auth-Token",
    ))] + [(case("X-Admin-PIN-Policy"), "public-policy")]
    params = {name: MARKERS[i] for i, name in enumerate(credentials)}
    params.update({"headers": tuple(headers), "nested": ({"current_pin": 1, "public_port": 1},),
                   "data": json.dumps({"current_pin": MARKERS[10], "public": "visible-json"}),
                   "path": "/api/health?current_pin=" + MARKERS[11] + "&%70asscode=" + MARKERS[12] + "&output=1"})
    original = copy.deepcopy(params)
    safe = redact(params)
    description = act("request", **params).describe()
    record = {"features": ["F-SEC-014"], "timestamp": {"started": "2026-11-04"}, "level": "V1",
              "commit": {"short": "00000000"}, "scenario": "synthetic.writer", "client": "api", "diagnostics": params}
    path = write_record(tmp_path, record)
    assert_safe(path.read_bytes())
    assert_safe(description.encode())
    assert_safe(json.dumps(safe).encode())
    assert safe["nested"][0] == {"current_pin": "***", "public_port": 1}
    assert safe["headers"][-1] == (case("X-Admin-PIN-Policy"), "public-policy")
    assert "visible-json" in description and "output=1" in description
    assert params == original and params["headers"] is not safe["headers"]


@pytest.mark.parametrize("shape", ("tuple", "serialized"))
@pytest.mark.parametrize("comparison", ("matched", "wrong", "mask"))
@pytest.mark.parametrize("integer_pin", (False, True), ids=("string-pin", "integer-pin"))
async def test_loopback_carriers_all_runner_sinks_and_raw_verdicts(
    bounded_http, tmp_path, monkeypatch, capsys, caplog, shape, comparison, integer_pin,
):
    pin = 1 if integer_pin else MARKERS[0]
    body = ({"current_pin": pin, "public": "visible-body", "port": 1}, {"api_key": MARKERS[1]})
    serialized = json.dumps(body)
    headers = (("X-Passcode", MARKERS[2]), ("X-Admin-PIN-Policy", "public-policy"))
    path = "/exchange?current_passcode=" + MARKERS[3] + "&port=1"
    wire = []

    async def exchange(request):
        wire.append({"method": request.method, "path": request.path_qs, "body": await request.text(),
                     "headers": {name: request.headers[name] for name, _ in headers}})
        return web.json_response({"current_pin": pin, "data": {"api_key": MARKERS[1]}, "port": 1,
                                  "public": "visible-response"})

    app = web.Application()
    app.router.add_post("/exchange", exchange)
    server = await bounded_http(app)
    url = str(server.make_url("/"))
    api = ApiClient()
    seen = []
    perform = api.perform

    async def capture(action):
        result = await perform(action)
        seen.append(result)
        return result

    monkeypatch.setattr(api, "perform", capture)
    params = {"json": body} if shape == "tuple" else {"data": serialized}
    action = act("request", method="POST", path=path, headers=headers, **params)
    original = copy.deepcopy(action.params)
    expected = pin if comparison == "matched" else (2 if integer_pin else MARKERS[4]) if comparison == "wrong" else "***"
    sc = scenario(action, (Response(status=200, json={"current_pin": expected}),), setup=(action,), cleanup=(action,))
    runner = runner_at(url, tmp_path, monkeypatch)
    await api.start(HubInfo(url))
    try:
        outcome = await asyncio.wait_for(runner._run_one(sc, api), 8)
    finally:
        await asyncio.wait_for(api.stop(), 2)
    assert len(wire) == 3 and all(item["method"] == "POST" and item["path"] == path for item in wire)
    assert all(json.loads(item["body"]) == list(body) for item in wire)
    assert all(item["headers"] == dict(headers) for item in wire)
    assert action.params == original
    assert action.params.get("json") is body if shape == "tuple" else action.params["data"] is serialized
    result = seen[0]
    assert result.body["current_pin"] == pin
    assert result.requests[0]["response"] is result.body
    assert result.requests[0]["body"] is (body if shape == "tuple" else serialized)
    assert outcome.status == ("pass" if comparison == "matched" else "fail")
    record = persist_and_scan(runner, outcome, tmp_path, capsys, caplog, result.steps)
    assert record["checks"][0]["result"] == outcome.status
    assert "visible-response" in record["checks"][0]["detail"]
    assert "visible-body" in " ".join(record["procedure"])
    assert all(any(label in step for step in record["procedure"]) for label in ("setup (api)", "action (api)", "cleanup (api)"))
    assert result.body["data"]["api_key"] == MARKERS[1]
    observed = record["observations"]["requests"][0]
    assert observed["response"]["current_pin"] == "***" and observed["response"]["port"] == 1
    displayed_body = observed["body"]
    assert displayed_body[0]["current_pin"] == "***" and displayed_body[0]["port"] == 1


@pytest.mark.parametrize("comparison", ("matched", "wrong", "mask"))
async def test_hub_query_sensitive_equals_and_actual_values(
    bounded_http, tmp_path, monkeypatch, capsys, caplog, comparison,
):
    async def exchange(request):
        assert request.query["current_pin"] == MARKERS[0]
        return web.json_response({"current_pin": MARKERS[1], "public": "hub-visible"})

    app = web.Application()
    app.router.add_get("/hub", exchange)
    server = await bounded_http(app)
    url = str(server.make_url("/"))
    path = "/hub?current_pin=" + MARKERS[0]
    expected = MARKERS[1] if comparison == "matched" else MARKERS[2] if comparison == "wrong" else "***"
    exp = Hub(path, "current_pin", equals=expected)
    sc = scenario(act("request", path=path), (exp, Hub(path, "current_pin", not_equals=MARKERS[3])))
    runner = runner_at(url, tmp_path, monkeypatch)
    api = ApiClient()
    # A mismatch has the production four-second bound; no test changes the comparator.
    await api.start(HubInfo(url))
    try:
        outcome = await asyncio.wait_for(runner._run_one(sc, api), 7)
    finally:
        await asyncio.wait_for(api.stop(), 2)
    assert outcome.status == ("pass" if comparison == "matched" else "fail")
    record = persist_and_scan(runner, outcome, tmp_path, capsys, caplog, (exp.describe(),))
    assert record["checks"][1]["result"] == "pass"
    assert record["observations"]["hub_reads"][0]["response"]["public"] == "hub-visible"


@pytest.mark.parametrize("path,field,value,public", (
    ("/api/system-shortcuts/mute_all_audio", "data.key", "mute_all_audio", True),
    ("/api/auth/api-keys", "data.key", MARKERS[0], False),
    ("/api/system-shortcuts/mute_all_audio", "data.key", MARKERS[0], False),
    ("/api/system-shortcuts/mute_all_audio", "data.key", 1, False),
    ("/api/profile/profile1", "data.password_protected", True, True),
    ("/api/v2/scenes/scene1", "data.scene.password_protected", False, True),
    ("/api/profile/profile1", "data.password_protected", MARKERS[0], False),
    ("/api/profile/profile1", "data.password_protected", 1, False),
    ("/unknown", "data.password_protected", True, False),
))
async def test_trusted_public_context_and_negative_controls(
    bounded_http, tmp_path, monkeypatch, capsys, caplog, path, field, value, public,
):
    body = {"data": {"scene": {"password_protected": value}}} if "scene." in field else {"data": {field.split(".")[-1]: value}}

    async def exchange(request):
        return web.json_response(body)

    app = web.Application()
    app.router.add_get(path, exchange)
    server = await bounded_http(app)
    url = str(server.make_url("/"))
    runner = runner_at(url, tmp_path, monkeypatch)
    api = ApiClient()
    action = act("request", path=path)
    sc = scenario(action, (Response(status=200, json=body), Hub(path, field, equals=value)))
    await api.start(HubInfo(url))
    try:
        outcome = await asyncio.wait_for(runner._run_one(sc, api), 5)
    finally:
        await asyncio.wait_for(api.stop(), 2)
    assert outcome.status == "pass"
    record = persist_and_scan(runner, outcome, tmp_path, capsys, caplog)
    description = record["checks"][1]["description"]
    assert (f" == {value!r} (HTTP" in description) is public
    assert ("***" in description) is (not public)
    observed = record["observations"]["requests"][0]["response"]
    assert observed == (body if public else {"data": {"scene": {"password_protected": "***"}}}
                        if "scene." in field else {"data": {field.split(".")[-1]: "***"}})


@pytest.mark.parametrize("failure", ("setup", "prepare", "action", "cleanup", "transport", "opaque-response"))
async def test_blocked_error_cleanup_summary_and_truncation(
    bounded_http, tmp_path, monkeypatch, capsys, caplog, failure,
):
    async def exchange(request):
        if failure == "opaque-response":
            return web.Response(text="echo " + MARKERS[0] + " " * 600)
        return web.json_response({"public": "error-visible"}, status=400 if failure == "setup" else 200)

    app = web.Application()
    app.router.add_get("/error", exchange)
    server = await bounded_http(app)
    url = str(server.make_url("/"))
    runner = runner_at(url, tmp_path, monkeypatch)
    api = ApiClient()
    action = act("request", path="/error?current_pin=" + MARKERS[1])
    sc = scenario(action, (Response(status=200),), setup=(action,) if failure == "setup" else (), cleanup=(action,))
    if failure == "prepare":
        monkeypatch.setattr(api, "prepare", AsyncMock(side_effect=RuntimeError("echo " + MARKERS[0])))
    if failure in {"action", "transport"}:
        if failure == "action":
            monkeypatch.setattr(api, "perform", AsyncMock(side_effect=RuntimeError("echo " + MARKERS[0])))
        else:
            # Actual perform error path, without an uncontrolled real network timeout.
            monkeypatch.setattr(api, "request", AsyncMock(side_effect=aiohttp.ClientError("echo " + MARKERS[0])))
    if failure == "cleanup":
        original = ApiClient.perform

        async def cleanup_error(self, action):
            if self is not api:
                raise RuntimeError("echo " + MARKERS[0])
            return await original(self, action)

        monkeypatch.setattr(ApiClient, "perform", cleanup_error)
    await api.start(HubInfo(url))
    try:
        outcome = await asyncio.wait_for(runner._run_one(sc, api), 5)
    finally:
        await asyncio.wait_for(api.stop(), 2)
    assert outcome.status == ("blocked" if failure in {"setup", "prepare", "action"}
                              else "fail" if failure == "transport" else "pass")
    record = persist_and_scan(runner, outcome, tmp_path, capsys, caplog)
    if failure == "cleanup":
        assert "RuntimeError" in " ".join(record["observations"]["notes"])
    if failure == "opaque-response":
        assert "opaque body suppressed" in record["checks"][0]["detail"]
    # Also prove summary persistence is its own boundary for external outcomes.
    raw_outcome = Outcome("synthetic.external", "api", "blocked", reason="echo " + MARKERS[0])
    runner.outcomes = [raw_outcome]
    runner._write_summary()
    assert_safe((tmp_path / "run-summary.json").read_bytes())
    assert raw_outcome.reason.endswith(MARKERS[0])


@pytest.mark.parametrize("error", (False, True))
async def test_ha_options_named_default_and_error_paths(
    bounded_http, tmp_path, monkeypatch, capsys, caplog, error,
):
    wire = []

    async def exchange(request):
        body = await request.json() if request.can_read_body else None
        wire.append((request.method, request.path, body, request.headers.get("Authorization")))
        if request.path.endswith("/entry"):
            return web.json_response([])
        if request.path.endswith("/options/flow"):
            return web.json_response({"type": "form", "flow_id": "opt", "data_schema": [
                {"name": "api_key", "default": MARKERS[0], "type": "string"},
                {"name": "scan_interval", "default": 5, "type": "integer"},
            ]})
        if request.path.endswith("/flow/opt"):
            if error:
                return web.Response(status=400, text="opaque echo " + MARKERS[0])
            return web.json_response({"type": "create_entry"})
        if request.path.endswith("/flow"):
            return web.json_response({"type": "form", "step_id": "user", "flow_id": "user"})
        return web.json_response({"type": "create_entry", "result": {"entry_id": "entry-public"}})

    app = web.Application()
    app.router.add_route("*", "/{rest:.*}", exchange)
    server = await bounded_http(app)
    url = str(server.make_url("/"))
    ha = HomeAssistantClient()
    ha.url = url.rstrip("/")
    ha.token = MARKERS[1]
    ha._session = aiohttp.ClientSession()
    monkeypatch.setattr(ha, "_wait_loaded", AsyncMock())
    options = {"api_key": MARKERS[0], "scan_interval": 5}
    action = act("ha_config_flow", options=options)
    original = copy.deepcopy(options)
    runner = runner_at(url, tmp_path, monkeypatch)
    sc = scenario(action, (Response(status=200),), clients=("ha",))
    results = []
    perform = ha.perform

    async def capture(action):
        result = await perform(action)
        results.append(result)
        return result

    monkeypatch.setattr(ha, "perform", capture)
    try:
        outcome = await asyncio.wait_for(runner._run_one(sc, ha), 6)
    finally:
        await asyncio.wait_for(ha.stop(), 2)
    assert outcome.status == ("blocked" if error else "pass")
    assert options == original
    options_wire = next(item for item in wire if item[1].endswith("/flow/opt"))
    assert options_wire[2] == original and options_wire[3] == "Bearer " + MARKERS[1]
    if not error:
        result = results[0]
        req = next(r for r in result.requests if r["path"].endswith("/flow/opt"))
        assert req["body"] is options
        form = next(r for r in result.requests if r["path"].endswith("/options/flow"))["response"]
        assert form["data_schema"][0]["default"] == MARKERS[0]
    record = persist_and_scan(runner, outcome, tmp_path, capsys, caplog,
                              results[0].steps if results else ())
    if not error:
        assert "scan_interval" in " ".join(record["procedure"])
        form = next(r for r in record["observations"]["requests"] if r["path"].endswith("/options/flow"))["response"]
        assert form["data_schema"][0]["default"] == "***"
        assert form["data_schema"][1]["default"] == 5


async def test_client_state_diagnostic_scope(tmp_path, monkeypatch, capsys, caplog):
    runner = runner_at("http://127.0.0.1:1", tmp_path, monkeypatch)
    client = SimpleNamespace(name="ha", observes=True, observe=AsyncMock(return_value=MARKERS[0]))
    exp = ClientState("entry.api_key", equals=MARKERS[0], timeout=0)
    sc = scenario(act("ha_config_flow"), (exp,), clients=("ha",))
    check = await runner._check(exp, sc, client, SimpleNamespace(), {}, 0, SimpleNamespace(), None, 0, [])
    assert check["result"] == "pass"
    assert_safe(json.dumps(check).encode())
    logging.getLogger("c4.control").warning("public-log-control")
    assert "public-log-control" in caplog.text


def test_public_shortcut_action_and_precise_type_context():
    description = act("shortcut_run", key="mute_all_audio", params={"pin": 1, "output": 1}).describe()
    assert "key='mute_all_audio'" in description and "'pin': '***'" in description
    assert "'output': 1" in description
    for value in (True, False, None, 1, MARKERS[0]):
        assert redact({"pin": value, "key": value, "password": value}) == {
            "pin": "***", "key": "***", "password": "***",
        }
    for value in (1, None, MARKERS[0]):
        assert redact({"password_protected": value}, path="/api/profile/p") == {"password_protected": "***"}
    assert "'password_protected': True" in act("request", path="/api/profile/p", json={"password_protected": True}).describe()
    untrusted = {"method": "GET", "status": 200, "path": "/api/system-shortcuts/mute_all_audio",
                 "response": {"key": "mute_all_audio"}}
    assert redact(untrusted)["response"]["key"] == "***"


async def test_client_unavailable_error_stdout_and_summary(tmp_path, monkeypatch, capsys, caplog):
    runner = runner_at("http://127.0.0.1:1", tmp_path, monkeypatch)
    client = SimpleNamespace(name="ha", hub_mode="api", start=AsyncMock(side_effect=RuntimeError("echo " + MARKERS[0])))
    monkeypatch.setattr("tools.validate.runner.make_client", lambda name: client)
    monkeypatch.setattr(runner, "_use_hub_mode", lambda mode: None)
    monkeypatch.setattr(runner, "_use_scenario_environment", lambda sc: None)
    sc = scenario(act("ha_config_flow"), clients=("ha",))
    await asyncio.wait_for(runner._run_client("ha", [sc]), 3)
    runner._write_summary()
    captured = capsys.readouterr()
    assert "RuntimeError" in captured.out and "unavailable" in captured.out
    for name, text in (("stdout.log", captured.out), ("stderr.log", captured.err), ("captured.log", caplog.text)):
        (tmp_path / name).write_text(text, encoding="utf-8")
        assert_safe(text.encode())
    assert_safe((tmp_path / "run-summary.json").read_bytes())
    assert runner.outcomes[0].status == "skipped"


async def test_genuinely_created_api_key_stays_raw_and_private(bounded_http, tmp_path, monkeypatch, capsys, caplog):
    from rest_api.app import create_rest_app

    server = await bounded_http(create_rest_app(tmp_path / "product"))
    url = str(server.make_url("/"))
    api = ApiClient()
    runner = runner_at(url, tmp_path / "run", monkeypatch)
    action = act("request", method="POST", path="/api/auth/api-keys", json={"name": "public-generated-key"})
    await api.start(HubInfo(url))
    try:
        result = await asyncio.wait_for(api.perform(action), 5)
        assert result.status == 201 and result.ok
        generated = result.body["key"]
        assert isinstance(generated, str) and len(generated) >= 32
        assert result.requests[0]["response"] is result.body
        checks = []
        for value, verdict in ((generated, "pass"), ("***", "fail")):
            exp = Response(status=201, json={"key": value})
            check = await runner._check(exp, scenario(action), api, result, {}, 0, None, api, 0, [])
            assert check["result"] == verdict
            assert generated not in json.dumps(check)
            checks.append(check)
        path = write_record(tmp_path / "writer", {
            "features": ["F-SEC-014"], "timestamp": {"started": "2026-11-04"}, "level": "V1",
            "commit": {"short": "00000000"}, "scenario": "synthetic.created", "client": "api",
            "requests": result.requests, "steps": result.steps, "checks": checks,
        })
        assert generated.encode() not in path.read_bytes()
        assert generated not in " ".join(result.steps)
        assert result.body["key"] is generated
        status, _, _ = await api.request("DELETE", "/api/auth/api-keys/" + result.body["id"])
        assert status == 200
    finally:
        await asyncio.wait_for(api.stop(), 2)


@pytest.mark.parametrize("structured", (False, True))
async def test_ha_http_opaque_error_copy_before_truncation(bounded_http, structured):
    raw = {"message": "echo " + MARKERS[0], "public": "status-metadata"}
    received = []

    async def exchange(request):
        received.append((request.query["api_key"], await request.json()))
        return web.json_response(raw, status=400) if structured else web.Response(
            status=400, text="opaque echo " + MARKERS[0] + "x" * 600,
        )

    app = web.Application()
    app.router.add_post("/bad", exchange)
    server = await bounded_http(app)
    ha = HomeAssistantClient()
    ha.url = str(server.make_url("/")).rstrip("/")
    ha._session = aiohttp.ClientSession()
    body = {"api_key": MARKERS[1]}
    records = []
    try:
        with pytest.raises(RuntimeError) as error:
            await asyncio.wait_for(ha._http("POST", "/bad?api_key=" + MARKERS[2], body, record=records), 3)
    finally:
        await asyncio.wait_for(ha.stop(), 2)
    assert received == [(MARKERS[2], body)]
    assert records[0]["body"] is body
    assert records[0]["response"] == (raw if structured else "opaque echo " + MARKERS[0] + "x" * (500 - 12 - len(MARKERS[0])))
    text = str(error.value)
    assert "POST /bad?api_key=***: HTTP 400" in text
    assert_safe(text.encode())


# Coordinator-authorized catalog-context correction. Keep the original C4 cases
# above intact; these exercise actual supported product callers and the gap.
@pytest.mark.parametrize("prefix", ("/api/shortcuts", "/api/system-shortcuts"))
@pytest.mark.parametrize("view,keys", (
    ("favorites", ("route_all_to_output", "route_one_to_one")),
    ("dashboard", ("power_off_all", "mute_all_audio")),
))
@pytest.mark.parametrize("index", (0, 1, -1))
async def test_catalog_context_real_favorites_dashboard(
    bounded_http, tmp_path, monkeypatch, capsys, caplog, prefix, view, keys, index,
):
    from rest_api.app import create_rest_app
    from rest_api.utils import set_system_shortcut_manager
    from system_shortcuts import SystemShortcutManager

    app = create_rest_app(tmp_path / "product")
    manager = SystemShortcutManager(tmp_path / "shortcut-prefs")
    assert manager.update_prefs("power_off_all", dashboard_visible=True)
    assert manager.update_prefs("mute_all_audio", dashboard_visible=True)
    set_system_shortcut_manager(manager)
    server = await bounded_http(app)
    url = str(server.make_url("/"))
    path = prefix + "/" + view + "?current_pin=" + MARKERS[0] + "&public=1"
    action = act("request", path=path)
    field = f"data.shortcuts[{index}].key"
    expected = keys[index]
    sc = scenario(action, (Response(status=200, json={"data": {"count": 2}}),
                           Hub(path, field, equals=expected)))
    runner = runner_at(url, tmp_path / "run", monkeypatch)
    api = ApiClient()
    results = []
    perform = api.perform

    async def capture(action):
        result = await perform(action)
        results.append(result)
        return result

    monkeypatch.setattr(api, "perform", capture)
    await api.start(HubInfo(url))
    try:
        outcome = await asyncio.wait_for(runner._run_one(sc, api), 6)
    finally:
        await asyncio.wait_for(api.stop(), 2)
    assert outcome.status == "pass"
    raw = results[0]
    assert tuple(item["key"] for item in raw.body["data"]["shortcuts"]) == keys
    assert raw.requests[0]["response"] is raw.body and raw.requests[0]["path"] == path
    record = persist_and_scan(runner, outcome, tmp_path / "run", capsys, caplog, raw.steps)
    observed = record["observations"]["requests"][0]["response"]["data"]["shortcuts"]
    assert tuple(item["key"] for item in observed) == keys
    assert f" == {expected!r}" in record["checks"][1]["description"]
    assert expected in record["checks"][1]["detail"]
    assert record["observations"]["hub_reads"][0]["response"]["data"]["shortcuts"][index]["key"] == expected
    assert tuple(item["key"] for item in raw.body["data"]["shortcuts"]) == keys


@pytest.mark.parametrize("alias,key", (
    ("builtin.one_to_one", "route_one_to_one"), ("builtin.all_to_out_1", "route_all_to_output"),
))
async def test_catalog_context_real_supported_aliases(
    bounded_http, tmp_path, monkeypatch, capsys, caplog, alias, key,
):
    from rest_api.app import create_rest_app
    from rest_api.utils import set_system_shortcut_manager
    from system_shortcuts import SystemShortcutManager

    app = create_rest_app(tmp_path / "product")
    set_system_shortcut_manager(SystemShortcutManager(tmp_path / "shortcut-prefs"))
    server = await bounded_http(app)
    url = str(server.make_url("/"))
    path = "/api/shortcuts/" + alias
    runner = runner_at(url, tmp_path, monkeypatch)
    api = ApiClient()
    sc = scenario(act("request", path=path), (Response(status=200, json={"data": {"key": key}}),
                                            Hub(path, "data.key", equals=key)))
    await api.start(HubInfo(url))
    try:
        outcome = await asyncio.wait_for(runner._run_one(sc, api), 5)
    finally:
        await asyncio.wait_for(api.stop(), 2)
    assert outcome.status == "pass"
    record = persist_and_scan(runner, outcome, tmp_path, capsys, caplog)
    assert record["observations"]["requests"][0]["response"]["data"]["key"] == key
    assert f" == {key!r}" in record["checks"][1]["description"]
    assert "'key': '" + key + "'" in record["checks"][0]["description"]


@pytest.mark.parametrize("kind,path", (
    ("unknown", "/api/shortcuts/favorites"), ("created", "/api/shortcuts/favorites"),
    ("integer", "/api/shortcuts/favorites"), ("boolean", "/api/shortcuts/favorites"),
    ("null", "/api/shortcuts/favorites"), ("known", "/api/shortcuts/favorites-extra"),
    ("known", "/api/auth/api-keys"),
))
async def test_catalog_context_negative_keys_types_and_exact_routes(
    bounded_http, tmp_path, monkeypatch, capsys, caplog, kind, path,
):
    from rest_api.app import create_rest_app

    product = await bounded_http(create_rest_app(tmp_path / "product"))
    product_api = ApiClient()
    await product_api.start(HubInfo(str(product.make_url("/"))))
    key_id = None
    try:
        created = await asyncio.wait_for(product_api.perform(act(
            "request", method="POST", path="/api/auth/api-keys", json={"name": "public-catalog-control"},
        )), 4)
        assert created.status == 201
        genuine = created.body["key"]
        key_id = created.body["id"]
        value = {"unknown": MARKERS[1], "created": genuine, "integer": 1, "boolean": True,
                 "null": None, "known": "power_off_all"}[kind]
        body = {"data": {"shortcuts": [
            {"key": "mute_all_audio", "api_key": MARKERS[2]}, {"key": value},
            {"nested": {"key": "power_off_all"}},
        ], "key": "route_one_to_one"}, "public": "catalog-public-control"}
        original = copy.deepcopy(body)

        async def exchange(request):
            return web.json_response(body)

        app = web.Application()
        app.router.add_get(path, exchange)
        server = await bounded_http(app)
        url = str(server.make_url("/"))
        runner = runner_at(url, tmp_path / "run", monkeypatch)
        api = ApiClient()
        captured = []
        perform = api.perform

        async def capture(action):
            result = await perform(action)
            captured.append(result)
            return result

        monkeypatch.setattr(api, "perform", capture)
        sc = scenario(act("request", path=path), (Response(status=200, json=body),
                                                Hub(path, "data.shortcuts[1].key", equals=value)))
        await api.start(HubInfo(url))
        try:
            outcome = await asyncio.wait_for(runner._run_one(sc, api), 5)
        finally:
            await asyncio.wait_for(api.stop(), 2)
        assert outcome.status == "pass"
        result = captured[0]
        assert result.body == original and result.requests[0]["response"] is result.body
        record = persist_and_scan(runner, outcome, tmp_path / "run", capsys, caplog, result.steps)
        observed = record["observations"]["requests"][0]["response"]["data"]
        assert observed["shortcuts"][0]["key"] == ("mute_all_audio" if kind != "known" else "***")
        assert observed["shortcuts"][0]["api_key"] == "***"
        assert observed["shortcuts"][1]["key"] == "***"
        assert observed["shortcuts"][2]["nested"]["key"] == "***" and observed["key"] == "***"
        assert " == '***'" in record["checks"][1]["description"]
        assert body == original and result.body == original
        for member in (tmp_path / "run").rglob("*"):
            if member.is_file():
                assert genuine.encode() not in member.read_bytes()
    finally:
        if key_id is not None:
            status, _, _ = await asyncio.wait_for(product_api.request("DELETE", "/api/auth/api-keys/" + key_id), 4)
            assert status == 200
        await asyncio.wait_for(product_api.stop(), 2)
