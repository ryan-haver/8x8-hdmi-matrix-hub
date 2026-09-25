#!/usr/bin/env python3
"""Query and print the input names reported by a real OREI matrix.

Hardware-in-the-loop script (not a pytest test).
Run directly with: python tools/hil/input_names.py <matrix_ip> [port]
(or set MATRIX_HOST / MATRIX_PORT).
"""

import asyncio
import logging
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from orei_matrix import OreiMatrix  # noqa: E402

logging.basicConfig(level=logging.DEBUG)


async def show_input_names(host: str, port: int = 443):
    """Query and display input names from the matrix."""
    matrix = OreiMatrix(host, port)

    print("Connecting to matrix...")
    if not await matrix.connect():
        print("Failed to connect!")
        return

    print("\nQuerying input names...")
    input_names = await matrix.get_all_input_names()

    print("\nInput Names:")
    for num, name in input_names.items():
        print(f"  Input {num}: {name}")

    await matrix.disconnect()


if __name__ == "__main__":
    _host = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("MATRIX_HOST")
    if not _host:
        print("Usage: python tools/hil/input_names.py <matrix_ip> [port]  (or set MATRIX_HOST)")
        sys.exit(1)
    _port = int(sys.argv[2]) if len(sys.argv) > 2 else int(os.environ.get("MATRIX_PORT", "443"))
    asyncio.run(show_input_names(_host, _port))
