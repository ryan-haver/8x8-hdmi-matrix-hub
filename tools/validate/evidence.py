"""Evidence records (VALIDATION_PLAN §4): build, write, load.

Layout (see ``docs/validation/evidence/README.md``)::

    <root>/<primary feature id>/<YYYY-MM-DD>-<level>-<shortsha>-<scenario id>-<client>.json
    <root>/<primary feature id>/<...>/  artifacts (screenshots, logs) next to the record

A record proves every feature in its ``features`` list; it is stored once,
under the first one. The ledger indexes records by their ``features`` field.
"""

from __future__ import annotations

import json
import re
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .model import Level

ROOT = Path(__file__).resolve().parents[2]
COMMITTED_EVIDENCE = ROOT / "docs" / "validation" / "evidence"
SCHEMA_PATH = ROOT / "docs" / "validation" / "evidence.schema.json"
SCHEMA_VERSION = 1

RESULTS = ("pass", "fail", "blocked")


def record_stem(date: str, level: str, short_sha: str, scenario: str, client: str) -> str:
    """``<YYYY-MM-DD>-<level>-<shortsha>-<scenario>-<client>``; also the record's artifact directory."""
    return f"{date}-{level}-{short_sha}-{scenario}-{client}"


def record_filename(record: dict[str, Any]) -> str:
    return record_stem(record["timestamp"]["started"][:10], record["level"], record["commit"]["short"],
                       record["scenario"], record["client"]) + ".json"


def record_path(root: Path, record: dict[str, Any]) -> Path:
    return root / record["features"][0] / record_filename(record)


_SCALAR_LIST = re.compile(r"\[\s*\n\s*((?:[^\[\]{}\n]+,\s*\n\s*)*[^\[\]{}\n]+)\s*\n\s*\]")


def dumps(record: dict[str, Any]) -> str:
    """Indented JSON with short scalar lists (routing, port flags) kept on one line."""
    text = json.dumps(record, indent=2, sort_keys=False, default=str, ensure_ascii=False)

    def one_line(m: re.Match[str]) -> str:
        joined = "[" + ", ".join(part.strip() for part in m.group(1).split(",\n")) + "]"
        return joined if len(joined) <= 100 else m.group(0)

    return _SCALAR_LIST.sub(one_line, text)


def write_record(root: Path, record: dict[str, Any]) -> Path:
    path = record_path(root, record)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(dumps(record) + "\n", encoding="utf-8")
    return path


@dataclass(frozen=True)
class LoadedRecord:
    path: Path
    data: dict[str, Any]

    @property
    def level(self) -> Level:
        return Level.parse(self.data["level"])

    @property
    def result(self) -> str:
        return str(self.data["result"])

    @property
    def features(self) -> list[str]:
        return list(self.data.get("features", []))

    @property
    def sha(self) -> str:
        return str(self.data.get("commit", {}).get("sha", ""))

    @property
    def started(self) -> str:
        return str(self.data.get("timestamp", {}).get("started", ""))


def iter_records(roots: Iterable[Path]) -> list[LoadedRecord]:
    """Every ``*.json`` evidence record below the given roots (other JSON files are skipped)."""
    records: list[LoadedRecord] = []
    seen: set[Path] = set()
    for root in roots:
        if not root.exists():
            continue
        for path in sorted(root.rglob("*.json")):
            real = path.resolve()
            if real in seen:
                continue
            seen.add(real)
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, ValueError):
                continue
            if isinstance(data, dict) and data.get("schema_version") == SCHEMA_VERSION and "scenario" in data:
                records.append(LoadedRecord(path, data))
    return records


_SECRET_KEYS = re.compile(r"pass(word|code)?|secret|token|api[_-]?key", re.IGNORECASE)


def redact(value: Any) -> Any:
    """Drop secrets from anything that goes into a record."""
    if isinstance(value, dict):
        return {k: ("***" if _SECRET_KEYS.search(str(k)) else redact(v)) for k, v in value.items()}
    if isinstance(value, list):
        return [redact(v) for v in value]
    return value
