#!/usr/bin/env python3
"""Test querying input names from the OREI matrix."""
import asyncio
import logging
import os
import pytest
from orei_matrix import OreiMatrix

logging.basicConfig(level=logging.DEBUG)

# Skip unless MATRIX_HOST environment variable is set
pytestmark = pytest.mark.skipif(
    not os.environ.get("MATRIX_HOST"),
    reason="Manual test - requires MATRIX_HOST environment variable"
)


async def test_input_names():
    """Query and display input names from the matrix."""
    host = os.environ.get("MATRIX_HOST", "192.168.0.100")
    matrix = OreiMatrix(host, 443)
    
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
    asyncio.run(test_input_names())
