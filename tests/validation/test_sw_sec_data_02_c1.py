"""Synthetic VAL-15 regressions at the recursive and actual persistence boundaries."""

import copy
import json
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from aiohttp import web

from tools.validate.clients.api import ApiClient
from tools.validate.clients.base import HubInfo
from tools.validate.evidence import redact, write_record
from tools.validate.model import Scenario, act
from tools.validate.runner import Runner, RunOptions, WsObserver

PUBLIC = {
    "Origin": "https://public.example",
    "Vary": "Origin",
    "X-Correlation-ID": "public-correlation",
    "Content-Type": "application/json",
    "X-Admin-PIN-Policy": "public-policy",
}
CREDENTIALS = ("X-Admin-PIN", "X-API-Key", "Authorization", "Cookie")


def synthetic_headers():
    return {**PUBLIC, **{name: f"synthetic-credential-{i}" for i, name in enumerate(CREDENTIALS)}}


def no_credentials(text):
    # Boolean assertions keep synthetic marker values out of public failure receipts.
    return not any(f"synthetic-credential-{i}" in text for i in range(len(CREDENTIALS)))


@pytest.mark.parametrize("case", (str.lower, str.upper, str.swapcase))
def test_recursive_redaction_and_action_description_preserve_inputs(case):
    headers = {case(k): v for k, v in synthetic_headers().items()}
    request = {"headers": headers, "nested": [{"headers": headers.copy()}],
               "password": "synthetic-old-secret", "url": "/public?key=synthetic-query&output=2"}
    original = copy.deepcopy(request)
    safe = redact(request)
    description = act("request", path="/exchange", **request).describe()
    mapping_safe = no_credentials(json.dumps(safe))
    description_safe = no_credentials(description)
    assert mapping_safe is True
    assert description_safe is True
    for where in (safe["headers"], safe["nested"][0]["headers"]):
        assert all(where[case(k)] == "***" for k in CREDENTIALS)
        assert all(where[case(k)] == v for k, v in PUBLIC.items())
    assert safe["password"] == "***"
    assert safe["url"] == "/public?key=***&output=2"
    assert (request == original) is True


def test_writer_masks_unredacted_nested_diagnostics_without_mutation(tmp_path):
    record = {
        "features": ["F-SEC-014"], "timestamp": {"started": "2026-10-28T00:00:00Z"},
        "level": "V1", "commit": {"short": "00000000"}, "scenario": "synthetic.writer", "client": "api",
        "observations": {"client_diagnostics": {"nested": [{"headers": synthetic_headers()}], "pin": "old-pin"}},
    }
    original = copy.deepcopy(record)
    path = write_record(tmp_path, record)
    raw = path.read_bytes()
    bytes_safe = no_credentials(raw.decode())
    assert bytes_safe is True
    diagnostic = json.loads(raw)["observations"]["client_diagnostics"]
    assert diagnostic["pin"] == "***"
    assert all(diagnostic["nested"][0]["headers"][k] == v for k, v in PUBLIC.items())
    assert (record == original) is True


@pytest.mark.parametrize("diagnostics", (False, True), ids=("api", "diagnostic-client"))
async def test_runner_writes_safe_requests_diagnostics_and_procedure(
    aiohttp_client, tmp_path, monkeypatch, diagnostics,
):
    transmitted = []

    async def exchange(request):
        received = {k: request.headers[k] for k in synthetic_headers()}
        transmitted.append(received)
        return web.json_response({"nested": [{"headers": received}], "passcode": "old-passcode"})

    app = web.Application()
    app.router.add_get("/exchange", exchange)
    server = await aiohttp_client(app)
    url = str(server.make_url("/"))
    api = ApiClient()
    # A non-API client places its body in client_diagnostics. This is an HTTP
    # transport double for that branch, not a browser execution claim.
    if diagnostics:
        api.name = "browser"
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
    action = act("request", path="/exchange", headers=synthetic_headers())
    original = copy.deepcopy(action.params)
    # Response expectations stringify bodies into check details, a separate
    # unsupported text boundary reported to the coordinator. Observe the actual
    # HTTP result below without converting its credential mapping to free text.
    scenario = Scenario(id="synthetic.redaction", title="Synthetic HTTP redaction", features=("F-SEC-014",),
                        action=action, expect=(), clients=(api.name,),
                        covers=("tools/validate/evidence.py",))
    await api.start(HubInfo(url))
    try:
        outcome = await runner._run_one(scenario, api)
    finally:
        await api.stop()
    assert outcome.status == "pass"
    assert len(results) == 1 and results[0].ok and results[0].status == 200
    assert (transmitted == [original["headers"]]) is True
    assert (action.params == original) is True
    paths = list((tmp_path / "evidence").rglob("*.json"))
    assert len(paths) == 1
    raw = paths[0].read_bytes()
    bytes_safe = no_credentials(raw.decode())
    assert bytes_safe is True
    record = json.loads(raw)
    assert no_credentials("\n".join(record["procedure"])) is True
    assert "public-correlation" in "\n".join(record["procedure"])
    observed = record["observations"]["requests"][0]["response"]["nested"][0]["headers"]
    assert all(observed[k] == "***" for k in CREDENTIALS)
    assert all(observed[k] == v for k, v in PUBLIC.items())
    if diagnostics:
        assert record["observations"]["client_diagnostics"]["nested"][0]["headers"] == observed
    assert record["observations"]["requests"][0]["response"]["passcode"] == "***"
