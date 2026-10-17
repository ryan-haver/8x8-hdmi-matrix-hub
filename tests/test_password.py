"""
Unit tests for password.py (Phase 8, WP-F1).

Tests cover: PBKDF2 hash creation, verification, validation; the async
helpers that keep PBKDF2 off the event loop (SEC-06); hashing a plaintext PIN
found on load (F-SEC-004); reading a requested PIN change (SEC-05); and the
per-item wrong-PIN limiter (F-SEC-007).
"""

import asyncio
import threading
import time

import pytest

import password
from password import (
    MAX_PIN_FAILURES,
    PIN_CLEAR,
    PIN_LOCKOUT_SCHEDULE,
    PIN_SET,
    PasscodeAttemptTracker,
    PasswordError,
    check_pin_lockout,
    ensure_hashed_passcode,
    hash_passcode,
    hash_passcode_async,
    is_passcode_hash,
    needs_passcode,
    record_pin_failure,
    record_pin_success,
    requested_pin_change,
    reset_pin_lockout,
    verify_passcode,
    verify_passcode_async,
)


@pytest.fixture(autouse=True)
def _fresh_pin_tracker():
    """The hub-wide tracker is module state; every test starts and ends clean."""
    reset_pin_lockout()
    yield
    reset_pin_lockout()


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


class TestStoredAsHash:
    """F-SEC-004: passcodes are only ever stored as PBKDF2 hashes."""

    def test_hash_has_the_documented_format(self):
        """pbkdf2_sha256$iterations$32-hex salt$64-hex hash, and no trace of the PIN."""
        stored = hash_passcode("482916")
        algo, iterations, salt, digest = stored.split("$")
        assert (algo, iterations) == ("pbkdf2_sha256", "600000")
        assert len(salt) == 32 and len(digest) == 64
        assert "482916" not in stored
        assert is_passcode_hash(stored)

    def test_iterations_follow_the_env_var(self, monkeypatch):
        monkeypatch.setenv("MATRIX_PASSWORD_ITERATIONS", "1000")
        stored = hash_passcode("1234")
        assert stored.split("$")[1] == "1000"
        assert verify_passcode("1234", stored) is True

    @pytest.mark.parametrize(
        "value",
        ["1234", "", "pbkdf2_sha256$x$00$00", "pbkdf2_sha256$1000$zz$00", "md5$1$00$00", "pbkdf2_sha256$1000$00", None, 1234],
    )
    def test_is_passcode_hash_rejects_non_hashes(self, value):
        assert is_passcode_hash(value) is False

    def test_ensure_hashed_leaves_empty_values_and_hashes_alone(self):
        stored = hash_passcode("1234")
        assert ensure_hashed_passcode(None) is None
        assert ensure_hashed_passcode("") == ""
        assert ensure_hashed_passcode(stored) == stored

    def test_ensure_hashed_hashes_a_raw_pin(self, monkeypatch):
        """A plaintext PIN found on load is replaced by a hash that verifies against it."""
        monkeypatch.setenv("MATRIX_PASSWORD_ITERATIONS", "1000")
        result = ensure_hashed_passcode("90210")
        assert result != "90210" and is_passcode_hash(result)
        assert verify_passcode("90210", result) is True

    def test_ensure_hashed_keeps_garbage_which_never_verifies(self):
        """Neither a hash nor a PIN: kept as-is, and every passcode fails against it (fails closed)."""
        assert ensure_hashed_passcode("not-a-hash") == "not-a-hash"
        with pytest.raises(PasswordError):
            verify_passcode("1234", "not-a-hash")


class TestAsyncHelpers:
    """SEC-06: PBKDF2 runs in a thread, never on the event loop."""

    async def test_hash_and_verify_async_round_trip(self, monkeypatch):
        monkeypatch.setenv("MATRIX_PASSWORD_ITERATIONS", "1000")
        stored = await hash_passcode_async("2468")
        assert is_passcode_hash(stored)
        assert await verify_passcode_async("2468", stored) is True
        assert await verify_passcode_async("1357", stored) is False

    async def test_async_helpers_raise_the_same_errors(self):
        with pytest.raises(PasswordError):
            await hash_passcode_async("12")
        with pytest.raises(PasswordError):
            await verify_passcode_async("1234", "bogus")

    async def test_pbkdf2_runs_off_the_event_loop_thread(self, monkeypatch):
        monkeypatch.setenv("MATRIX_PASSWORD_ITERATIONS", "1000")
        threads = []
        real_verify = password.verify_passcode
        real_hash = password.hash_passcode

        def spy_verify(*args):
            threads.append(threading.current_thread())
            return real_verify(*args)

        def spy_hash(*args):
            threads.append(threading.current_thread())
            return real_hash(*args)

        monkeypatch.setattr(password, "verify_passcode", spy_verify)
        monkeypatch.setattr(password, "hash_passcode", spy_hash)
        stored = await hash_passcode_async("1234")
        await verify_passcode_async("1234", stored)
        assert len(threads) == 2
        assert threading.main_thread() not in threads

    async def test_wrong_pin_burst_does_not_stall_the_loop(self, monkeypatch):
        """While a burst of slow verifications runs, a ticker on the loop keeps ticking."""
        monkeypatch.setenv("MATRIX_PASSWORD_ITERATIONS", "200000")
        stored = hash_passcode("1234")
        started = time.perf_counter()
        verify_passcode("0000", stored)
        one_check = time.perf_counter() - started

        loop = asyncio.get_running_loop()
        ticks: list[float] = []
        stop = asyncio.Event()

        async def ticker():
            while not stop.is_set():
                ticks.append(loop.time())
                await asyncio.sleep(0.005)

        task = asyncio.create_task(ticker())
        await asyncio.sleep(0)
        results = await asyncio.gather(*(verify_passcode_async("0000", stored) for _ in range(4)))
        stop.set()
        await task

        assert results == [False] * 4
        gaps = [b - a for a, b in zip(ticks, ticks[1:], strict=False)]
        # A blocking check would freeze the loop for at least one_check per call.
        assert max(gaps) < one_check, (max(gaps), one_check)


class TestRequestedPinChange:
    """SEC-05: reading what a create/update body asks for."""

    @pytest.mark.parametrize(
        "body",
        [{"remove_passcode": True}, {"passcode": None}, {"passcode": ""}, {"password_protected": False}],
    )
    def test_clear_forms(self, body):
        assert requested_pin_change(body, has_own_pin=True) == (PIN_CLEAR, None, None)

    def test_clear_on_an_unprotected_item_is_no_change(self):
        assert requested_pin_change({"password_protected": False}, has_own_pin=False) == (None, None, None)

    def test_set(self):
        assert requested_pin_change({"passcode": "5678"}, has_own_pin=False) == (PIN_SET, "5678", None)
        assert requested_pin_change({"passcode": "5678", "password_protected": True}, has_own_pin=True) == (
            PIN_SET,
            "5678",
            None,
        )

    def test_flag_alone_on_a_protected_item_is_no_change(self):
        """The editors send password_protected: true on every save."""
        assert requested_pin_change({"password_protected": True, "name": "x"}, has_own_pin=True) == (None, None, None)
        assert requested_pin_change({"password_protected": True}, has_own_pin=False, protected=True) == (
            None,
            None,
            None,
        )

    def test_unrelated_body_is_no_change(self):
        assert requested_pin_change({"name": "Renamed"}, has_own_pin=True) == (None, None, None)

    @pytest.mark.parametrize(
        ("body", "message"),
        [
            ({"password_protected": True}, "passcode required"),
            ({"passcode": "12"}, "4-8 digits"),
            ({"passcode": "abcd"}, "4-8 digits"),
            ({"passcode": 1234}, "4-8 digits"),
            ({"passcode": "1234", "remove_passcode": True}, "Conflicting"),
            ({"passcode": "1234", "password_protected": False}, "Conflicting"),
            ({"remove_passcode": True, "password_protected": True}, "Conflicting"),
            ({"password_protected": "yes"}, "true or false"),
            ({"remove_passcode": 1}, "true or false"),
        ],
    )
    def test_errors(self, body, message):
        action, pin, error = requested_pin_change(body, has_own_pin=False)
        assert (action, pin) == (None, None)
        assert message in error


class FakeClock:
    def __init__(self):
        self.now = 1000.0

    def __call__(self) -> float:
        return self.now


class TestAttemptTracker:
    """F-SEC-007: wrong PINs per item are limited with growing lockouts."""

    def test_four_wrong_pins_are_free_the_fifth_locks_for_30s(self):
        clock = FakeClock()
        tracker = PasscodeAttemptTracker(clock=clock)
        for _ in range(MAX_PIN_FAILURES - 1):
            assert tracker.record_failure("profile:a") == 0.0
            assert tracker.check("profile:a") == 0.0
        assert tracker.record_failure("profile:a") == 30.0
        assert tracker.check("profile:a") == 30.0
        clock.now += 29
        assert tracker.check("profile:a") == pytest.approx(1.0)
        clock.now += 1
        assert tracker.check("profile:a") == 0.0

    def test_lockouts_grow_and_cap(self):
        clock = FakeClock()
        tracker = PasscodeAttemptTracker(clock=clock)
        for _ in range(MAX_PIN_FAILURES - 1):
            tracker.record_failure("k")
        lockouts = []
        for _ in range(len(PIN_LOCKOUT_SCHEDULE) + 2):
            lockouts.append(tracker.record_failure("k"))
            clock.now += lockouts[-1]
        assert lockouts == [30.0, 120.0, 600.0, 1800.0, 3600.0, 3600.0, 3600.0]

    def test_a_correct_pin_resets_the_item(self):
        tracker = PasscodeAttemptTracker(clock=FakeClock())
        for _ in range(MAX_PIN_FAILURES):
            tracker.record_failure("k")
        tracker.record_success("k")
        assert tracker.check("k") == 0.0
        assert tracker.failures("k") == 0

    def test_items_are_independent(self):
        tracker = PasscodeAttemptTracker(clock=FakeClock())
        for _ in range(MAX_PIN_FAILURES):
            tracker.record_failure("scene:a")
        assert tracker.check("scene:a") > 0
        assert tracker.check("scene:b") == 0.0
        assert tracker.check("profile:a") == 0.0

    def test_reset_one_or_all(self):
        tracker = PasscodeAttemptTracker(clock=FakeClock())
        for key in ("a", "b"):
            for _ in range(MAX_PIN_FAILURES):
                tracker.record_failure(key)
        tracker.reset("a")
        assert tracker.check("a") == 0.0 and tracker.check("b") > 0
        tracker.reset()
        assert tracker.check("b") == 0.0

    def test_brute_forcing_a_4_digit_pin_takes_months(self):
        """Simulate an attacker trying PINs as fast as the limiter allows for 30 days: well under 10,000 guesses."""
        clock = FakeClock()
        tracker = PasscodeAttemptTracker(clock=clock)
        guesses = 0
        end = clock.now + 30 * 24 * 3600
        while clock.now < end:
            wait = tracker.check("k")
            if wait > 0:
                clock.now += wait
                continue
            tracker.record_failure("k")
            guesses += 1
        assert guesses < 1000

    async def test_attempt_records_results(self):
        tracker = PasscodeAttemptTracker(clock=FakeClock())

        async def wrong():
            return False

        async def right():
            return True

        for _ in range(MAX_PIN_FAILURES - 1):
            assert (await tracker.attempt("k", wrong)).ok is False
        assert tracker.failures("k") == MAX_PIN_FAILURES - 1
        assert (await tracker.attempt("k", right)).ok is True
        assert tracker.failures("k") == 0

    async def test_attempt_while_locked_does_not_verify(self):
        tracker = PasscodeAttemptTracker(clock=FakeClock())
        for _ in range(MAX_PIN_FAILURES):
            tracker.record_failure("k")
        called = []

        async def verify():
            called.append(1)
            return True

        result = await tracker.attempt("k", verify)
        assert (result.ok, result.locked, result.retry_after) == (False, True, 30.0)
        assert called == []

    async def test_malformed_pin_counts_as_wrong(self):
        tracker = PasscodeAttemptTracker(clock=FakeClock())

        async def verify():
            raise PasswordError("passcode must be 4-8 digits")

        result = await tracker.attempt("k", verify)
        assert (result.ok, result.locked) == (False, False)
        assert tracker.failures("k") == 1

    async def test_parallel_attempts_cannot_outrun_the_limiter(self):
        """Only one check per item runs at a time; the rest are refused without verifying."""
        tracker = PasscodeAttemptTracker(clock=FakeClock())
        verified = []

        async def slow_wrong():
            verified.append(1)
            await asyncio.sleep(0.01)
            return False

        results = await asyncio.gather(*(tracker.attempt("k", slow_wrong) for _ in range(50)))
        assert len(verified) == 1
        assert sum(r.locked for r in results) == 49
        assert tracker.failures("k") == 1

    def test_module_level_helpers_share_one_tracker(self):
        for _ in range(MAX_PIN_FAILURES):
            record_pin_failure("profile:x")
        assert check_pin_lockout("profile:x") > 0
        record_pin_success("profile:x")
        assert check_pin_lockout("profile:x") == 0.0
        for _ in range(MAX_PIN_FAILURES):
            record_pin_failure("profile:x")
        reset_pin_lockout("profile:x")
        assert check_pin_lockout("profile:x") == 0.0
