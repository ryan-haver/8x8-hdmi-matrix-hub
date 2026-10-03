"""Unit tests: what a Telnet answer proves (BE-36 preset reads, BE-37 CEC outcomes).

``TelnetClient._send_raw`` is replaced by canned answers, so these tests pin
the classification only; the simulator tests (tests/sim/test_sim_preset_slots.py,
tests/sim/test_sim_cec_ambiguity.py) prove the effect end to end.
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from telnet_client import CecOutcome, CommandError, TelnetClient  # noqa: E402

FULL = "r preset 1!\r\n" + "".join(f"output{o}->input{o % 8 + 1}\r\n" for o in range(1, 9))


def _client(answer=None, error=None):
    client = TelnetClient("127.0.0.1", 23)

    async def send_raw(command):
        if error is not None:
            raise error
        return answer

    client._send_raw = send_raw  # type: ignore[method-assign]
    return client


@pytest.mark.asyncio
async def test_complete_preset_answer_is_a_read():
    info = await _client(FULL).get_preset_info(1)
    assert info == {"preset": 1, "routing": {o: o % 8 + 1 for o in range(1, 9)}, "saved": True}


@pytest.mark.asyncio
async def test_empty_slot_answer_is_a_read():
    info = await _client("r preset 5!\r\npreset 5 is none,please save a preset\r\n").get_preset_info(5)
    assert info == {"preset": 5, "routing": {}, "saved": False}


@pytest.mark.asyncio
@pytest.mark.parametrize("answer", [
    "",  # no answer (timeout)
    "r preset 1!\r\n",  # only the echo
    "r preset 1!\r\noutput1->input2\r\noutput2->input3\r\n",  # cut short
    "E01\r\n",  # error code
])
async def test_incomplete_preset_answer_is_not_a_read(answer):
    """BE-36: part of a slot, or nothing, must never be reported as its stored routing."""
    assert await _client(answer).get_preset_info(1) is None


@pytest.mark.asyncio
@pytest.mark.parametrize(("answer", "error", "outcome"), [
    ("s cec hdmi out 1 vol+!\r\ncec hdmi out 1 vol+\r\n", None, CecOutcome.ACKNOWLEDGED),
    ("s cec hdmi out 1 vol+!\r\nE00\r\n", None, CecOutcome.REJECTED),
    ("", None, CecOutcome.UNKNOWN),  # written, no answer
    ("s cec hdmi out 1 vol+!\r\n", None, CecOutcome.UNKNOWN),  # written, only the echo
    (None, CommandError("connection closed by the matrix (EOF)", sent=True), CecOutcome.UNKNOWN),
    (None, CommandError("Not connected", sent=False), CecOutcome.NOT_SENT),
    (None, ConnectionError("Not connected"), CecOutcome.NOT_SENT),
])
async def test_cec_outcome(answer, error, outcome):
    """BE-37: only REJECTED and NOT_SENT prove the matrix did not run the command."""
    assert await _client(answer, error).send_cec("output", 1, "vol+") is outcome
