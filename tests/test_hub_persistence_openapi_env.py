"""WP-C3: versioned persistence migrations, OpenAPI generation, canonical env vars.

Covers PER-04 / API-12 (backup-before-migrate on real legacy file shapes),
API-21 / TD-09 / DOC-03 (the OpenAPI 3.1 document generated from the live REST
app) and the canonical environment variable table with single-warning
deprecated aliases.

The migration fixtures below are the shapes older releases actually wrote: a
list-shaped ``flic_buttons.json``, a bare-list ``scenes_v2.json``, an unversioned
``profiles.json`` and friends.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from hub.env import (
    ALL_ENV_VARS,
    CORE_ENV_VARS,
    ENV_ALIASES,
    INTEGRATION_ENV_VARS,
    RETIRED_ENV_VARS,
    env_bool,
    env_var,
    resolve_hub_env,
)
from hub.openapi import (
    OPENAPI_VERSION,
    RouteInfo,
    build_openapi_spec,
    envelope_schema,
    route_inventory,
    security_schemes,
    spec_to_json,
    tag_for,
    validate_openapi_spec,
)
from hub.persistence import (
    CURRENT_SCHEMA_VERSION,
    LEGACY_FILENAMES,
    MANAGED_FILENAMES,
    SCHEMA_VERSION_KEY,
    MigrationError,
    MigrationRegistry,
    SchemaVersionError,
    backup_path_for,
    load_versioned_json,
    migrate_all_data_files,
    migrate_data_file,
    save_versioned_json,
)
from hub.persistence.migrations import DEFAULT_REGISTRY, build_default_registry

# ---------------------------------------------------------------------------
# Legacy fixtures: exactly what v0 wrote, one per managed file
# ---------------------------------------------------------------------------

LEGACY_FLIC_LIST: list[dict[str, Any]] = [
    {"bdaddr": "80:e4:da:70:00:01", "name": "Couch Button", "serial": "BG12-A00001"},
    {"name": "Kitchen Button", "address": "80:e4:da:70:00:02"},
    {"name": "No address at all"},
]

LEGACY_SCENES_LIST: list[dict[str, Any]] = [
    {
        "id": "scene_movienight01",
        "name": "Movie Night",
        "actions": [{"type": "macro", "id": "macro_tv_on"}],
        "favorite": True,
    }
]

LEGACY_PROFILES_ENVELOPE: dict[str, Any] = {
    "version": 1,
    "profiles": [
        {
            "id": "movie_night",
            "name": "Movie Night",
            "outputs": {"1": {"input": 2, "enabled": True, "audio_mute": False}},
        }
    ],
}

LEGACY_PROFILES_LIST: list[dict[str, Any]] = [{"id": "raw", "name": "Bare list profile"}]

LEGACY_MACROS_LIST: list[dict[str, Any]] = [
    {
        "id": "macro_all_off",
        "name": "All Off",
        "steps": [{"command": "POWER_OFF", "targets": ["output_1"], "delay_ms": "500"}],
    }
]

LEGACY_SHORTCUTS_LIST: list[dict[str, Any]] = [
    {"id": "builtin.all_to_out_1", "name": "All to Out 1", "order": "0"},
    {"key": "user.a1b2c3", "label": "Lights", "icon": "L", "order": 7},
]

LEGACY_LAYOUT_LIST: list[dict[str, Any]] = [
    {"type": "profile", "id": "movie_night"},
    {"type": "preset", "id": "2", "order": "5"},
]

LEGACY_DEVICE_SETTINGS_LISTS: dict[str, Any] = {
    "version": 1,
    "inputs": [{"port": 1, "name": "Apple TV"}],
    "outputs": [{"port": 2, "name": "Soundbar"}],
    "presets": [{"number": 3, "name": "PS5"}],
}


def write_json(path: Path, payload: Any) -> Path:
    """Write ``payload`` as JSON and return the path."""
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.fixture
def rest_app(tmp_path):
    """A real REST app, built the way the hub builds it."""
    from rest_api.app import create_rest_app

    return create_rest_app(tmp_path / "app-data")


@pytest.fixture(scope="module")
def spec() -> dict[str, Any]:
    """The generated document, built once from the hub's own route inventory."""
    return build_openapi_spec()


# ---------------------------------------------------------------------------
# Migration framework
# ---------------------------------------------------------------------------


def test_current_schema_version_is_two():
    assert CURRENT_SCHEMA_VERSION == 2


def test_every_managed_file_is_registered():
    registered = set(DEFAULT_REGISTRY.filenames())
    assert registered == set(MANAGED_FILENAMES)
    assert registered == {
        "scenes_v2.json",
        "profiles.json",
        "cec_macros.json",
        "shortcuts.json",
        "dashboard_layout.json",
        "device_settings.json",
        "flic_buttons.json",
    }


def test_registry_knows_the_retired_shortcut_filename():
    assert LEGACY_FILENAMES == {"system_shortcuts.json": "shortcuts.json"}
    assert DEFAULT_REGISTRY.resolve("system_shortcuts.json") == "shortcuts.json"
    assert DEFAULT_REGISTRY.has("system_shortcuts.json")
    assert not DEFAULT_REGISTRY.has("profiles_v9.json")


def test_detect_version_ignores_the_unrelated_version_key():
    """``version`` is a file-format marker some files carried; only schema_version counts."""
    registry = build_default_registry()
    assert registry.detect_version({"profiles": []}) == 0
    assert registry.detect_version({"version": 2, "profiles": []}) == 0
    assert registry.detect_version({"schema_version": 1, "profiles": []}) == 1
    assert registry.detect_version({"schema_version": True}) == 0
    assert registry.detect_version({"schema_version": -3}) == 0
    assert registry.detect_version([{"id": "x"}]) == 0


def test_a_registered_file_always_has_a_migration_for_every_version():
    for spec_ in (DEFAULT_REGISTRY.spec(name) for name in MANAGED_FILENAMES):
        assert spec_.versions == tuple(range(1, CURRENT_SCHEMA_VERSION + 1))


def test_apply_raises_for_a_file_from_a_newer_release():
    with pytest.raises(SchemaVersionError):
        DEFAULT_REGISTRY.apply("profiles.json", {"schema_version": CURRENT_SCHEMA_VERSION + 1})


def test_apply_rejects_a_payload_that_is_neither_object_nor_list():
    with pytest.raises(MigrationError):
        DEFAULT_REGISTRY.apply("profiles.json", "not a file")


def test_apply_stamps_the_current_version_and_keeps_unknown_keys():
    migrated, applied = DEFAULT_REGISTRY.apply(
        "profiles.json", {"profiles": [], "operator_note": "keep me"}
    )
    assert migrated[SCHEMA_VERSION_KEY] == CURRENT_SCHEMA_VERSION
    assert migrated["operator_note"] == "keep me"
    assert applied == [1, CURRENT_SCHEMA_VERSION]


def test_registering_a_gap_in_the_chain_is_rejected():
    registry = MigrationRegistry(current_version=2)
    with pytest.raises(ValueError, match="no migration to version 2"):
        registry.register("x.json", description="x", migrations=[(1, lambda payload: payload)])


def test_migration_path_skips_versions_already_applied():
    chain = DEFAULT_REGISTRY.migration_path("profiles.json", 1)
    assert [version for version, _ in chain] == [CURRENT_SCHEMA_VERSION]


# ---------------------------------------------------------------------------
# Backup before migrate (PER-04)
# ---------------------------------------------------------------------------


def test_backup_is_written_before_the_file_is_migrated(tmp_path):
    """The backup holds the pre-migration bytes, byte for byte."""
    path = write_json(tmp_path / "profiles.json", LEGACY_PROFILES_ENVELOPE)
    original = path.read_text(encoding="utf-8")

    result = migrate_data_file(path)

    assert result.migrated
    assert result.from_version == 0
    assert result.to_version == CURRENT_SCHEMA_VERSION
    assert result.backup == backup_path_for(path, 0) == tmp_path / "profiles.json.v0.bak"
    assert result.backup.read_text(encoding="utf-8") == original
    assert result.backup.parent == path.parent  # same directory, always


def test_backup_path_names_the_version_it_came_from(tmp_path):
    path = write_json(tmp_path / "profiles.json", {"schema_version": 1, "profiles": []})
    result = migrate_data_file(path)
    assert result.from_version == 1
    assert result.backup.name == "profiles.json.v1.bak"
    assert result.backup.exists()


def test_the_migrated_file_carries_the_current_schema_version(tmp_path):
    path = write_json(tmp_path / "profiles.json", LEGACY_PROFILES_ENVELOPE)
    migrate_data_file(path)
    assert read_json(path)[SCHEMA_VERSION_KEY] == CURRENT_SCHEMA_VERSION


def test_an_existing_backup_is_never_overwritten(tmp_path):
    """A second migration of the same version keeps the bytes the operator started from."""
    path = write_json(tmp_path / "profiles.json", LEGACY_PROFILES_ENVELOPE)
    original = path.read_text(encoding="utf-8")

    first = migrate_data_file(path)
    assert first.migrated
    # Put different v0 content back and migrate again: same target backup name.
    write_json(path, {"profiles": [{"id": "later", "name": "Written after the first migration"}]})
    second = migrate_data_file(path)

    assert second.migrated
    assert first.backup == second.backup
    assert second.backup.read_text(encoding="utf-8") == original
    assert read_json(path)["profiles"][0]["id"] == "later"


def test_backup_can_be_skipped(tmp_path):
    path = write_json(tmp_path / "profiles.json", LEGACY_PROFILES_ENVELOPE)
    result = migrate_data_file(path, backup=False)
    assert result.migrated
    assert result.backup is None
    assert list(tmp_path.glob("*.bak")) == []


def test_migrating_twice_is_a_no_op(tmp_path):
    path = write_json(tmp_path / "profiles.json", LEGACY_PROFILES_ENVELOPE)
    migrate_data_file(path)
    after_first = path.read_text(encoding="utf-8")

    again = migrate_data_file(path)

    assert again.status == "current"
    assert again.applied == ()
    assert path.read_text(encoding="utf-8") == after_first


def test_a_missing_file_is_reported_not_raised(tmp_path):
    result = migrate_data_file(tmp_path / "profiles.json")
    assert result.status == "missing"
    assert not result.migrated


def test_corrupt_json_is_left_untouched(tmp_path):
    path = tmp_path / "profiles.json"
    path.write_text("{not json", encoding="utf-8")

    result = migrate_data_file(path)

    assert result.status == "unreadable"
    assert path.read_text(encoding="utf-8") == "{not json"
    assert list(tmp_path.glob("*.bak")) == []


def test_a_file_from_a_newer_release_is_left_untouched(tmp_path):
    payload = {"schema_version": CURRENT_SCHEMA_VERSION + 5, "profiles": []}
    path = write_json(tmp_path / "profiles.json", payload)

    result = migrate_data_file(path)

    assert result.status == "unsupported"
    assert read_json(path) == payload
    assert list(tmp_path.glob("*.bak")) == []


def test_an_unmanaged_file_name_is_a_programming_error(tmp_path):
    path = write_json(tmp_path / "not_mine.json", {})
    with pytest.raises(KeyError):
        migrate_data_file(path)


# ---------------------------------------------------------------------------
# The legacy shapes, file by file
# ---------------------------------------------------------------------------


def test_list_shaped_flic_buttons_become_a_map_keyed_by_address(tmp_path):
    path = write_json(tmp_path / "flic_buttons.json", LEGACY_FLIC_LIST)

    migrate_data_file(path)
    migrated = read_json(path)

    assert migrated[SCHEMA_VERSION_KEY] == CURRENT_SCHEMA_VERSION
    assert set(migrated) - {SCHEMA_VERSION_KEY} == {"80:e4:da:70:00:01", "80:e4:da:70:00:02"}
    assert migrated["80:e4:da:70:00:01"]["serial"] == "BG12-A00001"
    # ``address`` is the legacy spelling of ``bdaddr``; a button without any
    # address cannot be addressed later, so it is dropped rather than invented.
    assert migrated["80:e4:da:70:00:02"]["bdaddr"] == "80:e4:da:70:00:02"


def test_flic_buttons_that_are_already_a_map_keep_their_entries(tmp_path):
    legacy = {"80:e4:da:70:00:01": {"bdaddr": "80:e4:da:70:00:01", "name": "Couch"}}
    path = write_json(tmp_path / "flic_buttons.json", legacy)

    migrate_data_file(path)

    migrated = read_json(path)
    assert migrated["80:e4:da:70:00:01"]["name"] == "Couch"
    assert migrated["80:e4:da:70:00:01"]["serial"] == ""


def test_bare_list_scenes_v2_is_wrapped_and_given_defaults(tmp_path):
    path = write_json(tmp_path / "scenes_v2.json", LEGACY_SCENES_LIST)

    migrate_data_file(path)
    scene = read_json(path)["scenes"][0]

    assert scene["id"] == "scene_movienight01"
    assert scene["steps"] == [{"type": "macro", "id": "macro_tv_on"}]  # from the legacy ``actions``
    assert scene["actions"] == scene["steps"]  # nothing is deleted
    assert scene["dashboard_visible"] is False
    assert scene["dashboard_order"] == 0
    assert scene["overrides"] == {}
    assert scene["execution_history"] == []


def test_unversioned_profiles_get_the_v2_fields(tmp_path):
    path = write_json(tmp_path / "profiles.json", LEGACY_PROFILES_ENVELOPE)

    migrate_data_file(path)
    payload = read_json(path)
    profile = payload["profiles"][0]

    assert payload["version"] == 1  # a pre-existing top-level key is left alone
    assert profile["pinned"] is True
    assert profile["pin_order"] == 0
    assert profile["password_protected"] is False
    assert profile["passcode_hash"] == ""
    assert profile["execution_log"] == []
    assert profile["outputs"]["1"]["input"] == 2


def test_bare_list_profiles_is_wrapped(tmp_path):
    path = write_json(tmp_path / "profiles.json", LEGACY_PROFILES_LIST)
    migrate_data_file(path)
    payload = read_json(path)
    assert [p["id"] for p in payload["profiles"]] == ["raw"]
    assert payload["version"] == 2


def test_bare_list_macros_are_wrapped_and_steps_normalised(tmp_path):
    path = write_json(tmp_path / "cec_macros.json", LEGACY_MACROS_LIST)

    migrate_data_file(path)
    macro = read_json(path)["macros"][0]

    assert macro["continue_on_error"] is False
    assert macro["steps"][0]["delay_ms"] == 500  # coerced from the string "500"
    assert macro["steps"][0]["command"] == "POWER_OFF"


def test_list_shaped_shortcuts_get_the_current_keys(tmp_path):
    path = write_json(tmp_path / "shortcuts.json", LEGACY_SHORTCUTS_LIST)

    migrate_data_file(path)
    shortcuts = read_json(path)
    records = {k: v for k, v in shortcuts.items() if k != SCHEMA_VERSION_KEY}

    assert set(records) == {"route_all_to_output", "user.a1b2c3"}  # all_to_out_1 renamed
    assert records["route_all_to_output"]["label"] == "All to Out 1"
    assert records["route_all_to_output"]["enabled"] is True
    assert records["user.a1b2c3"]["order"] == 7
    assert records["user.a1b2c3"]["params"] == {}


def test_the_retired_shortcut_filename_is_migrated_in_place(tmp_path):
    path = write_json(tmp_path / "system_shortcuts.json", LEGACY_SHORTCUTS_LIST)

    result = migrate_data_file(path)

    assert result.migrated
    assert path.name == "system_shortcuts.json"  # renamed on disk by nobody
    assert read_json(path)[SCHEMA_VERSION_KEY] == CURRENT_SCHEMA_VERSION
    assert (tmp_path / "system_shortcuts.json.v0.bak").exists()


def test_bare_list_dashboard_layout_is_wrapped(tmp_path):
    path = write_json(tmp_path / "dashboard_layout.json", LEGACY_LAYOUT_LIST)

    migrate_data_file(path)
    cards = read_json(path)["cards"]

    assert [c["id"] for c in cards] == ["movie_night", "2"]
    assert [c["order"] for c in cards] == [0, 5]  # coerced from "5"


def test_device_settings_port_lists_become_port_keyed_maps(tmp_path):
    path = write_json(tmp_path / "device_settings.json", LEGACY_DEVICE_SETTINGS_LISTS)

    migrate_data_file(path)
    settings = read_json(path)

    assert settings["inputs"] == {"1": {"name": "Apple TV"}}
    assert settings["outputs"] == {"2": {"name": "Soundbar"}}
    assert settings["presets"] == {"3": {"name": "PS5"}}
    assert settings["version"] == 1  # untouched


def test_migrations_never_drop_records_that_are_not_objects(tmp_path):
    path = write_json(tmp_path / "profiles.json", {"profiles": ["nonsense", None, {"id": "ok"}]})
    migrate_data_file(path)
    assert [p["id"] for p in read_json(path)["profiles"]] == ["ok"]


# ---------------------------------------------------------------------------
# Whole-directory migration and the load/save helpers
# ---------------------------------------------------------------------------


def test_migrate_all_data_files_covers_every_managed_file(tmp_path):
    write_json(tmp_path / "scenes_v2.json", LEGACY_SCENES_LIST)
    write_json(tmp_path / "profiles.json", LEGACY_PROFILES_LIST)
    write_json(tmp_path / "cec_macros.json", LEGACY_MACROS_LIST)
    write_json(tmp_path / "shortcuts.json", LEGACY_SHORTCUTS_LIST)
    write_json(tmp_path / "dashboard_layout.json", LEGACY_LAYOUT_LIST)
    write_json(tmp_path / "device_settings.json", LEGACY_DEVICE_SETTINGS_LISTS)
    write_json(tmp_path / "flic_buttons.json", LEGACY_FLIC_LIST)

    results = migrate_all_data_files(tmp_path)

    assert set(results) == set(MANAGED_FILENAMES)
    assert all(result.migrated for result in results.values())
    assert sorted(p.name for p in tmp_path.glob("*.bak")) == sorted(f"{n}.v0.bak" for n in MANAGED_FILENAMES)


def test_migrate_all_data_files_skips_what_is_not_there(tmp_path):
    write_json(tmp_path / "profiles.json", LEGACY_PROFILES_LIST)
    results = migrate_all_data_files(tmp_path)
    assert set(results) == {"profiles.json"}


def test_migrate_all_data_files_on_a_missing_directory_is_empty(tmp_path):
    assert migrate_all_data_files(tmp_path / "never-created") == {}


def test_migrate_all_data_files_accepts_an_explicit_filename_list(tmp_path):
    write_json(tmp_path / "profiles.json", LEGACY_PROFILES_LIST)
    write_json(tmp_path / "shortcuts.json", LEGACY_SHORTCUTS_LIST)
    results = migrate_all_data_files(tmp_path, filenames=["profiles.json"])
    assert set(results) == {"profiles.json"}


def test_load_versioned_json_returns_the_migrated_payload(tmp_path):
    write_json(tmp_path / "profiles.json", LEGACY_PROFILES_LIST)
    payload = load_versioned_json(tmp_path / "profiles.json")
    assert payload[SCHEMA_VERSION_KEY] == CURRENT_SCHEMA_VERSION
    assert payload["profiles"][0]["pinned"] is True
    assert (tmp_path / "profiles.json.v0.bak").exists()


def test_load_versioned_json_can_read_the_file_as_it_is(tmp_path):
    write_json(tmp_path / "profiles.json", LEGACY_PROFILES_LIST)
    payload = load_versioned_json(tmp_path / "profiles.json", migrate=False)
    assert SCHEMA_VERSION_KEY not in payload
    assert list(tmp_path.glob("*.bak")) == []


def test_load_versioned_json_returns_the_default_for_a_missing_file(tmp_path):
    assert load_versioned_json(tmp_path / "nope.json", default={"profiles": []}) == {"profiles": []}


def test_load_versioned_json_returns_the_default_for_corrupt_json(tmp_path):
    path = tmp_path / "profiles.json"
    path.write_text("{oops", encoding="utf-8")
    assert load_versioned_json(path, default={"profiles": []}) == {"profiles": []}


def test_load_versioned_json_ignores_a_file_it_does_not_manage(tmp_path):
    path = write_json(tmp_path / "security.json", {"api_keys": {}})
    assert load_versioned_json(path) == {"api_keys": {}}


def test_save_versioned_json_stamps_the_current_version(tmp_path):
    path = tmp_path / "profiles.json"
    assert save_versioned_json(path, {"profiles": [{"id": "x"}]})
    assert read_json(path) == {
        SCHEMA_VERSION_KEY: CURRENT_SCHEMA_VERSION,
        "profiles": [{"id": "x"}],
    }


def test_save_versioned_json_replaces_a_stale_stamp(tmp_path):
    path = write_json(tmp_path / "profiles.json", {"schema_version": 1, "profiles": []})
    save_versioned_json(path, {"schema_version": 0, "profiles": []})
    assert read_json(path)[SCHEMA_VERSION_KEY] == CURRENT_SCHEMA_VERSION


def test_save_versioned_json_refuses_a_non_object_payload(tmp_path):
    path = tmp_path / "profiles.json"
    assert save_versioned_json(path, [{"id": "x"}]) is False
    assert not path.exists()


def test_a_saved_file_needs_no_migration(tmp_path):
    path = tmp_path / "scenes_v2.json"
    save_versioned_json(path, {"scenes": []})
    assert migrate_data_file(path).status == "current"


def test_a_custom_registry_does_not_touch_the_default(tmp_path):
    path = write_json(tmp_path / "toy.json", {"schema_version": 0, "things": []})
    registry = MigrationRegistry(current_version=1)
    registry.register(
        "toy.json",
        description="toy",
        migrations=[(1, lambda payload: {"things": payload.get("things", []), "seen": True})],
    )

    result = migrate_data_file(path, registry=registry)

    assert result.migrated
    assert read_json(path) == {"schema_version": 1, "things": [], "seen": True}
    assert "toy.json" not in DEFAULT_REGISTRY.filenames()


# ---------------------------------------------------------------------------
# OpenAPI 3.1 (API-21, TD-09, DOC-03)
# ---------------------------------------------------------------------------


def test_the_generated_document_is_a_valid_openapi_31_document(spec):
    assert spec["openapi"] == OPENAPI_VERSION == "3.1.0"
    assert validate_openapi_spec(spec) == []


def test_the_specification_is_json_serialisable(spec):
    assert json.loads(spec_to_json(spec))["openapi"] == "3.1.0"


def test_info_carries_the_given_title_and_version(rest_app):
    document = build_openapi_spec(rest_app, title="Hub API", version="9.9.9")
    assert document["info"]["title"] == "Hub API"
    assert document["info"]["version"] == "9.9.9"


def test_the_envelope_schema_is_defined_and_complete(spec):
    envelope = spec["components"]["schemas"]["ApiResponseEnvelope"]
    assert envelope_schema() == envelope
    assert envelope["type"] == "object"
    assert set(envelope["properties"]) == {"success", "data", "error", "error_id"}
    assert envelope["properties"]["success"]["type"] == "boolean"
    assert envelope["properties"]["error"]["type"] == ["string", "null"]
    assert envelope["properties"]["error_id"]["type"] == ["string", "null"]


def test_the_three_security_schemes_are_defined(spec):
    schemes = spec["components"]["securitySchemes"]
    assert security_schemes() == schemes
    assert schemes["AdminSessionCookie"] == {
        "type": "apiKey",
        "in": "cookie",
        "name": "orei_session",
        "description": schemes["AdminSessionCookie"]["description"],
    }
    assert schemes["ControlApiKeyHeader"]["name"] == "X-API-Key"
    assert schemes["ControlApiKeyQuery"] == {
        "type": "apiKey",
        "in": "query",
        "name": "key",
        "description": schemes["ControlApiKeyQuery"]["description"],
    }


def test_paths_come_from_the_live_router(rest_app):
    """Every route the app registers is in the document, and nothing else is."""
    live = {(route.method, route.path) for route in route_inventory(rest_app)}
    assert live, "the app registers routes"
    assert ("GET", "/api/health") in live
    assert ("POST", "/api/output/{output}/source") in live

    documented = build_openapi_spec(rest_app)["paths"]
    assert live == {(method.upper(), path) for path, item in documented.items() for method in item}


def test_the_head_routes_aiohttp_adds_are_not_documented(spec):
    assert not any("head" in item for item in spec["paths"].values())


def test_path_parameters_are_declared_on_every_operation(spec):
    operation = spec["paths"]["/api/output/{output}/source"]["post"]
    parameters = {p["name"]: p for p in operation["parameters"]}
    assert parameters["output"]["in"] == "path"
    assert parameters["output"]["required"] is True


def test_a_regex_path_converter_does_not_reach_the_template(rest_app):
    """``/css/{path:.*}`` is documented as ``/css/{path}``: OpenAPI has no regex in a template."""
    document = build_openapi_spec(rest_app)
    assert "/css/{path}" in document["paths"]

    parameter = document["paths"]["/css/{path}"]["get"]["parameters"][0]
    assert parameter["name"] == "path"
    assert parameter["in"] == "path"
    assert parameter["schema"] == {"type": "string"}


def test_every_json_operation_answers_with_the_envelope(spec):
    for path, item in spec["paths"].items():
        if not path.startswith("/api"):
            continue
        for method, operation in item.items():
            schema = operation["responses"]["200"]["content"]["application/json"]["schema"]
            assert schema == {"$ref": "#/components/schemas/ApiResponseEnvelope"}, f"{method} {path}"


def test_the_web_ui_and_websocket_are_not_forced_into_the_envelope(spec):
    assert "content" not in spec["paths"]["/ws"]["get"]["responses"]["200"]
    assert "content" not in spec["paths"]["/ui"]["get"]["responses"]["200"]


def test_write_operations_document_a_request_body_and_the_auth_failures(spec):
    operation = spec["paths"]["/api/profile"]["post"]
    assert "application/json" in operation["requestBody"]["content"]
    assert {"401", "403"} <= set(operation["responses"])
    assert "401" not in spec["paths"]["/api/status"]["get"]["responses"]


def test_every_operation_carries_security_and_a_tag(spec):
    for path, item in spec["paths"].items():
        for method, operation in item.items():
            assert operation["tags"], f"{method} {path}"
            assert operation["operationId"], f"{method} {path}"
            if path.startswith("/api"):
                assert operation["security"] == [
                    {"AdminSessionCookie": []},
                    {"ControlApiKeyHeader": []},
                    {"ControlApiKeyQuery": []},
                ]


def test_operation_ids_are_unique(spec):
    ids = [operation["operationId"] for item in spec["paths"].values() for operation in item.values()]
    assert len(ids) == len(set(ids))


def test_tags_are_declared_and_match_the_operations(spec):
    declared = [tag["name"] for tag in spec["tags"]]
    used = {tag for item in spec["paths"].values() for op in item.values() for tag in op["tags"]}
    assert used <= set(declared)
    assert declared == sorted(declared, key=declared.index)  # stable, declared once each


@pytest.mark.parametrize(
    ("path", "expected"),
    [
        ("/api/status", "status"),
        ("/api/output/{output}/source", "matrix"),
        ("/api/v2/scenes/{scene_id}", "v2"),
        ("/api/cec/macros", "cec"),
        ("/api/ext-audio/mode", "audio"),
        ("/api/auth/status", "auth"),
        ("/ws", "websocket"),
        ("/ui", "web-ui"),
        ("/assets/logo.svg", "static"),
        ("/", "root"),
    ],
)
def test_tag_for_derives_the_tag_from_the_path(path, expected):
    assert tag_for(path) == expected


def test_route_inventory_reports_one_entry_per_method_and_path(rest_app):
    inventory = route_inventory(rest_app)
    assert inventory
    assert all(isinstance(route, RouteInfo) for route in inventory)
    assert inventory == sorted(inventory, key=lambda r: (r.method, r.path))
    assert len({(r.method, r.path) for r in inventory}) == len(inventory)


def test_build_openapi_spec_without_an_app_uses_the_hub_route_inventory(spec):
    """No argument means the document is built from the hub's own REST app."""
    assert spec["paths"]["/api/health"]["get"]["operationId"] == "get_api_health"
    assert len(spec["paths"]) > 50


def test_validate_rejects_a_document_that_is_not_openapi_31():
    assert validate_openapi_spec({"openapi": "3.0.0", "info": {}, "paths": {}})
    assert any("ApiResponseEnvelope" in problem for problem in validate_openapi_spec(
        {"openapi": "3.1.0", "info": {"title": "t", "version": "1"}, "paths": {}}
    ))


def test_validate_rejects_a_dangling_ref_and_an_undeclared_path_parameter():
    document = {
        "openapi": "3.1.0",
        "info": {"title": "t", "version": "1"},
        "paths": {"/a/{id}": {"get": {"operationId": "x", "responses": {"200": {}}}}},
        "components": {
            "schemas": {"ApiResponseEnvelope": {"type": "object"}},
            "securitySchemes": {
                "AdminSessionCookie": {},
                "ControlApiKeyHeader": {},
                "ControlApiKeyQuery": {},
            },
        },
    }
    problems = validate_openapi_spec(document)
    assert any("path parameter 'id' is not declared" in problem for problem in problems)

    document["paths"]["/a/{id}"]["get"]["responses"]["200"]["content"] = {
        "application/json": {"schema": {"$ref": "#/components/schemas/Nope"}}
    }
    assert any("unresolvable $ref" in problem for problem in validate_openapi_spec(document))


# ---------------------------------------------------------------------------
# Canonical environment variables (DI-12)
# ---------------------------------------------------------------------------


def test_the_core_and_integration_tables_cover_the_documented_variables():
    assert set(CORE_ENV_VARS) == {
        "MATRIX_HOST",
        "MATRIX_PORT",
        "MATRIX_USER",
        "MATRIX_PASSWORD",
        "MATRIX_VERIFY_TLS",
        "API_PORT",
        "DATA_DIR",
        "LOG_LEVEL",
        "ADMIN_PIN",
        "CONTROL_PIN",
        "ALLOWED_HOSTS",
        "CORS_ALLOWED_ORIGINS",
    }
    assert set(INTEGRATION_ENV_VARS) == {
        "UC_ENABLED",
        "UC_INTEGRATION_HTTP_PORT",
        "UC_INTEGRATION_INTERFACE",
        "UC_DISABLE_MDNS_PUBLISH",
        "UC_CONFIG_HOME",
        "UC_DRIVER_URL",
        "UC_AUTH_TOKEN",
        "FLIC_ENABLED",
        "HA_DISCOVERY_ENABLED",
    }
    assert set(ALL_ENV_VARS) == set(CORE_ENV_VARS) | set(INTEGRATION_ENV_VARS)


def test_every_variable_documents_itself():
    for name, var in ALL_ENV_VARS.items():
        assert var.name == name
        assert var.description.strip()
        assert var.kind in ("core", "integration")
        assert env_var(name) is var
    assert env_var("NOT_A_VARIABLE") is None


def test_secrets_are_marked_so_they_never_reach_a_doc_page():
    assert {name for name, var in ALL_ENV_VARS.items() if var.secret} == {
        "MATRIX_PASSWORD",
        "ADMIN_PIN",
        "CONTROL_PIN",
        "UC_AUTH_TOKEN",
    }


def test_the_documented_aliases_are_the_retired_spellings():
    assert ENV_ALIASES == {
        "MATRIX_HOST": ("OREI_HOST",),
        "MATRIX_PORT": ("OREI_PORT",),
        "API_PORT": ("REST_API_PORT", "OREI_API_PORT"),
        "DATA_DIR": ("MATRIX_DATA_DIR",),
        "UC_INTEGRATION_HTTP_PORT": ("UC_PORT",),
        "UC_DISABLE_MDNS_PUBLISH": ("UC_DISABLE_MDNS",),
    }
    assert set(RETIRED_ENV_VARS) == {"USE_MODULAR", "WEBUI_ENABLED"}
    for reason in RETIRED_ENV_VARS.values():
        assert reason.strip()


def test_every_alias_points_at_a_canonical_variable():
    for canonical, aliases in ENV_ALIASES.items():
        assert canonical in ALL_ENV_VARS
        for alias in aliases:
            assert alias not in ALL_ENV_VARS, alias
            assert alias.isupper()


def test_canonical_values_pass_through_unchanged():
    values, warnings = resolve_hub_env({"MATRIX_HOST": "10.0.0.5", "API_PORT": "9000"})
    assert values == {"MATRIX_HOST": "10.0.0.5", "API_PORT": "9000"}
    assert warnings == []


def test_unset_variables_are_absent_from_the_result():
    values, _ = resolve_hub_env({})
    assert values == {}


@pytest.mark.parametrize(
    ("alias", "canonical", "value"),
    [
        ("OREI_HOST", "MATRIX_HOST", "10.0.0.5"),
        ("OREI_PORT", "MATRIX_PORT", "8443"),
        ("REST_API_PORT", "API_PORT", "9000"),
        ("OREI_API_PORT", "API_PORT", "9001"),
        ("MATRIX_DATA_DIR", "DATA_DIR", "/data"),
        ("UC_PORT", "UC_INTEGRATION_HTTP_PORT", "9096"),
        ("UC_DISABLE_MDNS", "UC_DISABLE_MDNS_PUBLISH", "true"),
    ],
)
def test_each_deprecated_alias_is_honoured_with_one_warning(alias, canonical, value):
    values, warnings = resolve_hub_env({alias: value})
    assert values[canonical] == value
    assert warnings == [f"{alias} -> use {canonical}"]


def test_a_canonical_value_wins_over_its_alias():
    values, warnings = resolve_hub_env({"MATRIX_HOST": "10.0.0.5", "OREI_HOST": "10.0.0.9"})
    assert values["MATRIX_HOST"] == "10.0.0.5"
    assert warnings == ["OREI_HOST ignored (MATRIX_HOST is set)"]


def test_an_agreeing_alias_does_not_warn():
    values, warnings = resolve_hub_env({"API_PORT": "9000", "REST_API_PORT": "9000"})
    assert values["API_PORT"] == "9000"
    assert warnings == []


def test_an_empty_canonical_value_lets_the_alias_through():
    values, warnings = resolve_hub_env({"MATRIX_HOST": "   ", "OREI_HOST": "10.0.0.5"})
    assert values["MATRIX_HOST"] == "10.0.0.5"
    assert warnings == ["OREI_HOST -> use MATRIX_HOST"]


def test_the_first_of_several_api_port_aliases_wins_and_only_one_warns():
    values, warnings = resolve_hub_env({"REST_API_PORT": "9000", "OREI_API_PORT": "9001"})
    assert values["API_PORT"] == "9000"
    assert warnings == ["REST_API_PORT -> use API_PORT", "OREI_API_PORT ignored (API_PORT is set)"]


@pytest.mark.parametrize("name", sorted(RETIRED_ENV_VARS))
def test_a_retired_variable_warns_once_and_never_resolves(name):
    values, warnings = resolve_hub_env({name: "true"})
    assert name not in values
    assert warnings == [f"{name} is ignored ({RETIRED_ENV_VARS[name]})"]


def test_a_retired_variable_set_to_nothing_is_not_warned_about():
    _, warnings = resolve_hub_env({"USE_MODULAR": "", "WEBUI_ENABLED": "  "})
    assert warnings == []


def test_several_deprecated_names_each_get_exactly_one_warning():
    _, warnings = resolve_hub_env(
        {
            "OREI_HOST": "10.0.0.5",
            "REST_API_PORT": "9000",
            "USE_MODULAR": "true",
            "WEBUI_ENABLED": "false",
        }
    )
    assert warnings == [
        "OREI_HOST -> use MATRIX_HOST",
        "REST_API_PORT -> use API_PORT",
        "USE_MODULAR is ignored (the mode follows UC_ENABLED)",
        "WEBUI_ENABLED is ignored (the web UI and kiosk are part of the core and always served)",
    ]


def test_the_result_is_in_declaration_order():
    values, _ = resolve_hub_env({"UC_ENABLED": "true", "MATRIX_HOST": "10.0.0.5", "LOG_LEVEL": "DEBUG"})
    assert list(values) == ["MATRIX_HOST", "LOG_LEVEL", "UC_ENABLED"]


@pytest.mark.parametrize(
    ("value", "expected"),
    [("1", True), ("true", True), ("YES", True), ("on", True), ("0", False), ("false", False), ("off", False)],
)
def test_env_bool_reads_the_documented_spellings(value, expected):
    assert env_bool(value) is expected


def test_env_bool_falls_back_for_blank_and_unknown_values():
    assert env_bool(None, default=True) is True
    assert env_bool("   ", default=True) is True
    assert env_bool("maybe", default=True) is True
    assert env_bool("maybe") is False


def test_resolve_hub_env_matches_what_the_runtime_exported():
    """``run.py`` already resolves the same aliases; the two must not disagree."""
    import run

    environ = {"REST_API_PORT": "9000", "OREI_HOST": "10.0.0.5", "UC_PORT": "9096"}
    values, _ = resolve_hub_env(environ)
    settings = run.load_settings(environ)

    assert values["API_PORT"] == str(settings.api_port)
    assert values["MATRIX_HOST"] == settings.matrix_host
    assert values["UC_INTEGRATION_HTTP_PORT"] == str(settings.uc_port)
