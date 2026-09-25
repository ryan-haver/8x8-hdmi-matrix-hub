"""Shared helpers and fixtures for the Home Assistant component tests (TST-01).

These tests use a real ``hass`` instance from
``pytest-homeassistant-custom-component`` (see ``requirements-test-ha.txt``,
Python 3.13). The hub's REST API is served by ``aioclient_mock``, which
returns the contract fixtures in ``tests/fixtures/api/``. Those are the real
hub responses produced by ``tools/gen_contract_fixtures.py``, not
hand-written shapes (TST-02).

The fixtures are registered through ``conftest.py``.
"""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

import pytest
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from pytest_homeassistant_custom_component.common import MockConfigEntry
from pytest_homeassistant_custom_component.test_util.aiohttp import AiohttpClientMocker

from custom_components.hdmi_matrix.const import DOMAIN

FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "api"

HOST = "192.0.2.10"
PORT = 8080
BASE_URL = f"http://{HOST}:{PORT}"

# Hub routes the component polls, and the contract fixture for each.
READ_ROUTES = {
    "/api/health": "health.json",
    "/api/status": "status.json",
    "/api/status/outputs": "status_outputs.json",
    "/api/status/inputs": "status_inputs.json",
}

# Generic success body for write endpoints (shape of rest_api.utils._json_response).
WRITE_OK = {"success": True, "data": {}, "error": None}


def load_fixture(name: str) -> dict[str, Any]:
    """Load a contract fixture (a full ``{success, data, error}`` body)."""
    return json.loads((FIXTURE_DIR / name).read_text(encoding="utf-8"))


class MockHub:
    """The hub's REST API as seen by the component, backed by ``aioclient_mock``."""

    def __init__(self, aioclient_mock: AiohttpClientMocker) -> None:
        self.mock = aioclient_mock
        self.responses: dict[str, dict[str, Any]] = {route: load_fixture(name) for route, name in READ_ROUTES.items()}
        self.status_codes: dict[str, int] = {}
        self.register()

    def register(self) -> None:
        """(Re)register every route. Clears the recorded calls."""
        self.mock.clear_requests()
        for route, body in self.responses.items():
            self.mock.get(f"{BASE_URL}{route}", json=body, status=self.status_codes.get(route, 200))
        # Any write endpoint succeeds.
        self.mock.post(_any_path(), json=WRITE_OK)

    def set_response(self, route: str, body: dict[str, Any] | None = None, status: int = 200) -> None:
        """Change what a read route returns (e.g. to simulate an error)."""
        if body is not None:
            self.responses[route] = body
        self.status_codes[route] = status
        self.register()

    def fixture_copy(self, route: str) -> dict[str, Any]:
        """Deep copy of the current body for ``route``, for editing."""
        return copy.deepcopy(self.responses[route])

    def posts(self, path: str) -> list[Any]:
        """JSON payloads of every POST made to ``path`` (payload is None if absent)."""
        return [
            data
            for method, url, data, _headers in self.mock.mock_calls
            if method.lower() == "post" and url.path == path
        ]


def _any_path():
    import re

    return re.compile(rf"^{re.escape(BASE_URL)}/api/.*")


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Allow loading custom_components/hdmi_matrix in every test."""
    return


@pytest.fixture
def hub(aioclient_mock: AiohttpClientMocker) -> MockHub:
    """Hub API mock that serves the contract fixtures."""
    return MockHub(aioclient_mock)


@pytest.fixture
def config_entry() -> MockConfigEntry:
    """A config entry for the matrix at HOST:PORT."""
    return MockConfigEntry(
        domain=DOMAIN,
        title=f"HDMI Matrix ({HOST})",
        data={"host": HOST, "port": PORT},
        unique_id=HOST,
    )


@pytest.fixture
async def setup_integration(hass: HomeAssistant, hub: MockHub, config_entry: MockConfigEntry) -> MockConfigEntry:
    """Set up the integration against the mocked hub and return the entry."""
    config_entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()
    return config_entry


def entity_id(hass: HomeAssistant, platform: str, unique_suffix: str) -> str:
    """Resolve an entity_id from the unique_id ``f"{HOST}_{unique_suffix}"``."""
    registry = er.async_get(hass)
    resolved = registry.async_get_entity_id(platform, DOMAIN, f"{HOST}_{unique_suffix}")
    assert resolved is not None, f"no {platform} entity with unique_id {HOST}_{unique_suffix}"
    return resolved
