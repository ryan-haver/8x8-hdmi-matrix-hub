"""HIL capture tool, probe mode, against the simulator."""

from __future__ import annotations

import asyncio

from tests.hil_tools.helpers import FW, ScriptedConsole, load, make_opts, new_sim
from tools.hil.capture import cli, run_capture
from tools.hil.capture.fixtures import RecordIds
from tools.simulator import protocol as proto


async def test_probe_mode_answers_login_session_and_telnet_questions(tmp_path):
    """One full probe run: wrong password, session mechanism and idle expiry,
    Telnet error codes and framing, no-op acks, two sessions, and a push window
    during which the "operator" plugs a cable and changes routing on the panel."""
    async with new_sim(session_ttl_s=0.4) as s:
        initial_routing = s.state.routing
        loop = asyncio.get_running_loop()

        async def operator_at_the_matrix() -> None:
            await asyncio.sleep(0.1)
            await s.cable_event("output", 3, True)
            s.state.outputs[7].source = 5  # front-panel routing change (no push in the simulator)
            await asyncio.sleep(0.1)
            await s.cable_event("output", 3, False)

        def on_ask(prompt: str) -> str | None:
            if "start the window" in prompt:
                loop.create_task(operator_at_the_matrix())
                return ""
            if "Restore it?" in prompt:
                return "y"
            return None

        console = ScriptedConsole(on_ask=on_ask)
        opts = make_opts(s, tmp_path / "{firmware}", mode="probe", idle_waits=[0.1, 0.6], push_seconds=0.5,
                         telnet_timeout=0.5, yes=False)
        code, cap = await run_capture(opts, console)
        assert code == cli.EXIT_OK, (cap.errors, console.text)
        # The routing the operator changed during the window was restored.
        assert s.state.routing == initial_routing
        # Only the deliberately unknown commands went unrecognised.
        assert {e["command"] for e in s.unrecognised()} == {"hil capture unknown", None, "hilcapture unknown"}

    root = tmp_path / FW
    no_session = load(root, RecordIds.PROBE_NO_SESSION)
    assert no_session["findings"]["classification"] == "json"

    wrong = load(root, RecordIds.PROBE_WRONG_PASSWORD)["findings"]
    assert wrong["result"] == proto.LOGIN_FAIL_RESULT and wrong["echoes_comhead"] is True
    # The simulator ends the IP's session on a failed login.
    assert wrong["main_session_after_wrong_login"] == "json"

    assert load(root, RecordIds.PROBE_SESSION_MECHANISM)["findings"]["mechanism"] == "ip"

    idle = load(root, RecordIds.PROBE_IDLE_EXPIRY)
    assert idle["findings"]["alive_after_s"] == 0.1 and idle["findings"]["expired_after_s"] == 0.6
    assert idle["steps"][-1]["relogin_works"] is True

    unknown = load(root, RecordIds.PROBE_UNKNOWN_COMHEAD)["findings"]
    assert unknown["json"] == {"comhead": "hil capture unknown", "result": proto.UNKNOWN_COMMAND_RESULT}
    assert load(root, RecordIds.PROBE_GARBAGE_BODY)["findings"]["json"] == {"comhead": None, "result": 0}

    cec = load(root, RecordIds.PROBE_CEC_SHAPES)["findings"]
    assert cec["state_changed"] is False and cec["single_result"] == proto.RESULT_OK

    errors = load(root, RecordIds.PROBE_TELNET_ERRORS)["findings"]
    assert errors["by_command"]["hilcapture unknown"]["error_code"] == proto.TELNET_ERR_UNKNOWN
    assert errors["by_command"]["r link in 9"]["error_code"] == proto.TELNET_ERR_PARAM
    assert errors["state_changed"] == []

    framing = {v["variant"]: v for v in load(root, RecordIds.PROBE_TELNET_FRAMING)["variants"]}
    assert framing["no_bang_then_bang"]["first_response"] == ""  # nothing until "!" arrives
    assert framing["no_bang_then_bang"]["second_response"] == "BK-808\r\n"
    assert framing["pipelined"]["first_response"] == "BK-808\r\nfw version: V1.10.02\r\n"

    acks = load(root, RecordIds.PROBE_TELNET_NOOP_ACKS)
    assert acks["findings"]["state_changed"] == []
    assert [ex["response"]["text"] for ex in acks["exchanges"]][:2] == ["output8->input1\r\n", "beep on\r\n"]

    assert load(root, RecordIds.PROBE_TELNET_SECOND_SESSION)["findings"] == {
        "second_session_works": True, "first_session_still_works": True,
    }

    push = load(root, RecordIds.PROBE_PUSH_WINDOW)["findings"]
    assert push["lines"] == ["hdmi output 3: connect", "hdmi output 3: disconnect"]
    assert push["cable_events_parsed"] == [["output", "3", "connect"], ["output", "3", "disconnect"]]
    assert push["unrecognised_lines"] == []
    assert ["routing", 8, 1, 5] in push["state_changes"] and push["restored"] is True
    assert any("PUSH NOTIFICATION WINDOW" in line for line in console.text.splitlines())


async def test_probe_warns_when_a_session_is_already_active(tmp_path):
    """--no-auth simulator: a read without login returns data, which the probe flags."""
    async with new_sim(require_login=False) as s:
        code, cap = await run_capture(make_opts(s, tmp_path / "out", mode="probe", telnet=False),
                                      ScriptedConsole())
    assert code == cli.EXIT_OK
    assert load(tmp_path / "out", RecordIds.PROBE_NO_SESSION)["findings"]["classification"] == "data"
    assert any("no-session probe" in w for w in cap.warnings)
    assert load(tmp_path / "out", RecordIds.PROBE_SESSION_MECHANISM)["findings"]["mechanism"] == "ip-or-no-auth"
