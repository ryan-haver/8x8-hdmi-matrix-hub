"""HIL-A capture tool: record raw BK-808 responses as golden fixtures.

Run it with ``python -m tools.hil.capture --host <ip> [--mode read|probe|write]``
(runbook: ``tools/hil/README.md``; file format: ``tests/fixtures/device/README.md``).

Embedding (tests do this against the simulator)::

    from tools.hil.capture import Options, run_capture

    code, cap = await run_capture(Options(host="127.0.0.1", port=8443, password="admin", yes=True))
"""

from .cli import build_parser, main, options_from_args, run_capture
from .context import Capture, CaptureError, Console, Options, RestoreError

__all__ = [
    "Capture",
    "CaptureError",
    "Console",
    "Options",
    "RestoreError",
    "build_parser",
    "main",
    "options_from_args",
    "run_capture",
]
