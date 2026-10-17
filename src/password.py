"""
Password protection for Profiles and Scenes.

Uses PBKDF2-HMAC-SHA256 for PIN hashing. No external dependencies.

Storage format: pbkdf2_sha256$iterations$salt$hash
- Salt: 16 bytes, hex-encoded (32 chars)
- Hash: 32 bytes, hex-encoded (64 chars)
- Default iterations: 600,000 (OWASP 2023 recommendation for PINs)

The REST layer uses the ``*_async`` helpers, which run PBKDF2 in a thread so a
burst of wrong PINs cannot stall the event loop (SEC-06), and the per-item
attempt limiter below, which locks an item out after repeated wrong PINs
(SEC-06 / F-SEC-007).
"""

import asyncio
import hashlib
import hmac
import os
import re
import time
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
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


def is_valid_passcode(passcode: Any) -> bool:
    """Return True if ``passcode`` is a 4-8 digit string."""
    try:
        _validate_passcode(passcode)
    except PasswordError:
        return False
    return True


def is_passcode_hash(value: Any) -> bool:
    """Return True if ``value`` is a well-formed ``pbkdf2_sha256$iterations$salt$hash`` string."""
    if not isinstance(value, str):
        return False
    parts = value.split("$")
    if len(parts) != 4 or parts[0] != "pbkdf2_sha256":
        return False
    try:
        return int(parts[1]) > 0 and len(bytes.fromhex(parts[2])) > 0 and len(bytes.fromhex(parts[3])) > 0
    except ValueError:
        return False


def ensure_hashed_passcode(value: str | None) -> str | None:
    """
    Return a stored passcode value that is safe to keep (F-SEC-004).

    None, empty strings and PBKDF2 hashes are returned unchanged. A raw 4-8
    digit PIN (e.g. hand-edited into profiles.json) is hashed. Anything else
    is returned unchanged; it never verifies, so the item stays locked.
    """
    if not value or is_passcode_hash(value):
        return value
    if is_valid_passcode(value):
        return hash_passcode(value)
    return value


async def hash_passcode_async(passcode: str) -> str:
    """:func:`hash_passcode` in the default thread executor (SEC-06)."""
    return await asyncio.get_running_loop().run_in_executor(None, hash_passcode, passcode)


async def verify_passcode_async(passcode: str, stored_hash: str) -> bool:
    """:func:`verify_passcode` in the default thread executor (SEC-06); raises the same errors."""
    return await asyncio.get_running_loop().run_in_executor(None, verify_passcode, passcode, stored_hash)


# =============================================================================
# Requested PIN changes (SEC-05)
# =============================================================================

PIN_SET = "set"
PIN_CLEAR = "clear"


def requested_pin_change(
    data: dict[str, Any], has_own_pin: bool, protected: bool | None = None
) -> tuple[str | None, str | None, str | None]:
    """
    Read the PIN change a create/update request body asks for.

    ``passcode: "5678"`` sets or changes the PIN; ``remove_passcode: true``,
    ``passcode: null``/``""`` or ``password_protected: false`` clear it.
    ``password_protected: true`` without a passcode is accepted only when the
    item is already protected (the editors send the flag on every save).

    :param data: request body
    :param has_own_pin: whether the item has its own PIN (only that can be cleared)
    :param protected: whether the item is protected at all, own PIN or
                      inherited (defaults to ``has_own_pin``)
    :returns: ``(action, new_pin, error)``; action is :data:`PIN_SET`,
              :data:`PIN_CLEAR` or None (no change)
    """
    if protected is None:
        protected = has_own_pin
    flag = data.get("password_protected")
    if flag is not None and not isinstance(flag, bool):
        return None, None, "password_protected must be true or false"
    remove = data.get("remove_passcode")
    if remove is not None and not isinstance(remove, bool):
        return None, None, "remove_passcode must be true or false"
    has_value = "passcode" in data and data["passcode"] not in (None, "")
    wants_clear = remove is True or ("passcode" in data and not has_value) or flag is False

    if wants_clear:
        if has_value or flag is True:
            return None, None, "Conflicting passcode fields: cannot set and remove the passcode together"
        return (PIN_CLEAR if has_own_pin else None), None, None
    if has_value:
        if not is_valid_passcode(data["passcode"]):
            return None, None, f"passcode must be {_MIN_PIN_LENGTH}-{_MAX_PIN_LENGTH} digits"
        return PIN_SET, data["passcode"], None
    if flag is True and not protected:
        return None, None, "passcode required when enabling password protection"
    return None, None, None


# =============================================================================
# Per-item wrong-PIN limiter (SEC-06 / F-SEC-007)
# =============================================================================

#: Wrong PINs allowed for one item before it is locked out
MAX_PIN_FAILURES = 5

#: Lockout after the 5th, 6th, 7th... consecutive wrong PIN (seconds; the last one repeats)
PIN_LOCKOUT_SCHEDULE: tuple[float, ...] = (30.0, 120.0, 600.0, 1800.0, 3600.0)

#: Retry-After for a request that arrives while another check of the same item runs
_IN_FLIGHT_RETRY_AFTER = 1.0


@dataclass
class _ItemAttempts:
    failures: int = 0
    locked_until: float = 0.0


@dataclass
class PinAttempt:
    """Outcome of :meth:`PasscodeAttemptTracker.attempt`."""

    ok: bool
    locked: bool = False
    retry_after: float = 0.0


@dataclass
class PasscodeAttemptTracker:
    """
    Counts wrong PINs per item (``"profile:<id>"``, ``"scene:<id>"``).

    The first ``max_failures - 1`` wrong PINs are free. The 5th locks the item
    for 30 s; each further wrong PIN after a lockout locks it again for longer
    (:data:`PIN_LOCKOUT_SCHEDULE`, capped at an hour), so at most one guess an
    hour gets through and a 4-digit PIN takes months to brute force. A correct
    PIN resets the item. Only one check per item runs at a time, so parallel
    requests cannot spend more guesses than the limiter allows.
    """

    max_failures: int = MAX_PIN_FAILURES
    schedule: tuple[float, ...] = PIN_LOCKOUT_SCHEDULE
    clock: Callable[[], float] = time.monotonic
    _items: dict[str, _ItemAttempts] = field(default_factory=dict)
    _in_flight: set[str] = field(default_factory=set)

    def check(self, item_key: str) -> float:
        """Seconds until ``item_key`` may be tried again (0.0 if it may be tried now)."""
        if item_key in self._in_flight:
            return _IN_FLIGHT_RETRY_AFTER
        state = self._items.get(item_key)
        if state is None:
            return 0.0
        return max(0.0, state.locked_until - self.clock())

    def record_failure(self, item_key: str) -> float:
        """Count a wrong PIN; returns the lockout it starts in seconds (0.0 if none)."""
        state = self._items.setdefault(item_key, _ItemAttempts())
        state.failures += 1
        if state.failures < self.max_failures:
            return 0.0
        step = min(state.failures - self.max_failures, len(self.schedule) - 1)
        lockout = self.schedule[step]
        state.locked_until = self.clock() + lockout
        return lockout

    def record_success(self, item_key: str) -> None:
        """Forget the wrong PINs of ``item_key``."""
        self._items.pop(item_key, None)

    def reset(self, item_key: str | None = None) -> None:
        """Forget one item (or every item when ``item_key`` is None)."""
        if item_key is None:
            self._items.clear()
            self._in_flight.clear()
        else:
            self._items.pop(item_key, None)
            self._in_flight.discard(item_key)

    def failures(self, item_key: str) -> int:
        """Consecutive wrong PINs recorded for ``item_key``."""
        state = self._items.get(item_key)
        return state.failures if state else 0

    async def attempt(self, item_key: str, verify: Callable[[], Awaitable[bool]]) -> PinAttempt:
        """
        Run one PIN check for ``item_key`` under the limiter.

        Returns ``locked=True`` without calling ``verify`` while the item is
        locked out (or already being checked). Otherwise awaits ``verify``;
        a :class:`PasswordError` (malformed PIN) counts as a wrong PIN.
        """
        retry_after = self.check(item_key)
        if retry_after > 0:
            return PinAttempt(ok=False, locked=True, retry_after=retry_after)
        self._in_flight.add(item_key)
        try:
            try:
                ok = await verify()
            except PasswordError:
                ok = False
        finally:
            self._in_flight.discard(item_key)
        if ok:
            self.record_success(item_key)
            return PinAttempt(ok=True)
        return PinAttempt(ok=False, retry_after=self.record_failure(item_key))


_PIN_TRACKER = PasscodeAttemptTracker()


def get_pin_tracker() -> PasscodeAttemptTracker:
    """The hub-wide per-item attempt tracker."""
    return _PIN_TRACKER


def check_pin_lockout(item_key: str) -> float:
    """Seconds until ``item_key`` may be tried again (0.0 if it may be tried now)."""
    return _PIN_TRACKER.check(item_key)


def record_pin_failure(item_key: str) -> float:
    """Count a wrong PIN for ``item_key``; returns the lockout it starts (seconds)."""
    return _PIN_TRACKER.record_failure(item_key)


def record_pin_success(item_key: str) -> None:
    """Forget the wrong PINs of ``item_key``."""
    _PIN_TRACKER.record_success(item_key)


def reset_pin_lockout(item_key: str | None = None) -> None:
    """Forget one item's attempts, or all of them (tests, item deletion)."""
    _PIN_TRACKER.reset(item_key)


async def attempt_pin(item_key: str, verify: Callable[[], Awaitable[bool]]) -> PinAttempt:
    """:meth:`PasscodeAttemptTracker.attempt` on the hub-wide tracker."""
    return await _PIN_TRACKER.attempt(item_key, verify)
