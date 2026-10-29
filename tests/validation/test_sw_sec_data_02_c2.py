"""Synthetic regressions for the two leased structured-body formatting boundaries."""

import copy
import json
from types import SimpleNamespace
from unittest.mock import AsyncMock

import jsonschema
import pytest
from aiohttp import web

from tools.validate.clients.api import ApiClient
from tools.validate.clients.base import HubInfo
from tools.validate.evidence import SCHEMA_PATH
from tools.validate.model import Response, Scenario, act
from tools.validate.runner import Runner, RunOptions, WsObserver


def payload():
    return {"pin": "c2-synthetic-first", "public": "public-body", "nested": [
        {"Authorization": "c2-synthetic-second", "items": [{"X-Admin-PIN": "c2-synthetic-third"}]},
    ]}


def safe_bytes(raw):
    return not any(value.encode() in raw for value in (
        "c2-synthetic-first", "c2-synthetic-second", "c2-synthetic-third", "c2-synthetic-header",
    ))


@pytest.mark.parametrize("shape", ("mapping", "list"))
@pytest.mark.parametrize("matches", (True, False), ids=("matched", "mismatched"))
async def test_actual_runner_masks_body_text_without_changing_exchange(
    aiohttp_client, tmp_path, monkeypatch, shape, matches,
):
    body = payload() if shape == "mapping" else [payload(), {"public": "public-list"}]
    original = copy.deepcopy(body)
    headers = {"X-Admin-PIN": "c2-synthetic-header", "X-Correlation-ID": "public-correlation"}
    transmitted = []

    async def exchange(request):
        transmitted.append({"method": request.method, "path": request.path,
                            "headers": {name: request.headers[name] for name in headers},
                            "body": await request.json()})
        return web.json_response(body, headers={"Vary": "Origin", "Set-Cookie": "c2-synthetic-header"})

    app = web.Application()
    app.router.add_post("/synthetic-exchange", exchange)
    server = await aiohttp_client(app)
    url = str(server.make_url("/"))
    api = ApiClient()
    results = []
    perform = api.perform

    async def capture_result(action):
        result = await perform(action)
        results.append(result)
        return result

    monkeypatch.setattr(api, "perform", capture_result)
    runner = Runner(RunOptions(out_dir=tmp_path, hub_url=url))
    runner.hub = SimpleNamespace(base_url=url, external_url=url, entry=url)
    runner.device = SimpleNamespace(state=AsyncMock(return_value={"routing": [1]}))
    monkeypatch.setattr(runner, "_wait_hub_telnet", AsyncMock())
    monkeypatch.setattr(WsObserver, "start", AsyncMock())
    monkeypatch.setattr(WsObserver, "sync", AsyncMock(return_value=True))
    monkeypatch.setattr(WsObserver, "stop", AsyncMock())
    action = act("request", method="POST", path="/synthetic-exchange", json=body, headers=headers)
    original_params = copy.deepcopy(action.params)
    # Expected-value descriptions are a separate, readonly model.py boundary.
    # Persist only public expectations here; test raw secret comparisons below.
    expected_json = {"public": "public-body" if matches else "different-public"} if shape == "mapping" else None
    expectation = Response(status=200, json=expected_json,
                           headers={"Vary": "Origin" if matches else "different-public"},
                           absent_headers=("X-Absent-Public",))
    scenario = Scenario(id="synthetic.body_text", title="Synthetic structured body formatting",
                        features=("F-SEC-014",), action=action, expect=(expectation,),
                        covers=("tools/validate/clients/api.py", "tools/validate/runner.py"))
    await api.start(HubInfo(url))
    try:
        outcome = await runner._run_one(scenario, api)
    finally:
        await api.stop()

    assert (transmitted == [{"method": "POST", "path": "/synthetic-exchange",
                             "headers": headers, "body": original}]) is True
    assert (action.params == original_params and body == original) is True
    assert action.params["json"] is body
    assert len(results) == 1
    result = results[0]
    assert result.ok and result.status == 200
    assert (result.body == original) is True
    assert result.requests[0]["body"] is body
    assert result.requests[0]["response"] is result.body
    assert outcome.status == ("pass" if matches else "fail")

    paths = list((tmp_path / "evidence").rglob("*.json"))
    assert len(paths) == 1
    raw = paths[0].read_bytes()
    record = json.loads(raw)
    assert not list(jsonschema.Draft202012Validator(json.loads(SCHEMA_PATH.read_text())).iter_errors(record))
    procedure_raw = json.dumps(record["procedure"]).encode()
    checks_raw = json.dumps(record["checks"]).encode()
    # Save count/boolean-only receipts even for the before-fix failing oracle.
    receipt = {"record_safe": safe_bytes(raw), "procedure_safe": safe_bytes(procedure_raw),
               "checks_safe": safe_bytes(checks_raw), "records": len(paths)}
    (tmp_path / "byte-receipt.json").write_text(json.dumps(receipt), encoding="utf-8")
    assert receipt["procedure_safe"] is True
    assert receipt["checks_safe"] is True
    assert receipt["record_safe"] is True
    assert safe_bytes("\n".join(result.steps).encode()) is True
    assert "public-body" in procedure_raw.decode()
    assert "public-body" in checks_raw.decode()
    observed = record["observations"]["requests"][0]
    assert observed["response_headers"]["vary"] == "Origin"
    assert observed["response_headers"]["content-type"] == "application/json; charset=utf-8"
    assert observed["response_headers"]["set-cookie"] == "***"
    assert "set-cookie" in observed["response_headers_redacted"]
    assert record["checks"][0]["result"] == ("pass" if matches else "fail")

    if shape == "mapping":
        # Direct checks prove equality still uses raw body values. Their expected
        # descriptions are intentionally not persisted or claimed sanitized.
        raw_result = result.body
        for expected, verdict in ((original["pin"], "pass"), ("***", "fail")):
            check = await runner._check(Response(status=200, json={"pin": expected}), scenario,
                                        api, result, {}, 0, SimpleNamespace(), api, 0, [])
            assert check["result"] == verdict
        assert result.body is raw_result
        assert (result.body == original and action.params == original_params) is True
