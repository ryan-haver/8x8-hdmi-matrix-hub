"""Evidence records match docs/validation/evidence.schema.json (VALIDATION_PLAN §4)."""

from __future__ import annotations

import json

import pytest

from tools.validate.evidence import COMMITTED_EVIDENCE, SCHEMA_PATH, iter_records, record_filename, redact, write_record

from .helpers import make_record

jsonschema = pytest.importorskip("jsonschema")


@pytest.fixture(scope="module")
def validator():
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator.check_schema(schema)
    return jsonschema.Draft202012Validator(schema)


def test_valid_record(validator):
    assert list(validator.iter_errors(make_record())) == []


@pytest.mark.parametrize(
    ("over", "fragment"),
    [
        ({"level": "V1"}, "level"),
        ({"features": []}, "features"),
        ({"features": ["MTX-1"]}, "features"),
        ({"result": "ok"}, "result"),
        ({"scenario": "no-dot"}, "scenario"),
        ({"covers": []}, "covers"),
        ({"gate": "known-failure"}, "gate"),  # a pass is always gate ok
        ({"target": "hardware", "level": "V2"}, "level"),  # hardware evidence is V4
        ({"target": "hardware", "level": "V4"}, "operator"),  # and attested by a person
        ({"unexpected": 1}, "unexpected"),
    ],
)
def test_invalid_records(validator, over, fragment):
    errors = list(validator.iter_errors(make_record(**over)))
    assert errors, f"{over} should be rejected ({fragment})"


def test_hardware_record_with_operator(validator):
    rec = make_record(target="hardware", level="V4", operator="Ryan",
                      environment={"target": "hardware", "matrix": {"firmware_version": "V1.10.02"}})
    rec["environment"].pop("simulator")
    rec["observations"]["operator"] = [{"question": "Does TV show it?", "answer": "y", "media": ["img.jpg"],
                                        "at": "2026-09-25T10:00:00Z", "confirmed": True}]
    assert list(validator.iter_errors(rec)) == []


def test_write_and_load_round_trip(tmp_path):
    rec = make_record(features=["F-MTX-001", "F-API-005"])
    path = write_record(tmp_path, rec)
    assert path.parent.name == "F-MTX-001"
    assert path.name == record_filename(rec) == "2026-09-25-V2-00000000-routing.switch_one-api.json"
    (tmp_path / "F-MTX-001" / "notes.json").write_text('{"not": "a record"}')
    loaded = iter_records([tmp_path])
    assert len(loaded) == 1 and loaded[0].features == ["F-MTX-001", "F-API-005"]


def test_compact_serialisation_round_trips():
    from tools.validate.evidence import dumps
    from tools.validate.runner import compact_log

    rec = make_record()
    rec["observations"]["state_after"] = {"routing": [6, 2, 1, 1, 5, 6, 1, 1], "names": ["a, b", "c"]}
    text = dumps(rec)
    assert '"routing": [6, 2, 1, 1, 5, 6, 1, 1]' in text
    assert json.loads(text) == rec
    log = compact_log([
        {"t": 1, "channel": "http", "command": "get video status", "payload": {"x": 1}, "response": {"big": 1}},
        {"t": 2, "channel": "http", "command": "cec command", "payload": {"index": 1}, "response": {"result": 1}},
        {"t": 3, "channel": "http", "command": "get output status", "fault": "drop_http", "payload": {}},
    ])
    assert "payload" not in log[0] and log[1]["payload"] == {"index": 1} and log[2]["fault"] == "drop_http"


def test_redaction():
    assert redact({"password": "x", "nested": [{"passcode": "1234", "ok": 1}]}) == {
        "password": "***", "nested": [{"passcode": "***", "ok": 1}]}


def test_committed_evidence_is_schema_valid(validator):
    """Every record committed under docs/validation/evidence validates."""
    for rec in iter_records([COMMITTED_EVIDENCE]):
        errors = [f"{e.json_path}: {e.message}" for e in validator.iter_errors(rec.data)]
        assert errors == [], f"{rec.path}: {errors}"
