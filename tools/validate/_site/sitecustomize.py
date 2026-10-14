"""Harness startup hook for ``HubProcess`` subprocesses (TST-17).

RFC 6761 reserves ``.invalid`` as a domain that never resolves. On Windows,
OS DNS / LLMNR / NetBIOS fallback can take ~11 s to fail on ``*.invalid``,
exceeding the hub's 5 s connect/login timeout so a non-existent name is
misclassified as ``TIMEOUT`` instead of ``NOT_FOUND``. Fail ``*.invalid``
lookups immediately with ``EAI_NONAME`` inside harness-launched hubs.
"""

from __future__ import annotations

import importlib.util
import socket
import sys
from pathlib import Path
from typing import Any

_THIS_FILE = Path(__file__).resolve()

# Execute any downstream sitecustomize.py on sys.path first so our wrapper stays outermost.
for _entry in list(sys.path):
    if not _entry:
        continue
    _candidate = (Path(_entry) / "sitecustomize.py").resolve()
    if _candidate != _THIS_FILE and _candidate.is_file():
        _spec = importlib.util.spec_from_file_location("_chained_sitecustomize", _candidate)
        if _spec and _spec.loader:
            _mod = importlib.util.module_from_spec(_spec)
            _spec.loader.exec_module(_mod)
        break

_orig_getaddrinfo = socket.getaddrinfo


def _getaddrinfo(host: Any, port: Any, *args: Any, **kwargs: Any) -> Any:
    if isinstance(host, bytes):
        try:
            name = host.decode("ascii").rstrip(".").lower()
        except UnicodeDecodeError:
            name = ""
    elif isinstance(host, str):
        name = host.rstrip(".").lower()
    else:
        name = ""
    if name == "invalid" or name.endswith(".invalid"):
        raise socket.gaierror(socket.EAI_NONAME, "Name or service not known")
    return _orig_getaddrinfo(host, port, *args, **kwargs)


socket.getaddrinfo = _getaddrinfo  # type: ignore[assignment]
