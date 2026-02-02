#!/usr/bin/env python3
"""
Compare HTTP vs HTTPS responses to see what's different.

NOTE: This is a manual/interactive test requiring hardware.
Run directly with: python tests/test_http_vs_https.py 192.168.1.100
"""
import asyncio
import json
import os

import pytest
import aiohttp

# Skip in pytest runs - this is a manual hardware test
pytestmark = pytest.mark.skipif(
    not os.environ.get("MATRIX_HOST"),
    reason="Manual hardware test - set MATRIX_HOST to run"
)

async def test_preset(protocol: str, host: str, port: int, preset: int):
    """Test a single preset with given protocol."""
    print(f"\n{'='*70}")
    print(f"Testing {protocol.upper()} on port {port} - Preset {preset}")
    print(f"{'='*70}")
    
    try:
        # Create session with SSL disabled for HTTPS
        connector = aiohttp.TCPConnector(ssl=False) if protocol == "https" else None
        async with aiohttp.ClientSession(
            cookie_jar=aiohttp.CookieJar(),
            connector=connector
        ) as session:
            url = f"{protocol}://{host}:{port}/cgi-bin/instr"
            
            # Login first
            print("Logging in...")
            login_cmd = {"comhead": "login", "user": "Admin", "password": "admin"}
            async with session.post(url, json=login_cmd, timeout=aiohttp.ClientTimeout(total=5)) as resp:
                text = await resp.text()
                login_result = json.loads(text)
                print(f"  Login response: {login_result}")
            
            # Send preset command
            print(f"Sending preset {preset} command...")
            preset_cmd = {"comhead": "preset set", "language": 0, "index": preset}
            print(f"  Command: {preset_cmd}")
            
            async with session.post(url, json=preset_cmd, timeout=aiohttp.ClientTimeout(total=5)) as resp:
                text = await resp.text()
                result = json.loads(text)
                print(f"  Response: {result}")
                print(f"  Status: {resp.status}")
                print(f"  Headers: {dict(resp.headers)}")
                
                # Check cookies
                cookies = session.cookie_jar.filter_cookies(url)
                if cookies:
                    print(f"  Cookies: {dict(cookies)}")
                
            return result
            
    except Exception as ex:
        print(f"  ERROR: {ex}")
        return None

async def main():
    host = "192.168.0.100"
    preset = 1
    
    print("\nThis will test the same preset command via HTTP and HTTPS")
    print("WATCH YOUR MATRIX to see which one actually changes routing!")
    
    input("\nPress Enter to test HTTP (port 80)...")
    await test_preset("http", host, 80, preset)
    
    input("\nPress Enter to test HTTPS (port 443)...")
    await test_preset("https", host, 443, preset)
    
    print("\n" + "="*70)
    print("Which one changed your matrix routing? HTTP, HTTPS, or both?")
    print("="*70)

if __name__ == "__main__":
    asyncio.run(main())
