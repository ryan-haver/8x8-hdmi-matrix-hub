#!/usr/bin/env python3
"""
Deprecated: use ``python run.py`` (core only unless UC_ENABLED=true).

Kept as a thin alias so existing commands keep working. The options map onto
run.py's environment variables and the hub always starts core only (no Remote
integration). It used to import ``src.rest_api`` while the modules import
``rest_api``, which created duplicate module instances (BE-19); going through
run.py fixes that. Removed in Phase 4 (docs/REMEDIATION_PLAN.md).

Usage:
    python run_server.py [--host MATRIX_HOST] [--port API_PORT] [--matrix-port MATRIX_PORT]
                         [--config-dir DATA_DIR] [--debug]
"""

from __future__ import annotations

import argparse
import os
import sys

import run


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Deprecated alias of run.py (core only)")
    parser.add_argument("--host", help="matrix IP address (MATRIX_HOST)")
    parser.add_argument("--port", type=int, help="REST API / web UI port (API_PORT)")
    parser.add_argument("--matrix-port", type=int, help="matrix HTTPS port (MATRIX_PORT)")
    parser.add_argument("--config-dir", help="persistent data directory (DATA_DIR)")
    parser.add_argument("--debug", action="store_true", help="LOG_LEVEL=DEBUG")
    args = parser.parse_args(argv)

    overrides = {
        "MATRIX_HOST": args.host,
        "API_PORT": str(args.port) if args.port else None,
        "MATRIX_PORT": str(args.matrix_port) if args.matrix_port else None,
        "DATA_DIR": args.config_dir,
        "LOG_LEVEL": "DEBUG" if args.debug else None,
    }
    for name, value in overrides.items():
        if value:
            os.environ[name] = value
    if args.config_dir and not os.environ.get("UC_CONFIG_HOME"):
        os.environ["UC_CONFIG_HOME"] = args.config_dir
    if os.environ.get("OREI_CONFIG_DIR") and not os.environ.get("DATA_DIR"):
        os.environ["DATA_DIR"] = os.environ["OREI_CONFIG_DIR"]
    os.environ["UC_ENABLED"] = "false"
    print("run_server.py is deprecated; use `python run.py` (see docs/DOCKER.md)", file=sys.stderr)
    return run.main([])


if __name__ == "__main__":
    sys.exit(main())
