"""Opt-in real Chromium checks for the bounded lockout bridge and saved bytes.

Run with SW_SEC_AUTH_BROWSER_TESTS=1 and the locked npm/Chromium dependencies.
The normal runner campaign separately exercises the full run.py subprocess.
"""

import json
import os
from dataclasses import asdict

import pytest

from tests import test_security_v3_hardening_scenarios as security_tests
from tests.validation.scenarios.sw_sec_auth_01 import PEER_ID, PIN, SCENARIOS, SCENE_STEPS, create_profile
from tools.validate.clients.api import ApiClient
from tools.validate.clients.base import HubInfo
from tools.validate.clients.browser import BrowserClient
from tools.validate.evidence import redact
from tools.validate.model import act
from tools.validate.runner import _is_read

auth_hub = security_tests.hub
security_environment = security_tests.security_environment
simulator = security_tests.simulator


@pytest.mark.skipif(os.environ.get("SW_SEC_AUTH_BROWSER_TESTS") != "1", reason="opt-in real Chromium bridge test")
@pytest.mark.parametrize("kind", ("profile", "scene"))
async def test_ui_lockout_preserves_device_and_saved_bytes_then_allows_peer(auth_hub, kind, tmp_path):
    client, _, sim, data = auth_hub
    scenario = next(sc for sc in SCENARIOS if sc.id == f"sw_sec_auth_01.{kind}_locked")
    api, browser = ApiClient(), BrowserClient()
    info = HubInfo(str(client.make_url("/")), artifacts_dir=tmp_path / "screenshots")
    receipt = {"scope": "real Chromium, in-process hub + simulator; source-only", "actions": []}
    await api.start(info)
    try:
        for step in scenario.setup:
            result = await api.perform(step)
            assert result.ok, result
        await browser.start(info)
        before = sim.state.to_dict()
        saved = {name: (data / name).read_bytes() for name in ("profiles.json", "scenes_v2.json")}
        cursor = len(sim.log)
        browser.context = {"artifacts_dir": str(tmp_path / "locked")}
        result = await browser.perform(scenario.action)
        receipt["actions"].append(asdict(result))
        assert result.error is None, result.error
        assert result.status == 429
        assert await browser.observe("pin.wrong_attempts") == 5
        assert await browser.observe("pin.lockout_visible") is True
        assert await browser.observe("pin.retry_after_positive") is True
        assert "Too many wrong passcodes" in await browser.observe("toast.error")
        assert len(result.body["dialogs"]) == 5
        assert all(attempt == {"status": 403, "code": "invalid_passcode"}
                   for attempt in result.body["pin_probe"]["attempts"])
        assert result.screenshots and all(os.path.isfile(path) for path in result.screenshots)
        assert not result.body["page_errors"]
        assert sim.state.to_dict() == before
        assert not [entry for entry in list(sim.log)[cursor:] if not _is_read(entry)]
        assert {name: (data / name).read_bytes() for name in saved} == saved

        # Correct PIN cannot bypass the same item's lock. The API complement
        # checks the actual header too; no prompt occurs for a locked UI item.
        path = (f"/api/profile/{scenario.action.params['profile_id']}/recall" if kind == "profile" else
                f"/api/v2/scenes/{scenario.action.params['scene_id']}/execute")
        status, body, _ = await api.request("POST", path, {"passcode": PIN})
        assert status == 429 and body["data"]["error"] == "passcode_locked"
        assert sim.state.to_dict() == before
        assert {name: (data / name).read_bytes() for name in saved} == saved
        assert not [entry for entry in list(sim.log)[cursor:] if not _is_read(entry)]

        if kind == "profile":
            assert (await api.perform(create_profile(PEER_ID, source=7))).ok
            control = act("profile_recall", profile_id=PEER_ID, passcode=PIN)
            expected_source = 7
        else:
            status, _, _ = await api.request("PUT", "/api/v2/scenes/scene_kidslocked", {"steps": SCENE_STEPS})
            assert status == 200
            control = act("scene_run", scene_id="scene_kidslocked", passcode=PIN)
            expected_source = 6
        browser.context = {"artifacts_dir": str(tmp_path / "peer")}
        result = await browser.perform(control)
        receipt["actions"].append(asdict(result))
        assert result.error is None and result.status == 200, result
        assert sim.state.outputs[0].source == expected_source
        assert before["outputs"][0]["source"] != expected_source
        assert any(not _is_read(entry) for entry in list(sim.log)[cursor:])

        # The bridge must reject unbounded attempts before any UI request.
        browser.context = {"artifacts_dir": str(tmp_path / "bounded-guard")}
        result = await browser.perform(act(
            scenario.action.intent, **{**scenario.action.params,
                                       "pin_lockout": {"attempts": 6, "wrong_passcode": "9999"}},
        ))
        receipt["actions"].append(asdict(result))
        assert "requires five numeric wrong-PIN attempts" in result.error
        assert result.status is None and result.requests == []

        # Calibrate the negative oracle: supplying the real PIN to an unlocked
        # peer must stop at its first successful request, never report lockout.
        browser.context = {"artifacts_dir": str(tmp_path / "allowed-oracle")}
        result = await browser.perform(act(
            control.intent, **{**control.params,
                               "pin_lockout": {"attempts": 5, "wrong_passcode": PIN}},
        ))
        receipt["actions"].append(asdict(result))
        assert "wrong-PIN attempt 1 did not return 403 invalid_passcode" in result.error
        attempts = result.body["pin_probe"]["attempts"]
        assert len(attempts) == 1 and attempts[0]["status"] == 200 and attempts[0].get("code") is None
        assert await browser.observe("pin.lockout_visible") is None
    finally:
        receipt["client"] = browser.environment()
        (tmp_path / "browser-lockout.json").write_text(json.dumps(redact(receipt), indent=2) + "\n", encoding="utf-8")
        await browser.stop()
        await api.stop()
