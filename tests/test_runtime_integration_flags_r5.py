"""Tests for R5: Flic, UC, and HA integration flags, route inventories, and import boundaries."""

from __future__ import annotations

import logging
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from aiohttp import web
from aiohttp.test_utils import TestClient

from hub.runtime.integrations import bind_integrations, build_integration_loader
from rest_api.app import create_rest_app

# =============================================================================
# 1. Eight boolean combinations of (UC_ENABLED, FLIC_ENABLED, HA_DISCOVERY_ENABLED)
# =============================================================================

@pytest.mark.parametrize(
    "uc,flic,ha,expected_names",
    [
        (False, False, False, set()),
        (False, False, True, {"homeassistant"}),
        (False, True, False, {"flic"}),
        (False, True, True, {"flic", "homeassistant"}),
        (True, False, False, {"unfolded_circle"}),
        (True, False, True, {"unfolded_circle", "homeassistant"}),
        (True, True, False, {"unfolded_circle", "flic"}),
        (True, True, True, {"unfolded_circle", "flic", "homeassistant"}),
    ],
)
def test_all_eight_boolean_combinations(uc: bool, flic: bool, ha: bool, expected_names: set[str]):
    """Verify loader enables exact expected integrations for all 8 flag combinations."""
    environ = {
        "UC_ENABLED": "true" if uc else "false",
        "FLIC_ENABLED": "true" if flic else "false",
        "HA_DISCOVERY_ENABLED": "true" if ha else "false",
    }
    loader = build_integration_loader(environ)
    enabled_entries = loader.registry.enabled(loader.environ)
    assert {e.name for e in enabled_entries} == expected_names

    loaded = loader.load()
    assert set(loaded.keys()) == expected_names


# =============================================================================
# 2. Defaults when unset or blank
# =============================================================================

def test_flag_defaults_when_unset():
    """Unset flags default to: FLIC_ENABLED=True, UC_ENABLED=False, HA_DISCOVERY_ENABLED=False."""
    loader = build_integration_loader({})
    enabled_names = {e.name for e in loader.registry.enabled(loader.environ)}
    assert enabled_names == {"flic"}
    assert loader.environ["FLIC_ENABLED"] == "true"


def test_flag_defaults_when_blank():
    """Blank flags default to: FLIC_ENABLED=True, UC_ENABLED=False, HA_DISCOVERY_ENABLED=False."""
    environ = {"UC_ENABLED": "  ", "FLIC_ENABLED": " ", "HA_DISCOVERY_ENABLED": ""}
    loader = build_integration_loader(environ)
    enabled_names = {e.name for e in loader.registry.enabled(loader.environ)}
    assert enabled_names == {"flic"}
    assert loader.environ["FLIC_ENABLED"] == "true"


# =============================================================================
# 3. Explicit false spellings
# =============================================================================

@pytest.mark.parametrize("false_val", ["0", "false", "FALSE", "no", "NO", "off", "OFF", " false "])
def test_flic_explicit_false_spellings(false_val: str):
    """All explicit false spellings disable FLIC_ENABLED."""
    loader = build_integration_loader({"FLIC_ENABLED": false_val})
    enabled_names = {e.name for e in loader.registry.enabled(loader.environ)}
    assert "flic" not in enabled_names
    assert loader.environ["FLIC_ENABLED"] == "false"


@pytest.mark.parametrize("false_val", ["0", "false", "FALSE", "no", "NO", "off", "OFF", " false "])
def test_uc_and_ha_explicit_false_spellings(false_val: str):
    """All explicit false spellings keep UC and HA disabled."""
    loader = build_integration_loader({"UC_ENABLED": false_val, "HA_DISCOVERY_ENABLED": false_val})
    enabled_names = {e.name for e in loader.registry.enabled(loader.environ)}
    assert "unfolded_circle" not in enabled_names
    assert "homeassistant" not in enabled_names


# =============================================================================
# 4. Permissive non-blank Flic spelling with warning
# =============================================================================

@pytest.mark.parametrize("unrec_val", ["maybe", "enabled", "2", "foo"])
def test_flic_unrecognized_spelling_warns_and_retains_enabled(unrec_val: str, caplog):
    """Unrecognized non-blank FLIC_ENABLED values warn and retain enabled default."""
    with caplog.at_level(logging.WARNING):
        loader = build_integration_loader({"FLIC_ENABLED": unrec_val})
    assert any("Unrecognized FLIC_ENABLED spelling" in record.message for record in caplog.records)
    enabled_names = {e.name for e in loader.registry.enabled(loader.environ)}
    assert "flic" in enabled_names
    assert loader.environ["FLIC_ENABLED"] == "true"


# =============================================================================
# 5. Route counts and route absence
# =============================================================================

def test_routes_presence_when_flic_enabled():
    """When Flic is enabled, loader routes include register and buttons."""
    loader = build_integration_loader({"FLIC_ENABLED": "true"})
    loader.load()
    routes = loader.routes()
    paths = [r[1] for r in routes]
    assert "/api/integrations/flic/register" in paths
    assert "/api/integrations/flic/buttons" in paths
    assert len(routes) == 2


def test_routes_absence_when_flic_disabled():
    """When Flic is disabled, loader routes are empty."""
    loader = build_integration_loader({"FLIC_ENABLED": "false"})
    loader.load()
    routes = loader.routes()
    assert routes == []


def test_rest_app_route_inventory_with_flic_flag(tmp_path: Path):
    """create_rest_app route count reflects Flic flag (177 with Flic, 175 without)."""
    # 1. Enabled via environment (default)
    app_enabled = create_rest_app(data_dir=tmp_path, integration_routes=[
        ("POST", "/api/integrations/flic/register", MagicMock()),
        ("GET", "/api/integrations/flic/buttons", MagicMock()),
    ])
    routes_enabled = [r.resource.canonical for r in app_enabled.router.routes()]
    assert "/api/integrations/flic/register" in routes_enabled
    assert "/api/integrations/flic/buttons" in routes_enabled
    count_enabled = len(routes_enabled)

    # 2. Disabled via empty integration_routes
    app_disabled = create_rest_app(data_dir=tmp_path, integration_routes=[])
    routes_disabled = [r.resource.canonical for r in app_disabled.router.routes()]
    assert "/api/integrations/flic/register" not in routes_disabled
    assert "/api/integrations/flic/buttons" not in routes_disabled
    count_disabled = len(routes_disabled)

    assert count_enabled == count_disabled + 2
    # Verify core routes remain present regardless of Flic status
    for core_route in ["/api/switch", "/api/health", "/api/presets", "/api/power/on", "/api/status"]:
        assert core_route in routes_disabled
        assert core_route in routes_enabled


def test_standalone_rest_app_honors_flic_env_disable(tmp_path: Path, monkeypatch):
    """Standalone create_rest_app() with no runtime honors FLIC_ENABLED=false."""
    monkeypatch.setenv("FLIC_ENABLED", "false")
    app = create_rest_app(data_dir=tmp_path)
    routes = [r.resource.canonical for r in app.router.routes()]
    assert "/api/integrations/flic/register" not in routes
    assert "/api/integrations/flic/buttons" not in routes


def test_standalone_rest_app_honors_flic_env_default(tmp_path: Path, monkeypatch):
    """Standalone create_rest_app() with unset FLIC_ENABLED mounts Flic routes."""
    monkeypatch.delenv("FLIC_ENABLED", raising=False)
    app = create_rest_app(data_dir=tmp_path)
    routes = [r.resource.canonical for r in app.router.routes()]
    assert "/api/integrations/flic/register" in routes
    assert "/api/integrations/flic/buttons" in routes


# =============================================================================
# 6. Import trace proof: disabled integrations do not load their modules
# =============================================================================

def test_disabled_integrations_not_loaded(monkeypatch):
    """Disabled integrations are not loaded into memory by loader.load()."""
    loader = build_integration_loader({
        "UC_ENABLED": "false",
        "FLIC_ENABLED": "false",
        "HA_DISCOVERY_ENABLED": "false",
    })
    loaded = loader.load()
    assert loaded == {}
    assert loader.routes() == []
    assert loader.health_summary() == {}


# =============================================================================
# 7. One loaded registry: runtime registry is shared
# =============================================================================

def test_one_registry_shared_in_runtime():
    """bind_integrations syncs the active Flic registry across the runtime and rest_api."""
    from rest_api import integrations as rest_int

    loader = build_integration_loader({"FLIC_ENABLED": "true"})
    loader.load()
    flic_integration = loader.integrations["flic"]

    mock_runtime = MagicMock()
    mock_runtime.loader = loader
    mock_runtime.reconfigure = MagicMock()
    mock_runtime.address = None
    mock_runtime.driver_metadata = Path("driver.json")

    bind_integrations(loader, mock_runtime)

    # rest_api.integrations module should point to the exact same registry
    assert rest_int._default_registry is flic_integration.registry
    assert rest_int._default_integration is flic_integration
    assert rest_int._registered_buttons is flic_integration.registry._buttons


# =============================================================================
# 8. Preserved Flic auth/body contracts
# =============================================================================

@pytest.mark.asyncio
async def test_flic_route_auth_and_body_contract(aiohttp_client, tmp_path: Path):
    """Preserve exact request validation and response shapes for Flic endpoints."""
    loader = build_integration_loader({"FLIC_ENABLED": "true", "MATRIX_DATA_DIR": str(tmp_path)})
    loader.load()
    flic = loader.integrations["flic"]

    app = web.Application()
    for method, path, handler in flic.routes():
        app.router.add_route(method, path, handler)

    client: TestClient = await aiohttp_client(app)

    # 1. Invalid JSON body -> 400
    resp = await client.post(
        "/api/integrations/flic/register",
        data="not-json",
        headers={"Content-Type": "application/json"},
    )
    assert resp.status == 400
    data = await resp.json()
    assert data["success"] is False
    assert "Invalid JSON" in data["error"]

    # 2. Non-list buttons payload -> 400
    resp = await client.post(
        "/api/integrations/flic/register",
        json={"buttons": "not-a-list"},
    )
    assert resp.status == 400
    data = await resp.json()
    assert data["success"] is False
    assert "Invalid buttons payload" in data["error"]

    # 3. Valid registration -> 200 with count
    resp = await client.post(
        "/api/integrations/flic/register",
        json={"buttons": [{"bdaddr": "aa:bb:cc:dd:ee:01", "name": "Living Room", "serial": "S1"}]},
    )
    assert resp.status == 200
    data = await resp.json()
    assert data["success"] is True
    assert data["data"]["count"] == 1

    # 4. List buttons -> 200 with buttons list
    resp = await client.get("/api/integrations/flic/buttons")
    assert resp.status == 200
    data = await resp.json()
    assert data["success"] is True
    assert len(data["data"]["buttons"]) == 1
    assert data["data"]["buttons"][0]["name"] == "Living Room"
    assert data["data"]["buttons"][0]["bdaddr"] == "aa:bb:cc:dd:ee:01"
