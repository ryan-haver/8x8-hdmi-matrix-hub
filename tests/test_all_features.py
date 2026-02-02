#!/usr/bin/env python3
"""
Test all OREI Matrix features: power, video switching, status, and presets.

NOTE: This is a manual/interactive test requiring hardware.
Run directly with: python tests/test_all_features.py 192.168.1.100
"""
import asyncio
import logging
import os
import sys

import pytest

# Skip in pytest runs - this is a manual hardware test
pytestmark = pytest.mark.skipif(
    not os.environ.get("MATRIX_HOST"),
    reason="Manual hardware test - set MATRIX_HOST to run"
)

from orei_matrix import OreiMatrix

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

_LOG = logging.getLogger(__name__)


async def test_all_features(host: str, port: int = 443):
    """Test all matrix features."""
    _LOG.info("="*70)
    _LOG.info("OREI Matrix Full Feature Test")
    _LOG.info("="*70)
    _LOG.info(f"Target: https://{host}:{port}")
    _LOG.info("")
    
    matrix = OreiMatrix(host, port)
    
    # Connect and authenticate
    _LOG.info("1. Testing Connection & Authentication...")
    if not await matrix.connect():
        _LOG.error("Connection failed!")
        return
    _LOG.info("   ✓ Connected and authenticated")
    _LOG.info("")
    
    # Get initial status
    _LOG.info("2. Getting Current Status...")
    status = await matrix.get_status()
    _LOG.info(f"   Power: {status.get('power', 'unknown')}")
    _LOG.info(f"   Current Routing: {status.get('routing', [])}")
    _LOG.info(f"   Input Names: {status.get('input_names', [])}")
    _LOG.info(f"   Output Names: {status.get('output_names', [])}")
    _LOG.info("")
    
    # Test power control
    _LOG.info("3. Testing Power Control...")
    input("   Press Enter to turn matrix OFF (standby)...")
    if await matrix.power_off():
        _LOG.info("   ✓ Matrix powered OFF")
    await asyncio.sleep(3)
    
    input("   Press Enter to turn matrix back ON...")
    if await matrix.power_on():
        _LOG.info("   ✓ Matrix powered ON")
    await asyncio.sleep(2)
    _LOG.info("")
    
    # Test video switching
    _LOG.info("4. Testing Video Switching...")
    _LOG.info("   Switching Input 2 to Output 1...")
    if await matrix.switch_input(2, 1):
        _LOG.info("   ✓ Input 2 → Output 1")
    await asyncio.sleep(2)
    
    _LOG.info("   Switching Input 5 to Output 1...")
    if await matrix.switch_input(5, 1):
        _LOG.info("   ✓ Input 5 → Output 1")
    await asyncio.sleep(2)
    _LOG.info("")
    
    # Test preset recall
    _LOG.info("5. Testing Preset Recall...")
    for preset in [1, 2]:
        _LOG.info(f"   Recalling Preset {preset}...")
        if await matrix.recall_scene(preset):
            _LOG.info(f"   ✓ Preset {preset} recalled")
        await asyncio.sleep(3)
    _LOG.info("")
    
    # Get final status
    _LOG.info("6. Final Status Check...")
    status = await matrix.get_status()
    _LOG.info(f"   Power: {status.get('power', 'unknown')}")
    _LOG.info(f"   Current Routing: {status.get('routing', [])}")
    _LOG.info(f"   Last Preset: {status.get('current_scene', 'none')}")
    _LOG.info("")
    
    # Disconnect
    await matrix.disconnect()
    _LOG.info("="*70)
    _LOG.info("All Tests Complete!")
    _LOG.info("="*70)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_all_features.py <matrix_ip> [port]")
        print("Default port is 443 (HTTPS)")
        sys.exit(1)
    
    host = sys.argv[1]
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 443
    
    asyncio.run(test_all_features(host, port))
