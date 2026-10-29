"""Synthetic expected-JSON display checks through the real HTTP/runner writer path.

Only unrelated device readback and WS startup/synchronization are doubled. These
fixtures make no physical, browser, or V2/V3 qualification claim.
"""

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


def sensitive_values():
    return tuple(f"c3-synthetic-private-{i}" for i in range(7))


def payload():
    values = sensitive_values()
    return {
        "pin": values[0], "public": "public-expected",
        "nested": {"Authorization": values[1], "public": "public-nested", "items": [
            {"X-Admin-PIN": values[2], "api_key": values[3], "public": "public-item"},
            [{"password": values[4]}],
        ]},
    }


def safe_bytes(raw):
    return not any(value.encode() in raw for value in sensitive_values())


@pytest.mark.parametrize("comparison", ("matched", "top-mismatch", "nested-mismatch", "list-mismatch", "masked-mismatch"))
async def test_expected_json_actual_runner_persistence(
    aiohttp_client, tmp_path, monkeypatch, comparison,
):
    request_body = payload()
    body_original = copy.deepcopy(request_body)
    expected = copy.deepcopy(request_body)
    if comparison == "top-mismatch":
        expected["pin"] = sensitive_values()[5]
    elif comparison == "nested-mismatch":
        expected["nested"]["Authorization"] = sensitive_values()[5]
    elif comparison == "list-mismatch":
        expected["nested"]["items"][1][0]["password"] = sensitive_values()[5]
    elif comparison == "masked-mismatch":
        expected["pin"] = "***"
    expected_original = copy.deepcopy(expected)
    expected_nested = expected["nested"]
    expected_items = expected_nested["items"]
    headers = {"X-Admin-PIN": sensitive_values()[6], "X-Correlation-ID": "public-correlation"}
    transmitted = []

    async def exchange(request):
        transmitted.append({"method": request.method, "path": request.path,
                            "headers": {name: request.headers[name] for name in headers},
                            "body": await request.json()})
        # An extra field proves that the real subset comparison is still used.
        return web.json_response({**request_body, "extra": "public-extra"},
                                 headers={"Vary": "Origin", "Set-Cookie": sensitive_values()[6]})

    app = web.Application()
    app.router.add_post("/synthetic-expected", exchange)
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
    action = act("request", method="POST", path="/synthetic-expected", json=request_body, headers=headers)
    action_original = copy.deepcopy(action.params)
    expectation = Response(status=200, min_status=200, json=expected, headers={"Vary": "Origin"},
                           absent_headers=("X-Absent-Public",))
    description = expectation.describe()
    scenario = Scenario(id="synthetic.expected_json", title="Synthetic expected JSON description",
                        features=("F-SEC-014",), action=action, expect=(expectation,),
                        covers=("tools/validate/model.py",))
    await api.start(HubInfo(url))
    try:
        outcome = await runner._run_one(scenario, api)
    finally:
        await api.stop()

    assert (transmitted == [{"method": "POST", "path": "/synthetic-expected",
                             "headers": headers, "body": body_original}]) is True
    assert (action.params == action_original and request_body == body_original) is True
    assert action.params["json"] is request_body
    assert expectation.json is expected
    assert expected["nested"] is expected_nested
    assert expected_nested["items"] is expected_items
    assert (expected == expected_original) is True
    assert len(results) == 1
    result = results[0]
    assert result.ok and result.status == 200
    assert (result.body == {**body_original, "extra": "public-extra"}) is True
    assert result.requests[0]["body"] is request_body
    assert result.requests[0]["response"] is result.body
    verdict = "pass" if comparison == "matched" else "fail"
    assert outcome.status == verdict

    paths = list((tmp_path / "evidence").rglob("*.json"))
    assert len(paths) == 1
    raw = paths[0].read_bytes()
    record = json.loads(raw)
    assert not list(jsonschema.Draft202012Validator(json.loads(SCHEMA_PATH.read_text())).iter_errors(record))
    assert len(record["checks"]) == 1 and record["checks"][0]["result"] == verdict
    assert record["checks"][0]["description"] == description
    procedure_raw = json.dumps(record["procedure"]).encode()
    checks_raw = json.dumps(record["checks"]).encode()
    # These diagnostic copies and boolean receipts exist even if the oracle fails.
    (tmp_path / "procedure.json").write_bytes(procedure_raw)
    (tmp_path / "checks.json").write_bytes(checks_raw)
    receipt = {"record_safe": safe_bytes(raw), "procedure_safe": safe_bytes(procedure_raw),
               "checks_safe": safe_bytes(checks_raw), "description_safe": safe_bytes(description.encode()),
               "records": len(paths), "raw_inputs_unchanged": True, "raw_verdict_correct": True}
    (tmp_path / "byte-receipt.json").write_text(json.dumps(receipt), encoding="utf-8")
    assert receipt["description_safe"] is True
    assert receipt["procedure_safe"] is True
    assert receipt["checks_safe"] is True
    assert receipt["record_safe"] is True
    assert safe_bytes("\n".join(result.steps).encode()) is True
    for public in ("public-expected", "public-nested", "public-item"):
        assert public in description and public.encode() in procedure_raw and public.encode() in checks_raw
    assert "HTTP 200 and HTTP >= 200" in description
    assert "headers equal (names: Vary) and headers absent: X-Absent-Public" in description
    observed = record["observations"]["requests"][0]
    assert observed["response_headers"]["vary"] == "Origin"
    assert observed["response_headers"]["content-type"] == "application/json; charset=utf-8"
    assert observed["response_headers"]["set-cookie"] == "***"
    assert "set-cookie" in observed["response_headers_redacted"]
    assert (expected == expected_original and action.params == action_original) is True


@pytest.mark.parametrize(("expectation", "description"), (
    (Response(), "response "),
    (Response(status=(200, 201), json={}), "response HTTP (200, 201)"),
    (Response(min_status=400, json={"public": [1, {"value": "visible"}]}),
     "response HTTP >= 400 and body contains {'public': [1, {'value': 'visible'}]}"),
))
def test_public_response_description_format(expectation, description):
    assert expectation.describe() == description
