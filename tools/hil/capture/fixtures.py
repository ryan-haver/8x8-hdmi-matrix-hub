"""On-disk format of HIL-A device captures (``tests/fixtures/device/<fw>/``).

The format is documented for humans in ``tests/fixtures/device/README.md``.
This module is the single source of truth for code: the capture tool writes
with :class:`CaptureWriter`, and the simulator's golden mode
(``tools/simulator/golden.py``) reads with :func:`iter_records`.

Pure standard library, so the simulator can import it without pulling in the
capture tool's network code.
"""

from __future__ import annotations

import base64
import datetime as _dt
import json
import re
from collections.abc import Iterator
from pathlib import Path
from typing import Any

#: Written into every record and the manifest. Bump on incompatible changes.
FORMAT = "orei-hil-capture/1"

MANIFEST = "manifest.json"
RESTORE_LOG = "write/restore-log.jsonl"
REDACTED = "***REDACTED***"

#: Secrets shorter than this are not scrubbed from free text (they would
#: mangle unrelated data); they are still removed from login requests by field.
MIN_SCRUB_LEN = 4


class RecordIds:
    """Record ids (path under the firmware folder, without ``.json``).

    Shared by the capture tool and the simulator's golden loader/report.
    """

    LOGIN = "http/login"
    INDEX_PAGE = "http/index_page"
    TELNET_BANNER = "telnet/banner"
    TELNET_STATUS = "telnet/status"

    PROBE_NO_SESSION = "probe/http_no_session"
    PROBE_WRONG_PASSWORD = "probe/login_wrong_password"
    PROBE_LOGIN_OK = "probe/login_ok"
    PROBE_SESSION_MECHANISM = "probe/session_mechanism"
    PROBE_IDLE_EXPIRY = "probe/session_idle_expiry"
    PROBE_UNKNOWN_COMHEAD = "probe/http_unknown_comhead"
    PROBE_GARBAGE_BODY = "probe/http_garbage_body"
    PROBE_CEC_SHAPES = "probe/cec_enable_shapes"
    PROBE_TELNET_ERRORS = "probe/telnet_errors"
    PROBE_TELNET_FRAMING = "probe/telnet_framing"
    PROBE_TELNET_NOOP_ACKS = "probe/telnet_noop_set_acks"
    PROBE_TELNET_SECOND_SESSION = "probe/telnet_second_session"
    PROBE_PUSH_WINDOW = "probe/telnet_push_window"

    WRITE_SNAPSHOT_INITIAL = "write/snapshot-initial"
    WRITE_SNAPSHOT_FINAL = "write/snapshot-final"

    @staticmethod
    def http_read(slug: str) -> str:
        return f"http/{slug}"

    @staticmethod
    def telnet_read(slug: str) -> str:
        return f"telnet/{slug}"

    @staticmethod
    def write(test_id: str) -> str:
        return f"write/{test_id}"


# --------------------------------------------------------------------- helpers


def b64(data: bytes) -> str:
    return base64.b64encode(data).decode("ascii")


def unb64(text: str) -> bytes:
    return base64.b64decode(text.encode("ascii"))


def utc_now() -> str:
    return _dt.datetime.now(_dt.UTC).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def slug(text: str) -> str:
    """``"get video status"`` -> ``"get_video_status"``."""
    return re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_") or "blank"


def firmware_folder_name(device: dict[str, Any]) -> str:
    """Folder name for a device: ``<model>_<mcu version>_web-<web version>``.

    ``device`` is the identity the capture tool builds from ``get status`` and
    ``get network`` (keys ``model``, ``mcu_version``, ``web_version``). Unsafe
    characters are replaced so the name works on every OS.
    """
    parts = [str(device.get("model") or "unknown-model")]
    mcu = device.get("mcu_version")
    parts.append(str(mcu) if mcu else "unknown-fw")
    web = device.get("web_version")
    if web:
        parts.append(f"web-{web}")
    name = "_".join(parts)
    return re.sub(r"[^A-Za-z0-9._-]+", "-", name).strip("-.") or "unknown-firmware"


# ------------------------------------------------------------------- redaction


def _redact_with_segments(raw: bytes, lens: list[int], usable: list[str]) -> tuple[bytes, list[int]]:
    """Redact ``raw`` and recompute the TCP segment lengths recorded for it.

    Replacing a secret changes the body length, so the segment whose bytes
    were replaced must shrink or grow by the same amount; otherwise the
    recorded segments no longer add up to the body and a replay splits it at
    the wrong offsets. Replacement bytes are credited to the segment the
    secret starts in; removed bytes are taken from the segments they were in.
    """
    matches: list[tuple[int, int]] = []
    pos = 0
    needles = [s.encode("utf-8") for s in usable]
    while pos < len(raw):
        found = [(raw.find(n, pos), n) for n in needles]
        found = [(i, n) for i, n in found if i >= 0]
        if not found:
            break
        start, needle = min(found, key=lambda f: (f[0], -len(f[1])))
        matches.append((start, start + len(needle)))
        pos = start + len(needle)
    if not matches:
        return raw, lens
    marker = REDACTED.encode()
    new = bytearray()
    last = 0
    for start, end in matches:
        new += raw[last:start] + marker
        last = end
    new += raw[last:]
    bounds, offset = [], 0
    for n in lens:
        bounds.append((offset, offset + n))
        offset += n
    new_lens = []
    for a, b in bounds:
        removed = sum(max(0, min(b, end) - max(a, start)) for start, end in matches)
        added = sum(len(marker) for start, _ in matches if a <= start < b)
        new_lens.append((b - a) - removed + added)
    return bytes(new), new_lens


def scrub(obj: Any, secrets: list[str]) -> tuple[Any, bool]:
    """Replace every secret in strings and base64 fields. Returns (obj, changed).

    A base64 body with recorded TCP segments (``chunks`` with ``len``) keeps
    its segment lengths consistent with the redacted body.
    """
    usable = [s for s in secrets if s and len(s) >= MIN_SCRUB_LEN]
    if not usable:
        return obj, False
    changed = False

    def walk(value: Any, key: str = "") -> Any:
        nonlocal changed
        if isinstance(value, dict):
            chunks = value.get("chunks")
            if (
                isinstance(value.get("body_b64"), str)
                and isinstance(chunks, list)
                and chunks
                and all(isinstance(c, dict) and isinstance(c.get("len"), int) for c in chunks)
            ):
                try:
                    raw = unb64(value["body_b64"])
                except (ValueError, TypeError):
                    raw = None
                if raw is not None and sum(c["len"] for c in chunks) == len(raw):
                    new_raw, new_lens = _redact_with_segments(raw, [c["len"] for c in chunks], usable)
                    out = {k: walk(v, k) for k, v in value.items() if k not in ("body_b64", "chunks")}
                    if new_raw != raw:
                        changed = True
                    out["body_b64"] = b64(new_raw)
                    out["chunks"] = [{**walk(c), "len": n} for c, n in zip(chunks, new_lens, strict=True)]
                    return {k: out[k] for k in value}  # keep the original key order
            return {k: walk(v, k) for k, v in value.items()}
        if isinstance(value, list):
            return [walk(v, key) for v in value]
        if isinstance(value, str):
            if key.endswith("_b64") or key == "b64":
                try:
                    raw = unb64(value)
                except (ValueError, TypeError):
                    raw = None
                if raw is not None:
                    new = raw
                    for s in usable:
                        new = new.replace(s.encode("utf-8"), REDACTED.encode())
                    if new != raw:
                        changed = True
                        return b64(new)
                return value
            new_text = value
            for s in usable:
                new_text = new_text.replace(s, REDACTED)
            if new_text != value:
                changed = True
            return new_text
        return value

    return walk(obj), changed


def find_secrets(path: Path, secrets: list[str]) -> list[str]:
    """Return a description of every place a secret appears in ``path``.

    Checks the raw file text and every ``*_b64`` field decoded, so a password
    cannot hide in a base64 body.
    """
    usable = [s for s in secrets if s and len(s) >= MIN_SCRUB_LEN]
    if not usable:
        return []
    hits: list[str] = []
    text = path.read_text(encoding="utf-8", errors="replace")
    for s in usable:
        if s in text:
            hits.append(f"{path}: plain text")
    if path.suffix == ".json":
        try:
            doc = json.loads(text)
        except ValueError:
            return hits

        def walk(value: Any, key: str = "") -> None:
            if isinstance(value, dict):
                for k, v in value.items():
                    walk(v, k)
            elif isinstance(value, list):
                for v in value:
                    walk(v, key)
            elif isinstance(value, str) and (key.endswith("_b64") or key == "b64"):
                try:
                    raw = unb64(value)
                except (ValueError, TypeError):
                    return
                for s in usable:
                    if s.encode("utf-8") in raw:
                        hits.append(f"{path}: base64 field {key}")

        walk(doc)
    return hits


# ----------------------------------------------------------------------- write


class CaptureWriter:
    """Writes records under one firmware folder, scrubbing secrets first."""

    def __init__(self, root: Path, secrets: list[str]) -> None:
        self.root = Path(root)
        self.secrets = [s for s in secrets if s]
        self.written: list[str] = []

    def _path(self, record_id: str, suffix: str = ".json") -> Path:
        path = self.root / (record_id + suffix if not record_id.endswith(suffix) else record_id)
        path.parent.mkdir(parents=True, exist_ok=True)
        return path

    def write_record(self, record_id: str, record: dict[str, Any]) -> Path:
        doc = {"format": FORMAT, "id": record_id, **record}
        doc, changed = scrub(doc, self.secrets)
        if changed:
            doc.setdefault("redactions", []).append("secret value scrubbed from stored text/bytes")
        path = self._path(record_id)
        path.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
        if record_id not in self.written:
            self.written.append(record_id)
        return path

    def append_jsonl(self, rel_path: str, entry: dict[str, Any]) -> Path:
        path = self.root / rel_path
        path.parent.mkdir(parents=True, exist_ok=True)
        entry, _ = scrub(entry, self.secrets)
        with open(path, "a", encoding="utf-8", newline="\n") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
            f.flush()
        return path

    def update_manifest(self, device: dict[str, Any], run: dict[str, Any]) -> Path:
        """Merge this run into ``manifest.json`` (runs are appended)."""
        path = self.root / MANIFEST
        manifest: dict[str, Any] = {}
        if path.exists():
            try:
                manifest = json.loads(path.read_text(encoding="utf-8"))
            except ValueError:
                manifest = {}
        manifest["format"] = FORMAT
        manifest["firmware_folder"] = self.root.name
        merged_device = dict(manifest.get("device") or {})
        merged_device.update({k: v for k, v in device.items() if v not in (None, "")})
        manifest["device"] = merged_device
        manifest.setdefault("runs", []).append(run)
        answers: dict[str, list[str]] = manifest.get("answers") or {}
        for aid, ids in (run.get("answers") or {}).items():
            merged = answers.setdefault(aid, [])
            for rid in ids:
                if rid not in merged:
                    merged.append(rid)
        manifest["answers"] = dict(sorted(answers.items()))
        manifest, _ = scrub(manifest, self.secrets)
        self.root.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
        return path

    def verify_no_secrets(self) -> list[str]:
        hits: list[str] = []
        if not self.root.exists():
            return hits
        for file in sorted(self.root.rglob("*")):
            if file.is_file() and file.suffix in (".json", ".jsonl", ".md", ".txt"):
                hits += find_secrets(file, self.secrets)
        return hits


# ------------------------------------------------------------------------ read


def load_manifest(root: str | Path) -> dict[str, Any]:
    path = Path(root) / MANIFEST
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def iter_records(root: str | Path) -> Iterator[tuple[str, dict[str, Any]]]:
    """Yield ``(record_id, record)`` for every capture record under ``root``."""
    root = Path(root)
    for file in sorted(root.rglob("*.json")):
        if file.name == MANIFEST:
            continue
        try:
            doc = json.loads(file.read_text(encoding="utf-8"))
        except ValueError:
            continue
        if not isinstance(doc, dict) or doc.get("format") != FORMAT:
            continue
        record_id = doc.get("id") or file.relative_to(root).with_suffix("").as_posix()
        yield record_id, doc


def iter_exchanges(obj: Any) -> Iterator[dict[str, Any]]:
    """Every HTTP/Telnet exchange nested anywhere inside a record."""
    if isinstance(obj, dict):
        if obj.get("kind") in ("http", "telnet") and "response" in obj:
            yield obj
            return
        for value in obj.values():
            yield from iter_exchanges(value)
    elif isinstance(obj, list):
        for value in obj:
            yield from iter_exchanges(value)


def response_body(exchange: dict[str, Any]) -> bytes | None:
    """Exact response bytes of an exchange (``None`` if there was no response)."""
    resp = exchange.get("response")
    if not isinstance(resp, dict) or "body_b64" not in resp:
        return None
    return unb64(resp["body_b64"])


def response_json(exchange: dict[str, Any]) -> Any:
    resp = exchange.get("response")
    if not isinstance(resp, dict):
        return None
    return resp.get("json")


def headers_named(headers: list[str] | None, name: str) -> list[str]:
    """Values of every ``"Name: value"`` header called ``name`` (case-insensitive)."""
    out = []
    for item in headers or []:
        key, _, value = item.partition(":")
        if key.strip().lower() == name.lower():
            out.append(value.strip())
    return out


def header(headers: list[str] | None, name: str) -> str | None:
    values = headers_named(headers, name)
    return values[0] if values else None
