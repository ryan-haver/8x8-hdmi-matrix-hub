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
from urllib.parse import unquote, urlsplit

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
    # Callers may supply structured diagnostics without redacting them first.
    # Sanitize a copy at persistence as well as at individual capture boundaries.
    safe = redact(record)
    observations = record.get("observations")
    if isinstance(observations, dict):
        for name in ("requests", "hub_reads"):
            if name in observations:
                safe["observations"][name] = redact(observations[name], exchanges=True)
    path.write_text(dumps(safe) + "\n", encoding="utf-8")
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


_SECRET_KEYS = re.compile(r"pass(word|code)?|secret|token|api[_-]?key|(?:^|[_-])pin(?:$|[_-])", re.IGNORECASE)
_CREDENTIAL_HEADERS = frozenset({
    "authorization", "proxy-authorization", "cookie", "set-cookie", "x-admin-pin", "x-passcode",
    "x-api-key", "api-key", "x-auth-token", "x-access-token", "orei_session", "orei_device_token",
})
_PUBLIC_SHORTCUTS = frozenset({
    "route_all_to_output", "route_one_to_one", "power_off_all", "mute_all_audio", "unmute_all_audio",
    "beep_on", "beep_off", "panel_lock_on", "panel_lock_off", "system_reboot",
    "lcd_timeout_off", "lcd_timeout_10s", "lcd_timeout_30s", "lcd_timeout_60s", "lcd_timeout_always_on",
    *(f"preset_recall_{n}" for n in range(1, 9)),
})


def _secret_name(name: str, *, header: bool = False) -> bool:
    name = name.lower()
    # Header identity is exact, never a substring match on a public policy header.
    if header or name.startswith("x-"):
        return name in _CREDENTIAL_HEADERS
    return name in {"key", "pin", "authorization", "proxy-authorization", "cookie", "set-cookie", "orei_session"} or bool(
        _SECRET_KEYS.search(name)
    )


def _query_copy(text: str) -> str:
    def mask(match: re.Match[str]) -> str:
        return match[1] + ("***" if _secret_name(unquote(match[2])) else match[3])

    return re.sub(r"([?&]([^?&=\s]+)=)([^&#\s\"'<>]*)", mask, text)


def _public_field(name: str, value: Any, path: str, field: str) -> bool:
    route = urlsplit(path).path
    if name == "key" and field in {"key", "data.key"} and type(value) is str and value in _PUBLIC_SHORTCUTS:
        return route in {"shortcut_run", f"/api/shortcuts/{value}", f"/api/system-shortcuts/{value}"}
    if name == "password_protected" and type(value) is bool:
        return bool(re.fullmatch(r"/api/profile(?:/[^/]+)?|/api/v2/scenes(?:/[^/]+)?", route)) and field in {
            "password_protected", "data.password_protected", "scene.password_protected", "data.scene.password_protected",
        }
    return False


def display_error(value: Any) -> str:
    """Opaque error prose can echo credentials under arbitrary labels. Suppress it.

    Preserve exception class, with HTTP method/status supplied separately by the
    caller. This is deliberately not a claim to parse arbitrary prose safely.
    """
    if isinstance(value, str) and re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*: <error text suppressed>", value):
        return value  # Preserve already-sanitized exception-class metadata.
    prefix = f"{type(value).__name__}: " if isinstance(value, BaseException) else ""
    return prefix + "<error text suppressed>"


def display_body(value: Any, *, path: str = "", field_path: str = "") -> Any:
    """Structured/serialized JSON diagnostics, or a safe opaque-body placeholder."""
    if isinstance(value, (str, bytes, bytearray)):
        try:
            parsed = json.loads(value)
        except (ValueError, UnicodeError):
            return "<opaque body suppressed>"
        if not isinstance(parsed, (dict, list)):
            return "<opaque body suppressed>"
        value = parsed
    return redact(value, path=path, field_path=field_path)


def redact(value: Any, *, path: str = "", field_path: str = "", headers: bool = False,
           exchanges: bool = False) -> Any:
    """Display copy for supported dict/list/tuple, header pairs and JSON strings.

    Transport objects and comparisons must keep their originals. Public field
    exceptions require both a trusted route/field and the precise public type.
    Arbitrary Mapping/custom sequences and unknown prose are outside this parser.
    """
    if field_path and _secret_name(field_path.rsplit(".", 1)[-1], header=headers) and not _public_field(
        field_path.rsplit(".", 1)[-1], value, path, field_path
    ):
        return "***"
    if isinstance(value, dict):
        # Only the caller's known exchange collection supplies trusted context.
        # A body with method/path/status fields cannot grant itself exceptions.
        exchange_path = value.get("path") if exchanges and "method" in value and "status" in value else None
        out = {}
        for k, v in value.items():
            name = str(k)
            child_field = f"{field_path}.{name}" if field_path else name
            if exchange_path is not None and name in {"body", "response"}:
                out[k] = display_body(v, path=str(exchange_path))
            elif name in {"json", "body"} and path:
                out[k] = display_body(v, path=path)
            elif name in {"error", "blocked_reason", "aborted"} and v:
                out[k] = display_error(v)
            elif name == "data" and isinstance(v, (str, bytes, bytearray)):
                out[k] = display_body(v, path=path)
            elif _secret_name(name, header=headers) and not _public_field(name, v, path, child_field):
                out[k] = "***"
            elif name == "default" and _secret_name(str(value.get("name", ""))):
                # HA's serialized form schema names a field next to its default.
                out[k] = "***"
            else:
                out[k] = redact(v, path=path, field_path=child_field, headers=name.lower() in {
                    "headers", "response_headers", "cookies",
                })
        return out
    if isinstance(value, (list, tuple)):
        if headers:
            pairs = [
                (item[0], "***" if _secret_name(str(item[0]), header=True) else redact(item[1]))
                if isinstance(item, (list, tuple)) and len(item) == 2 else redact(item)
                for item in value
            ]
        else:
            pairs = [redact(v, path=path, field_path="", exchanges=exchanges) for v in value]
        return tuple(pairs) if isinstance(value, tuple) else pairs
    if isinstance(value, str):
        if value.lstrip().startswith(("{", "[")):
            try:
                return json.dumps(redact(json.loads(value), path=path), ensure_ascii=False)
            except ValueError:
                return "<malformed JSON suppressed>"
        return _query_copy(value)
    return value
