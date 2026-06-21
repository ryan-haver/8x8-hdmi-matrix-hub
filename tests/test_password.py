"""
Unit tests for password.py (Phase 8).

Tests cover: PBKDF2 hash creation, verification, validation.
"""

import pytest

from password import (
    PasswordError,
    hash_passcode,
    needs_passcode,
    verify_passcode,
)


class TestHashPasscode:
    """Tests for hash_passcode()."""

    def test_hash_returns_string(self):
        """hash_passcode returns a string."""
        result = hash_passcode("1234")
        assert isinstance(result, str)

    def test_hash_starts_with_pbkdf2_prefix(self):
        """Hash starts with 'pbkdf2_sha256' prefix."""
        result = hash_passcode("1234")
        assert result.startswith("pbkdf2_sha256")

    def test_different_passcodes_different_hashes(self):
        """Different passcodes produce different hashes."""
        h1 = hash_passcode("1234")
        h2 = hash_passcode("5678")
        assert h1 != h2

    def test_same_passcode_different_salt(self):
        """Same passcode with different salts produces different hashes."""
        h1 = hash_passcode("1234")
        h2 = hash_passcode("1234")
        assert h1 != h2  # Different salt = different hash


class TestVerifyPasscode:
    """Tests for verify_passcode()."""

    def test_verify_correct(self):
        """Correct passcode returns True."""
        h = hash_passcode("1234")
        assert verify_passcode("1234", h) is True

    def test_verify_incorrect(self):
        """Incorrect passcode returns False."""
        h = hash_passcode("1234")
        assert verify_passcode("5678", h) is False

    def test_verify_invalid_format_raises(self):
        """Non-numeric passcode raises PasswordError."""
        h = hash_passcode("1234")
        with pytest.raises(PasswordError):
            verify_passcode("wrong", h)


class TestNeedsPasscode:
    """Tests for needs_passcode()."""

    def test_none_returns_false(self):
        """None returns False."""
        assert needs_passcode(None) is False

    def test_empty_returns_false(self):
        """Empty string returns False."""
        assert needs_passcode("") is False

    def test_hash_returns_true(self):
        """Non-empty hash returns True."""
        h = hash_passcode("1234")
        assert needs_passcode(h) is True


class TestPasswordError:
    """Tests for PasswordError exception."""

    def test_is_value_error(self):
        """PasswordError inherits from ValueError."""
        assert issubclass(PasswordError, ValueError)
