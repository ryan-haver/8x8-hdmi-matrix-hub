"""
Password protection for Profiles and Scenes.

Uses PBKDF2-HMAC-SHA256 for PIN hashing. No external dependencies.

Storage format: pbkdf2_sha256$iterations$salt$hash
- Salt: 16 bytes, hex-encoded (32 chars)
- Hash: 32 bytes, hex-encoded (64 chars)
- Default iterations: 600,000 (OWASP 2023 recommendation for PINs)
"""

import hashlib
import hmac
import os
import re
from typing import Any


class PasswordError(ValueError):
    """Raised when passcode verification fails or passcode format is invalid."""

    pass


_MIN_PIN_LENGTH = 4
_MAX_PIN_LENGTH = 8


def _iterations() -> int:
    """Return the PBKDF2 iteration count. Configurable via env var for testing."""
    return int(os.environ.get("MATRIX_PASSWORD_ITERATIONS", "600000"))


def hash_passcode(passcode: str) -> str:
    """
    Hash a passcode and return the storage string.

    :param passcode: 4-8 digit numeric passcode
    :returns: storage string of the form ``pbkdf2_sha256$iterations$salt$hash``
    :raises PasswordError: if passcode format is invalid
    """
    _validate_passcode(passcode)

    salt = os.urandom(16)
    stored = hashlib.pbkdf2_hmac(
        "sha256",
        passcode.encode("utf-8"),
        salt,
        _iterations(),
        dklen=32,
    )
    return f"pbkdf2_sha256${_iterations()}${salt.hex()}${stored.hex()}"


def verify_passcode(passcode: str, stored_hash: str) -> bool:
    """
    Verify a passcode against a stored hash.

    :param passcode: plaintext passcode to verify
    :param stored_hash: storage string from :func:`hash_passcode`
    :returns: True if the passcode matches
    :raises PasswordError: if the hash format is unrecognized
    """
    _validate_passcode(passcode)

    parts = stored_hash.split("$")
    if len(parts) != 4 or parts[0] != "pbkdf2_sha256":
        raise PasswordError(f"Unrecognized hash format: {parts[0]!r}")

    try:
        iterations = int(parts[1])
        salt = bytes.fromhex(parts[2])
        expected = bytes.fromhex(parts[3])
    except (ValueError, TypeError) as e:
        raise PasswordError(f"Malformed hash string: {e}") from e

    computed = hashlib.pbkdf2_hmac(
        "sha256",
        passcode.encode("utf-8"),
        salt,
        iterations,
        dklen=32,
    )

    return hmac.compare_digest(computed, expected)


def _validate_passcode(passcode: str) -> None:
    """Raise PasswordError if passcode is not a 4-8 digit string."""
    if not isinstance(passcode, str):
        raise PasswordError("passcode must be a string")
    if not re.fullmatch(r"\d{" + str(_MIN_PIN_LENGTH) + r"," + str(_MAX_PIN_LENGTH) + r"}", passcode):
        raise PasswordError(f"passcode must be {_MIN_PIN_LENGTH}-{_MAX_PIN_LENGTH} digits")


def needs_passcode(stored_hash: str | None) -> bool:
    """Return True if a non-None hash is set."""
    return stored_hash is not None and stored_hash != ""
