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
import re
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
#: The matrix MAC in the contract fixture (status_device.json), as Home Assistant formats it.
MAC = "02:00:00:0b:08:08"

# Hub routes the component reads, and the contract fixture for each.
READ_ROUTES = {
    "/api/health": "health.json",
    "/api/status": "status.json",
    "/api/status/outputs": "status_outputs.json",
    "/api/status/inputs": "status_inputs.json",
    "/api/status/device": "status_device.json",
}

# Generic success body for write endpoints (shape of rest_api.utils._json_response).
WRITE_OK = {"success": True, "data": {}, "error": None}


def load_fixture(name: str) -> dict[str, Any]:
    """Load a contract fixture (a full ``{success, data, error}`` body)."""
    return json.loads((FIXTURE_DIR / name).read_text(encoding="utf-8"))


def _route(path: str) -> re.Pattern[str]:
    """Any hub host/port, exactly this path (so tests can add a second hub)."""
    return re.compile(rf"^http://[^/]+{re.escape(path)}$")


class MockHub:
    """The hub's REST API as seen by the component, backed by ``aioclient_mock``."""

    def __init__(self, aioclient_mock: AiohttpClientMocker) -> None:
        self.mock = aioclient_mock
        self.responses: dict[str, dict[str, Any]] = {route: load_fixture(name) for route, name in READ_ROUTES.items()}
        self.status_codes: dict[str, int] = {}
        self.read_exc: dict[str, Exception] = {}
        self.post_overrides: dict[str, dict[str, Any]] = {}
        #: ``{(base_url, route): body}``: what one particular hub answers (a second matrix).
        self.host_responses: dict[tuple[str, str], dict[str, Any]] = {}
        self.register()

    def register(self) -> None:
        """(Re)register every route. Clears the recorded calls."""
        self.mock.clear_requests()
        for (base_url, route), body in self.host_responses.items():
            self.mock.get(f"{base_url}{route}", json=body)
        for route, body in self.responses.items():
            if route in self.read_exc:
                self.mock.get(_route(route), exc=self.read_exc[route])
            else:
                self.mock.get(_route(route), json=body, status=self.status_codes.get(route, 200))
        for path, kwargs in self.post_overrides.items():
            self.mock.post(_route(path), **kwargs)
        # Any other write endpoint succeeds.
        self.mock.post(re.compile(r"^http://[^/]+/api/.*"), json=WRITE_OK)

    def set_response(self, route: str, body: dict[str, Any] | None = None, status: int = 200) -> None:
        """Change what a read route returns (e.g. to simulate an error)."""
        if body is not None:
            self.responses[route] = body
        self.status_codes[route] = status
        self.read_exc.pop(route, None)
        self.register()

    def set_read_error(self, route: str, exc: Exception) -> None:
        """Make a read route fail at the network level."""
        self.read_exc[route] = exc
        self.register()

    def set_post(self, path: str, body: dict[str, Any] | None = None, status: int = 200,
                 exc: Exception | None = None) -> None:
        """Make one write endpoint answer differently (error body, HTTP status, network error)."""
        self.post_overrides[path] = {"exc": exc} if exc is not None else {"json": body, "status": status}
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

    def all_posts(self) -> list[str]:
        return [url.path for method, url, _d, _h in self.mock.mock_calls if method.lower() == "post"]


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
    """A config entry for the matrix behind the hub at HOST:PORT (unique id: the matrix MAC)."""
    return MockConfigEntry(
        domain=DOMAIN,
        title=f"HDMI Matrix ({HOST})",
        data={"host": HOST, "port": PORT},
        unique_id=MAC,
    )


@pytest.fixture
async def setup_integration(hass: HomeAssistant, hub: MockHub, config_entry: MockConfigEntry) -> MockConfigEntry:
    """Set up the integration against the mocked hub and return the entry."""
    config_entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()
    return config_entry


def entity_id(hass: HomeAssistant, platform: str, unique_suffix: str, prefix: str = MAC) -> str:
    """Resolve an entity_id from the unique_id ``f"{prefix}_{unique_suffix}"``."""
    registry = er.async_get(hass)
    resolved = registry.async_get_entity_id(platform, DOMAIN, f"{prefix}_{unique_suffix}")
    assert resolved is not None, f"no {platform} entity with unique_id {prefix}_{unique_suffix}"
    return resolved


def coordinator(entry: MockConfigEntry):
    """The entry's coordinator (``entry.runtime_data``, HA-07)."""
    return entry.runtime_data.coordinator


async def refresh(hass: HomeAssistant, entry: MockConfigEntry) -> None:
    await coordinator(entry).async_refresh()
    await hass.async_block_till_done()
