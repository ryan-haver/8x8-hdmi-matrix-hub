"""Opt-in ambient legacy catalogs for combined suites (pytest -p this module)."""

import json

import pytest

CATALOGS = {
    "profiles.json": {"profiles": [{"id": "foreign", "name": "Foreign", "outputs": {}}]},
    "cec_macros.json": {"macros": [{"id": "foreign", "name": "Foreign", "steps": []}]},
    "scenes_v2.json": {"scenes": [{"id": "foreign", "name": "Foreign", "steps": []}]},
    "scenes.json": {"scenes": [{"id": "foreign", "name": "Foreign", "steps": []}]},
    "system_shortcuts.json": {"mute_all_audio": {"favorite": True, "dashboard_visible": True, "order": 99}},
    "shortcuts.json": {"mute_all_audio": {"label": "Foreign alias"}},
    "dashboard_layout.json": {"cards": [{"type": "profile", "id": "foreign", "order": 0}]},
    "device_settings.json": {"inputs": {"1": {"name": "Foreign"}}},
    "flic_buttons.json": {},
}


@pytest.fixture(scope="session", autouse=True)
def synthetic_ambient_legacy_sources(tmp_path_factory):
    """Exercise real suites with a populated, unrelated old installation present."""
    import persistence

    legacy = tmp_path_factory.mktemp("unrelated-installation")
    for name, payload in {**CATALOGS, "scenes.json": CATALOGS["scenes_v2.json"]}.items():
        (legacy / name).write_text(json.dumps(payload), encoding="utf-8")
    before = {p: p.read_bytes() for p in legacy.iterdir()}
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(persistence, "get_legacy_data_paths", lambda: [legacy])
        yield legacy
    assert {p: p.read_bytes() for p in legacy.iterdir()} == before
