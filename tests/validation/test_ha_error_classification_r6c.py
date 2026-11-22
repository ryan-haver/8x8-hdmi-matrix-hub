"""R6C validation tests: error classification for Home Assistant negative responses.

Proves that legitimate application-level negative responses (such as HA service validation
errors mapping to HTTP 400) are distinguished from transport/replay failures.

Invariants verified:
1. Valid captured HA 400 negative response satisfies Response(400) without generic transport guard failure.
2. Unexpected status (e.g. 500 when 400 expected) or unhandled application errors fail.
3. Errors without an explicit negative Response expectation fail.
4. Transport failures always fail.
5. Flic replay errors (e.g. Node missing) fail even if a status code happens to match.
6. HomeAssistantClient._service classifies completed WS error responses with valid error_kind.
"""

from __future__ import annotations

import asyncio
from typing import Any
from unittest.mock import AsyncMock

import pytest

from rest_api.app import create_rest_app
from tools.validate.clients.base import ActionResult, Client, HubInfo
from tools.validate.clients.ha import HomeAssistantClient
from tools.validate.device import SimDevice
from tools.validate.model import DeviceUnchanged, NoCommand, Response, Scenario, act
from tools.validate.runner import Runner, RunOptions
from tools.validate.stack import SimulatorProcess

CAPTURED_HA_ERROR = {
    "code": "service_validation_error",
    "message": (
        "Validation error: Displays (outputs) do not accept the CEC command play. "
        "Allowed: power_on, power_off, mute, volume_down, volume_up, active"
    ),
    "translation_key": "cec_command_not_for_outputs",
    "translation_placeholders": {
        "command": "play",
        "allowed": "power_on, power_off, mute, volume_down, volume_up, active",
    },
    "translation_domain": "hdmi_matrix",
}

CAPTURED_HA_WS_RESPONSE = {
    "id": 1,
    "type": "result",
    "success": False,
    "error": CAPTURED_HA_ERROR,
}


class StubbedClient(Client):
    """Client for testing runner error classification without starting Docker containers."""

    name = "ha"
    hub_mode = "api"
    observes = True
    intents = frozenset({"ha_service", "flic_sdk_event"})

    def __init__(self, action_result: ActionResult) -> None:
        super().__init__()
        self._action_result = action_result

    async def start(self, hub: HubInfo) -> None:
        pass

    async def perform(self, action: Any) -> ActionResult:
        return self._action_result

    async def stop(self) -> None:
        pass


@pytest.fixture
async def runner_context(tmp_path, aiohttp_server):
    """Real REST server + simulator harness for Runner._run_one."""
    server = await aiohttp_server(create_rest_app())
    sim = SimulatorProcess(log_dir=tmp_path / "sim")
    await asyncio.to_thread(sim.start)
    hub_url = str(server.make_url("/")).rstrip("/")
    async with SimDevice(sim.control_url) as dev:
        runner = Runner(RunOptions(
            clients=("ha",),
            out_dir=tmp_path / "proof",
            hub_url=hub_url,
            sim_control_url=sim.control_url,
        ))
        runner.hub = runner._hardware_hub("api")
        runner.device = dev
        try:
            yield runner, dev, hub_url
        finally:
            await asyncio.to_thread(sim.stop)


def _make_ha_cec_scenario(*, expect_response: bool = True, expected_status: int | tuple[int, ...] = 400) -> Scenario:
    expectations: list[Any] = [NoCommand("*"), DeviceUnchanged()]
    if expect_response:
        expectations.insert(0, Response(status=expected_status))
    return Scenario(
        id="ha.service_cec_invalid",
        title="Home Assistant: a source-only CEC command sent to a display is rejected",
        kind="failure",
        features=("F-HA-012",),
        clients=("ha",),
        action=act(
            "ha_service",
            domain="hdmi_matrix",
            service="send_cec_command",
            data={"port_type": "output", "port_num": 1, "command": "play"},
        ),
        expect=tuple(expectations),
        covers=("tools/validate/clients/ha.py", "tools/validate/runner.py"),
    )


# ---------------------------------------------------------------------------
# Reproduction & Verification Tests
# ---------------------------------------------------------------------------

async def test_reproduce_captured_ha_400_rejected_by_generic_guard(runner_context):
    """Deterministic reproduction: on base59aa, captured HA 400 fails the transport guard.

    With the proposed fix, this must pass with zero failed checks and gate 'ok'.
    """
    runner, dev, _ = runner_context
    error_msg = f"{CAPTURED_HA_ERROR['code']}: {CAPTURED_HA_ERROR['message']}"

    # Build ActionResult mirroring exact HA client behavior on base59aa
    action_result = ActionResult(
        intent="ha_service",
        ok=False,
        status=400,
        error=error_msg,
        requests=[{
            "method": "call_service",
            "path": "hdmi_matrix.send_cec_command",
            "body": {"port_type": "output", "port_num": 1, "command": "play"},
            "status": 400,
            "response": {"success": False, "error": CAPTURED_HA_ERROR},
            "via": "home assistant websocket api",
            "elapsed_ms": 1.8,
        }],
        steps=[f"call_service hdmi_matrix.send_cec_command -> {error_msg}"],
        body={"home_assistant": "2026.9.3", "entry_id": "test_entry"},
    )
    # If error_kind exists on ActionResult, set it to "application"
    if hasattr(action_result, "error_kind"):
        action_result.error_kind = "application"

    client = StubbedClient(action_result)
    scenario = _make_ha_cec_scenario(expected_status=400)

    outcome = await runner._run_one(scenario, client)

    # On base59aa (unfixed), outcome.status is 'fail' because the guard adds FAIL.
    # After the approved fix, outcome.status must be 'pass'.
    assert outcome.status == "pass", f"Failed checks: {outcome.failed_checks}"
    assert outcome.gate == "ok"
    assert outcome.failed_checks == []


async def test_reproduce_captured_ha_500_matrix_unreachable_rejected_by_generic_guard(runner_context):
    """Deterministic reproduction for second case: HA matrix_unreachable expected 500.

    When HA returns home_assistant_error (status 500) and scenario explicitly expects
    Response(500), generic guard on base59aa rejected it. Approved fix accepts it.
    """
    runner, dev, _ = runner_context
    error_msg = "home_assistant_error: Failed to call service switch/turn_on: matrix unreachable"
    action_result = ActionResult(
        intent="output_mute",
        ok=False,
        status=500,
        error=error_msg,
        requests=[{
            "method": "call_service",
            "path": "switch.turn_on",
            "body": {"entity_id": "switch.output_1_mute"},
            "status": 500,
            "response": {"success": False, "error": {"code": "home_assistant_error", "message": "matrix unreachable"}},
            "via": "home assistant websocket api",
            "elapsed_ms": 2.5,
        }],
        steps=[f"call_service switch.turn_on -> {error_msg}"],
        body={"home_assistant": "2026.9.3", "entry_id": "test_entry"},
    )
    if hasattr(action_result, "error_kind"):
        action_result.error_kind = "application"

    client = StubbedClient(action_result)
    scenario = Scenario(
        id="ha.matrix_unreachable",
        title="Home Assistant: matrix unreachable",
        kind="failure",
        features=("F-HA-013",),
        clients=("ha",),
        action=act("output_mute", output=1, muted=True),
        expect=(Response(status=500), NoCommand("*"), DeviceUnchanged()),
        covers=("tools/validate/clients/ha.py", "tools/validate/runner.py"),
    )

    outcome = await runner._run_one(scenario, client)
    assert outcome.status == "pass", f"Failed checks: {outcome.failed_checks}"
    assert outcome.gate == "ok"
    assert outcome.failed_checks == []


async def test_unexpected_500_application_status_still_fails(runner_context):
    """If HA returns 500 when 400 was expected, the run must fail."""
    runner, dev, _ = runner_context
    action_result = ActionResult(
        intent="ha_service",
        ok=False,
        status=500,
        error="home_assistant_error: Internal server error",
        requests=[{
            "method": "call_service",
            "path": "hdmi_matrix.send_cec_command",
            "body": {},
            "status": 500,
            "response": {"success": False, "error": {"code": "home_assistant_error", "message": "Internal error"}},
            "via": "home assistant websocket api",
            "elapsed_ms": 2.0,
        }],
        body={"home_assistant": "2026.9.3", "entry_id": "test_entry"},
    )
    if hasattr(action_result, "error_kind"):
        action_result.error_kind = "application"

    client = StubbedClient(action_result)
    scenario = _make_ha_cec_scenario(expected_status=400)

    outcome = await runner._run_one(scenario, client)
    assert outcome.status == "fail"
    assert outcome.gate == "regression"


async def test_malformed_response_fails_guard(runner_context):
    """If the response is missing or malformed, the run must fail."""
    runner, dev, _ = runner_context
    action_result = ActionResult(
        intent="ha_service",
        ok=False,
        status=400,
        error="service_validation_error: invalid",
        requests=[],  # empty requests = malformed exchange
        body=None,
    )
    if hasattr(action_result, "error_kind"):
        action_result.error_kind = "application"

    client = StubbedClient(action_result)
    scenario = _make_ha_cec_scenario(expected_status=400)

    outcome = await runner._run_one(scenario, client)
    assert outcome.status == "fail"
    assert any("replay or transport error" in c["description"] for c in outcome.failed_checks)


async def test_error_without_response_expectation_fails(runner_context):
    """An application error must fail if the scenario did NOT expect a negative Response."""
    runner, dev, _ = runner_context
    action_result = ActionResult(
        intent="ha_service",
        ok=False,
        status=400,
        error="service_validation_error: unexpected",
        requests=[{
            "method": "call_service",
            "path": "hdmi_matrix.send_cec_command",
            "status": 400,
            "response": {"success": False, "error": {"code": "service_validation_error"}},
        }],
    )
    if hasattr(action_result, "error_kind"):
        action_result.error_kind = "application"

    client = StubbedClient(action_result)
    # Scenario has NoCommand and DeviceUnchanged, but NO Response expectation
    scenario = _make_ha_cec_scenario(expect_response=False)

    outcome = await runner._run_one(scenario, client)
    assert outcome.status == "fail"
    assert any("replay or transport error" in c["description"] for c in outcome.failed_checks)


async def test_actual_transport_failure_always_fails(runner_context):
    """Actual transport / timeout errors must always fail."""
    runner, dev, _ = runner_context
    action_result = ActionResult(
        intent="ha_service",
        ok=False,
        status=None,
        error="Cannot connect to host 127.0.0.1:8123: [Errno 111] Connection refused",
        requests=[],
    )
    if hasattr(action_result, "error_kind"):
        action_result.error_kind = "transport"

    client = StubbedClient(action_result)
    scenario = _make_ha_cec_scenario(expected_status=400)

    outcome = await runner._run_one(scenario, client)
    assert outcome.status == "fail"
    assert any("replay or transport error" in c["description"] for c in outcome.failed_checks)


@pytest.mark.parametrize("status_code", [200, 400])
async def test_flic_replay_error_still_fails_even_if_status_matches(runner_context, status_code):
    """A Flic replay error (missing Node) must fail even if status happens to match."""
    runner, dev, _ = runner_context
    action_result = ActionResult(
        intent="flic_sdk_event",
        ok=False,
        status=status_code,
        error="Flic replay requires Node.js; executable not found",
        requests=[],
    )
    if hasattr(action_result, "error_kind"):
        action_result.error_kind = "replay"

    client = StubbedClient(action_result)
    client.name = "flic"
    scenario = _make_ha_cec_scenario(expected_status=status_code)

    outcome = await runner._run_one(scenario, client)
    assert outcome.status == "fail"
    assert any("replay or transport error" in c["description"] for c in outcome.failed_checks)


# ---------------------------------------------------------------------------
# HomeAssistantClient._service classification tests
# ---------------------------------------------------------------------------

async def test_ha_client_service_classifies_application_error():
    """HomeAssistantClient._service correctly classifies WS service errors."""
    ha_client = HomeAssistantClient()
    ha_client._ws_message = AsyncMock(return_value=CAPTURED_HA_WS_RESPONSE)

    result = ActionResult(intent="ha_service", ok=False)
    await ha_client._service(
        "hdmi_matrix",
        "send_cec_command",
        {"port_type": "output", "port_num": 1, "command": "play"},
        result,
    )

    assert result.status == 400
    assert result.ok is False
    assert result.error == f"{CAPTURED_HA_ERROR['code']}: {CAPTURED_HA_ERROR['message']}"
    assert len(result.requests) == 1
    assert result.requests[0]["status"] == 400
    assert result.requests[0]["response"]["success"] is False
    assert result.error_kind == "application"


async def test_client_filtered_negative_response_fails_for_other_client(runner_context):
    """If negative Response is filtered to a different client (e.g. api), ha client must fail."""
    runner, dev, _ = runner_context
    action_result = ActionResult(
        intent="ha_service",
        ok=False,
        status=400,
        error=f"{CAPTURED_HA_ERROR['code']}: {CAPTURED_HA_ERROR['message']}",
        error_kind="application",
        requests=[{
            "method": "call_service",
            "path": "hdmi_matrix.send_cec_command",
            "status": 400,
            "response": {"success": False, "error": CAPTURED_HA_ERROR},
        }],
    )
    client = StubbedClient(action_result)
    # Scenario has Response(400) ONLY for client "api"
    scenario = Scenario(
        id="ha.service_cec_invalid_filtered",
        title="Filtered response",
        kind="failure",
        features=("F-HA-012",),
        clients=("ha",),
        action=act("ha_service", domain="hdmi_matrix", service="send_cec_command"),
        expect=(Response(status=400, clients=("api",)), NoCommand("*"), DeviceUnchanged()),
        covers=("tools/validate/runner.py",),
    )

    outcome = await runner._run_one(scenario, client)
    assert outcome.status == "fail"
    assert any("replay or transport error" in c["description"] for c in outcome.failed_checks)


async def test_unknown_ws_error_code_not_classified_as_application(runner_context):
    """Unknown WS error codes fall back to 500 and are NOT classified as application errors."""
    ha_client = HomeAssistantClient()
    unknown_error = {"code": "unknown_custom_crash", "message": "Boom"}
    ha_client._ws_message = AsyncMock(return_value={
        "id": 1, "type": "result", "success": False, "error": unknown_error,
    })

    result = ActionResult(intent="ha_service", ok=False)
    await ha_client._service("hdmi_matrix", "send_cec_command", {}, result)

    assert result.status == 500
    assert result.ok is False
    assert result.error_kind is None  # Must NOT be classified as application!

    # When evaluated by runner against a scenario expecting 500, it still fails because error_kind != application
    runner, dev, _ = runner_context
    client = StubbedClient(result)
    scenario = Scenario(
        id="ha.matrix_unreachable",
        title="Home Assistant: matrix unreachable",
        kind="failure",
        features=("F-HA-013",),
        clients=("ha",),
        action=act("output_mute", output=1, muted=True),
        expect=(Response(status=500), NoCommand("*"), DeviceUnchanged()),
        covers=("tools/validate/clients/ha.py", "tools/validate/runner.py"),
    )
    outcome = await runner._run_one(scenario, client)
    assert outcome.status == "fail"
    assert any("replay or transport error" in c["description"] for c in outcome.failed_checks)
