"""BE-37/BE-38: a Telnet CEC command whose outcome is unknown is not resent over HTTP,
except power on/off (``orei_matrix.CEC_SAFE_TO_RESEND``), which set a state.

The real ``OreiMatrix`` + ``TelnetClient`` against the simulator, with
``OREI_USE_TELNET_CEC`` on. The simulator runs a Telnet command before it
applies a reply fault, so after an interrupted or missing acknowledgement the
matrix may already have run the command; a second (HTTP) frame would run a
volume step twice.
"""

import pytest

import telnet_client
from device_codes import CEC_INPUT_COMMANDS, CEC_OUTPUT_COMMANDS


def _commands(simulator, channel):
    return [e["command"] for e in simulator.log if e["channel"] == channel]


@pytest.fixture
async def telnet_cec(matrix_with_telnet, monkeypatch):
    m = matrix_with_telnet
    assert await m.connect()
    assert m.telnet_connected
    monkeypatch.setattr(m, "_use_telnet_cec", True)
    return m


@pytest.mark.parametrize(
    ("is_output", "telnet_cmd"),
    [(False, "s cec in 8 vol+"), (True, "s cec hdmi out 8 vol+")],
)
@pytest.mark.parametrize("fault", ["telnet_close_mid_command", "telnet_silent"])
async def test_unknown_outcome_fails_without_http_resend(telnet_cec, simulator, is_output, telnet_cmd, fault):
    simulator.state.inputs[7].cec_enabled = 1
    simulator.state.outputs[7].cec_enabled = 1
    await telnet_cec.ensure_cec_enabled(8, is_output)  # warm the CEC flags first
    simulator.faults.update({fault: True, "telnet_fault_count": 1})
    start = len(simulator.log)

    assert await telnet_cec.send_cec("VOLUME_UP", 8, is_output=is_output) is False

    new = list(simulator.log)[start:]
    assert [e["command"] for e in new if e["channel"] == "telnet"] == [telnet_cmd]
    assert "cec command" not in [e["command"] for e in new if e["channel"] != "telnet"]
    assert "outcome unknown" in (telnet_cec._last_error or "")


async def test_rejected_command_still_falls_back_to_http(telnet_cec, simulator, monkeypatch):
    """E00 means the matrix did not run it, so the HTTP frame is the only one that runs."""
    monkeypatch.setitem(telnet_cec._CEC_NAME_TO_TELNET, "VOLUME_UP", "bogus")
    start = len(simulator.log)
    assert await telnet_cec.send_cec("VOLUME_UP", 1, is_output=True) is True
    new = list(simulator.log)[start:]
    assert "s cec hdmi out 1 bogus" in [e["command"] for e in new if e["channel"] == "telnet"]
    assert [e["command"] for e in new if e["command"] == "cec command"] == ["cec command"]


async def test_acknowledged_command_is_sent_once(telnet_cec, simulator):
    start = len(simulator.log)
    assert await telnet_cec.send_cec("VOLUME_UP", 1, is_output=True) is True
    new = list(simulator.log)[start:]
    assert [e["command"] for e in new if e["channel"] == "telnet"] == ["s cec hdmi out 1 vol+"]
    assert "cec command" not in [e["command"] for e in new]


async def test_send_cec_outcomes(telnet_cec, simulator):
    """The Telnet client tells unknown (written, answer lost) from not sent and rejected."""
    t = telnet_cec._telnet
    assert await t.send_cec("output", 1, "on") is telnet_client.CecOutcome.ACKNOWLEDGED
    assert await t.send_cec("input", 1, "bogus") is telnet_client.CecOutcome.REJECTED
    assert await t.send_cec("input", 9, "on") is telnet_client.CecOutcome.NOT_SENT
    simulator.faults.update({"telnet_close_mid_command": True, "telnet_fault_count": 1})
    assert await t.send_cec("output", 1, "vol+") is telnet_client.CecOutcome.UNKNOWN
    assert not t.connected  # the cut connection is detected (BE-29)
    assert await t.send_cec("output", 1, "vol+") is telnet_client.CecOutcome.NOT_SENT


# ----------------------------------------------------------------------------- BE-38

_ALL = [(False, n) for n in CEC_INPUT_COMMANDS] + [(True, n) for n in CEC_OUTPUT_COMMANDS]


def test_the_resend_safe_set_is_power_on_and_off_only():
    import orei_matrix

    assert orei_matrix.CEC_SAFE_TO_RESEND == frozenset({"POWER_ON", "POWER_OFF"})


@pytest.mark.parametrize(("is_output", "name"), _ALL, ids=[f"{'out' if o else 'in'}-{n}" for o, n in _ALL])
async def test_http_fallback_after_an_unknown_outcome_only_for_power(telnet_cec, simulator, is_output, name):
    """BE-38: power on/off are resent over HTTP after a lost Telnet answer; every other command is not."""
    simulator.state.inputs[7].cec_enabled = 1
    simulator.state.outputs[7].cec_enabled = 1
    await telnet_cec.ensure_cec_enabled(8, is_output)
    simulator.faults.update({"telnet_close_mid_command": True, "telnet_fault_count": 1})
    start = len(simulator.log)

    ok = await telnet_cec.send_cec(name, 8, is_output=is_output)

    new = list(simulator.log)[start:]
    telnet = [e["command"] for e in new if e["channel"] == "telnet" and e["command"].startswith("s cec")]
    http = [e for e in new if e["channel"] != "telnet" and e["command"] == "cec command"]
    assert len(telnet) == 1  # the Telnet frame whose answer was cut
    if name in ("POWER_ON", "POWER_OFF"):
        assert ok is True
        assert len(http) == 1 and http[0]["payload"]["port"] == [0] * 7 + [1]
    else:
        assert ok is False
        assert http == []
