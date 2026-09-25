"""
Telnet RFC 854 Protocol Helpers.

Provides filters for handling Telnet IAC (Interpret As Command) negotiation
bytes that appear during initial connection to the OREI BK-808 matrix.

:copyright: (c) 2026 by Custom Integration.
:license: Mozilla Public License Version 2.0, see LICENSE for more details.
"""

import re
from enum import Enum

# =============================================================================
# Response classification (BE-07)
#
# Checked against the probe and write captures of a BK-808 with MCU V1.10.01
# (tests/fixtures/device/BK-808_V1.10.01_web-V2.00.03/{probe,write}).
# =============================================================================

# Captured on V1.10.01: "E00" answers a command the matrix does not know
# ("hilcapture unknown", "s av 7 8", "s out 8 stream 0", an unknown CEC word).
TELNET_ERR_UNKNOWN_COMMAND = "E00"
# Captured on V1.10.01: "E01" answers a known command with a bad parameter
# ("r link in 9", "s cec in 9 on", "s output 9 in source 1", "s power 0").
TELNET_ERR_BAD_PARAMETER = "E01"
# Every error code the matrix may send ("E02" was accepted by earlier client
# code; it has never been seen).
TELNET_ERROR_CODES = frozenset({TELNET_ERR_UNKNOWN_COMMAND, TELNET_ERR_BAD_PARAMETER, "E02"})
# Confirmed on MCU V1.10.01 (read capture, tests/fixtures/device/
# BK-808_V1.10.01_web-V2.00.03/telnet): the device echoes every command line
# ("r link in 1!") before its answer, and the `status` dump ("get the unit all
# status:" and 108 more lines) ends with the MAC address line and one empty line.
STATUS_DUMP_LAST_LINE = "mac address:"
_MAC_RE = re.compile(r"mac address:\s*([0-9a-f]{2}[:-]){5}[0-9a-f]{2}", re.IGNORECASE)
# Confirmed on V1.10.01: `r link in|out N` answers "hdmi input|output N: connect|disconnect".
_LINK_RE = re.compile(r"\b(connect|disconnect)\b", re.IGNORECASE)
# Confirmed on V1.10.01: `r preset N` answers one "outputX->inputY" line per
# output (8 lines, each in its own TCP segment ~2 ms apart), or
# "preset N is none,please save a preset" for an empty slot.
_ROUTE_RE = re.compile(r"\boutput(\d+)->input(\d+)\b", re.IGNORECASE)
_PRESET_NONE_RE = re.compile(r"^preset\s+\d+\s+is\s+none\b", re.IGNORECASE)
PRESET_OUTPUTS = 8
#: Reads whose answer has no known last line (``r fw version`` sends 4 lines
#: over ~10 ms on V1.10.01). After their first answer line the client keeps
#: reading until the device has been silent this long, so the rest of the
#: answer does not leak into the next command.
READ_SETTLE_S = 0.1
# Successful set commands answer with the echo of the command line, then one
# or more acknowledgement lines and no error code. Captured on V1.10.01:
# "s output 8 in source 8" -> "output8->input8" (8 lines for output 0),
# "s beep 0" -> "beep off", "s lock 1" -> "panel button lock on",
# "power 0" -> "power off". A line identical to the command we sent is treated
# as the echo, not as the acknowledgement. CEC and preset acknowledgements are
# not captured yet.


def complete_lines(response: str) -> list[str]:
    """Non-empty lines of ``response`` that ended with a line terminator."""
    text = response.replace("\r\n", "\n").replace("\r", "\n")
    parts = text.split("\n")
    parts.pop()  # the part after the last terminator is incomplete (or "")
    return [line.strip() for line in parts if line.strip()]


def response_error(response: str) -> str | None:
    """The error code (``E00``/``E01``/...) in ``response``, or None."""
    for line in complete_lines(response):
        if line.upper() in TELNET_ERROR_CODES:
            return line.upper()
    # An error code is short; accept it even without its line terminator.
    tail = response.strip().upper()
    return tail if tail in TELNET_ERROR_CODES else None


def _norm(command: str) -> str:
    return " ".join(command.strip().lower().split())


def _is_echo(line: str, command: str) -> bool:
    return _norm(line.rstrip("!")) == _norm(command)


def answer_lines(response: str, command: str) -> list[str]:
    """The complete lines of ``response`` without the device's echo of ``command``."""
    return [line for line in complete_lines(response) if not _is_echo(line, command)]


def preset_routing(response: str) -> dict[int, int]:
    """``{output: input}`` from an ``r preset N`` answer (empty for an empty slot)."""
    routing: dict[int, int] = {}
    for line in complete_lines(response):
        for out, inp in _ROUTE_RE.findall(line):
            routing[int(out)] = int(inp)
    return routing


def is_preset_empty(response: str) -> bool:
    """True if an ``r preset N`` answer says the slot is empty."""
    return any(_PRESET_NONE_RE.match(line) for line in complete_lines(response))


def needs_settle(command: str) -> bool:
    """Whether ``command`` is a read whose answer has no known last line (see READ_SETTLE_S)."""
    cmd = _norm(command)
    return cmd.startswith("r ") and not cmd.startswith(("r link", "r preset"))


def is_response_complete(response: str, command: str) -> bool:
    """Whether ``response`` is the whole answer to ``command`` (BE-07).

    - any error code completes every command;
    - ``status`` completes on its last line (``mac address: ...``);
    - ``r link ...`` completes on its ``connect``/``disconnect`` line;
    - ``r preset N`` completes on its eighth routing line, or on the "is none"
      line of an empty slot (V1.10.01 sends the 8 lines one by one; completing
      on the first one returned a single output's routing);
    - everything else (reads and set commands alike) completes on the first
      full line that is not the echo of the command. Set commands therefore
      return as soon as the matrix acknowledges them instead of waiting the
      whole command timeout. Reads in :func:`needs_settle` then keep reading
      until the device goes quiet (``TelnetClient._send_raw``).
    """
    if not response:
        return False
    if response_error(response) is not None:
        return True

    lines = complete_lines(response)
    cmd = _norm(command)

    if cmd == "status":
        if any(line.lower().startswith(STATUS_DUMP_LAST_LINE) for line in lines):
            return True
        # Last line may arrive without a terminator: accept a full MAC.
        return _MAC_RE.search(response) is not None

    if cmd.startswith("r link"):
        return any(_LINK_RE.search(line) for line in lines)

    if cmd.startswith("r preset"):
        return is_preset_empty(response) or len(preset_routing(response)) >= PRESET_OUTPUTS

    return any(not _is_echo(line, cmd) for line in lines)


def is_acknowledged(response: str, command: str) -> bool:
    """True if a set command was acknowledged: an answer line and no error code."""
    if response_error(response) is not None:
        return False
    return any(not _is_echo(line, command) for line in complete_lines(response))


class _IACState(Enum):
    """State machine states for IAC protocol handling."""

    DATA = "data"          # Normal data, looking for IAC (0xFF)
    IAC = "iac"            # Got IAC, next byte is command
    IAC_CMD = "iac_cmd"    # Processing IAC command byte
    IAC_SB = "iac_sb"     # Inside subnegotiation (after IAC SB)
    IAC_SB_SE = "iac_sb_se"  # Got IAC SE, subnegotiation complete


# Telnet IAC command bytes
IAC = 0xFF
IAC_WILL = 0xFB
IAC_WONT = 0xFC
IAC_DO = 0xFD
IAC_DONT = 0xFE
IAC_SB = 0xFA
IAC_SE = 0xF0


class TelnetIACFilter:
    """
    Filter for handling Telnet IAC (Interpret As Command) bytes.

    Implements RFC 854 state machine:
    - Strips IAC negotiation sequences from incoming data
    - Auto-declines all IAC options (WILL → DONT, DO → WONT)
    - Escapes outgoing 0xFF bytes as 0xFF 0xFF

    :param feed(data: bytes) -> Tuple[bytes, bytes]:
        Accepts raw bytes, returns (user_data, response_bytes).
        response_bytes contains IAC auto-reply bytes to send to the server.
    """

    def __init__(self) -> None:
        self._state = _IACState.DATA
        self._sb_data: list[int] = []  # Accumulated subnegotiation data

    def feed(self, data: bytes) -> tuple[bytes, bytes]:
        """
        Process incoming bytes through the IAC filter.

        :param data: Raw bytes from Telnet connection
        :return: Tuple of (filtered_user_data, auto_reply_bytes)
            - filtered_user_data: bytes without IAC negotiation sequences
            - auto_reply_bytes: IAC replies to send back (DONT/WONT responses)
        """
        user_data_parts: list[bytes] = []
        response_parts: list[bytes] = []

        for byte in data:
            if self._state == _IACState.DATA:
                if byte == IAC:
                    self._state = _IACState.IAC
                else:
                    user_data_parts.append(bytes([byte]))

            elif self._state == _IACState.IAC:
                # After IAC, the next byte determines the command
                if byte == IAC:
                    # IAC IAC → escaped 0xFF in data (RFC 854 §3)
                    user_data_parts.append(bytes([IAC]))
                    self._state = _IACState.DATA
                elif byte == IAC_SB:
                    # Subnegotiation begin
                    self._state = _IACState.IAC_SB
                    self._sb_data = []
                elif byte == IAC_SE:
                    # Empty subnegotiation (shouldn't happen normally)
                    self._state = _IACState.DATA
                    self._sb_data = []
                elif byte in (IAC_WILL, IAC_WONT, IAC_DO, IAC_DONT):
                    # Command that needs auto-reply
                    self._cmd_byte = byte
                    self._state = _IACState.IAC_CMD
                else:
                    # Other IAC commands (DONT, WONT for already-declined, etc.)
                    # Just acknowledge and return to data state
                    self._state = _IACState.DATA

            elif self._state == _IACState.IAC_CMD:
                # Second byte of IAC command: the option byte
                option = byte
                cmd = self._cmd_byte

                # Auto-decline all options per RFC 854 §4
                if cmd == IAC_WILL:
                    # Server offers to use an option → reply DONT
                    response_parts.append(bytes([IAC, IAC_DONT, option]))
                elif cmd == IAC_DO:
                    # Server asks us to use an option → reply WONT
                    response_parts.append(bytes([IAC, IAC_WONT, option]))
                # IAC_WONT and IAC_DONT require no response

                self._state = _IACState.DATA
                self._sb_data = []

            elif self._state == _IACState.IAC_SB:
                # Inside subnegotiation, accumulate data until IAC SE
                if byte == IAC:
                    self._state = _IACState.IAC_SB_SE
                else:
                    self._sb_data.append(byte)

            elif self._state == _IACState.IAC_SB_SE:
                # After IAC within subnegotiation
                if byte == IAC_SE:
                    # End of subnegotiation
                    self._state = _IACState.DATA
                    self._sb_data = []
                elif byte == IAC:
                    # Escaped IAC inside subnegotiation
                    self._sb_data.append(IAC)
                    self._state = _IACState.IAC_SB
                else:
                    # Something else — treat as data and return to SB state
                    self._sb_data.append(IAC)
                    self._sb_data.append(byte)
                    self._state = _IACState.IAC_SB

        # Combine results
        user_data = b"".join(user_data_parts)
        response = b"".join(response_parts)

        return (user_data, response)

    def escape_ff(self, data: bytes) -> bytes:
        """
        Escape 0xFF bytes in outgoing data per RFC 854 §3.

        Any 0xFF byte in the output stream must be escaped as 0xFF 0xFF
        to distinguish it from an IAC command byte.

        :param data: Raw bytes to send
        :return: Escaped bytes safe for Telnet transmission
        """
        # Replace each 0xFF with 0xFF 0xFF
        return data.replace(bytes([IAC]), bytes([IAC, IAC]))
