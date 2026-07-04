"""
Telnet RFC 854 Protocol Helpers.

Provides filters for handling Telnet IAC (Interpret As Command) negotiation
bytes that appear during initial connection to the OREI BK-808 matrix.

:copyright: (c) 2026 by Custom Integration.
:license: Mozilla Public License Version 2.0, see LICENSE for more details.
"""

from enum import Enum
from typing import Tuple


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

    def feed(self, data: bytes) -> Tuple[bytes, bytes]:
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
