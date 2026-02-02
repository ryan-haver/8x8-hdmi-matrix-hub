#!/usr/bin/env python3
"""
Start just the Web UI/REST API for development testing.

This connects to the real matrix and serves the Web UI without
requiring the Unfolded Circle integration API.

Usage: python scripts/start_webui.py
"""

import asyncio
import logging
import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from aiohttp import web
from orei_matrix import OreiMatrix
from rest_api import create_rest_app, set_matrix_device

# Configuration - uses same defaults as test suite
MATRIX_HOST = os.environ.get("MATRIX_HOST", "192.168.0.100")
MATRIX_PORT = int(os.environ.get("MATRIX_PORT", "443"))
API_PORT = int(os.environ.get("API_PORT", "8080"))

# Config directory for scenes
CONFIG_DIR = os.path.join(os.path.dirname(__file__), "..", "data")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
_LOG = logging.getLogger("webui")


async def main():
    """Start the Web UI server."""
    _LOG.info("=" * 60)
    _LOG.info("OREI Matrix Web UI - Development Server")
    _LOG.info("=" * 60)
    
    # Connect to matrix
    _LOG.info(f"Connecting to matrix at {MATRIX_HOST}:{MATRIX_PORT}...")
    matrix = OreiMatrix(MATRIX_HOST, MATRIX_PORT)
    connected = await matrix.connect()
    
    if not connected:
        _LOG.error(f"Failed to connect to matrix at {MATRIX_HOST}:{MATRIX_PORT}")
        _LOG.error("Check that the matrix is powered on and network accessible")
        return
    
    _LOG.info("✓ Connected to matrix")
    
    # Get input names
    status = await matrix.get_video_status()
    input_names = {}
    if status and "allinputname" in status:
        for i, name in enumerate(status["allinputname"], 1):
            input_names[i] = name
    else:
        # Default names
        for i in range(1, 9):
            input_names[i] = f"Input {i}"
    
    # Configure REST API with matrix, input names, and config directory
    set_matrix_device(matrix, input_names, CONFIG_DIR)
    
    # Create and start app
    app = create_rest_app()
    runner = web.AppRunner(app)
    await runner.setup()
    
    site = web.TCPSite(runner, "0.0.0.0", API_PORT)
    await site.start()
    
    _LOG.info("")
    _LOG.info(f"✓ Web UI running at: http://localhost:{API_PORT}")
    _LOG.info(f"  API docs at: http://localhost:{API_PORT}/api")
    _LOG.info("")
    _LOG.info("Press Ctrl+C to stop")
    _LOG.info("=" * 60)
    
    # Keep running
    try:
        while True:
            await asyncio.sleep(3600)
    except asyncio.CancelledError:
        pass
    finally:
        _LOG.info("Shutting down...")
        await runner.cleanup()
        await matrix.disconnect()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        _LOG.info("Stopped by user")
