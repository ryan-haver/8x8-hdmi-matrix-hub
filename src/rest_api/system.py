"""
System information endpoints.

Report how persistent storage was resolved and whether it is usable, so
operators can verify their Docker volume mounts. SEC-11: the responses carry
no filesystem paths and no file names; those stay in the server log.
"""

import logging
import os
from typing import Any

from aiohttp import web

from persistence import get_config_dir, get_data_dir

from .utils import _json_response, safe_error_message

_LOG = logging.getLogger("rest_api.system")


def _storage_source() -> str:
    """Which setting chose the data directory (the order of ``persistence.get_data_dir``)."""
    if os.environ.get("MATRIX_DATA_DIR"):
        return "MATRIX_DATA_DIR"
    if os.environ.get("UC_CONFIG_HOME"):
        return "UC_CONFIG_HOME"
    return "default"


def _storage_summary() -> dict[str, Any]:
    """Path-free storage diagnostics: where the setting came from, existence, writability, file count."""
    data_dir = get_data_dir()
    config_dir = get_config_dir()
    data_dir_exists = data_dir.is_dir()

    file_count: int | None = 0
    if data_dir_exists:
        try:
            file_count = sum(1 for entry in data_dir.iterdir() if entry.is_file())
        except OSError as exc:
            _LOG.warning("Could not list the data directory %s: %s", data_dir, exc)
            file_count = None

    return {
        "source": _storage_source(),
        "data_dir_exists": data_dir_exists,
        "config_dir_exists": config_dir.is_dir(),
        "writable": data_dir_exists and os.access(data_dir, os.W_OK),
        "file_count": file_count,
    }


async def handle_get_storage(request: web.Request) -> web.Response:
    """GET /api/system/storage - Report whether persistent storage is set up and usable.

    Useful for verifying that ``MATRIX_DATA_DIR`` or ``UC_CONFIG_HOME`` took
    effect inside the container, and when debugging "my settings didn't
    persist" reports. The resolved paths are logged, never returned (SEC-11).
    """
    try:
        _LOG.debug("Storage layout: data_dir=%s config_dir=%s", get_data_dir(), get_config_dir())
        return _json_response(True, _storage_summary())
    except Exception as exc:
        return _json_response(False, error=safe_error_message(exc, "getting storage layout"), status=500)


async def handle_get_info(request: web.Request) -> web.Response:
    """GET /api/system/info - Return basic runtime system information."""
    try:
        info = {
            "python_version": _get_python_version(),
            "platform": os.name,
            "rest_api_version": _get_rest_api_version(),
            "storage": _storage_summary(),
        }
        return _json_response(True, info)
    except Exception as exc:
        return _json_response(False, error=safe_error_message(exc, "getting system info"), status=500)


def _get_python_version() -> str:
    """Return the Python version as a string."""
    import sys

    return f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"


def _get_rest_api_version() -> str:
    """Return the REST API version, falling back to 'unknown' on import error."""
    try:
        from .utils import API_VERSION  # type: ignore[attr-defined]

        return str(API_VERSION)
    except (ImportError, AttributeError):
        return "unknown"
