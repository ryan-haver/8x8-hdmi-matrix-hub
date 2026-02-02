#!/usr/bin/env python3
"""
Standalone REST API server for OREI Matrix.

This script starts the REST API server and connects to the OREI Matrix hardware.
Run this instead of `python -m http.server` to get full matrix functionality.

Usage:
    python run_server.py [options]

Options:
    --host HOST         Matrix IP address (default: 192.168.0.100 or OREI_HOST env)
    --port PORT         REST API port (default: 8080 or OREI_API_PORT env)
    --matrix-port PORT  Matrix HTTPS port (default: 443)
    --config-dir DIR    Configuration directory (default: ./config)

Environment Variables:
    OREI_HOST           Matrix IP address
    OREI_PORT           Matrix HTTPS port (default: 443)
    OREI_API_PORT       REST API port (default: 8080)
    OREI_USER           Matrix username (default: Admin)
    OREI_PASSWORD       Matrix password (default: admin)
    OREI_USE_TELNET_CEC Use Telnet for CEC commands (default: false)
"""

import argparse
import asyncio
import logging
import os
import signal
import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.orei_matrix import OreiMatrix
from src.rest_api.app import create_rest_app, RestApiServer
from src.rest_api.utils import set_matrix_device

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
_LOG = logging.getLogger("run_server")


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="OREI Matrix REST API Server")
    parser.add_argument(
        "--host",
        default=os.environ.get("OREI_HOST", "192.168.0.100"),
        help="Matrix IP address (default: 192.168.0.100)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.environ.get("OREI_API_PORT", "8080")),
        help="REST API port (default: 8080)"
    )
    parser.add_argument(
        "--matrix-port",
        type=int,
        default=int(os.environ.get("OREI_PORT", "443")),
        help="Matrix HTTPS port (default: 443)"
    )
    parser.add_argument(
        "--config-dir",
        default=os.environ.get("OREI_CONFIG_DIR", "./config"),
        help="Configuration directory (default: ./config)"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )
    
    args = parser.parse_args()
    
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Create config directory if needed
    config_dir = Path(args.config_dir)
    config_dir.mkdir(parents=True, exist_ok=True)
    
    _LOG.info("=" * 60)
    _LOG.info("OREI Matrix REST API Server")
    _LOG.info("=" * 60)
    _LOG.info(f"Matrix Host: {args.host}:{args.matrix_port}")
    _LOG.info(f"API Port: {args.port}")
    _LOG.info(f"Config Dir: {config_dir}")
    _LOG.info("=" * 60)
    
    # Create and connect to the matrix
    _LOG.info(f"Connecting to matrix at {args.host}:{args.matrix_port}...")
    matrix = OreiMatrix(host=args.host, port=args.matrix_port, use_https=True)
    
    # Try to connect with retries
    if not await matrix.connect_with_retry(max_retries=3):
        _LOG.error("Failed to connect to matrix. Check the IP address and network connection.")
        _LOG.error("The server will continue but API calls will fail until the matrix is reachable.")
        # Continue anyway - the API can report connection errors
    else:
        _LOG.info("✓ Connected to matrix successfully!")
    
    # Set up the REST API with the matrix device
    set_matrix_device(
        device=matrix,
        config_dir=str(config_dir)
    )
    
    # Create and start the REST API server
    server = RestApiServer(host="0.0.0.0", port=args.port)
    
    try:
        await server.start()
        _LOG.info("")
        _LOG.info("Server is running. Press Ctrl+C to stop.")
        _LOG.info(f"  API Root: http://localhost:{args.port}/api")
        _LOG.info(f"  Web UI:   http://localhost:{args.port}/ui")
        _LOG.info("")
        
        # Wait forever until interrupted
        while True:
            await asyncio.sleep(3600)
            
    except asyncio.CancelledError:
        _LOG.info("Server cancelled...")
    except Exception as e:
        _LOG.error(f"Server error: {e}")
        raise
    finally:
        _LOG.info("Shutting down...")
        # Use timeout to prevent hanging
        try:
            await asyncio.wait_for(server.stop(), timeout=5.0)
        except asyncio.TimeoutError:
            _LOG.warning("Server stop timed out")
        try:
            await asyncio.wait_for(matrix.disconnect(), timeout=5.0)
        except asyncio.TimeoutError:
            _LOG.warning("Matrix disconnect timed out")
        _LOG.info("Server stopped.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nShutdown complete.")

