#!/usr/bin/env python3
"""
Manual interactive test for OREI Matrix presets.
Send commands one at a time with confirmation.
"""
import asyncio
import json
import sys
import aiohttp

# Session for keeping login state
_session = None

async def send_preset(host: str, port: int, preset_num: int):
    """Send a single preset command via HTTPS."""
    global _session
    try:
        # Create session with SSL disabled and cookie jar if not exists
        if _session is None:
            connector = aiohttp.TCPConnector(ssl=False)
            _session = aiohttp.ClientSession(
                cookie_jar=aiohttp.CookieJar(),
                connector=connector
            )
            
            # Login first
            protocol = "https" if port == 443 else "http"
            url = f"{protocol}://{host}:{port}/cgi-bin/instr"
            login_cmd = {"comhead": "login", "user": "Admin", "password": "admin"}
            print(f"   Logging in to {protocol}://{host}:{port}...")
            
            async with _session.post(url, json=login_cmd, timeout=aiohttp.ClientTimeout(total=5)) as resp:
                text = await resp.text()
                result = json.loads(text)
                print(f"   Login result: {result}")
                if result.get("result") != 1:
                    print(f"   ⚠️  Login may have failed!")
        
        # Send preset command
        protocol = "https" if port == 443 else "http"
        url = f"{protocol}://{host}:{port}/cgi-bin/instr"
        command = {
            "comhead": "preset set",
            "language": 0,
            "index": preset_num
        }
        
        print(f"   Sending: {json.dumps(command)}")
        
        async with _session.post(url, json=command, timeout=aiohttp.ClientTimeout(total=5)) as resp:
            text = await resp.text()
            result = json.loads(text)
            print(f"   Response: {result}")
            
            if result.get("result") == 1:
                print(f"   ✅ Matrix confirmed preset {preset_num}")
                return True
            else:
                print(f"   ⚠️  Matrix returned result: {result.get('result')}")
                return False
        
    except Exception as ex:
        print(f"   ❌ ERROR: {ex}")
        return False

async def cleanup():
    """Close the session."""
    global _session
    if _session:
        await _session.close()
        _session = None

async def main():
    if len(sys.argv) < 2:
        print("Usage: python test_manual.py <matrix_ip> [port]")
        print("Default port is 443 (HTTPS)")
        sys.exit(1)
    
    host = sys.argv[1]
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 443
    protocol = "https" if port == 443 else "http"
    
    print("="*70)
    print("OREI Matrix Manual Preset Test")
    print("="*70)
    print(f"Target: {protocol}://{host}:{port}")
    print()
    print("This will send preset commands ONE AT A TIME.")
    print("Watch your matrix CAREFULLY for any routing changes!")
    print("="*70)
    print()
    
    try:
        while True:
            preset = input("\nEnter preset number (1-8) or 'q' to quit: ").strip()
            
            if preset.lower() == 'q':
                print("Exiting...")
                break
            
            try:
                preset_num = int(preset)
                if preset_num < 1 or preset_num > 8:
                    print("❌ Invalid preset. Must be 1-8.")
                    continue
            except ValueError:
                print("❌ Invalid input. Enter a number 1-8 or 'q'.")
                continue
            
            print(f"\n{'='*70}")
            print(f"🎬 SENDING PRESET {preset_num}")
            print(f"{'='*70}")
            print("👀 WATCH YOUR MATRIX NOW!")
            print()
            
            success = await send_preset(host, port, preset_num)
            
            if success:
                print("\n✅ Command sent and confirmed by matrix!")
            else:
                print("\n❌ Command may have failed")
            
            response = input("\nDid you see the routing change? (y/n): ").strip().lower()
            if response == 'y':
                print(f"🎉 SUCCESS! Preset {preset_num} is working via {protocol.upper()}!")
            else:
                print("❌ No change observed.")
    finally:
        await cleanup()
        if response == 'y':
            print("🎉 SUCCESS! Preset command is working!")
            print(f"   The correct command format is:")
            print(f'   {{"comhead": "preset set", "language": 0, "index": {preset_num}}}')
        else:
            print("❌ No change observed. The matrix may not be responding to commands.")
            print("   Possible issues:")
            print("   - Preset might not be configured on the matrix")
            print("   - Wrong protocol or command format")
            print("   - Matrix web UI might use different endpoint")

if __name__ == "__main__":
    asyncio.run(main())
