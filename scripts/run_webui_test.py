#!/usr/bin/env python3
"""
Start REST API server connected to the REAL OREI matrix for Web UI testing.

Usage: python scripts/run_webui_test.py

Access the UI at: http://localhost:8080/ui
"""

import asyncio
import json
import logging
import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

# Configure logging BEFORE importing modules
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    datefmt='%H:%M:%S'
)

# Reduce noise from some libraries
logging.getLogger("aiohttp").setLevel(logging.WARNING)
logging.getLogger("asyncio").setLevel(logging.WARNING)

_LOG = logging.getLogger("webui_server")

from orei_matrix import OreiMatrix
from rest_api import create_rest_app, set_matrix_device

from aiohttp import web


async def main():
    """Start the server connected to the real matrix."""
    print("=" * 60)
    print("OREI Matrix Web UI Server")
    print("=" * 60)
    
    # Load config
    config_path = Path(__file__).parent.parent / "data" / "config_state.json"
    config = {}
    if config_path.exists():
        with open(config_path) as f:
            config = json.load(f)
        _LOG.info(f"Loaded config from {config_path}")
    
    host = config.get("host", "192.168.0.100")
    port = config.get("port", 443)
    
    print(f"\nConnecting to matrix at {host}:{port}...")
    _LOG.info(f"Connecting to matrix at {host}:{port}")
    
    # Create real matrix connection
    matrix = OreiMatrix(host=host, port=port, use_https=True)
    
    try:
        await matrix.connect()
        print("✓ Connected to matrix!")
        _LOG.info("Connected to matrix successfully")
    except Exception as e:
        print(f"✗ Failed to connect: {e}")
        _LOG.error(f"Failed to connect to matrix: {e}", exc_info=True)
        print("\nRunning anyway - will show connection errors in UI")
    
    # Get input names from matrix or config
    input_names = {}
    preset_names = config.get("preset_names", {})
    
    # Try to get names from the matrix itself
    if matrix.connected:
        try:
            _LOG.debug("Fetching input names from matrix...")
            input_status = await matrix.get_input_status()
            _LOG.debug(f"Input status response: {input_status}")
            if input_status and "inputname" in input_status:
                for i, name in enumerate(input_status["inputname"], 1):
                    input_names[i] = name
                print(f"✓ Loaded {len(input_names)} input names from matrix")
                _LOG.info(f"Loaded input names: {input_names}")
        except Exception as e:
            print(f"  Could not load input names: {e}")
            _LOG.error(f"Could not load input names: {e}", exc_info=True)
    
    # Fall back to preset names from config
    if not input_names:
        for key, value in preset_names.items():
            input_names[int(key)] = value
        print(f"✓ Using {len(input_names)} names from config")
        _LOG.info(f"Using names from config: {input_names}")
    
    # Initialize the app with real matrix
    # Third parameter is config_dir for SceneManager
    config_dir = str(Path(__file__).parent.parent / "data")
    set_matrix_device(matrix, input_names, config_dir)
    _LOG.info(f"Matrix device configured, config_dir={config_dir}")
    
    app = create_rest_app()
    runner = web.AppRunner(app, access_log=_LOG)
    await runner.setup()
    
    site = web.TCPSite(runner, "0.0.0.0", 8080)
    await site.start()
    
    print("\n✓ Server started!")
    print("\n  Web UI: http://127.0.0.1:8080/ui")
    print("  API:    http://127.0.0.1:8080/api")
    print(f"\n  Matrix: {host}:{port} ({'connected' if matrix.connected else 'disconnected'})")
    print("\nPress Ctrl+C to stop...\n")
    _LOG.info("Server started on http://0.0.0.0:8080")
    
    try:
        # Keep running
        while True:
            await asyncio.sleep(3600)
    except KeyboardInterrupt:
        print("\nShutting down...")
        _LOG.info("Shutting down server...")
    finally:
        await matrix.disconnect()
        await runner.cleanup()
        _LOG.info("Server stopped")


if __name__ == "__main__":
    asyncio.run(main())
