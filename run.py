#!/usr/bin/env python3
"""
Start script for OREI HDMI Matrix integration.

Usage: python3 run.py
"""

import sys
import os
import runpy

# Get project root directory
project_root = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(project_root, "src")

# Add src directory to path
sys.path.insert(0, src_path)

# Run the driver as __main__ so the startup code executes
if __name__ == "__main__":
    os.chdir(project_root)  # Change to project root for driver.json
    runpy.run_path(os.path.join(src_path, "driver.py"), run_name="__main__")
