"""
System information endpoints.

Exposes the resolved storage layout and runtime metadata so operators
can verify their Docker volume mounts are pointing where they expect.
"""

import logging
import os
from pathlib import Path

from aiohttp import web

from persistence import describe_storage_layout
from .utils import _json_response

_LOG = logging.getLogger("rest_api.system")


async def handle_get_storage(request: web.Request) -> web.Response:
    """GET /api/system/storage - Return the resolved persistent storage layout.

    Useful for verifying that ``MATRIX_DATA_DIR`` and ``UC_CONFIG_HOME``
    point where the operator expects inside the container. Also handy
    when debugging "my settings didn't persist" reports.
    """
    try:
        layout = describe_storage_layout()

        # Enrich with size/contents info for diagnostics.
        data_dir = Path(layout["data_dir"])
        config_dir = Path(layout["config_dir"])

        layout["data_dir_exists"] = data_dir.exists()
        layout["config_dir_exists"] = config_dir.exists()

        # List top-level files in the data dir (if it exists) so the
        # operator can see what state has been written.
        if data_dir.exists() and data_dir.is_dir():
            try:
                layout["data_dir_files"] = sorted(
                    entry.name for entry in data_dir.iterdir() if entry.is_file()
                )
            except OSError as exc:
                layout["data_dir_files"] = []
                layout["data_dir_error"] = str(exc)
        else:
            layout["data_dir_files"] = []

        return _json_response(True, layout)
    except Exception as exc:
        _LOG.error("Error getting storage layout: %s", exc)
        return _json_response(False, error=str(exc), status=500)


async def handle_get_info(request: web.Request) -> web.Response:
    """GET /api/system/info - Return basic runtime system information."""
    try:
        info = {
            "python_version": _get_python_version(),
            "platform": os.name,
            "rest_api_version": _get_rest_api_version(),
            "storage": describe_storage_layout(),
        }
        return _json_response(True, info)
    except Exception as exc:
        _LOG.error("Error getting system info: %s", exc)
        return _json_response(False, error=str(exc), status=500)


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