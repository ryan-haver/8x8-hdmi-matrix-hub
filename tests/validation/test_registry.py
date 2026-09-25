"""The feature registry is complete, consistent and honest (docs/validation/features.yaml)."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from tools.validate.model import Level
from tools.validate.registry import (
    AREA_TARGETS,
    AREAS,
    Finding,
    load_features,
    load_findings,
    load_pending,
    parse_register,
    validate_features,
)
from tools.validate.scenarios import discover

ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture(scope="module")
def features():
    return load_features()


@pytest.fixture(scope="module")
def findings():
    return load_findings()


@pytest.fixture(scope="module")
def scenarios():
    return discover()


def _rest_entries(features) -> list[str]:
    return [r for f in features for r in f["interfaces"].get("rest", [])]


def test_registry_is_valid(features, findings, scenarios):
    assert validate_features(features, findings, set(scenarios)) == []


def test_ids_unique_and_every_area_present(features):
    ids = [f["id"] for f in features]
    assert len(ids) == len(set(ids))
    assert {f["area"] for f in features} == set(AREAS)
    assert len(features) >= 200


def test_every_finding_link_exists(features, findings):
    for f in features:
        for ref in f["findings"]:
            assert ref in findings, f"{f['id']}: {ref} missing from the register"


def test_open_critical_high_findings_cap_recorded_level(features, findings):
    for f in features:
        blocking = [x for x in f["findings"] if findings[x].blocking]
        if blocking:
            assert Level.parse(f["current"]) <= Level.V1, f"{f['id']} is above V1 despite {blocking}"


def test_scenario_links_are_symmetric(features, scenarios):
    by_id = {f["id"]: f for f in features}
    for sc in scenarios.values():
        for fid in sc.all_features:
            assert fid in by_id, f"scenario {sc.id} proves unknown feature {fid}"
            assert sc.id in by_id[fid]["scenarios"], f"{fid} does not list scenario {sc.id}"
    for f in features:
        for sid in f["scenarios"]:
            assert f["id"] in scenarios[sid].all_features, f"{f['id']} lists {sid}, which does not prove it"


def test_scenario_findings_exist(scenarios, findings):
    for sc in scenarios.values():
        for ref in sc.known_findings:
            assert ref in findings, f"scenario {sc.id} links unknown finding {ref}"


def test_targets_follow_the_plan(features):
    for f in features:
        target = Level.parse(f["target"])
        assert target >= AREA_TARGETS[f["area"]] or f.get("target_note"), f["id"]


# ------------------------------------------------------------------ completeness against the sources


def _route_covered(method: str, path: str, entries: list[str]) -> bool:
    for e in entries:
        if e.startswith("all "):
            continue
        m = re.match(r"^([A-Z|]+)\s+(\S+)", e)
        if m:
            methods, epath = m.group(1).split("|"), m.group(2).split("?")[0]
            if method in methods and epath == path:
                return True
            # "GET /api/system-shortcuts/favorites|dashboard" style alternatives in the last segment
            if method in methods and "|" in epath:
                head, _, alts = epath.rpartition("/")
                if any(f"{head}/{a}" == path for a in alts.split("|")):
                    return True
        # "/api/shortcuts* (10 aliases)"
        star = re.match(r"^(/\S+)\*", e)
        if star and path.startswith(star.group(1)):
            return True
    return False


def test_every_rest_route_is_in_the_registry(features):
    from tests.route_inventory import registered_routes

    entries = _rest_entries(features)
    assert not _route_covered("GET", "/api/does-not-exist", entries)
    assert not _route_covered("DELETE", "/api/switch", entries)
    missing = sorted(f"{m} {p}" for m, p in registered_routes() if not _route_covered(m, p, entries))
    assert missing == [], "REST routes without a feature: " + ", ".join(missing)


def test_every_ws_event_is_in_the_registry(features):
    sources = "\n".join(
        (ROOT / p).read_text(encoding="utf-8")
        for p in ("src/rest_api/websocket.py", "src/rest_api/control.py", "src/rest_api/outputs.py",
                  "src/rest_api/cec.py", "src/rest_api/device_settings.py", "src/rest_api/core.py",
                  "src/scene_execution.py", "src/driver.py")
    )
    emitted = set(re.findall(r'broadcast_status_update\(\s*"([a-z_]+)"', sources))
    emitted |= set(re.findall(r'"event":\s*"([a-z_]+)"', sources))
    declared = {e for f in features for e in f["interfaces"].get("ws", [])}
    assert emitted - declared == set(), f"WebSocket events without a feature: {sorted(emitted - declared)}"


def test_every_hub_comhead_is_in_the_registry(features):
    text = (ROOT / "src" / "orei_matrix.py").read_text(encoding="utf-8")
    comheads = set(re.findall(r'"comhead":\s*"([^"]+)"', text))
    declared = " ".join(e for f in features for e in f["interfaces"].get("device", []))
    missing = sorted(c for c in comheads if c not in declared)
    assert missing == [], f"comheads without a feature: {missing}"


def test_ha_services_and_entities_are_in_the_registry(features):
    services = re.findall(r"^([a-z_]+):", (ROOT / "custom_components/hdmi_matrix/services.yaml").read_text(encoding="utf-8"),
                          re.MULTILINE)
    declared = " ".join(e for f in features for e in f["interfaces"].get("ha", []))
    for s in services:
        assert f"hdmi_matrix.{s}" in declared, f"HA service {s} has no feature"
    for platform in ("select", "switch", "button", "binary_sensor"):
        assert f"{platform}." in declared, f"HA {platform} entities have no feature"


def test_ui_references_exist_in_the_catalog(features):
    catalog = (ROOT / "tests/e2e/visual/catalog.ts").read_text(encoding="utf-8")
    names = set(re.findall(r"name: '([^']+)'", catalog))
    templated = re.findall(r"name: `([^`]+)`", catalog)
    for f in features:
        for key in ("ui", "kiosk"):
            for entry in f["interfaces"].get(key, []):
                if "/" not in entry or " " in entry:
                    continue  # prose, not a catalog entry
                prefix_ok = any(entry.startswith(t.split("${")[0]) for t in templated)
                assert entry in names or prefix_ok, f"{f['id']}: {entry} is not a catalog entry"


# ------------------------------------------------------------------ register parsing


def test_register_parser_reads_every_section():
    findings = load_findings()
    for prefix in ("BE", "API", "PER", "SEC", "HA", "DEP", "TST", "UI", "DOC", "UC"):
        assert any(k.startswith(prefix + "-") for k in findings), prefix
    assert findings["BE-01"].severity == "C"
    assert findings["DOC-03"].severity == "—"


def test_register_closed_markers():
    text = "\n".join([
        "## 4. Findings register",
        "| ID | Sev | Finding | Location | Phase |",
        "| --- | --- | --- | --- | --- |",
        "| ~~BE-01~~ | C | fixed thing | x | 1 |",
        "| BE-02 | H | still open; mentions closed drawers and a falsely ✅ claim | x | 1 |",
        "| BE-03 | H | fixed via PR | x | 1 ✅ closed #12 |",
        "## 5. Something else",
        "| BE-99 | C | outside the register | x | 1 |",
    ])
    f = parse_register(text)
    assert not f["BE-01"].open and f["BE-02"].open and not f["BE-03"].open
    assert "BE-99" not in f


def test_pending_findings_are_well_formed():
    pending = load_pending()
    assert pending, "findings_pending.yaml should list the validation findings"
    for fid, f in pending.items():
        assert re.fullmatch(r"VAL-\d{2}", fid)
        assert f.severity in ("C", "H", "M", "L")
        assert isinstance(f, Finding) and f.text


def test_validator_flags_common_mistakes(findings):
    good = {
        "id": "F-MTX-900", "area": "matrix", "title": "t", "claim": "c", "interfaces": {"rest": ["GET /x"]},
        "target": "V4", "current": "V1", "basis": "b", "evidence": [], "findings": [], "scenarios": [],
    }
    assert validate_features([good], findings) == []
    bad_level = {**good, "current": "V2", "basis": "trust me"}
    assert any("basis" in p for p in validate_features([bad_level], findings))
    capped = {**good, "current": "V2", "basis": "tests/x.py", "findings": ["BE-01"]}
    assert any("cap it at V1" in p for p in validate_features([capped], findings))
    unknown = {**good, "findings": ["ZZ-01"]}
    assert any("ZZ-01" in p for p in validate_features([unknown], findings))
    dup = validate_features([good, good], findings)
    assert any("duplicate" in p for p in dup)
    wrong_prefix = {**good, "id": "F-CEC-900"}
    assert any("F-MTX-NNN" in p for p in validate_features([wrong_prefix], findings))
    low_target = {**good, "target": "V2"}
    assert any("target_note" in p for p in validate_features([low_target], findings))
    missing = {k: v for k, v in good.items() if k != "basis"}
    assert any("missing fields" in p for p in validate_features([missing], findings))
