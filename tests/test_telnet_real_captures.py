"""HIL-03: the hub's Telnet code against bytes captured from a real BK-808.

The records in ``tests/fixtures/device/BK-808_V1.10.01_web-V2.00.03/telnet``
were recorded from the owner's matrix (MCU V1.10.01, web V2.00.03) by
``python -m tools.hil.capture --mode read``. Each keeps the exact bytes and the
TCP segment boundaries (``chunks``) the device sent. These tests feed them
through the real parsing paths:

* per segment, the way ``TelnetClient._send_raw`` sees them: IAC filter, then
  ``_telnet_proto.is_response_complete`` after every read;
* a replay server that sends the captured segments with their recorded timing
  to a real ``TelnetClient`` (connect, banner, echo, ``status``, ``r link``,
  ``r preset``, ``r fw version``, ``r type``).

No test here talks to a device.
"""

from __future__ import annotations

import asyncio
import contextlib
import re
from pathlib import Path
from typing import Any

import pytest

import telnet_client
from _telnet_proto import (
    TelnetIACFilter,
    answer_lines,
    is_preset_empty,
    is_response_complete,
    needs_settle,
    preset_routing,
)
from telnet_client import TelnetClient
from tools.hil.capture.fixtures import iter_exchanges, iter_records, unb64

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "device" / "BK-808_V1.10.01_web-V2.00.03"

#: What the owner's matrix reported when it was captured (cross-checked with
#: the HTTP reads of the same session).
INPUT_CABLES = {1: False, 2: False, 3: False, 4: False, 5: False, 6: False, 7: True, 8: True}
OUTPUT_CABLES = {1: True, 2: True, 3: False, 4: False, 5: False, 6: False, 7: False, 8: False}
PRESET_1 = {1: 2, 2: 4, 3: 4, 4: 4, 5: 4, 6: 4, 7: 4, 8: 4}


def _load() -> dict[str, dict[str, Any]]:
    """record id -> the record's single Telnet exchange."""
    out: dict[str, dict[str, Any]] = {}
    for record_id, record in iter_records(FIXTURE):
        if record_id.startswith("telnet/"):
            (ex,) = list(iter_exchanges(record))
            out[record_id] = ex
    return out


CAPTURES = _load()
READS = {ex["command"]: ex for rid, ex in CAPTURES.items() if rid != "telnet/banner"}
BANNER = CAPTURES["telnet/banner"]


def body(ex: dict[str, Any]) -> bytes:
    return unb64(ex["response"]["body_b64"])


def segments(ex: dict[str, Any]) -> list[bytes]:
    """The response split at the TCP segment boundaries the capture recorded."""
    data, out, pos = body(ex), [], 0
    for chunk in ex["response"]["chunks"]:
        out.append(data[pos:pos + chunk["len"]])
        pos += chunk["len"]
    assert pos == len(data) and b"".join(out) == data
    return out


def test_the_captures_are_the_read_session():
    assert len(READS) == 27  # status, r fw version, r type, r link in/out 1-8, r preset 1-8
    assert body(BANNER).startswith(b"\xff\xfb\x03")  # IAC WILL SGA ...


# ------------------------------------------------------------------ banner


def test_banner_iac_is_filtered_and_declined_and_the_firmware_is_parsed():
    f = TelnetIACFilter()
    text, replies = b"", b""
    for seg in segments(BANNER):
        user, reply = f.feed(seg)
        text, replies = text + user, replies + reply
    assert b"\xff" not in text
    # WILL SGA is declined with DONT SGA; WONT/DONT need no answer.
    assert replies == b"\xff\xfe\x03"
    decoded = text.decode()
    assert decoded.startswith("****************welcome **************\r\n")
    match = re.search(r"fw version\s*:\s*v?([\d.]+)", decoded, re.IGNORECASE)  # TelnetClient.connect
    assert match and match.group(1) == "1.10.01"


# ------------------------------------------------- completion, segment by segment


def _complete_at(ex: dict[str, Any]) -> int | None:
    """Index of the first segment after which the client considers the answer complete."""
    f = TelnetIACFilter()
    response = ""
    for i, seg in enumerate(segments(ex)):
        user, _ = f.feed(seg)
        response += user.decode("utf-8", errors="replace")
        if is_response_complete(response, ex["command"]):
            return i
    return None


@pytest.mark.parametrize("command", sorted(READS))
def test_every_captured_read_completes_only_when_the_answer_is_there(command):
    ex = READS[command]
    n = len(segments(ex))
    at = _complete_at(ex)
    assert at is not None, f"{command!r} never completes"
    assert at >= 1, f"{command!r} completed on its echo"
    if command == "status":
        # Completes on the MAC line; only the trailing empty line comes later.
        assert b"".join(segments(ex)[at + 1:]) == b"\r\n"
    elif command == "r fw version":
        # No known last line: completes on the first of its 4 answer lines, and
        # TelnetClient._send_raw reads the rest of the burst (READ_SETTLE_S).
        assert needs_settle(command) and at == 1 and n == 5
    else:
        assert at == n - 1, f"{command!r} completed after segment {at} of {n}"


def test_preset_completion_waits_for_all_eight_lines():
    """Regression: `r preset 1` arrives as one segment per line; completing on the
    first non-echo line returned a single output's routing."""
    ex = READS["r preset 1"]
    first_line = b"".join(segments(ex)[:2]).decode()
    assert first_line == "r preset 1!\r\noutput1->input2\r\n"
    assert not is_response_complete(first_line, "r preset 1")
    assert is_response_complete(body(ex).decode(), "r preset 1")
    assert preset_routing(body(ex).decode()) == PRESET_1


# ------------------------------------------------------------------ parsing


def test_status_dump_parses_into_the_captured_state():
    text = body(READS["status"]).decode()
    status = TelnetClient("x")._parse_status_response(text)
    assert status.power is True and status.beep is True and status.panel_lock is False
    assert status.lcd_timeout == 30
    assert {p: s.connected for p, s in status.inputs.items()} == INPUT_CABLES
    assert {p: s.connected for p, s in status.outputs.items()} == OUTPUT_CABLES
    # "output 1 ext-audio->input1" lines must not be read as video routing.
    assert status.routing == dict.fromkeys(range(1, 9), 7)
    assert all(o.source == 7 for o in status.outputs.values())
    assert {o.hdcp for o in status.outputs.values()} == {"follow sink"}
    assert [status.outputs[i].stream_enabled for i in range(1, 9)] == [True, True] + [False] * 6
    assert status.outputs[1].video_mode == "pass-through" and status.outputs[2].video_mode == "audio only"
    assert {o.hdr_mode for o in status.outputs.values()} == {"pass-through"}
    assert not any(o.arc or o.audio_mute for o in status.outputs.values())
    assert {i.edid for i in status.inputs.values()} == {"frl12g_8k_hdr,7.1ch"}
    assert TelnetClient.connections_from_status(status) == {"inputs": INPUT_CABLES, "outputs": OUTPUT_CABLES}


@pytest.mark.parametrize("port", range(1, 9))
def test_link_answers_parse_and_agree_with_the_status_dump(port):
    assert TelnetClient._parse_link_response(body(READS[f"r link in {port}"]).decode(), "input", port) \
        == INPUT_CABLES[port]
    assert TelnetClient._parse_link_response(body(READS[f"r link out {port}"]).decode(), "output", port) \
        == OUTPUT_CABLES[port]


@pytest.mark.parametrize("n", range(2, 9))
def test_empty_preset_slots_are_recognised(n):
    text = body(READS[f"r preset {n}"]).decode()
    assert text == f"r preset {n}!\r\npreset {n} is none,please save a preset\r\n"
    assert is_preset_empty(text) and preset_routing(text) == {}


def test_type_answer_without_the_echo():
    assert answer_lines(body(READS["r type"]).decode(), "r type") == ["8x8 hdmi2.1 matrix"]


# --------------------------------------------------------- replay to a real client


class ReplayDevice:
    """Replays the captured segments, with their recorded timing, for each command."""

    def __init__(self) -> None:
        self.received = bytearray()
        self.server: asyncio.Server | None = None
        self.port = 0

    async def __aenter__(self) -> ReplayDevice:
        self.server = await asyncio.start_server(self._client, "127.0.0.1", 0)
        self.port = self.server.sockets[0].getsockname()[1]
        return self

    async def __aexit__(self, *exc: object) -> None:
        assert self.server is not None
        self.server.close()
        with contextlib.suppress(Exception):
            await asyncio.wait_for(self.server.wait_closed(), 2)

    @staticmethod
    async def _send(ex: dict[str, Any], writer: asyncio.StreamWriter) -> None:
        loop = asyncio.get_running_loop()
        start = loop.time()
        for seg, chunk in zip(segments(ex), ex["response"]["chunks"], strict=True):
            delay = start + chunk["t_ms"] / 1000 - loop.time()
            if delay > 0:
                await asyncio.sleep(delay)
            writer.write(seg)
            await writer.drain()

    async def _client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        try:
            await self._send(BANNER, writer)
            buf = b""
            while data := await reader.read(1024):
                self.received += data
                buf += data
                while b"!\r\n" in buf:
                    raw, buf = buf.split(b"!\r\n", 1)
                    command = raw.replace(b"\xff\xfe\x03", b"").decode().strip()
                    await self._send(READS[command], writer)
        except (ConnectionError, asyncio.CancelledError):
            pass
        finally:
            writer.close()


async def test_real_telnet_client_against_replayed_device(monkeypatch):
    monkeypatch.setattr(TelnetClient, "_schedule_reconnect", lambda self: None)
    async with ReplayDevice() as device:
        client = TelnetClient("127.0.0.1", device.port)
        assert await client.connect()
        try:
            assert client.firmware_version == "1.10.01"  # from the banner, IAC filtered
            # Back to back, so any part of one answer left unread would be
            # taken as the next command's answer.
            assert await client.get_firmware_version() == "1.10.01"
            assert await client.get_preset_info(1) == {"preset": 1, "routing": PRESET_1, "saved": True}
            assert await client.get_preset_info(2) == {"preset": 2, "routing": {}, "saved": False}
            assert await client.get_device_type() == "8x8 hdmi2.1 matrix"
            assert await client.get_all_connections() == {"inputs": INPUT_CABLES, "outputs": OUTPUT_CABLES}
            assert await client.get_input_connection(7) is True
            assert await client.get_output_connection(3) is False
            status = await client.get_full_status()
            assert status.routing == dict.fromkeys(range(1, 9), 7)
            assert await client.get_preset_info(8) == {"preset": 8, "routing": {}, "saved": False}
            assert client.connected
        finally:
            await client.disconnect()
    # The client declined the device's WILL SGA and sent every command as "<cmd>!\r\n".
    assert bytes(device.received).startswith(b"\xff\xfe\x03")
    assert b"r fw version!\r\n" in device.received and b"status!\r\n" in device.received


def test_settle_window_is_longer_than_the_device_gaps_between_lines():
    """`r fw version` lines follow each other within a few ms; READ_SETTLE_S must cover that."""
    chunks = READS["r fw version"]["response"]["chunks"]
    gaps = [(b["t_ms"] - a["t_ms"]) / 1000 for a, b in zip(chunks[1:], chunks[2:], strict=False)]
    assert max(gaps) < telnet_client.READ_SETTLE_S / 5
