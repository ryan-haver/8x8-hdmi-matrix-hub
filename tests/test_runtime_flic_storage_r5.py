"""R5 Flic Button Persistent Storage and R2 Boundary Tests.

Validates:
- Flic button storage using R2 safe persistence boundary (load_versioned_json, flat_map_records, save_versioned_json).
- schema_version and metadata exclusion from button listing, counting, and public APIs.
- Preservation of top-level metadata and private button extensions across saves.
- Strict public projection (bdaddr, name, serial only; no secrets or storage extensions).
- Write refusal on blocked paths (is_write_blocked) with transactional in-memory rollback.
- Safe handling of missing, corrupt, or future schema files.
- Single registry sharing between hub runtime and REST API layers.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from hub.integrations.flic import FlicButtonRegistry, FlicIntegration, FlicIntegrationConfig
from hub.persistence import (
    CURRENT_SCHEMA_VERSION,
    SCHEMA_VERSION_KEY,
    load_versioned_json,
    reset_preparation,
)
from hub.persistence.migrations import block_path


@pytest.fixture(autouse=True)
def clean_write_blocks():
    """Ensure any blocked paths are cleared after each test."""
    yield
    reset_preparation()


def test_empty_registry_initialization(tmp_path: Path):
    """When flic_buttons.json does not exist, registry initializes empty."""
    file_path = tmp_path / "flic_buttons.json"
    registry = FlicButtonRegistry(file_path=file_path)

    assert len(registry) == 0
    assert registry.list_buttons() == []
    assert not file_path.exists()


def test_register_buttons_creates_versioned_storage(tmp_path: Path):
    """Registering buttons saves a valid versioned JSON payload stamped with CURRENT_SCHEMA_VERSION."""
    file_path = tmp_path / "flic_buttons.json"
    registry = FlicButtonRegistry(file_path=file_path)

    count = registry.register_buttons([
        {"bdaddr": "aa:bb:cc:dd:ee:01", "name": "Living Room", "serial": "FL1001"},
        {"bdaddr": "aa:bb:cc:dd:ee:02", "name": "Kitchen", "serial": "FL1002"},
    ])

    assert count == 2
    assert len(registry) == 2
    assert file_path.exists()

    raw = json.loads(file_path.read_text(encoding="utf-8"))
    assert raw[SCHEMA_VERSION_KEY] == CURRENT_SCHEMA_VERSION
    assert "aa:bb:cc:dd:ee:01" in raw
    assert "aa:bb:cc:dd:ee:02" in raw
    assert raw["aa:bb:cc:dd:ee:01"]["name"] == "Living Room"
    assert raw["aa:bb:cc:dd:ee:02"]["serial"] == "FL1002"


def test_schema_version_and_metadata_skipped_in_listing_and_len(tmp_path: Path):
    """schema_version and top-level metadata keys are never treated or counted as buttons."""
    file_path = tmp_path / "flic_buttons.json"
    # Seed file directly with schema_version and metadata
    payload = {
        SCHEMA_VERSION_KEY: CURRENT_SCHEMA_VERSION,
        "site_id": "building-A",
        "description": "Smart button layout",
        "aa:bb:cc:dd:ee:01": {
            "bdaddr": "aa:bb:cc:dd:ee:01",
            "name": "Hallway",
            "serial": "FL1003",
        },
    }
    file_path.write_text(json.dumps(payload), encoding="utf-8")

    registry = FlicButtonRegistry(file_path=file_path)
    # len must be exactly 1 button, not 3 or 4
    assert len(registry) == 1

    buttons = registry.list_buttons()
    assert len(buttons) == 1
    assert buttons[0]["bdaddr"] == "aa:bb:cc:dd:ee:01"
    assert buttons[0]["name"] == "Hallway"

    # Verify no metadata leaked into buttons dict
    assert "schema_version" not in registry._buttons
    assert "site_id" not in registry._buttons
    assert "description" not in registry._buttons


def test_public_projection_omits_private_extensions(tmp_path: Path):
    """list_buttons projects only bdaddr, name, serial; private extensions are not exposed."""
    file_path = tmp_path / "flic_buttons.json"
    payload = {
        SCHEMA_VERSION_KEY: CURRENT_SCHEMA_VERSION,
        "aa:bb:cc:dd:ee:01": {
            "bdaddr": "aa:bb:cc:dd:ee:01",
            "name": "Office",
            "serial": "FL1004",
            "auth_token": "secret_token_12345",
            "battery_mv": 3050,
            "custom_payload": {"nested": "value"},
        },
    }
    file_path.write_text(json.dumps(payload), encoding="utf-8")

    registry = FlicButtonRegistry(file_path=file_path)
    buttons = registry.list_buttons()

    assert len(buttons) == 1
    button = buttons[0]
    # Only established public fields are present
    assert set(button.keys()) == {"bdaddr", "name", "serial"}
    assert button["bdaddr"] == "aa:bb:cc:dd:ee:01"
    assert button["name"] == "Office"
    assert button["serial"] == "FL1004"
    assert "auth_token" not in button
    assert "battery_mv" not in button
    assert "custom_payload" not in button


def test_private_extensions_preserved_across_save(tmp_path: Path):
    """When updating button fields, existing private storage extensions are preserved."""
    file_path = tmp_path / "flic_buttons.json"
    payload = {
        SCHEMA_VERSION_KEY: CURRENT_SCHEMA_VERSION,
        "aa:bb:cc:dd:ee:01": {
            "bdaddr": "aa:bb:cc:dd:ee:01",
            "name": "Office Old",
            "serial": "FL1005",
            "internal_flag": True,
            "private_id": 42,
        },
    }
    file_path.write_text(json.dumps(payload), encoding="utf-8")

    registry = FlicButtonRegistry(file_path=file_path)
    # Update public name and add a second button
    registry.register_buttons([
        {"bdaddr": "aa:bb:cc:dd:ee:01", "name": "Office Renamed", "serial": "FL1005"},
        {"bdaddr": "aa:bb:cc:dd:ee:02", "name": "Garage", "serial": "FL1006"},
    ])

    # Re-read raw disk contents
    raw = json.loads(file_path.read_text(encoding="utf-8"))
    assert raw["aa:bb:cc:dd:ee:01"]["name"] == "Office Renamed"
    # Private extensions must still be in the stored record!
    assert raw["aa:bb:cc:dd:ee:01"]["internal_flag"] is True
    assert raw["aa:bb:cc:dd:ee:01"]["private_id"] == 42


def test_top_level_metadata_preserved_across_save(tmp_path: Path):
    """Top-level custom metadata in flic_buttons.json is preserved when buttons are modified."""
    file_path = tmp_path / "flic_buttons.json"
    payload = {
        SCHEMA_VERSION_KEY: CURRENT_SCHEMA_VERSION,
        "region": "us-west",
        "custom_settings": {"timeout": 30},
        "aa:bb:cc:dd:ee:01": {
            "bdaddr": "aa:bb:cc:dd:ee:01",
            "name": "Basement",
            "serial": "FL1007",
        },
    }
    file_path.write_text(json.dumps(payload), encoding="utf-8")

    registry = FlicButtonRegistry(file_path=file_path)
    registry.register_buttons([
        {"bdaddr": "aa:bb:cc:dd:ee:02", "name": "Attic", "serial": "FL1008"},
    ])

    raw = json.loads(file_path.read_text(encoding="utf-8"))
    assert raw.get("region") == "us-west"
    assert raw.get("custom_settings") == {"timeout": 30}
    assert "aa:bb:cc:dd:ee:01" in raw
    assert "aa:bb:cc:dd:ee:02" in raw


def test_write_refusal_when_path_blocked(tmp_path: Path):
    """When persistence blocks writes, registry refuses to save and rolls back memory state."""
    file_path = tmp_path / "flic_buttons.json"
    registry = FlicButtonRegistry(file_path=file_path)
    registry.register_buttons([
        {"bdaddr": "aa:bb:cc:dd:ee:01", "name": "Initial", "serial": "FL01"},
    ])
    assert len(registry) == 1

    # Block write access via R2 mechanism
    block_path(file_path, "Simulated disk freeze / migration barrier")

    # save() returns False
    assert registry.save() is False

    # register_buttons raises RuntimeError and leaves in-memory state unchanged
    with pytest.raises(RuntimeError, match="Failed to save registered Flic buttons"):
        registry.register_buttons([
            {"bdaddr": "aa:bb:cc:dd:ee:02", "name": "Failed", "serial": "FL02"},
        ])

    # Memory state rolled back to previous
    assert len(registry) == 1
    assert "aa:bb:cc:dd:ee:02" not in registry._buttons


def test_corrupt_or_invalid_json_handling(tmp_path: Path):
    """Corrupted JSON on disk is handled without crashing; returns empty button set."""
    file_path = tmp_path / "flic_buttons.json"
    file_path.write_text("{invalid json truncated", encoding="utf-8")

    registry = FlicButtonRegistry(file_path=file_path)
    assert len(registry) == 0
    assert registry.list_buttons() == []


def test_future_schema_version_handling(tmp_path: Path):
    """Future schema version causes safe empty load rather than unhandled exception."""
    file_path = tmp_path / "flic_buttons.json"
    payload = {
        SCHEMA_VERSION_KEY: 9999,
        "aa:bb:cc:dd:ee:01": {"bdaddr": "aa:bb:cc:dd:ee:01", "name": "Future"},
    }
    file_path.write_text(json.dumps(payload), encoding="utf-8")

    registry = FlicButtonRegistry(file_path=file_path)
    assert len(registry) == 0
    assert registry.list_buttons() == []


def test_single_registry_shared_with_rest(tmp_path: Path):
    """The runtime Flic registry is directly shared with rest_api.integrations."""
    import rest_api.integrations as rest_int
    from hub.runtime.integrations import bind_integrations, build_integration_loader

    file_path = tmp_path / "flic_buttons.json"
    registry = FlicButtonRegistry(file_path=file_path)
    integration = FlicIntegration(
        config=FlicIntegrationConfig(enabled=True, data_dir=tmp_path),
        registry=registry,
    )

    loader = build_integration_loader({"FLIC_ENABLED": "true"})
    loader.load()
    # Inject our test registry into loader
    loader.integrations["flic"] = integration

    # Mock runtime with bind_integrations
    class MockRuntime:
        reconfigure = lambda self: None
        address = None
        driver_metadata = Path(".")

    bind_integrations(loader, MockRuntime())

    # Verify rest_api uses the exact same registry instance
    assert rest_int._default_registry is registry

    # Register via registry
    registry.register_buttons([
        {"bdaddr": "aa:bb:cc:dd:ee:99", "name": "Shared Button", "serial": "FL99"},
    ])

    # Must be visible in rest_api.integrations
    assert "aa:bb:cc:dd:ee:99" in rest_int._registered_buttons
    assert any(b["bdaddr"] == "aa:bb:cc:dd:ee:99" for b in rest_int._default_registry.list_buttons())
