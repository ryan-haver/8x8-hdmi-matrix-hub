"""Real HTTP observations and negative controls for API response headers."""

import asyncio
import copy
import json
from dataclasses import asdict, replace
from types import SimpleNamespace

import jsonschema
import pytest
from aiohttp import web

from rest_api import create_rest_app
from tests.validation.scenarios.sw_api_read_04 import CORS_HEADERS, SCENARIOS
from tools.validate.clients.api import ApiClient
from tools.validate.clients.base import HubInfo
from tools.validate.evidence import SCHEMA_PATH, iter_records, redact
from tools.validate.model import Response, act
from tools.validate.runner import Runner, RunOptions
from tools.validate.scenarios import discover
from tools.validate.stack import HubProcess


@pytest.fixture
async def observed(aiohttp_client):
    async def handler(request):
        response = web.json_response({"success": True, "message": "public"})
        response.headers.update(CORS_HEADERS)
        response.headers["Authorization"] = "Bearer private-auth-value"
        response.headers["X-Refresh-Token"] = "private-token-value"
        response.headers["X-API-Key"] = "private-key-value"
        response.headers["X-Unknown"] = "private-unknown-value"
        response.set_cookie("session", "private-cookie-value", httponly=True, samesite="Strict")
        response.set_cookie("remembered", "private-second-cookie")
        return response

    app = web.Application()
    app.router.add_get("/exchange", handler)
    server = await aiohttp_client(app)
    api = ApiClient()
    await api.start(HubInfo(str(server.make_url("/"))))
    try:
        result = await api.perform(act("request", path="/exchange"))
        assert result.ok and result.status == 200 and result.body["success"] is True
        yield api, result
    finally:
        await api.stop()


async def check(tmp_path, api, result, expectation, *, name="api"):
    runner = Runner(RunOptions(target="sim", clients=("api",), out_dir=tmp_path))
    # Response checks never consult device/observer state.
    runner.device = object()
    return await runner._check(expectation, SCENARIOS[0], SimpleNamespace(name=name), result,
                               {}, 0, None, api, 0, [])


@pytest.mark.parametrize(("expectation", "verdict"), [
    (Response(status=200, json={"success": True}, headers={"vArY": "Origin"}), "pass"),
    (Response(headers={"Vary": "origin"}), "fail"),  # value equality is exact
    (Response(headers={"Access-Control-Max-Age": "0"}), "fail"),
    (Response(absent_headers=("vArY",)), "fail"),
    (Response(absent_headers=("Access-Control-Allow-Origin",)), "pass"),
    (Response(headers={"X-Missing": "value"}), "fail"),
    (Response(headers={"Set-Cookie": "***"}), "fail"),
    (Response(absent_headers=("SET-cookie",)), "fail"),
])
async def test_actual_exchange_header_oracles(observed, tmp_path, expectation, verdict):
    api, result = observed
    outcome = await check(tmp_path, api, result, expectation)
    assert outcome["result"] == verdict, outcome


@pytest.mark.parametrize("mutation", ("capture", "redaction", "all", "earlier_only", "status"))
async def test_missing_final_observation_never_proves_absence(observed, tmp_path, mutation):
    api, original = observed
    result = copy.deepcopy(original)
    if mutation == "capture":
        result.requests[-1].pop("response_headers")
    elif mutation == "redaction":
        result.requests[-1].pop("response_headers_redacted")
    elif mutation == "all":
        result.requests.clear()
    elif mutation == "earlier_only":
        result.requests.append({"status": 200})
    else:
        result.requests[-1]["status"] = 201
    outcome = await check(tmp_path, api, result, Response(absent_headers=("X-Absent",)))
    assert outcome["result"] == "fail", outcome
    assert "not observed" in outcome["detail"]


async def test_sensitive_capture_and_diagnostics_never_persist_values(observed, tmp_path):
    api, result = observed
    record = result.requests[-1]
    names = ("authorization", "x-refresh-token", "x-api-key", "x-unknown", "set-cookie")
    assert all(record["response_headers"][name] == "***" for name in names)
    assert set(names) <= set(record["response_headers_redacted"])
    outcomes = []
    for name in names:
        for expectation in (Response(headers={name.upper(): "private-expected-value"}),
                            Response(absent_headers=(name.upper(),))):
            outcome = await check(tmp_path, api, result, expectation)
            assert outcome["result"] == "fail", outcome
            outcomes.append(outcome)
    persisted = json.dumps(redact({"action": asdict(result), "checks": outcomes}))
    assert "private-" not in persisted
    assert "Set-Cookie".lower() in persisted


@pytest.mark.parametrize("name", ("browser", "ha", "uc", "flic"))
async def test_non_api_header_expectations_fail_even_with_capture(observed, tmp_path, name):
    api, result = observed
    for expectation in (Response(headers={"Vary": "Origin"}), Response(absent_headers=("X-Absent",))):
        assert (await check(tmp_path, api, result, expectation, name=name))["result"] == "fail"


async def test_browser_status_and_api_only_body_compatibility(observed, tmp_path):
    api, result = observed
    result.status, result.body, result.requests = 403, {"success": False}, []
    expectation = Response(status=(401, 403), min_status=400, json={"success": True})
    assert (await check(tmp_path, api, result, expectation, name="browser"))["result"] == "pass"
    assert (await check(tmp_path, api, result, expectation))["result"] == "fail"
    assert (await check(tmp_path, api, result, Response(status=200), name="browser"))["result"] == "fail"
    result.status = None
    assert (await check(tmp_path, api, result, Response(min_status=400), name="browser"))["result"] == "fail"


def test_config_recording_and_discovery_are_bounded(tmp_path):
    found = discover()
    assert {sc.id: sc for sc in SCENARIOS} == {k: v for k, v in found.items() if k.startswith("sw_api_read_04.")}
    for scenario in SCENARIOS:
        assert scenario.features == ("F-API-031",) and scenario.client_features == {}
        assert scenario.clients == ("api",) and scenario.targets == ("sim",) and not scenario.writes
        assert set(scenario.hub_env) == {"CORS_ALLOWED_ORIGINS"}
        process = HubProcess(matrix_host="127.0.0.1", matrix_port=1, telnet_port=2, log_dir=tmp_path,
                             extra_env={**scenario.hub_env, "ADMIN_PIN": "private-pin"})
        assert process.recorded_env()["CORS_ALLOWED_ORIGINS"] == scenario.hub_env["CORS_ALLOWED_ORIGINS"]
        assert "ADMIN_PIN" not in process.recorded_env()


async def test_global_middleware_topology_and_representative_preflight(aiohttp_client, tmp_path, monkeypatch):
    monkeypatch.setenv("CORS_ALLOWED_ORIGINS", "https://allowed.example")
    app = create_rest_app(data_dir=tmp_path / "hub-data")
    routes = sorted({(route.method, route.resource.canonical) for route in app.router.routes()
                     if route.method != "HEAD"})
    middleware = [mw.__name__ for mw in app.middlewares]
    assert not app._subapps and routes
    assert middleware.index("security_middleware") < middleware.index("cors_middleware")
    # All registered routes share the application middleware chain. Exercise
    # resource classes, including write and WS paths, without calling handlers.
    client = await aiohttp_client(app)
    for path in ("/api/health", "/api/switch", "/ui", "/ws", "/not-registered"):
        response = await client.options(path, headers={
            "Origin": "https://allowed.example", "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "X-API-Key, Content-Type",
        })
        assert response.status == 200 and await response.read() == b""
        assert response.headers["Access-Control-Allow-Origin"] == "https://allowed.example"
        assert all(response.headers[name] == value for name, value in CORS_HEADERS.items())
    audit = {"registered_routes": routes, "middleware": middleware, "subapps": 0,
             "limit": "Global chain audit plus representative OPTIONS; not every handler/error response tested"}
    (tmp_path / "middleware-audit.json").write_text(json.dumps(audit, indent=2) + "\n", encoding="utf-8")


def test_real_runner_negative_headers_are_failed_evidence(tmp_path):
    positive = SCENARIOS[0]
    wrong = replace(positive, id="sw_api_read_04.negative_wrong_value",
                    expect=(Response(status=200, headers={"Vary": "wrong"}),))
    unexpected = replace(positive, id="sw_api_read_04.negative_unexpected_presence",
                         expect=(Response(status=200, absent_headers=("Vary",)),))
    runner = Runner(RunOptions(target="sim", clients=("api",), out_dir=tmp_path))
    asyncio.run(runner.run([positive, wrong, unexpected]))
    assert [(o.status, o.gate) for o in runner.outcomes] == [
        ("pass", "ok"), ("fail", "regression"), ("fail", "regression"),
    ]
    validator = jsonschema.Draft202012Validator(json.loads(SCHEMA_PATH.read_text(encoding="utf-8")))
    records = list(iter_records([tmp_path / "evidence"]))
    assert len(records) == 3
    for record in records:
        validator.validate(record.data)
        assert record.data["level"] == "V2"
        assert record.data["environment"]["hub"]["env"]["CORS_ALLOWED_ORIGINS"] == ""
        assert record.data["observations"]["requests"][0]["response_headers"]["vary"] == "Origin"
