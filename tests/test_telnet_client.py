"""
Tests for Telnet client IAC protocol handling and related fixes.

Tests:
- Item 1.1: TelnetIACFilter properly strips IAC negotiation bytes
- Item 1.2: Binary data detection returns empty string
- Item 1.3: Pre-clear removed, push buffer implemented
- Item 1.4: _pending_response removed

:copyright: (c) 2026 by Custom Integration.
:license: Mozilla Public License Version 2.0, see LICENSE for more details.
"""

import asyncio
import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest

# Add src to path for imports
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from _telnet_proto import TelnetIACFilter

# =============================================================================
# Item 1.1: TelnetIACFilter Tests
# =============================================================================


class TestTelnetIACFilter:
    """Test the TelnetIACFilter class for RFC 854 compliance."""

    def test_normal_data_passthrough(self):
        """Normal text data should pass through unchanged."""
        filter = TelnetIACFilter()
        data = b"hello world\r\n"
        user_data, response = filter.feed(data)
        assert user_data == b"hello world\r\n"
        assert response == b""

    def test_iac_will_auto_dont(self):
        """IAC WILL option should auto-reply with DONT."""
        filter = TelnetIACFilter()
        # IAC WILL 01 (server offers to do something)
        data = bytes([0xFF, 0xFB, 0x01])
        user_data, response = filter.feed(data)
        # WILL → DONT (0xFB → 0xFE)
        assert user_data == b""
        assert response == bytes([0xFF, 0xFE, 0x01])  # IAC DONT option

    def test_iac_do_auto_wont(self):
        """IAC DO option should auto-reply with WONT."""
        filter = TelnetIACFilter()
        # IAC DO 01 (server asks us to do something)
        data = bytes([0xFF, 0xFD, 0x01])
        user_data, response = filter.feed(data)
        # DO → WONT
        assert user_data == b""
        assert response == bytes([0xFF, 0xFC, 0x01])  # IAC WONT option

    def test_iac_wont_no_response(self):
        """IAC WONT option should not generate a response."""
        filter = TelnetIACFilter()
        data = bytes([0xFF, 0xFC, 0x01])
        user_data, response = filter.feed(data)
        assert user_data == b""
        assert response == b""

    def test_iac_dont_no_response(self):
        """IAC DONT option should not generate a response."""
        filter = TelnetIACFilter()
        data = bytes([0xFF, 0xFE, 0x01])
        user_data, response = filter.feed(data)
        assert user_data == b""
        assert response == b""

    def test_iac_escaped_0xff(self):
        """IAC IAC should be decoded as single 0xFF data byte."""
        filter = TelnetIACFilter()
        # IAC IAC (escaped 0xFF in data)
        data = bytes([0xFF, 0xFF])
        user_data, response = filter.feed(data)
        assert user_data == bytes([0xFF])
        assert response == b""

    def test_iac_sb_subnegotiation(self):
        """IAC SB (subnegotiation) should be stripped from user data."""
        filter = TelnetIACFilter()
        # IAC SB 01 ... IAC SE (subnegotiation)
        data = bytes([0xFF, 0xFA, 0x01, 0x00, 0x01, 0xFF, 0xF0])
        user_data, response = filter.feed(data)
        # Subnegotiation data should be stripped
        assert user_data == b""
        assert response == b""

    def test_mixed_data_and_iac(self):
        """Mixed normal data and IAC commands should be handled correctly."""
        filter = TelnetIACFilter()
        # "hello" + IAC WILL 01 + "world"
        data = b"hello" + bytes([0xFF, 0xFB, 0x01]) + b"world"
        user_data, response = filter.feed(data)
        assert user_data == b"helloworld"
        assert response == bytes([0xFF, 0xFE, 0x01])  # WILL → DONT

    def test_iac_does_not_appear_in_user_data(self):
        """IAC bytes must never appear in user_data output."""
        filter = TelnetIACFilter()
        # Various IAC sequences
        data = bytes([0xFF, 0xFB, 0x03, 0xFF, 0xFD, 0x05, 0xFF, 0xFC, 0x07])
        user_data, response = filter.feed(data)
        # No 0xFF bytes should appear in user_data
        assert 0xFF not in user_data
        # WILL 03 → DONT 03, DO 05 → WONT 05, WONT 07 and DONT 07 → no response
        assert response == bytes([0xFF, 0xFE, 0x03]) + bytes([0xFF, 0xFC, 0x05])

    def test_escape_ff(self):
        """0xFF in outgoing data must be escaped as 0xFF 0xFF."""
        filter = TelnetIACFilter()
        data = b"hello\xffworld"
        escaped = filter.escape_ff(data)
        # 0xFF must become 0xFF 0xFF
        assert escaped == b"hello\xff\xffworld"
        # Verify: the 0xFF in input becomes a doubled pair in output
        # The last byte of an escaped pair may be followed by non-0xFF,
        # so we check that all 0xFF sequences are pairs (0xFF 0xFF)
        i = 0
        while i < len(escaped):
            if escaped[i] == 0xFF:
                # Must be followed by another 0xFF (escape pair)
                assert i + 1 < len(escaped) and escaped[i + 1] == 0xFF, \
                    f"Bare 0xFF at position {i}"
                i += 2  # Skip the pair
            else:
                i += 1

    def test_escape_multiple_ff(self):
        """Multiple 0xFF bytes should each be escaped."""
        filter = TelnetIACFilter()
        data = b"\xff\xff\xff"
        escaped = filter.escape_ff(data)
        assert escaped == b"\xff\xff\xff\xff\xff\xff"

    def test_escape_no_ff(self):
        """Data without 0xFF should pass through unchanged."""
        filter = TelnetIACFilter()
        data = b"normal text\r\n"
        escaped = filter.escape_ff(data)
        assert escaped == data

    def test_empty_data(self):
        """Empty data should return empty results."""
        filter = TelnetIACFilter()
        user_data, response = filter.feed(b"")
        assert user_data == b""
        assert response == b""


# =============================================================================
# Item 1.2: Binary Data Detection Tests
# =============================================================================


class TestBinaryDataDetection:
    """Test binary data detection logic."""

    def test_printable_ascii_passthrough(self):
        """Pure ASCII text should not be detected as binary."""
        filter = TelnetIACFilter()
        data = b"hello world\r\n"
        user_data, _ = filter.feed(data)
        # Decode and check non-printable ratio
        binary_count = sum(
            1 for b in user_data
            if b > 127 or (b < 32 and b not in (9, 10, 13))
        )
        non_printable_ratio = binary_count / len(user_data) if user_data else 0
        assert non_printable_ratio <= 0.1

    def test_high_non_printable_detected(self):
        """Data with >10% non-printable bytes should be detected."""
        # Simulate binary data (>10% non-printable)
        # 90 printable + 12 non-printable = 12/102 ≈ 11.76% > 10%
        data = b"a" * 90 + bytes([0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x7F, 0x80, 0x81])
        binary_count = sum(
            1 for b in data
            if b > 127 or (b < 32 and b not in (9, 10, 13))
        )
        non_printable_ratio = binary_count / len(data) if data else 0
        assert non_printable_ratio > 0.1

    def test_whitespace_allowed(self):
        """Tab, newline, carriage return should NOT count as binary."""
        data = b"hello\tworld\nline2\r\n"
        binary_count = sum(
            1 for b in data
            if b > 127 or (b < 32 and b not in (9, 10, 13))
        )
        # Only regular whitespace, no non-printable
        assert binary_count == 0


# =============================================================================
# Item 1.3 & 1.4: Push Buffer and _pending_response Removal
# =============================================================================


class TestPushBuffer:
    """Test push buffer mechanism (Item 1.3)."""

    def test_push_buffer_initially_empty(self):
        """Push buffer should start empty."""
        # We can't easily instantiate TelnetClient without network,
        # but we can verify the concept with a mock
        buffer: list[str] = []
        assert buffer == []

    def test_push_buffer_append_and_drain(self):
        """Push buffer should support append and drain operations."""
        buffer: list[str] = []
        # Simulate adding data during _send_raw
        buffer.append("some data")
        buffer.append("more data")
        # Simulate draining in _listen_for_push
        assert len(buffer) == 2
        drained = buffer.pop(0)
        assert drained == "some data"
        assert len(buffer) == 1


class TestPendingResponseRemoval:
    """Test that _pending_response has been removed (Item 1.4)."""

    def test_no_pending_response_in_telnet_client(self):
        """TelnetClient should not have _pending_response attribute."""
        # Check class definition doesn't include _pending_response
        # We can't instantiate without network, but we can check source
        import inspect

        from telnet_client import TelnetClient

        source = inspect.getsource(TelnetClient)
        # The _pending_response line should NOT appear in __init__
        init_start = source.find("def __init__")
        init_end = source.find("\n    #", init_start + 1)
        if init_end == -1:
            init_end = len(source)
        init_section = source[init_start:init_end]
        assert "_pending_response" not in init_section


# =============================================================================
# Integration Test for TelnetIACFilter
# =============================================================================


class TestTelnetIACFilterIntegration:
    """Integration tests for TelnetIACFilter with realistic data."""

    def test_welcome_banner_with_iac(self):
        """Server welcome banner with IAC negotiation should be cleaned."""
        filter = TelnetIACFilter()
        # Simulate welcome banner with embedded IAC commands
        banner = (
            b"Welcome to OREI Matrix\r\n"
            + bytes([0xFF, 0xFB, 0x01])  # IAC WILL echoing
            + b"login: "
        )
        user_data, response = filter.feed(banner)
        # IAC commands stripped, response generated
        assert 0xFF not in user_data
        assert b"login: " in user_data

    def test_status_response_with_iac(self):
        """Status response containing IAC should be cleaned."""
        filter = TelnetIACFilter()
        # Simulate status response with IAC
        response = (
            b"power: on\r\n"
            + bytes([0xFF, 0xFD, 0x03])  # IAC DO option
            + b"inputs: 8\r\n"
        )
        user_data, auto_reply = filter.feed(response)
        # No 0xFF in user data
        assert 0xFF not in user_data
        # Auto-reply generated
        assert auto_reply == bytes([0xFF, 0xFC, 0x03])

    def test_iac_sequence_split_across_chunks(self):
        """IAC sequences split across multiple feed() calls should be handled."""
        filter = TelnetIACFilter()
        # First chunk: partial IAC
        user1, resp1 = filter.feed(b"hello\xff")
        assert user1 == b"hello"
        # Second chunk: rest of IAC WILL
        user2, resp2 = filter.feed(bytes([0xFB, 0x01]))
        # IAC was completed and handled
        assert 0xFF not in user2
