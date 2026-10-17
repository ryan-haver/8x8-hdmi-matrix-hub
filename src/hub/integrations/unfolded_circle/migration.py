"""Legacy Unfolded Circle `config_state.json` migration helper (§5)."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

_LOG = logging.getLogger("uc.migration")

LEGACY_CONFIG_FILENAME = "config_state.json"
MIGRATED_CONFIG_FILENAME = "config_state.json.migrated"
DEFAULT_MATRIX_PORT = 443


def _parse_legacy_payload(raw: dict[str, Any]) -> dict[str, Any] | None:
    if not isinstance(raw, dict):
        return None
    host = str(raw.get("host") or "").strip()
    if not host:
        return None

    try:
        port = int(raw.get("port") or DEFAULT_MATRIX_PORT)
    except (TypeError, ValueError):
        port = DEFAULT_MATRIX_PORT
    if not (1 <= port <= 65535):
        port = DEFAULT_MATRIX_PORT

    telnet_port: int | None = None
    if "telnet_port" in raw and raw["telnet_port"] is not None:
        try:
            tp = int(raw["telnet_port"])
            if 1 <= tp <= 65535:
                telnet_port = tp
        except (TypeError, ValueError):
            telnet_port = None

    result: dict[str, Any] = {
        "host": host,
        "port": port,
        "telnet_port": telnet_port,
    }

    raw_inputs = raw.get("input_names") or raw.get("preset_names")
    if isinstance(raw_inputs, dict):
        parsed_in: dict[int, str] = {}
        for k, v in raw_inputs.items():
            try:
                parsed_in[int(k)] = str(v)
            except (TypeError, ValueError):
                continue
        if parsed_in:
            result["input_names"] = parsed_in

    raw_outputs = raw.get("output_names")
    if isinstance(raw_outputs, dict):
        parsed_out: dict[int, str] = {}
        for k, v in raw_outputs.items():
            try:
                parsed_out[int(k)] = str(v)
            except (TypeError, ValueError):
                continue
        if parsed_out:
            result["output_names"] = parsed_out

    if isinstance(raw.get("user"), str) and raw["user"].strip():
        result["user"] = raw["user"].strip()
    if isinstance(raw.get("password"), str):
        result["password"] = raw["password"]

    return result


def migrate_legacy_config_state(config_home: Path | str) -> dict[str, Any] | None:
    """Import legacy ``config_state.json`` and rename it to ``config_state.json.migrated`` idempotently.

    Returns the extracted configuration dictionary (``host``, ``port``, ``telnet_port``,
    plus optional ``input_names``, ``output_names``, ``user``, ``password``), or
    ``None`` if no legacy configuration exists or it is invalid.
    """
    base_dir = Path(config_home)
    legacy_path = base_dir / LEGACY_CONFIG_FILENAME
    migrated_path = base_dir / MIGRATED_CONFIG_FILENAME

    source_path: Path | None = None
    if legacy_path.exists():
        source_path = legacy_path
    elif migrated_path.exists():
        source_path = migrated_path
    else:
        return None

    try:
        raw_text = source_path.read_text(encoding="utf-8")
        raw_data = json.loads(raw_text)
    except (OSError, ValueError, TypeError) as exc:
        _LOG.warning("Failed to read legacy UC config state from %s: %s", source_path, exc)
        return None

    parsed = _parse_legacy_payload(raw_data)
    if parsed is None:
        return None

    if legacy_path.exists():
        try:
            migrated_path.write_text(raw_text, encoding="utf-8")
            legacy_path.unlink()
            _LOG.info("Migrated legacy %s -> %s", legacy_path, migrated_path)
        except OSError as exc:
            _LOG.warning("Could not write migrated config state %s: %s", migrated_path, exc)

    return parsed
