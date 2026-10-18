#!/usr/bin/env python3
"""Source/Docker compatibility entry for the packaged hub bootstrap."""

from __future__ import annotations

import sys
from pathlib import Path

# Source and Docker runs do not require an editable install.
sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from hub import cli

if __name__ == "__main__":
    sys.exit(cli.main())
else:
    # Preserve monkeypatch-based callers: run and hub.cli share actual globals.
    sys.modules[__name__] = cli
