"""WP-F1 access control end to end: the ``security_auth`` scenarios and the three auth configurations.

In process: the real hub app (wired like ``run.py`` modular mode, ``tests/sim/conftest.py``) talking to
the BK-808 simulator. Scenarios run the way ``tools.validate.runner`` runs them (setup and cleanup
through a helper client, the action through a client of its own, both without cookies on an IP host),
including the raw ``headers`` / ``data`` the ``cross_site_*`` scenarios send. The scenarios the
runner's api client can already send also run through the real runner (hub subprocess + simulator).

The configurations: no PIN, Admin PIN, Admin + Control PIN (remembered-device cookie, ``X-API-Key``
header and ``?key=`` query API keys).
"""

from __future__ import annotations

import asyncio
import json
import time
from typing import Any
from unittest.mock import AsyncMock

import aiohttp
import pytest

import orei_matrix
import telnet_client
from rest_api import reset_rate_limiter
from tests.sim.conftest import FAST_TELNET_TIMEOUT, _data_hub, make_simulator, sim_writes
from tests.validation.scenarios import security_auth
from tools.validate.clients.api import rest_call
from tools.validate.device import SimDevice
from tools.validate.model import (
    Action,
    CommandSent,
    Device,
    DeviceUnchanged,
    Hub,
    NoCommand,
    Response,
    Scenario,
    diff_states,
    path_matches,
    resolve,
)
from tools.validate.registry import load_findings
from tools.validate.runner import Runner, RunOptions, _subset
from tools.validate.scenarios import discover

ADMIN, CONTROL = security_auth.ADMIN_PIN, security_auth.CONTROL_PIN
SCENARIOS = {sc.id: sc for sc in security_auth.SCENARIOS}
#: Raw request parts the runner's api client does not send yet (tools/validate/clients/api.py).
RAW_PARAMS = ("headers", "data")
ENV = ("ADMIN_PIN", "CONTROL_PIN", "ADMIN_PIN_RESET", "API_KEY", "CONTROL_API_KEY", "CORS_ALLOWED_ORIGINS",
       "ALLOWED_HOSTS", "ALLOW_PUBLIC_MATRIX_HOST")


def _sets_pin(action: Action) -> str | None:
    p = action.params
    if p.get("path") == "/api/auth/pin" and (p.get("json") or {}).get("pin"):
        return p["json"].get("level", "admin")
    return None


def _clears_pin(action: Action) -> str | None:
    p = action.params
    if p.get("path") == "/api/auth/pin" and not (p.get("json") or {}).get("pin"):
        return p["json"].get("level", "admin")
    return None


# --------------------------------------------------------------------------- discovery


def test_discover_finds_every_security_auth_scenario():
    discovered = discover()  # raises on a duplicate id across all scenario modules
    ids = [sc.id for sc in security_auth.SCENARIOS]
    assert len(ids) == len(set(ids))
    assert {sid for sid in discovered if sid.startswith("security_auth.")} == set(ids)
    for sc in security_auth.SCENARIOS:
        assert discovered[sc.id] is sc
        assert sc.all_features <= {"F-SEC-001", "F-SEC-002", "F-SEC-003"}, sc.id
        assert sc.targets == ("sim",), sc.id
        assert "src/rest_api/security.py" in sc.covers, sc.id
    for feature in ("F-SEC-001", "F-SEC-002", "F-SEC-003"):
        assert any(feature in sc.features for sc in security_auth.SCENARIOS), feature


def test_every_pin_a_scenario_sets_is_cleared_again():
    for sc in security_auth.SCENARIOS:
        set_levels = {lvl for a in sc.setup if (lvl := _sets_pin(a))}
        cleared = {lvl for a in (sc.action, *sc.cleanup) if (lvl := _clears_pin(a))}
        assert set_levels <= cleared, f"{sc.id} leaves the {sorted(set_levels - cleared)} PIN set"
        if _sets_pin(sc.action):  # only as a request the hub must refuse
            assert sc.kind == "failure" and any(isinstance(e, Response) and e.status == 401 for e in sc.expect), sc.id


# --------------------------------------------------------------------------- the in-process hub


@pytest.fixture
async def hub(aiohttp_client, monkeypatch, tmp_path):
    """REST test client on the real hub app with a connected OreiMatrix on a fresh simulator."""
    monkeypatch.setenv("MATRIX_PASSWORD_ITERATIONS", "1000")
    for name in ENV:
        monkeypatch.delenv(name, raising=False)
    sim = make_simulator()
    await sim.start()
    monkeypatch.setenv("OREI_TELNET_PORT", str(sim.telnet_port))
    for name in ("OREI_USER", "OREI_PASSWORD", "OREI_USE_TELNET_CEC", "OREI_VERIFY_SSL"):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setattr(orei_matrix, "INITIAL_RETRY_DELAY", 0.01)
    monkeypatch.setattr(orei_matrix, "MAX_RETRY_DELAY", 0.05)
    monkeypatch.setattr(telnet_client, "COMMAND_TIMEOUT", FAST_TELNET_TIMEOUT)
    matrix = orei_matrix.OreiMatrix("127.0.0.1", port=sim.https_port, use_https=sim.tls)
    monkeypatch.setattr(matrix, "_connect_telnet", AsyncMock(return_value=False))
    try:
        async for client in _data_hub(aiohttp_client, matrix, monkeypatch, tmp_path):
            client.sim = sim  # type: ignore[attr-defined]
            yield client
    finally:
        await matrix.disconnect()
        await sim.stop()


async def _send(session: aiohttp.ClientSession, action: Action) -> tuple[int, Any]:
    """The ``request`` intent as the runner's api client sends it, plus raw ``headers`` / ``data``."""
    method, path, body = rest_call(action)
    kwargs: dict[str, Any] = {k: action.params[k] for k in RAW_PARAMS if k in action.params}
    if body is not None:
        kwargs["json"] = body
    async with session.request(method, path, **kwargs) as resp:
        text = await resp.text()
        try:
            return resp.status, json.loads(text) if text else None
        except ValueError:
            return resp.status, text


async def _check(exp, status: int, body: Any, dev: SimDevice, before: dict, cursor: int,
                 helper: aiohttp.ClientSession) -> str | None:
    """The runner's verdict for one expectation; returns why it failed, or ``None``."""
    if isinstance(exp, Response):
        allowed = exp.status if isinstance(exp.status, tuple) else (exp.status,)
        if exp.status is not None and status not in allowed:
            return f"HTTP {status} (body {body!r})"
        if exp.min_status is not None and status < exp.min_status:
            return f"HTTP {status}"
        if exp.json and not _subset(exp.json, body):
            return f"body {body!r}"
        return None
    if isinstance(exp, Hub):
        got_status, got = await _send(helper, Action("request", {"method": "GET", "path": exp.path}))
        if exp.status is not None and got_status != exp.status:
            return f"HTTP {got_status}"
        if not exp.field_path:
            return None
        try:
            value = resolve(got, exp.field_path)
        except KeyError:
            return f"{exp.field_path} absent in {got!r}"
        ok = value != exp.not_equals if exp.not_equals is not None else value == exp.equals
        return None if ok else f"{exp.field_path} = {value!r}"
    if isinstance(exp, Device):
        deadline = time.monotonic() + exp.timeout
        while True:
            value = resolve(await dev.state(), exp.path)
            if value == exp.equals or time.monotonic() >= deadline:
                return None if value == exp.equals else f"{exp.path} = {value!r}"
            await asyncio.sleep(0.05)
    if isinstance(exp, DeviceUnchanged):
        changed = [d for d in diff_states(before, await dev.state())
                   if not any(path_matches(d["path"], a) for a in exp.allow)]
        return f"unexpected changes {changed[:5]}" if changed else None
    entries = (await dev.log())[cursor:]
    if isinstance(exp, NoCommand):
        hits = [e for e in entries if e.get("channel") in ("http", "telnet")
                and (e.get("mutated") if exp.command == "*" else e.get("command") == exp.command)]
        return f"writes {[(e.get('command'), e.get('payload')) for e in hits]}" if hits else None
    if isinstance(exp, CommandSent):
        hits = [e for e in entries if e.get("channel") == exp.channel and e.get("command") == exp.command
                and (exp.payload is None or _subset(exp.payload, e.get("payload")))]
        ok = len(hits) == exp.count if exp.count is not None else bool(hits)
        return None if ok else f"{len(hits)} matching of {[(e.get('command'), e.get('payload')) for e in entries]}"
    raise AssertionError(f"{type(exp).__name__} has no in-process check; add one before using it here")


async def _run(sc: Scenario, client, session: aiohttp.ClientSession, helper: aiohttp.ClientSession,
               monkeypatch) -> list[str]:
    """One scenario: reset, setup, action, checks, cleanup. Returns the failed checks."""
    failures: list[str] = []
    reset_rate_limiter()
    async with SimDevice(client.sim.control_url) as dev:
        await dev.reset(sc.sim_state)
        with monkeypatch.context() as env:
            for key, value in sc.hub_env.items():
                env.setenv(key, value)
            try:
                for step in sc.setup:
                    status, body = await _send(helper, step)
                    assert 200 <= status < 300, f"{sc.id}: setup {step.describe()} -> HTTP {status} {body!r}"
                before = await dev.state()
                cursor = len(await dev.log())
                status, body = await _send(session, sc.action)
                for exp in sc.expect:
                    why = await _check(exp, status, body, dev, before, cursor, helper)
                    if why:
                        failures.append(f"{sc.id}: {exp.describe()}: {why}")
            finally:
                for step in sc.cleanup:
                    status, body = await _send(helper, step)
                    assert 200 <= status < 300, f"{sc.id}: cleanup {step.describe()} -> HTTP {status} {body!r}"
    status, body = await _send(helper, Action("request", {"method": "GET", "path": "/api/auth/status"}))
    assert status == 200 and body["admin_pin_set"] is False and body["control_pin_set"] is False, \
        f"{sc.id} left the hub locked: {body!r}"
    return failures


def _sessions(client) -> tuple[aiohttp.ClientSession, aiohttp.ClientSession]:
    """Action and helper clients like the runner's: separate, and cookie-less on an IP host."""
    base = str(client.make_url("/"))
    return aiohttp.ClientSession(base_url=base), aiohttp.ClientSession(base_url=base)


@pytest.mark.parametrize("sid", list(SCENARIOS))
async def test_scenario_in_process(sid, hub, monkeypatch):
    session, helper = _sessions(hub)
    async with session, helper:
        assert await _run(SCENARIOS[sid], hub, session, helper, monkeypatch) == []


async def test_scenarios_in_sequence_leave_the_hub_open(hub, monkeypatch):
    """The whole module in discovery order on one hub and one action client, as a runner session does."""
    session, helper = _sessions(hub)
    failures: list[str] = []
    async with session, helper:
        for sc in security_auth.SCENARIOS:
            failures += await _run(sc, hub, session, helper, monkeypatch)
        status, body = await _send(helper, Action("request", {"method": "GET", "path": "/api/auth/status"}))
    assert failures == []
    assert status == 200 and body == {"admin_pin_set": False, "control_pin_set": False,
                                      "session_level": "none", "device_remembered": False}


# --------------------------------------------------------------------------- the three configurations


async def _status(client, **kw) -> dict:
    resp = await client.get("/api/auth/status", **kw)
    assert resp.status == 200
    return await resp.json()


async def _switch(client, input_: int, **kw) -> int:
    return (await client.post("/api/switch", json={"input": input_, "output": 1}, **kw)).status


async def test_configuration_no_pin(hub):
    sim = hub.sim
    assert await _status(hub) == {"admin_pin_set": False, "control_pin_set": False,
                                  "session_level": "none", "device_remembered": False}
    assert (await hub.get("/api/auth/devices")).status == 200
    assert (await hub.get("/api/auth/api-keys")).status == 200
    assert (await hub.post("/api/settings/test-connection", json={})).status == 200
    assert await _switch(hub, 4) == 200
    assert sim.state.outputs[0].source == 4
    assert len(sim_writes(sim, "video switch")) == 1


async def test_configuration_admin_pin(hub):
    sim = hub.sim
    assert (await hub.post("/api/auth/pin", json={"level": "admin", "pin": ADMIN})).status == 200
    assert (await _status(hub))["admin_pin_set"] is True
    # Admin routes are locked; control routes stay open without a Control PIN.
    assert (await hub.post("/api/settings/test-connection", json={})).status == 401
    assert (await hub.get("/api/auth/devices")).status == 401
    assert (await hub.post("/api/settings/test-connection", json={}, headers={"X-Admin-PIN": "0000"})).status == 401
    assert (await hub.post("/api/settings/test-connection", json={}, headers={"X-Admin-PIN": ADMIN})).status == 200
    assert await _switch(hub, 5) == 200 and sim.state.outputs[0].source == 5
    # Unlock: an HttpOnly, SameSite=Strict session cookie opens admin routes until lock.
    resp = await hub.post("/api/auth/unlock", json={"level": "admin", "pin": ADMIN})
    assert resp.status == 200
    cookie = resp.headers["Set-Cookie"]
    assert "orei_session=" in cookie and "HttpOnly" in cookie and "SameSite=Strict" in cookie
    assert (await _status(hub))["session_level"] == "admin"
    assert (await hub.get("/api/auth/devices")).status == 200
    assert (await hub.post("/api/auth/lock")).status == 200
    assert (await _status(hub))["session_level"] == "none"
    assert (await hub.post("/api/settings/test-connection", json={})).status == 401
    # Back to open.
    resp = await hub.post("/api/auth/pin", json={"level": "admin", "pin": None, "current_pin": ADMIN})
    assert await resp.json() == {"admin_pin_set": False, "control_pin_set": False}
    assert (await hub.post("/api/settings/test-connection", json={})).status == 200


async def test_configuration_admin_and_control_pin(hub):
    sim = hub.sim
    assert (await hub.post("/api/auth/pin", json={"level": "control", "pin": CONTROL})).status == 200
    assert (await hub.post("/api/auth/pin", json={"level": "admin", "pin": ADMIN})).status == 200
    status = await _status(hub)
    assert status["admin_pin_set"] and status["control_pin_set"]
    assert await _switch(hub, 6) == 401
    assert sim_writes(sim, "video switch") == []

    # Control unlock with "remember this device": session + long-lived device cookie.
    resp = await hub.post("/api/auth/unlock", json={"level": "control", "pin": CONTROL,
                                                    "remember_device": True, "device_name": "Kiosk"})
    assert resp.status == 200
    device_cookie = next(c for c in resp.headers.getall("Set-Cookie") if c.startswith("orei_device_token="))
    assert "HttpOnly" in device_cookie and "SameSite=Strict" in device_cookie
    assert await _switch(hub, 6) == 200 and sim.state.outputs[0].source == 6
    assert (await hub.post("/api/settings/test-connection", json={})).status == 401  # control is not admin
    # Lock ends the session; the remembered device still controls.
    await hub.post("/api/auth/lock")
    status = await _status(hub)
    assert (status["session_level"], status["device_remembered"]) == ("control", True)
    assert await _switch(hub, 7) == 200 and sim.state.outputs[0].source == 7

    # API keys are issued by an admin and grant control only (header or ?key=).
    admin = {"X-Admin-PIN": ADMIN}
    resp = await hub.post("/api/auth/api-keys", json={"name": "Home Assistant"}, headers=admin)
    assert resp.status == 201
    key = await resp.json()
    listed = await hub.get("/api/auth/api-keys", headers=admin)
    assert key["key"] not in await listed.text() and (await listed.json())[0]["name"] == "Home Assistant"
    devices = await (await hub.get("/api/auth/devices", headers=admin)).json()
    assert [d["name"] for d in devices] == ["Kiosk"]
    assert (await hub.delete(f"/api/auth/devices/{devices[0]['id']}", headers=admin)).status == 200
    assert (await _status(hub))["device_remembered"] is False
    assert await _switch(hub, 8) == 401

    assert await _switch(hub, 8, headers={"X-API-Key": key["key"]}) == 200
    assert sim.state.outputs[0].source == 8
    assert (await hub.post(f"/api/switch?key={key['key']}", json={"input": 2, "output": 1})).status == 200
    assert sim.state.outputs[0].source == 2
    assert (await _status(hub, headers={"X-API-Key": key["key"]}))["session_level"] == "control"
    assert (await hub.post("/api/settings/test-connection", json={}, headers={"X-API-Key": key["key"]})).status == 401
    assert await _switch(hub, 3, headers={"X-API-Key": "not-a-key"}) == 401
    assert (await hub.delete(f"/api/auth/api-keys/{key['id']}", headers=admin)).status == 200
    assert await _switch(hub, 3, headers={"X-API-Key": key["key"]}) == 401
    assert sim.state.outputs[0].source == 2
    assert len(sim_writes(sim, "video switch")) == 4

    # Back to open: the Control PIN first (needs the Admin PIN), then the Admin PIN.
    for level in ("control", "admin"):
        resp = await hub.post("/api/auth/pin", json={"level": level, "pin": None, "current_pin": ADMIN})
        assert resp.status == 200
    assert await _status(hub) == {"admin_pin_set": False, "control_pin_set": False,
                                  "session_level": "none", "device_remembered": False}
    assert await _switch(hub, 4) == 200


# --------------------------------------------------------------------------- through the real runner


def test_runner_scenarios_pass(tmp_path, monkeypatch):
    """Every scenario the runner's api client can send, on a real hub process + simulator."""
    monkeypatch.setenv("MATRIX_PASSWORD_ITERATIONS", "1000")
    for name in ENV:
        monkeypatch.delenv(name, raising=False)
    chosen = [sc for sc in security_auth.SCENARIOS if not set(RAW_PARAMS) & set(sc.action.params)]
    assert len(chosen) >= len(security_auth.SCENARIOS) - 5
    # status_open again at the end: the run must leave the hub open.
    chosen.append(SCENARIOS["security_auth.status_open"])
    runner = Runner(RunOptions(target="sim", clients=("api",), out_dir=tmp_path, findings=load_findings()))
    outcomes = asyncio.run(runner.run(chosen))
    assert [(o.scenario, o.status, o.gate) for o in outcomes] == [(sc.id, "pass", "ok") for sc in chosen], \
        [(o.scenario, o.failed_checks, o.reason) for o in outcomes if o.status != "pass"]
    assert {o.level for o in outcomes} == {"V2"}
