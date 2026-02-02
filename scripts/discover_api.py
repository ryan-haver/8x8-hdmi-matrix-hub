#!/usr/bin/env python3
"""
OREI BK-808 API Endpoint Discovery Tool

This script systematically tests all potential HTTP API endpoints to discover
undocumented commands that might provide additional functionality like input
cable/connection detection.
"""

import json
import sys
import ssl
import urllib3
import requests
from typing import Optional

# Disable SSL warnings for self-signed cert
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Matrix configuration
MATRIX_IP = "192.168.0.100"
MATRIX_PORT = 443
BASE_URL = f"https://{MATRIX_IP}:{MATRIX_PORT}/cgi-bin/instr"

# Session for maintaining login
session = requests.Session()
session.verify = False

def send_command(comhead: str, params: Optional[dict] = None, timeout: int = 5) -> dict:
    """Send a command to the matrix and return the response."""
    payload = {"comhead": comhead, "language": 0}
    if params:
        payload.update(params)
    
    try:
        response = session.post(BASE_URL, json=payload, timeout=timeout)
        return response.json()
    except requests.exceptions.Timeout:
        return {"error": "timeout"}
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}
    except json.JSONDecodeError:
        return {"error": "invalid_json", "raw": response.text[:200] if response else "no response"}

def login() -> bool:
    """Login to the matrix."""
    result = send_command("login", {"user": "Admin", "password": "admin"})
    # Check for multiple success conditions
    return result.get("result") == "success" or result.get("result") == 1 or result.get("comhead") == "login"

def test_endpoint(comhead: str, params: Optional[dict] = None) -> tuple:
    """Test an endpoint and return (success, response)."""
    result = send_command(comhead, params)
    
    # Determine if it's a valid endpoint
    if "error" in result:
        return False, result
    if result.get("comhead") == comhead:
        return True, result
    if "result" in result:
        return True, result
    
    return False, result

def main():
    print("=" * 70)
    print("OREI BK-808 API ENDPOINT DISCOVERY TOOL")
    print("=" * 70)
    print()
    
    # Login first
    print("[*] Logging in to matrix...")
    if not login():
        print("[!] Login failed!")
        sys.exit(1)
    print("[+] Login successful!")
    print()
    
    # Known working endpoints (from HAR file)
    known_endpoints = [
        "get system status",
        "get status",
        "get network",
        "get input status",
        "get output status",
        "get video status",
        "get cec status",
        "get ext-audio status",
        "get routing status",
    ]
    
    # Potential undiscovered GET endpoints to probe
    # Based on patterns from known endpoints and Control4/RTI drivers
    potential_get_endpoints = [
        # Input connection variants
        "get input connection",
        "get input connect",
        "get input connected",
        "get input cable",
        "get input hpd",
        "get input plug",
        "get input detect",
        "get input signal",
        "get input sync",
        "get input active",
        "get input inactive",
        "get input hot plug",
        "get input hotplug",
        "get all input status",
        "get all input",
        "get inputs",
        "get input info",
        "get input detail",
        "get input details",
        
        # HDMI specific
        "get hdmi status",
        "get hdmi input status",
        "get hdmi output status",
        "get hdmi input",
        "get hdmi output",
        "get hdmi info",
        
        # Output variants
        "get output connection",
        "get output connect",
        "get output cable",
        "get output signal",
        "get all output status",
        "get all output",
        "get outputs",
        "get output info",
        "get output detail",
        
        # General status variants  
        "get all status",
        "get full status",
        "get complete status",
        "get device status",
        "get matrix status",
        "get switch status",
        "get port status",
        "get all port status",
        "get connection status",
        "get connect status",
        "get link status",
        "get cable status",
        "get signal status",
        "get hpd status",
        "get plug status",
        "get detect status",
        "get sync status",
        "get active status",
        
        # Routing variants
        "get routing",
        "get route",
        "get routes",
        "get switch",
        "get switching",
        "get av status",
        "get av routing",
        "get source",
        "get sources",
        "get source status",
        
        # EDID variants
        "get edid",
        "get edid status",
        "get edid info",
        "get input edid",
        "get output edid",
        
        # HDCP variants
        "get hdcp",
        "get hdcp status",
        "get hdcp info",
        
        # HDR variants
        "get hdr",
        "get hdr status",
        "get hdr info",
        
        # Scaler variants
        "get scaler",
        "get scaler status",
        "get video mode",
        
        # ARC variants
        "get arc",
        "get arc status",
        "get audio status",
        
        # Mute variants
        "get mute",
        "get mute status",
        "get audio mute",
        
        # Preset variants
        "get preset",
        "get presets",
        "get preset status",
        "get scene",
        "get scenes",
        
        # Device info variants
        "get info",
        "get device",
        "get device info",
        "get firmware",
        "get version",
        "get model",
        "get serial",
        
        # Debug/diagnostic endpoints
        "get debug",
        "get log",
        "get logs",
        "get diagnostics",
        "get diagnostic",
        "get test",
        "get raw status",
        "get telnet",
        
        # Alternative naming patterns
        "input status",
        "output status",
        "system status",
        "read input status",
        "read output status",
        "read system status",
        "query input status",
        "query output status",
        "query system status",
        "r status",
        "r input status",
        "r output status",
    ]
    
    # Test known endpoints first
    print("[*] Testing KNOWN endpoints...")
    print("-" * 70)
    for endpoint in known_endpoints:
        success, result = test_endpoint(endpoint)
        status = "✓" if success else "✗"
        print(f"  {status} {endpoint}")
        if success and "error" not in result:
            # Show keys only
            keys = [k for k in result.keys() if k != "comhead"]
            print(f"      Keys: {', '.join(keys)}")
    print()
    
    # Test potential undiscovered endpoints
    print("[*] Testing POTENTIAL undiscovered endpoints...")
    print("-" * 70)
    
    discovered = []
    for endpoint in potential_get_endpoints:
        success, result = test_endpoint(endpoint)
        if success and "error" not in result:
            discovered.append((endpoint, result))
            print(f"  ✓ FOUND: {endpoint}")
            print(f"      Response: {json.dumps(result, indent=2)[:500]}")
        # Uncomment to see failed endpoints
        # else:
        #     print(f"  ✗ {endpoint}")
    
    print()
    print("=" * 70)
    print("DISCOVERY SUMMARY")
    print("=" * 70)
    
    if discovered:
        print(f"\n[+] Found {len(discovered)} undiscovered endpoint(s)!")
        for endpoint, result in discovered:
            print(f"\n  • {endpoint}")
            print(f"    {json.dumps(result, indent=4)}")
    else:
        print("\n[-] No undiscovered endpoints found with the tested patterns.")
        print("    The HTTP API may truly be limited to the known set.")
        print("    Consider using Telnet/TCP (port 23/8000) for additional capabilities.")
    
    print()
    
    # Try a few targeted tests with different parameter combinations
    print("[*] Testing specific parameter variations...")
    print("-" * 70)
    
    # Try get input status with additional params
    variations = [
        ("get input status", {"index": 0}),
        ("get input status", {"index": 1}),
        ("get input status", {"port": 1}),
        ("get input status", {"all": 1}),
        ("get input status", {"detail": 1}),
        ("get input status", {"connection": 1}),
        ("get output status", {"index": 0}),
        ("get output status", {"detail": 1}),
        ("get status", {"all": 1}),
        ("get status", {"detail": 1}),
    ]
    
    for endpoint, params in variations:
        success, result = test_endpoint(endpoint, params)
        if success:
            # Check if response has more keys than the base endpoint
            base_result = send_command(endpoint)
            if len(result.keys()) > len(base_result.keys()):
                print(f"  ✓ {endpoint} with {params} has MORE keys!")
                print(f"      Base keys: {list(base_result.keys())}")
                print(f"      Extended keys: {list(result.keys())}")
    
    print("\n[*] Discovery complete!")

if __name__ == "__main__":
    main()
