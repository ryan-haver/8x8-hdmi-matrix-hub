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
# Every constant below is taken from the simulator's documented assumptions
# (tools/simulator/protocol.py) and still has to be checked against captures
# from the real BK-808 in HIL-A (docs/REMEDIATION_PLAN.md §5.2).
# =============================================================================

# HIL-A: confirm — "E00" answers a command the matrix does not recognise.
TELNET_ERR_UNKNOWN_COMMAND = "E00"
# HIL-A: confirm — "E01" answers a recognised command with a bad parameter.
TELNET_ERR_BAD_PARAMETER = "E01"
# HIL-A: confirm — every error code the matrix may send ("E02" was accepted
# by earlier client code; its meaning is unknown).
TELNET_ERROR_CODES = frozenset({TELNET_ERR_UNKNOWN_COMMAND, TELNET_ERR_BAD_PARAMETER, "E02"})
# HIL-A: confirm — the `status` dump ends with the MAC address line.
STATUS_DUMP_LAST_LINE = "mac address:"
_MAC_RE = re.compile(r"mac address:\s*([0-9a-f]{2}[:-]){5}[0-9a-f]{2}", re.IGNORECASE)
# HIL-A: confirm — `r link in|out N` answers "hdmi input|output N: connect|disconnect".
_LINK_RE = re.compile(r"\b(connect|disconnect)\b", re.IGNORECASE)
# HIL-A: confirm — successful set commands answer with one or more
# acknowledgement lines (the simulator echoes the command without "s ", e.g.
# "cec in 1 on", "output1->input3", "save to preset 1") and no error code.
# A line identical to the command we sent is treated as a plain echo, not
# as the acknowledgement.


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


def _is_echo(line: str, command: str) -> bool:
    return line.lower().rstrip("!").strip() == command.strip().lower()


def is_response_complete(response: str, command: str) -> bool:
    """Whether ``response`` is the whole answer to ``command`` (BE-07).

    - any error code completes every command;
    - ``status`` completes on its last line (``mac address: ...``);
    - ``r link ...`` completes on its ``connect``/``disconnect`` line;
    - everything else (reads and set commands alike) completes on the first
      full line that is not an echo of the command. Set commands therefore
      return as soon as the matrix acknowledges them instead of waiting the
      whole command timeout.
    """
    if not response:
        return False
    if response_error(response) is not None:
        return True

    lines = complete_lines(response)
    cmd = command.strip().lower()

    if cmd == "status":
        if any(line.lower().startswith(STATUS_DUMP_LAST_LINE) for line in lines):
            return True
        # Last line may arrive without a terminator: accept a full MAC.
        return _MAC_RE.search(response) is not None

    if cmd.startswith("r link"):
        return any(_LINK_RE.search(line) for line in lines)

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
