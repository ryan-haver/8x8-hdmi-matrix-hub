#!/usr/bin/env python3
"""
8x8 HDMI Matrix Hub - Main Entry Point

Starts the core services and conditionally enables integration modules
based on environment variables (feature flags).

Usage:
    python run.py                    # Full mode (API + UC Driver)
    UC_ENABLED=false python run.py   # API-only mode

Environment Variables:
    MATRIX_HOST     - Matrix IP address (default: 192.168.0.100)
    API_PORT        - REST API port (default: 8080)
    UC_ENABLED      - Enable UC integration (default: true)
    UC_PORT         - UC WebSocket port (default: 9095)
    WEBUI_ENABLED   - Enable Web UI (default: true)
    LOG_LEVEL       - Logging level (default: INFO)
"""

import asyncio
import logging
import os
import sys
from pathlib import Path

# Configure logging
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
_LOG = logging.getLogger("run")

# Feature flags from environment
UC_ENABLED = os.environ.get("UC_ENABLED", "true").lower() == "true"
WEBUI_ENABLED = os.environ.get("WEBUI_ENABLED", "true").lower() == "true"
API_PORT = int(os.environ.get("API_PORT", os.environ.get("REST_API_PORT", "8080")))

# Project paths
PROJECT_ROOT = Path(__file__).parent
SRC_PATH = PROJECT_ROOT / "src"

# Add src directory to path
sys.path.insert(0, str(SRC_PATH))

# Check if ucapi is available (installed via requirements-uc.txt)
try:
    import ucapi
    UCAPI_AVAILABLE = True
except ImportError:
    UCAPI_AVAILABLE = False
    _LOG.info("ucapi module not available - UC integration disabled")

# Auto-disable UC if ucapi not installed
if UC_ENABLED and not UCAPI_AVAILABLE:
    _LOG.warning("UC_ENABLED=true but ucapi not installed. Disabling UC integration.")
    UC_ENABLED = False


def run_legacy_mode():
    """
    Run in legacy mode - executes the original driver.py which handles
    both the API and UC driver in a single process.
    
    This maintains full backward compatibility.
    """
    import runpy
    os.chdir(PROJECT_ROOT)
    runpy.run_path(str(SRC_PATH / "driver.py"), run_name="__main__")


async def run_modular_mode():
    """
    Run in modular mode - starts the REST API first, then optionally
    connects the UC driver via the API client.
    
    This is the new architecture where integrations consume the API.
    """
    from rest_api import RestApiServer, set_matrix_device
    from orei_matrix import OreiMatrix
    
    MATRIX_HOST = os.environ.get("MATRIX_HOST", "192.168.0.100")
    
    _LOG.info("=" * 60)
    _LOG.info("8x8 HDMI Matrix Hub - Modular Mode")
    _LOG.info("=" * 60)
    _LOG.info(f"  Matrix Host: {MATRIX_HOST}")
    _LOG.info(f"  API Port:    {API_PORT}")
    _LOG.info(f"  UC Enabled:  {UC_ENABLED}")
    _LOG.info(f"  Web UI:      {WEBUI_ENABLED}")
    _LOG.info("=" * 60)
    
    # Layer 1: Connect to hardware
    matrix = OreiMatrix(MATRIX_HOST)
    set_matrix_device(matrix)
    
    try:
        await matrix.connect()
        _LOG.info("✓ Connected to matrix hardware")
    except Exception as e:
        _LOG.warning(f"Could not connect to matrix on startup: {e}")
        _LOG.info("  Matrix will reconnect when available")
    
    # Layer 2: Start REST API (always)
    api_server = RestApiServer(host="0.0.0.0", port=API_PORT)
    await api_server.start()
    
    # Layer 3: Enable integrations based on feature flags
    if UC_ENABLED:
        _LOG.info("Starting UC integration in legacy mode (driver.py)...")
        # For now, fall back to legacy mode when UC is enabled
        # Full modular UC driver is a future enhancement
        run_legacy_mode()
        return
    
    # API-only mode - run until interrupted
    _LOG.info("Running in API-only mode. Press Ctrl+C to stop.")
    try:
        while True:
            await asyncio.sleep(3600)
    except asyncio.CancelledError:
        pass
    finally:
        await api_server.stop()
        if matrix.connected:
            await matrix.disconnect()


def main():
    """Main entry point."""
    # Check if we should use modular mode
    # For now, always use legacy mode for full compatibility
    # Set USE_MODULAR=true to try the new architecture
    USE_MODULAR = os.environ.get("USE_MODULAR", "false").lower() == "true"
    
    if USE_MODULAR and not UC_ENABLED:
        # Modular mode only works for API-only currently
        _LOG.info("Starting in modular mode (API-only)...")
        asyncio.run(run_modular_mode())
    else:
        # Legacy mode - full backward compatibility
        _LOG.info("Starting in legacy mode...")
        run_legacy_mode()


if __name__ == "__main__":
    main()
