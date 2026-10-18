"""Non-destructive Unfolded Circle `config_state.json` import and persistence helpers."""

from __future__ import annotations

import json
import logging
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from _file_io import atomic_write_json

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
    """Non-destructively import ``config_state.json`` (or fallback ``.migrated`` when absent).

    Contract rules (`RUNTIME_CONTRACT.md` §2, §4):
    - Never unlink or overwrite an existing primary ``config_state.json``.
    - Accept ``config_state.json.migrated`` only when ``config_state.json`` is absent;
      when restoring from ``.migrated``, write ``config_state.json`` without deleting
      ``.migrated`` or overwriting any existing file.
    - Retain address-bound ``user`` and ``password`` credentials.
    """
    base_dir = Path(config_home)
    primary_path = base_dir / LEGACY_CONFIG_FILENAME
    migrated_path = base_dir / MIGRATED_CONFIG_FILENAME

    from_migrated_only = False
    if primary_path.exists():
        source_path = primary_path
    elif migrated_path.exists():
        source_path = migrated_path
        from_migrated_only = True
    else:
        return None

    try:
        raw_text = source_path.read_text(encoding="utf-8")
        raw_data = json.loads(raw_text)
    except (OSError, ValueError, TypeError) as exc:
        _LOG.warning("Failed to read UC config state from %s: %s", source_path, exc)
        return None

    parsed = _parse_legacy_payload(raw_data)
    if parsed is None:
        return None

    if from_migrated_only and not primary_path.exists():
        try:
            atomic_write_json(primary_path, raw_data)
            _LOG.info("Restored primary %s from %s", primary_path, migrated_path)
        except OSError as exc:
            _LOG.warning("Could not restore primary config state %s: %s", primary_path, exc)

    return parsed


def load_config_state(config_home: Path | str) -> dict[str, Any] | None:
    """Load saved UC configuration from ``config_state.json`` (or ``.migrated`` fallback)."""
    return migrate_legacy_config_state(config_home)


def save_config_state(
    config_home: Path | str,
    *,
    host: str,
    port: int = DEFAULT_MATRIX_PORT,
    telnet_port: int | None = None,
    input_names: Mapping[int, str] | None = None,
    output_names: Mapping[int, str] | None = None,
    credentials: tuple[str, str] | None = None,
) -> Path:
    """Atomically persist ``config_state.json`` in ``config_home`` (mode 0600 on POSIX).

    ``credentials`` is ``(user, password)`` entered during Remote setup for this
    matrix address; when ``None`` (environment credentials), ``user``/``password``
    are omitted from the saved file (`UC-02`, `UC-05`).
    """
    base_dir = Path(config_home)
    target = base_dir / LEGACY_CONFIG_FILENAME

    payload: dict[str, Any] = {
        "host": str(host).strip(),
        "port": int(port),
        "input_names": {str(k): str(v) for k, v in (input_names or {}).items()},
    }
    if telnet_port is not None:
        payload["telnet_port"] = int(telnet_port)
    if output_names:
        payload["output_names"] = {str(k): str(v) for k, v in output_names.items()}
    if credentials is not None:
        user, password = credentials
        if user is not None and password is not None:
            payload["user"] = str(user)
            payload["password"] = str(password)

    atomic_write_json(target, payload)
    _LOG.info("Configuration saved to %s", target)
    return target
