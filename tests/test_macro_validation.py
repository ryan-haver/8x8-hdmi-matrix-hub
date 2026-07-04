"""Tests for macro endpoint input validation.

Validates the F12.1 / F12.2 / F12.4 / F12.5 fixes:

- Macro ``name`` must be a non-empty string under MAX_NAME_LEN chars
- Macro ``description`` must be under MAX_DESCRIPTION_LEN chars
- ``steps`` must be a list of 1..MAX_STEPS items
- Each step's ``command`` must be in the CEC command whitelist
- Each step's ``targets`` must be "input_N" / "output_N" with N=1-8
- ``command`` must match its target type (input command → input targets)
- ``delay_ms`` must be integer 0..MAX_DELAY_MS
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_PROJECT_ROOT / "src"))


# Build a minimal mock module manager before importing the handler module.
# The handler imports get_macro_manager from .utils at call-time so a
# module-level swap is sufficient.
@pytest.fixture
def mock_macro_manager(monkeypatch):
    """Provide a mock macro manager to the handler."""
    manager = MagicMock()
    manager.create_macro = MagicMock(
        return_value=MagicMock(
            id="macro_test",
            name="test",
            icon="⚡",
            description="",
            steps=[],
            created_at="2026-07-04T00:00:00Z",
            updated_at="2026-07-04T00:00:00Z",
            favorite=False,
            dashboard_visible=False,
            dashboard_order=0,
            to_dict=lambda: {
                "id": "macro_test",
                "name": "test",
                "icon": "⚡",
                "description": "",
                "steps": [],
                "created_at": "2026-07-04T00:00:00Z",
                "updated_at": "2026-07-04T00:00:00Z",
                "favorite": False,
                "dashboard_visible": False,
                "dashboard_order": 0,
            },
        )
    )

    async def _async_get_macro_manager():
        return manager

    monkeypatch.setattr(
        "rest_api.utils.get_macro_manager",
        _async_get_macro_manager,
    )
    return manager


@pytest.fixture
def make_request():
    """Build a mock aiohttp request with a JSON body."""
    def _factory(body):
        req = MagicMock()
        req.json = AsyncMock(return_value=body)
        req.match_info = {"macro_id": "macro_test"}
        return req

    return _factory


class TestMacroNameValidation:
    """F12.4: name length and type validation."""

    @pytest.mark.asyncio
    async def test_missing_name(self, mock_macro_manager, make_request):
        from rest_api.macros import handle_create_macro

        req = make_request({"steps": [{"command": "POWER_ON", "targets": ["input_1"]}]})
        resp = await handle_create_macro(req)
        assert resp.status == 400
        assert "name" in resp.text.lower()

    @pytest.mark.asyncio
    async def test_name_too_long(self, mock_macro_manager, make_request):
        from rest_api.macros import handle_create_macro

        req = make_request(
            {
                "name": "x" * 1000,  # exceeds MAX_NAME_LEN (200)
                "steps": [{"command": "POWER_ON", "targets": ["input_1"]}],
            }
        )
        resp = await handle_create_macro(req)
        assert resp.status == 400
        assert "200 characters" in resp.text or "exceeds" in resp.text.lower()

    @pytest.mark.asyncio
    async def test_name_not_string(self, mock_macro_manager, make_request):
        from rest_api.macros import handle_create_macro

        req = make_request({"name": 12345, "steps": []})
        resp = await handle_create_macro(req)
        assert resp.status == 400


class TestMacroStepCommandValidation:
    """F12.2: command must be in CEC whitelist."""

    @pytest.mark.asyncio
    async def test_unknown_command_rejected(self, mock_macro_manager, make_request):
        from rest_api.macros import handle_create_macro

        req = make_request(
            {
                "name": "evil",
                "steps": [
                    {"command": "EXEC_SHELL", "targets": ["input_1"]},
                ],
            }
        )
        resp = await handle_create_macro(req)
        assert resp.status == 400
        assert "unknown command" in resp.text.lower()

    @pytest.mark.asyncio
    async def test_command_not_string_rejected(self, mock_macro_manager, make_request):
        from rest_api.macros import handle_create_macro

        req = make_request(
            {
                "name": "test",
                "steps": [{"command": 12345, "targets": ["input_1"]}],
            }
        )
        resp = await handle_create_macro(req)
        assert resp.status == 400


class TestMacroTargetValidation:
    """F12.1: targets must be input_N / output_N with N=1-8."""

    @pytest.mark.asyncio
    async def test_invalid_target_format_rejected(self, mock_macro_manager, make_request):
        from rest_api.macros import handle_create_macro

        req = make_request(
            {
                "name": "test",
                "steps": [{"command": "POWER_ON", "targets": ["garbage"]}],
            }
        )
        resp = await handle_create_macro(req)
        assert resp.status == 400

    @pytest.mark.asyncio
    async def test_port_out_of_range_rejected(self, mock_macro_manager, make_request):
        from rest_api.macros import handle_create_macro

        req = make_request(
            {
                "name": "test",
                "steps": [{"command": "POWER_ON", "targets": ["input_99"]}],
            }
        )
        resp = await handle_create_macro(req)
        assert resp.status == 400

    @pytest.mark.asyncio
    async def test_empty_targets_rejected(self, mock_macro_manager, make_request):
        from rest_api.macros import handle_create_macro

        req = make_request(
            {
                "name": "test",
                "steps": [{"command": "POWER_ON", "targets": []}],
            }
        )
        resp = await handle_create_macro(req)
        assert resp.status == 400

    @pytest.mark.asyncio
    async def test_input_command_with_output_target_rejected(
        self, mock_macro_manager, make_request
    ):
        """Input-only commands can't target output ports."""
        from rest_api.macros import handle_create_macro

        req = make_request(
            {
                "name": "test",
                "steps": [{"command": "PLAY", "targets": ["output_1"]}],
            }
        )
        resp = await handle_create_macro(req)
        assert resp.status == 400
        assert "cannot target outputs" in resp.text.lower()

    @pytest.mark.asyncio
    async def test_output_command_with_input_target_rejected(
        self, mock_macro_manager, make_request
    ):
        """Output-only commands can't target input ports."""
        from rest_api.macros import handle_create_macro

        req = make_request(
            {
                "name": "test",
                "steps": [{"command": "ACTIVE", "targets": ["input_1"]}],
            }
        )
        resp = await handle_create_macro(req)
        assert resp.status == 400
        assert "cannot target inputs" in resp.text.lower()


class TestMacroStepCountLimit:
    """F12.5: max 100 steps per macro."""

    @pytest.mark.asyncio
    async def test_too_many_steps_rejected(self, mock_macro_manager, make_request):
        from rest_api.macros import handle_create_macro

        steps = [
            {"command": "POWER_ON", "targets": ["input_1"]}
            for _ in range(101)  # exceeds MAX_STEPS (100)
        ]
        req = make_request({"name": "huge", "steps": steps})
        resp = await handle_create_macro(req)
        assert resp.status == 400
        assert "max" in resp.text.lower() or "100" in resp.text


class TestMacroDelayValidation:
    """delay_ms must be integer 0..60000."""

    @pytest.mark.asyncio
    async def test_negative_delay_rejected(self, mock_macro_manager, make_request):
        from rest_api.macros import handle_create_macro

        req = make_request(
            {
                "name": "test",
                "steps": [
                    {"command": "POWER_ON", "targets": ["input_1"], "delay_ms": -100},
                ],
            }
        )
        resp = await handle_create_macro(req)
        assert resp.status == 400

    @pytest.mark.asyncio
    async def test_excessive_delay_rejected(self, mock_macro_manager, make_request):
        from rest_api.macros import handle_create_macro

        req = make_request(
            {
                "name": "test",
                "steps": [
                    {
                        "command": "POWER_ON",
                        "targets": ["input_1"],
                        "delay_ms": 999_999,  # exceeds MAX_DELAY_MS (60000)
                    },
                ],
            }
        )
        resp = await handle_create_macro(req)
        assert resp.status == 400


class TestMacroValidSubmission:
    """A well-formed macro should be accepted."""

    @pytest.mark.asyncio
    async def test_valid_macro_accepted(self, mock_macro_manager, make_request):
        from rest_api.macros import handle_create_macro

        req = make_request(
            {
                "name": "Movie Night",
                "steps": [
                    {"command": "POWER_ON", "targets": ["input_1", "input_2"]},
                    {"command": "SELECT", "targets": ["input_1"], "delay_ms": 500},
                ],
            }
        )
        resp = await handle_create_macro(req)
        # 200 = success
        assert resp.status == 200
        # And the manager was actually called
        mock_macro_manager.create_macro.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])