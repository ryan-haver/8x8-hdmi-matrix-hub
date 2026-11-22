"""Tests for Flic and Home Assistant modular integrations, manifest.json, and template."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from aiohttp import web

# Ensure local hub package directories are discoverable even if hub was imported
# from the parent editable install.
_src_dir = Path(__file__).resolve().parent.parent / "src"
if str(_src_dir) not in sys.path:
    sys.path.insert(0, str(_src_dir))
try:
    import hub

    _local_hub_dir = str(_src_dir / "hub")
    if _local_hub_dir not in hub.__path__:
        hub.__path__.append(_local_hub_dir)
except ImportError:
    pass

from hub.integrations.flic import (
    FlicButtonRegistry,
    FlicIntegration,
    FlicIntegrationConfig,
)
from hub.integrations.homeassistant import (
    HomeAssistantDiscoveryConfig,
    HomeAssistantDiscoveryIntegration,
)
from rest_api import integrations as rest_integrations

# =============================================================================
# 1. FlicIntegrationConfig Tests
# =============================================================================


def test_flic_config_defaults():
    """FlicIntegrationConfig defaults to enabled=True with no data_dir."""
    config = FlicIntegrationConfig()
    assert config.enabled is True
    assert config.data_dir is None


def test_flic_config_from_env_defaults():
    """When FLIC_ENABLED is unset, it defaults to enabled=True."""
    config = FlicIntegrationConfig.config_from_env({})
    assert config.enabled is True
    assert config.data_dir is None


@pytest.mark.parametrize("val", ["false", "FALSE", "0", "no", "NO", "off", "OFF"])
def test_flic_config_from_env_disabled_variants(val: str):
    """Explicit falsy values disable Flic integration."""
    config = FlicIntegrationConfig.config_from_env({"FLIC_ENABLED": val})
    assert config.enabled is False


@pytest.mark.parametrize("val", ["true", "TRUE", "1", "yes", "YES", "on", "ON"])
def test_flic_config_from_env_enabled_variants(val: str):
    """Explicit truthy values keep Flic integration enabled."""
    config = FlicIntegrationConfig.config_from_env({"FLIC_ENABLED": val})
    assert config.enabled is True


def test_flic_config_from_env_matrix_data_dir(tmp_path: Path):
    """MATRIX_DATA_DIR env var is respected."""
    custom_dir = tmp_path / "matrix_custom"
    config = FlicIntegrationConfig.config_from_env({
        "FLIC_ENABLED": "1",
        "MATRIX_DATA_DIR": str(custom_dir),
    })
    assert config.enabled is True
    assert config.data_dir == custom_dir


def test_flic_config_from_env_uc_config_home(tmp_path: Path):
    """UC_CONFIG_HOME appends /data for data_dir."""
    uc_home = tmp_path / "uc_home"
    config = FlicIntegrationConfig.config_from_env({
        "FLIC_ENABLED": "true",
        "UC_CONFIG_HOME": str(uc_home),
    })
    assert config.enabled is True
    assert config.data_dir == uc_home / "data"


# =============================================================================
# 2. FlicButtonRegistry Tests
# =============================================================================


def test_flic_registry_filepath_custom(tmp_path: Path):
    """Registry resolves file path from custom data_dir."""
    reg = FlicButtonRegistry(data_dir=tmp_path)
    assert reg.file_path == tmp_path / "flic_buttons.json"


def test_flic_registry_load_empty_or_missing(tmp_path: Path):
    """Loading from a non-existent file results in an empty registry."""
    reg = FlicButtonRegistry(data_dir=tmp_path)
    reg.load_if_needed()
    assert reg.list_buttons() == []
    assert len(reg) == 0


def test_flic_registry_load_legacy_list(tmp_path: Path):
    """Registry converts legacy list format into dictionary keyed by bdaddr."""
    file_path = tmp_path / "flic_buttons.json"
    legacy_data = [
        {"bdaddr": "aa:bb:cc:11:22:33", "name": "Living Room", "serial": "S1"},
        {"bdaddr": "aa:bb:cc:22:33:44", "name": "Office", "serial": "S2"},
    ]
    file_path.write_text(json.dumps(legacy_data), encoding="utf-8")

    reg = FlicButtonRegistry(file_path=file_path)
    reg.load_if_needed()
    assert len(reg) == 2
    buttons = {b["bdaddr"]: b for b in reg.list_buttons()}
    assert buttons["aa:bb:cc:11:22:33"]["name"] == "Living Room"
    assert buttons["aa:bb:cc:22:33:44"]["name"] == "Office"


def test_flic_registry_register_new_buttons(tmp_path: Path):
    """Registering new buttons updates in-memory registry and persists atomically."""
    reg = FlicButtonRegistry(data_dir=tmp_path)
    payload = [
        {"bdaddr": "11:22:33:44:55:66", "name": "Bedroom", "serial": "B1"},
        {"bdaddr": "55:66:77:88:99:aa", "name": "Kitchen"},
    ]
    count = reg.register_buttons(payload)
    assert count == 2
    assert len(reg) == 2

    # Verify persisted content on disk
    persisted = json.loads(reg.file_path.read_text(encoding="utf-8"))
    assert "11:22:33:44:55:66" in persisted
    assert persisted["11:22:33:44:55:66"]["name"] == "Bedroom"
    assert persisted["55:66:77:88:99:aa"]["name"] == "Kitchen"


def test_flic_registry_register_update_name(tmp_path: Path):
    """Registering an existing button with a changed name updates it."""
    reg = FlicButtonRegistry(data_dir=tmp_path)
    reg.register_buttons([{"bdaddr": "11:22:33:44:55:66", "name": "Old Name"}])

    reg.register_buttons([{"bdaddr": "11:22:33:44:55:66", "name": "New Name"}])
    buttons = {b["bdaddr"]: b for b in reg.list_buttons()}
    assert buttons["11:22:33:44:55:66"]["name"] == "New Name"

    persisted = json.loads(reg.file_path.read_text(encoding="utf-8"))
    assert persisted["11:22:33:44:55:66"]["name"] == "New Name"


def test_flic_registry_register_identical_is_noop(tmp_path: Path):
    """Registering identical buttons does not trigger an atomic write."""
    reg = FlicButtonRegistry(data_dir=tmp_path)
    reg.register_buttons([{"bdaddr": "11:22:33:44:55:77", "name": "Button"}])
    mtime_before = reg.file_path.stat().st_mtime

    with patch.object(reg, "save", wraps=reg.save) as mock_save:
        reg.register_buttons([{"bdaddr": "11:22:33:44:55:77", "name": "Button"}])
        mock_save.assert_not_called()

    assert reg.file_path.stat().st_mtime == mtime_before


def test_flic_registry_register_invalid_payload(tmp_path: Path):
    """Passing a non-list to register_buttons raises ValueError."""
    reg = FlicButtonRegistry(data_dir=tmp_path)
    with pytest.raises(ValueError, match="Buttons payload must be a list"):
        reg.register_buttons({"not": "a list"})  # type: ignore[arg-type]


def test_flic_registry_save_failure_rolls_back(tmp_path: Path):
    """If saving fails, the in-memory registry rolls back to previous state."""
    reg = FlicButtonRegistry(data_dir=tmp_path)
    reg.register_buttons([{"bdaddr": "00:00:00:00:00:01", "name": "Original"}])

    with patch.object(reg, "save", return_value=False):
        with pytest.raises(RuntimeError, match="Failed to save registered Flic buttons"):
            reg.register_buttons([{"bdaddr": "00:00:00:00:00:02", "name": "New"}])

    # Memory state rolled back
    assert len(reg) == 1
    assert "00:00:00:00:00:02" not in [b["bdaddr"] for b in reg.list_buttons()]


# =============================================================================
# 3. FlicIntegration Lifecycle & Health Tests
# =============================================================================


def test_flic_integration_metadata():
    """FlicIntegration specifies name='flic' and env_flag='FLIC_ENABLED'."""
    assert FlicIntegration.name == "flic"
    assert FlicIntegration.env_flag == "FLIC_ENABLED"


@pytest.mark.asyncio
async def test_flic_integration_lifecycle(tmp_path: Path):
    """FlicIntegration start loads the registry and stop clears client."""
    file_path = tmp_path / "flic_buttons.json"
    file_path.write_text(json.dumps({"00:00:00:00:00:03": {"bdaddr": "00:00:00:00:00:03", "name": "B1"}}), encoding="utf-8")

    registry = FlicButtonRegistry(file_path=file_path)
    integration = FlicIntegration(registry=registry)

    mock_client = MagicMock()
    await integration.start(mock_client)
    assert integration.hub_client is mock_client
    assert len(integration.registry) == 1

    await integration.stop()
    assert integration.hub_client is None


def test_flic_integration_health(tmp_path: Path):
    """health() reports status, enabled flag, and button count."""
    registry = FlicButtonRegistry(data_dir=tmp_path)
    registry.register_buttons([{"bdaddr": "00:00:00:00:00:03", "name": "B1"}])

    integration = FlicIntegration(config=FlicIntegrationConfig(enabled=True), registry=registry)
    h = integration.health()
    assert h["status"] == "ok"
    assert h["enabled"] is True
    assert h["registered_buttons_count"] == 1

    disabled_integration = FlicIntegration(config=FlicIntegrationConfig(enabled=False), registry=registry)
    dh = disabled_integration.health()
    assert dh["status"] == "disabled"
    assert dh["enabled"] is False
    assert dh["registered_buttons_count"] == 0


def test_flic_integration_routes_declaration():
    """routes() returns register and buttons route specifications."""
    integration = FlicIntegration()
    routes = integration.routes()
    assert len(routes) == 2
    methods = [r[0] for r in routes]
    paths = [r[1] for r in routes]
    assert "POST" in methods
    assert "GET" in methods
    assert "/api/integrations/flic/register" in paths
    assert "/api/integrations/flic/buttons" in paths


# =============================================================================
# 4. FlicIntegration Route Handler Tests (aiohttp)
# =============================================================================


@pytest.mark.asyncio
async def test_flic_routes_register_and_get(aiohttp_client, tmp_path: Path):
    """Integration routes handle POST registration and GET buttons list."""
    registry = FlicButtonRegistry(data_dir=tmp_path)
    integration = FlicIntegration(registry=registry)

    app = web.Application()
    for method, path, handler in integration.routes():
        app.router.add_route(method, path, handler)

    client = await aiohttp_client(app)

    # 1. GET initial (empty)
    resp = await client.get("/api/integrations/flic/buttons")
    assert resp.status == 200
    data = await resp.json()
    assert data["success"] is True
    assert data["data"]["buttons"] == []

    # 2. POST valid buttons
    payload = {"buttons": [{"bdaddr": "00:00:00:00:00:04", "name": "TV Power", "serial": "111"}]}
    post_resp = await client.post("/api/integrations/flic/register", json=payload)
    assert post_resp.status == 200
    post_data = await post_resp.json()
    assert post_data["success"] is True
    assert post_data["data"]["count"] == 1

    # 3. GET updated buttons
    get_resp = await client.get("/api/integrations/flic/buttons")
    assert get_resp.status == 200
    get_data = await get_resp.json()
    assert len(get_data["data"]["buttons"]) == 1
    assert get_data["data"]["buttons"][0]["name"] == "TV Power"

    # 4. POST invalid payload (buttons is not list)
    bad_resp = await client.post("/api/integrations/flic/register", json={"buttons": "not_a_list"})
    assert bad_resp.status == 400
    bad_data = await bad_resp.json()
    assert bad_data["success"] is False
    assert "Invalid buttons payload" in bad_data["error"]


# =============================================================================
# 5. rest_api/integrations.py Backward Compatibility Tests
# =============================================================================


@pytest.mark.asyncio
async def test_rest_api_integrations_routes(aiohttp_client, tmp_path: Path):
    """rest_api.integrations module handlers function properly with aiohttp."""
    file_path = tmp_path / "flic_buttons.json"
    rest_integrations._default_registry = FlicButtonRegistry(file_path=file_path)
    rest_integrations._default_integration = FlicIntegration(registry=rest_integrations._default_registry)
    rest_integrations._registered_buttons = rest_integrations._default_registry._buttons
    rest_integrations._loaded = False

    app = web.Application()
    app.router.add_post("/api/integrations/flic/register", rest_integrations.handle_register_flic_buttons)
    app.router.add_get("/api/integrations/flic/buttons", rest_integrations.handle_get_flic_buttons)

    client = await aiohttp_client(app)

    post_resp = await client.post(
        "/api/integrations/flic/register",
        json={"buttons": [{"bdaddr": "00:00:00:00:00:05", "name": "Living Room"}]},
    )
    assert post_resp.status == 200
    post_data = await post_resp.json()
    assert post_data["success"] is True
    assert post_data["data"]["count"] == 1

    get_resp = await client.get("/api/integrations/flic/buttons")
    assert get_resp.status == 200
    get_data = await get_resp.json()
    assert get_data["success"] is True
    assert len(get_data["data"]["buttons"]) == 1
    assert get_data["data"]["buttons"][0]["bdaddr"] == "00:00:00:00:00:05"


def test_rest_api_integrations_global_compatibility(tmp_path: Path):
    """rest_api.integrations preserves module globals and functions for existing tests."""
    file_path = tmp_path / "flic_buttons.json"
    rest_integrations._default_registry = FlicButtonRegistry(file_path=file_path)
    rest_integrations._registered_buttons = {"00:00:00:00:00:06": {"bdaddr": "00:00:00:00:00:06", "name": "Legacy"}}
    assert rest_integrations._save_buttons() is True

    # Check file on disk
    loaded = json.loads(file_path.read_text(encoding="utf-8"))
    assert "00:00:00:00:00:06" in loaded

    # Reset in-memory state and reload
    rest_integrations._registered_buttons = {}
    rest_integrations._loaded = False
    rest_integrations._load_buttons_if_needed()
    assert "00:00:00:00:00:06" in rest_integrations._registered_buttons


# =============================================================================
# 6. HomeAssistantDiscoveryConfig Tests
# =============================================================================


def test_ha_config_defaults():
    """HomeAssistantDiscoveryConfig defaults to disabled and port 8080."""
    cfg = HomeAssistantDiscoveryConfig()
    assert cfg.enabled is False
    assert cfg.api_port == 8080
    assert cfg.host_ip is None
    assert cfg.service_name == "OREI HDMI Matrix Hub"


def test_ha_config_from_env_enabled():
    """Config parses HA_DISCOVERY_ENABLED, API_PORT, HOST_IP, and service name."""
    cfg = HomeAssistantDiscoveryConfig.config_from_env({
        "HA_DISCOVERY_ENABLED": "true",
        "API_PORT": "9090",
        "HOST_IP": "192.168.1.150",
        "HA_DISCOVERY_SERVICE_NAME": "My Matrix Hub",
    })
    assert cfg.enabled is True
    assert cfg.api_port == 9090
    assert cfg.host_ip == "192.168.1.150"
    assert cfg.service_name == "My Matrix Hub"


def test_ha_config_from_env_port_fallback():
    """Invalid port falls back to 8080."""
    cfg = HomeAssistantDiscoveryConfig.config_from_env({
        "API_PORT": "invalid-port",
    })
    assert cfg.api_port == 8080


# =============================================================================
# 7. HomeAssistantDiscoveryIntegration Lifecycle & Health Tests
# =============================================================================


def test_ha_integration_metadata():
    """HomeAssistantDiscoveryIntegration specifies name and env_flag."""
    assert HomeAssistantDiscoveryIntegration.name == "homeassistant"
    assert HomeAssistantDiscoveryIntegration.env_flag == "HA_DISCOVERY_ENABLED"


def test_ha_build_zeroconf_properties_default():
    """build_zeroconf_properties returns standard service properties."""
    integration = HomeAssistantDiscoveryIntegration(
        config=HomeAssistantDiscoveryConfig(api_port=8080)
    )
    props = integration.build_zeroconf_properties()
    assert props["service"] == "orei_hdmi_matrix"
    assert props["api_port"] == "8080"
    assert props["path"] == "/api"
    assert "version" in props


def test_ha_build_zeroconf_properties_with_snapshot():
    """build_zeroconf_properties extracts connected, power, and mac from snapshot."""
    integration = HomeAssistantDiscoveryIntegration()
    snapshot = MagicMock()
    snapshot.connected = True
    snapshot.power = True
    snapshot.mac = "00:11:22:33:44:55"

    props = integration.build_zeroconf_properties(snapshot=snapshot)
    assert props["connected"] == "true"
    assert props["power"] == "true"
    assert props["mac"] == "00:11:22:33:44:55"


@pytest.mark.asyncio
async def test_ha_start_when_disabled_is_noop():
    """When disabled, start() performs no zeroconf operations."""
    mock_zc = MagicMock()
    mock_zc.async_register_service = AsyncMock()

    integration = HomeAssistantDiscoveryIntegration(
        config=HomeAssistantDiscoveryConfig(enabled=False),
        zeroconf=mock_zc,
    )
    await integration.start(MagicMock())
    mock_zc.async_register_service.assert_not_called()
    assert integration.health()["registered"] is False


@pytest.mark.asyncio
async def test_ha_start_and_stop_lifecycle_with_mock():
    """When enabled, start() registers service and stop() unregisters."""
    mock_zc = MagicMock()
    mock_zc.async_register_service = AsyncMock()
    mock_zc.async_unregister_service = AsyncMock()
    mock_zc.async_close = AsyncMock()

    cfg = HomeAssistantDiscoveryConfig(enabled=True, api_port=8080, host_ip="192.168.1.100")
    integration = HomeAssistantDiscoveryIntegration(config=cfg, zeroconf=mock_zc)

    hub_mock = MagicMock()
    await integration.start(hub_mock)

    assert mock_zc.async_register_service.called
    info_arg = mock_zc.async_register_service.call_args[0][0]
    assert info_arg.type == "_orei-hdmi-matrix._tcp.local."
    assert info_arg.port == 8080
    assert integration.health()["registered"] is True

    await integration.stop()
    mock_zc.async_unregister_service.assert_called_once()
    assert integration.health()["registered"] is False


@pytest.mark.asyncio
async def test_ha_start_handles_zeroconf_exception_gracefully():
    """If zeroconf fails during registration, start handles it without raising."""
    mock_zc = MagicMock()
    mock_zc.async_register_service = AsyncMock(side_effect=RuntimeError("Zeroconf failure"))

    cfg = HomeAssistantDiscoveryConfig(enabled=True)
    integration = HomeAssistantDiscoveryIntegration(config=cfg, zeroconf=mock_zc)

    # Should not raise exception
    await integration.start(MagicMock())
    assert integration.health()["registered"] is False
    assert integration.health()["status"] == "error"


# =============================================================================
# 8. Manifest.json Hassfest Ordering & Zeroconf Entry Tests
# =============================================================================


def test_manifest_json_exists():
    """custom_components/hdmi_matrix/manifest.json must exist."""
    root = Path(__file__).resolve().parent.parent
    manifest_path = root / "custom_components" / "hdmi_matrix" / "manifest.json"
    assert manifest_path.exists(), f"manifest.json not found at {manifest_path}"


def test_manifest_json_hassfest_key_ordering():
    """Hassfest requires domain and name first, followed by alphabetically sorted keys."""
    root = Path(__file__).resolve().parent.parent
    manifest_path = root / "custom_components" / "hdmi_matrix" / "manifest.json"
    content = manifest_path.read_text(encoding="utf-8")

    # Load with raw ordered pairs
    raw_dict = json.loads(content)
    keys = list(raw_dict.keys())

    assert keys[0] == "domain", "First key must be 'domain'"
    assert keys[1] == "name", "Second key must be 'name'"

    subsequent_keys = keys[2:]
    sorted_subsequent = sorted(subsequent_keys)
    assert subsequent_keys == sorted_subsequent, (
        f"Keys after 'domain' and 'name' must be alphabetically sorted: {subsequent_keys} != {sorted_subsequent}"
    )


def test_manifest_json_zeroconf_entry():
    """HomeAssistantDiscoveryIntegration SERVICE_TYPE matches _orei-hdmi-matrix._tcp.local."""
    from src.hub.integrations.homeassistant import SERVICE_TYPE

    assert SERVICE_TYPE == "_orei-hdmi-matrix._tcp.local."


# =============================================================================
# 9. docs/INTEGRATION_TEMPLATE.md Content Tests
# =============================================================================


def test_integration_template_doc_completeness():
    """docs/INTEGRATION_TEMPLATE.md must contain all required sections and methods."""
    root = Path(__file__).resolve().parent.parent
    doc_path = root / "docs" / "INTEGRATION_TEMPLATE.md"
    assert doc_path.exists(), "docs/INTEGRATION_TEMPLATE.md must exist"

    text = doc_path.read_text(encoding="utf-8")
    assert "config_from_env" in text
    assert "async def start" in text
    assert "async def stop" in text
    assert "def health" in text
    assert "routes" in text
    assert "HubClient" in text
