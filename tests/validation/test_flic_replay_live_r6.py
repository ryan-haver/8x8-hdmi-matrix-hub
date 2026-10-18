"""Live integration tests for the dedicated Flic replay client (R6).

Launches the real simulator and hub stack (run.py), performs generated requests,
and asserts:
- HTTP envelopes and status codes
- Simulator hardware state changes
- Ordered command-log deltas
- Exact-request replay vs known pre-fix defect reproduction
- Gesture matching vs duplicate / non-matching rejection
- Keyless vs keyed authentication (401 on missing/wrong key, 200 on header & query keys)
- Protected profile PIN refusal vs distinct manual passcode execution
- Redaction of keys, query parameters, and passcodes in evidence
"""

from __future__ import annotations

from typing import Any

import aiohttp
import pytest

from tools.validate.clients import FlicClient, NotSupportedError
from tools.validate.clients.base import HubInfo
from tools.validate.device import SimDevice
from tools.validate.model import act
from tools.validate.stack import HubProcess, SimulatorProcess

SHARED_API_KEY = "flic-live-test-key-42"


@pytest.fixture(scope="module")
def live_stack(tmp_path_factory):
    """Launch real simulator and hub stack with an API key pre-configured."""
    tmp_path = tmp_path_factory.mktemp("flic_live_stack")
    sim = SimulatorProcess(log_dir=tmp_path / "sim")
    sim.start()
    hub = HubProcess(
        matrix_host="127.0.0.1",
        matrix_port=sim.https_port,
        telnet_port=sim.telnet_port,
        log_dir=tmp_path / "hub",
        extra_env={
            "CONTROL_API_KEY": SHARED_API_KEY,
            "API_KEY": SHARED_API_KEY,
        },
    )
    hub.start()
    try:
        yield sim, hub
    finally:
        hub.stop()
        sim.stop()


@pytest.fixture
async def flic_client(live_stack):
    _, hub = live_stack
    client = FlicClient()
    await client.start(HubInfo(hub.base_url))
    try:
        yield client
    finally:
        await client.stop()


async def _reset_sim(sim: SimulatorProcess, seed: dict[str, Any] | None = None) -> None:
    async with SimDevice(sim.control_url) as dev:
        await dev.reset(seed)


async def _get_sim_state(sim: SimulatorProcess) -> dict[str, Any]:
    async with SimDevice(sim.control_url) as dev:
        return await dev.state()


async def _get_sim_log(sim: SimulatorProcess) -> list[dict[str, Any]]:
    async with SimDevice(sim.control_url) as dev:
        return await dev.log()


@pytest.mark.asyncio
async def test_live_pre_fix_all_output_defect_reproduction(live_stack, flic_client):
    """Concrete expected-defect reproduction: generated POST /api/input/{n} targets an absent route (404)."""
    sim, _ = live_stack
    await _reset_sim(sim)
    state_before = await _get_sim_state(sim)
    sources_before = [o["source"] for o in state_before["outputs"]]

    # Replay pre-fix generated request: POST /api/input/3
    result = await flic_client.perform(act("route_all", input=3, legacy_defect=True))

    # Assert HTTP envelope: 404 Not Found
    assert result.status == 404
    assert result.ok is False
    assert result.requests[0]["path"] == "/api/input/3"
    assert result.requests[0]["status"] == 404

    # Assert simulator state: untouched, no switch happened
    state_after = await _get_sim_state(sim)
    sources_after = [o["source"] for o in state_after["outputs"]]
    assert sources_after == sources_before
    assert 3 not in sources_after or sources_after != [3] * 8


@pytest.mark.asyncio
async def test_live_post_fix_all_output_exact_replay(live_stack, flic_client):
    """After narrow generator correction: generated POST /api/switch with JSON body routes all outputs."""
    sim, _ = live_stack
    await _reset_sim(sim)
    log_cursor = len(await _get_sim_log(sim))

    # Replay corrected generated request: POST /api/switch with {"input": 4}
    result = await flic_client.perform(act("route_all", input=4))

    assert result.status == 200
    assert result.ok is True
    assert result.requests[0]["path"] == "/api/switch"
    assert result.requests[0]["body"] == {"input": 4}

    # Assert simulator state: all 8 outputs routed to input 4
    state_after = await _get_sim_state(sim)
    assert [o["source"] for o in state_after["outputs"]] == [4] * 8

    # Assert command-log delta: matrix switch command sent
    recent_logs = (await _get_sim_log(sim))[log_cursor:]
    assert any("switch" in str(e.get("command", "")).lower() or str(e.get("command", "")).startswith("s ") for e in recent_logs)


@pytest.mark.asyncio
async def test_live_route_one_output_exact_replay(live_stack, flic_client):
    """Generated switch_output: POST /api/output/{out}/source with {"input": n}."""
    sim, _ = live_stack
    await _reset_sim(sim)
    log_cursor = len(await _get_sim_log(sim))

    result = await flic_client.perform(act("route", input=2, output=3))
    assert result.status == 200
    assert result.ok is True
    assert result.requests[0]["path"] == "/api/output/3/source"
    assert result.requests[0]["body"] == {"input": 2}

    state = await _get_sim_state(sim)
    assert state["outputs"][2]["source"] == 2

    recent_logs = (await _get_sim_log(sim))[log_cursor:]
    assert any("switch" in str(e.get("command", "")).lower() or str(e.get("command", "")).startswith("s ") for e in recent_logs)


@pytest.mark.asyncio
async def test_live_preset_recall_exact_replay(live_stack, flic_client):
    """Generated hardware preset: POST /api/preset/{n} with absent body."""
    sim, _ = live_stack
    await _reset_sim(sim)
    log_cursor = len(await _get_sim_log(sim))

    result = await flic_client.perform(act("preset_recall", preset=1))
    assert result.status == 200
    assert result.ok is True
    assert result.requests[0]["path"] == "/api/preset/1"
    assert result.requests[0]["body"] is None

    recent_logs = (await _get_sim_log(sim))[log_cursor:]
    assert any("preset" in str(e.get("command", "")).lower() or str(e.get("command", "")).startswith("r ") for e in recent_logs)


@pytest.mark.asyncio
async def test_live_cycle_input_exact_replay(live_stack, flic_client):
    """Generated cycle: POST /api/input/{next|previous}?output={out}."""
    sim, _ = live_stack
    await _reset_sim(sim)

    # Route output 1 to input 2 first
    await flic_client.perform(act("route", input=2, output=1))
    assert (await _get_sim_state(sim))["outputs"][0]["source"] == 2

    # Cycle next
    res_next = await flic_client.perform(act("cycle_input", cycle_dir="next", output=1))
    assert res_next.status == 200
    assert (await _get_sim_state(sim))["outputs"][0]["source"] == 3

    # Cycle previous
    res_prev = await flic_client.perform(act("cycle_input", cycle_dir="previous", output=1))
    assert res_prev.status == 200
    assert (await _get_sim_state(sim))["outputs"][0]["source"] == 2


@pytest.mark.asyncio
async def test_live_matrix_power_exact_replay(live_stack, flic_client):
    """Generated power: POST /api/power/on and /api/power/off."""
    sim, _ = live_stack
    await _reset_sim(sim)

    # Power off (standby)
    res_off = await flic_client.perform(act("matrix_power", on=False))
    assert res_off.status == 200
    assert (await _get_sim_state(sim))["system"]["power"] == 0

    # Power on
    res_on = await flic_client.perform(act("matrix_power", on=True))
    assert res_on.status == 200
    assert (await _get_sim_state(sim))["system"]["power"] == 1


@pytest.mark.asyncio
async def test_live_cec_and_refusal(live_stack, flic_client):
    """Generated CEC commands and refusal for unsupported combinations."""
    _, _ = live_stack

    # Valid CEC output volume
    res_vol = await flic_client.perform(act("volume_control", vol_dir="volume_up", output=1))
    assert res_vol.status == 200

    # Valid CEC output power_on
    res_cec = await flic_client.perform(act("cec_output", output=1, command="power_on"))
    assert res_cec.status == 200

    # Refusal: input device does not support volume_up or mute
    assert flic_client.supports(act("cec_input", input=1, command="volume_up")) is False
    with pytest.raises(NotSupportedError, match="cannot perform 'cec_input'"):
        await flic_client.perform(act("cec_input", input=1, command="volume_up"))


@pytest.mark.asyncio
async def test_live_flic_registration_persisted(live_stack, flic_client):
    """SDK startup button registration: POST /api/integrations/flic/register."""
    _, hub = live_stack
    buttons = [
        {"name": "Theater Remote Flic", "bdaddr": "90:88:a9:5b:10:99", "serial": "SN-THEATER-01"}
    ]
    res = await flic_client.perform(act("flic_register", buttons=buttons))
    assert res.status == 200
    assert res.ok is True

    # Verify buttons are retrievable via GET /api/integrations/flic/buttons
    async with aiohttp.ClientSession(base_url=hub.base_url) as session:
        async with session.get("/api/integrations/flic/buttons") as r:
            assert r.status == 200
            data = await r.json()
            persisted = data.get("data", {}).get("buttons", [])
            assert any(b["bdaddr"] == "90:88:a9:5b:10:99" for b in persisted)


@pytest.mark.asyncio
async def test_live_sdk_gesture_matching_and_rejection(live_stack, flic_client):
    """Live gesture replay: matching event triggers 1 action, non-matching triggers 0."""
    sim, _ = live_stack
    await _reset_sim(sim)

    # Route output 1 to input 1 initially
    await flic_client.perform(act("route", input=1, output=1))
    assert (await _get_sim_state(sim))["outputs"][0]["source"] == 1

    button_reg = {
        "90:88:a9:5b:10:01": {"name": "Lounge Flic", "bdaddr": "90:88:a9:5b:10:01"}
    }

    # 1. Matching Single Click on Lounge Flic -> routes output 1 to input 6
    act_match = act(
        "flic_sdk_event",
        button_identifier="Lounge Flic",
        gesture="single",
        target_type="switch_output",
        output_num=1,
        input_num=6,
        event={"eventName": "buttonSingleOrDoubleClickOrHold", "bdaddr": "90:88:a9:5b:10:01", "is_single_click": True},
        button_registry=button_reg,
    )
    res_match = await flic_client.perform(act_match)
    assert res_match.ok is True
    assert res_match.status == 200
    assert len(res_match.requests) == 1
    assert (await _get_sim_state(sim))["outputs"][0]["source"] == 6

    # 2. Non-matching Double Click on Lounge Flic -> 0 requests triggered
    act_mismatch_gesture = act(
        "flic_sdk_event",
        button_identifier="Lounge Flic",
        gesture="single",
        target_type="switch_output",
        output_num=1,
        input_num=2,
        event={"eventName": "buttonSingleOrDoubleClickOrHold", "bdaddr": "90:88:a9:5b:10:01", "is_double_click": True},
        button_registry=button_reg,
    )
    res_mismatch = await flic_client.perform(act_mismatch_gesture)
    assert res_mismatch.ok is True
    assert len(res_mismatch.requests) == 0
    # Simulator output 1 source MUST STILL be 6
    assert (await _get_sim_state(sim))["outputs"][0]["source"] == 6

    # 3. Non-matching Button Identifier -> 0 requests triggered
    act_wrong_btn = act(
        "flic_sdk_event",
        button_identifier="Lounge Flic",
        gesture="single",
        target_type="switch_output",
        output_num=1,
        input_num=2,
        event={"eventName": "buttonSingleOrDoubleClickOrHold", "bdaddr": "11:22:33:44:55:66", "is_single_click": True},
        button_registry=button_reg,
    )
    res_wrong_btn = await flic_client.perform(act_wrong_btn)
    assert res_wrong_btn.ok is True
    assert len(res_wrong_btn.requests) == 0
    assert (await _get_sim_state(sim))["outputs"][0]["source"] == 6


@pytest.mark.asyncio
async def test_live_keyed_mode_auth_and_redaction(live_stack, flic_client):
    """Keyed mode: assert 401 on keyless/wrong key, 200 on header/query keys, and redact keys."""
    sim, hub = live_stack
    await _reset_sim(sim)

    # 1. Enable control lock via REST API POST /api/auth/pin
    async with aiohttp.ClientSession(base_url=hub.base_url) as session:
        async with session.post("/api/auth/pin", json={"level": "control", "pin": "5555"}) as r:
            assert r.status == 200

    try:
        # A. Keyless request under keyed mode: must fail with 401
        res_keyless = await flic_client.perform(act("route", input=3, output=1))
        assert res_keyless.status == 401
        assert res_keyless.ok is False
        assert "Control unlock or API key required" in str(res_keyless.body)

        # B. Wrong API key in query: must fail with 401, key redacted
        res_wrong = await flic_client.perform(
            act("route", input=3, output=1, api_key="wrong-key-999", auth_mode="query")
        )
        assert res_wrong.status == 401
        assert res_wrong.requests[0]["path"] == "/api/output/1/source?key=***REDACTED***"
        assert "wrong-key-999" not in str(res_wrong.requests[0])

        # C. Valid API key in header (X-API-Key): succeeds with 200, key redacted
        res_header = await flic_client.perform(
            act("route", input=3, output=1, api_key=SHARED_API_KEY, auth_mode="header")
        )
        assert res_header.status == 200
        assert res_header.ok is True
        assert res_header.requests[0]["headers"]["X-API-Key"] == "***REDACTED***"
        assert SHARED_API_KEY not in str(res_header.requests[0])
        assert (await _get_sim_state(sim))["outputs"][0]["source"] == 3

        # D. Valid API key in query (?key=): succeeds with 200, key redacted
        res_query = await flic_client.perform(
            act("route", input=4, output=1, api_key=SHARED_API_KEY, auth_mode="query")
        )
        assert res_query.status == 200
        assert res_query.ok is True
        assert res_query.requests[0]["path"] == "/api/output/1/source?key=***REDACTED***"
        assert SHARED_API_KEY not in str(res_query.requests[0])
        assert (await _get_sim_state(sim))["outputs"][0]["source"] == 4

        # E. Valid API key in query with cycle action (&key=): succeeds with 200
        res_cycle = await flic_client.perform(
            act("cycle_input", cycle_dir="next", output=1, api_key=SHARED_API_KEY, auth_mode="query")
        )
        assert res_cycle.status == 200
        assert res_cycle.requests[0]["path"] == "/api/input/next?output=1&key=***REDACTED***"
        assert SHARED_API_KEY not in str(res_cycle.requests[0])
        assert (await _get_sim_state(sim))["outputs"][0]["source"] == 5

    finally:
        # Clear control PIN
        async with aiohttp.ClientSession(base_url=hub.base_url) as session:
            await session.post("/api/auth/pin", json={"level": "control", "pin": None})


@pytest.mark.asyncio
async def test_live_profile_pin_refusal_and_manual_passcode(live_stack, flic_client):
    """Drawer generated profile recall cannot supply PIN: assert refusal (403), distinct from manual passcode."""
    sim, hub = live_stack
    await _reset_sim(sim)

    # 1. Create a password-protected profile
    profile_payload = {
        "id": "protected_lounge",
        "name": "Protected Lounge",
        "passcode": "7788",
        "outputs": {"1": {"input": 7}},
    }
    profile_id = "protected_lounge"
    async with aiohttp.ClientSession(base_url=hub.base_url) as session:
        async with session.post("/api/profile", json=profile_payload) as r:
            assert r.status == 200

    try:
        # 2. Drawer generated request: POST /api/profile/{profile_id}/recall (absent body)
        res_drawer = await flic_client.perform(act("profile_recall", profile_id=profile_id))
        assert res_drawer.status == 403
        assert res_drawer.ok is False
        assert "passcode" in str(res_drawer.body).lower() or "protected" in str(res_drawer.body).lower()

        # Assert simulator output 1 was NOT switched to 7
        assert (await _get_sim_state(sim))["outputs"][0]["source"] != 7

        # 3. Explicit manual passcode variant: distinct label and redacted passcode
        res_manual = await flic_client.perform(
            act("profile_recall", profile_id=profile_id, manual_passcode="7788")
        )
        assert res_manual.status == 200
        assert res_manual.ok is True
        assert res_manual.requests[0]["metadata"]["request_type"] == "manual_passcode"
        assert res_manual.requests[0]["body"]["passcode"] == "***REDACTED***"
        assert "7788" not in str(res_manual.requests[0])

        # Simulator state updated to input 7
        assert (await _get_sim_state(sim))["outputs"][0]["source"] == 7

    finally:
        async with aiohttp.ClientSession(base_url=hub.base_url) as session:
            await session.delete(f"/api/profile/{profile_id}", headers={"X-Passcode": "7788"})
