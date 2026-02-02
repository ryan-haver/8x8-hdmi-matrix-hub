#!/usr/bin/env python3
"""
Test script for OREI HDMI Matrix connection.

This script tests the connection to your OREI BK-808 and verifies
that scene recall commands work correctly.

Configuration:
    Default matrix: 192.168.0.100:443 (from conftest.py)
    Override via environment variables:
        MATRIX_HOST - IP address of the matrix
        MATRIX_PORT - Port number (default 443)

Usage:
    # Run via pytest (uses conftest.py config)
    pytest tests/test_connection.py -v
    
    # Run directly for interactive mode
    python tests/test_connection.py

NOTE: These are hardware integration tests requiring a real matrix.
"""

import asyncio
import os
import sys
import logging

import pytest

# Get config from environment (same defaults as conftest.py)
MATRIX_HOST = os.environ.get("MATRIX_HOST", "192.168.0.100")
MATRIX_PORT = int(os.environ.get("MATRIX_PORT", "443"))
USE_MOCK = os.environ.get("USE_MOCK_MATRIX", "0") == "1"

# Skip if using mock mode
pytestmark = pytest.mark.skipif(
    USE_MOCK,
    reason="Hardware test - set USE_MOCK_MATRIX=0 to run"
)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
)

_LOG = logging.getLogger(__name__)

from orei_matrix import OreiMatrix


async def run_connection_test(host: str, port: int = 443):
    """
    Test connection and basic commands.
    
    NOTE: This is a manual test script, not a pytest test.
    Run directly: python tests/test_connection.py

    :param host: Matrix IP address
    :param port: Port (default 443 for HTTPS)
    """
    _LOG.info("=" * 60)
    _LOG.info("OREI BK-808 HDMI Matrix Connection Test")
    _LOG.info("=" * 60)
    _LOG.info("")
    _LOG.info("This test will verify connection and preset recall.")
    _LOG.info("Make sure your matrix has presets configured!")
    _LOG.info("")

    # Create matrix instance
    _LOG.info("Creating matrix instance for %s:%d", host, port)
    matrix = OreiMatrix(host, port)

    # Test connection
    _LOG.info("Testing connection...")
    connected = await matrix.connect()

    if not connected:
        _LOG.error("✗ Connection FAILED!")
        _LOG.error("")
        _LOG.error("Troubleshooting:")
        _LOG.error("  1. Verify the IP address is correct (check matrix IP INFO menu)")
        _LOG.error("  2. Ensure matrix and computer are on the same network")
        _LOG.error("  3. Try pinging the IP: ping %s", host)
        _LOG.error("  4. Check if port 443 is open (HTTPS)")
        _LOG.error("")
        return False

    _LOG.info("✓ Connection successful!")
    _LOG.info("")

    # Test preset recall
    _LOG.info("Testing preset recall commands...")
    _LOG.info("")
    _LOG.info("Watch your matrix - the inputs/outputs should switch!")
    _LOG.info("")

    for preset_num in range(1, 4):  # Test first 3 presets
        _LOG.info("Recalling Preset %d...", preset_num)
        success = await matrix.recall_scene(preset_num)

        if success:
            _LOG.info("  ✓ Preset %d command sent successfully", preset_num)
            _LOG.info("  → Check your matrix - did the routing change?")
        else:
            _LOG.warning("  ✗ Preset %d recall failed", preset_num)

        # Wait 5 seconds between commands to give matrix time to apply routing changes
        _LOG.info("  Waiting 5 seconds...")
        await asyncio.sleep(5)

    _LOG.info("")

    # Get status
    _LOG.info("Getting device status...")
    status = await matrix.get_status()
    _LOG.info("Status: %s", status)
    _LOG.info("")

    # Disconnect
    _LOG.info("Disconnecting...")
    await matrix.disconnect()
    _LOG.info("✓ Disconnected")
    _LOG.info("")

    _LOG.info("=" * 60)
    _LOG.info("Test Complete!")
    _LOG.info("=" * 60)
    _LOG.info("")
    _LOG.info("✓ ConVerify presets changed your matrix routing")
    _LOG.info("  2. Configure your presets on the matrix (if not done)")
    _LOG.info("  3. Run the integration: python3 driver.py")
    _LOG.info("  4t steps:")
    _LOG.info("  1. Configure your scenes on the matrix")
    _LOG.info("  2. Run the integration: python3 driver.py")
    _LOG.info("  3. Add the integration on your Remote 3")
    _LOG.info("")

    return True


async def interactive_test():
    """Run interactive test mode."""
    _LOG.info("=" * 60)
    _LOG.info("OREI BK-808 Interactive Test Mode")
    _LOG.info("=" * 60)
    _LOG.info("")

    # Get connection details
    host = input("Enter matrix IP address [192.168.1.100]: ").strip() or "192.168.1.100"
    port_str = input("Enter TCP port [23]: ").strip() or "23"

    try:
        port = int(port_str)
    except ValueError:
        _LOG.error("Invalid port number")
        return

    _LOG.info("")
    _LOG.info("Connecting to %s:%d...", host, port)
    _LOG.info("")

    matrix = OreiMatrix(host, port)
    connected = await matrix.connect()

    if not connected:
        _LOG.error("Connection failed!")
        return

    _LOG.info("✓ Connected successfully!")
    _LOG.info("")

    # Interactive command loop
    while True:
        _LOG.info("Commands:")
        _LOG.info("  1-8: Recall preset")
        _LOG.info("  s: Get status")
        _LOG.info("  q: Quit")
        _LOG.info("")

        cmd = input("Enter command: ").strip().lower()

        if cmd == "q":
            break
        elif cmd == "s":
            status = await matrix.get_status()
            _LOG.info("Status: %s", status)
        elif cmd.isdigit() and 1 <= int(cmd) <= 8:
            preset_num = int(cmd)
            _LOG.info("Recalling preset %d...", preset_num)
            _LOG.info("→ Watch your matrix for routing changes!")
            success = await matrix.recall_scene(preset_num)
            if success:
                _LOG.info("✓ Preset %d command sent", preset_num)
            else:
                _LOG.error("✗ Failed to send preset %d command", preset_num)
        else:
            _LOG.warning("Invalid command")

        _LOG.info("")

    await matrix.disconnect()
    _LOG.info("Disconnected")


def main():
    """Main entry point."""
    if len(sys.argv) == 1:
        # Use config defaults
        _LOG.info("Using matrix at %s:%d", MATRIX_HOST, MATRIX_PORT)
        _LOG.info("Override with: MATRIX_HOST=x.x.x.x MATRIX_PORT=443 python tests/test_connection.py")
        _LOG.info("")
        asyncio.run(run_connection_test(MATRIX_HOST, MATRIX_PORT))
    elif sys.argv[1] == "-i":
        # Interactive mode
        _LOG.info("Starting interactive mode...")
        _LOG.info("")
        asyncio.run(interactive_test())
    elif len(sys.argv) >= 2:
        # Command line override
        host = sys.argv[1]
        port = int(sys.argv[2]) if len(sys.argv) > 2 else MATRIX_PORT
        asyncio.run(run_connection_test(host, port))
    else:
        print(f"Usage: python3 test_connection.py              (uses {MATRIX_HOST}:{MATRIX_PORT})")
        print("   or: python3 test_connection.py <ip> [port]  (custom address)")
        print("   or: python3 test_connection.py -i           (interactive mode)")
        sys.exit(1)


if __name__ == "__main__":
    main()
