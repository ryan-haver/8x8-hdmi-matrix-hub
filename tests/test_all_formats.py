#!/usr/bin/env python3
"""
Test all possible command formats for OREI Matrix
Run this and watch your matrix to see which format works

NOTE: This is a manual/interactive test requiring hardware.
Run directly with: python tests/test_all_formats.py 192.168.1.100
"""
import asyncio
import os
import socket
import sys
import time

import pytest

# Skip in pytest runs - this is a manual hardware test
pytestmark = pytest.mark.skipif(
    not os.environ.get("MATRIX_HOST"),
    reason="Manual hardware test - set MATRIX_HOST to run"
)

async def test_format(host: str, port: int, command: str, description: str):
    """Test a single command format"""
    print(f"\n{'='*60}")
    print(f"Testing: {description}")
    print(f"Command: '{command}'")
    print(f"{'='*60}")
    
    try:
        reader, writer = await asyncio.open_connection(host, port)
        
        # Try with different line terminators
        terminators = [
            ("\r\n", "CRLF (\\r\\n)"),
            ("\n", "LF (\\n)"),
            ("\r", "CR (\\r)"),
            ("", "No terminator"),
            ("!", "Exclamation (!)"),
        ]
        
        for terminator, term_desc in terminators:
            cmd = f"{command}{terminator}"
            print(f"\n  → Sending with {term_desc}: '{command}{repr(terminator)}'")
            writer.write(cmd.encode("ascii"))
            await writer.drain()
            
            # Wait and check if there's a response
            print(f"     Waiting 2 seconds... WATCH YOUR MATRIX!")
            await asyncio.sleep(2)
            
            # Try to read any response
            try:
                writer.write(b"")  # Flush
                await writer.drain()
                if reader._buffer:
                    response = reader._buffer.decode('ascii', errors='ignore')
                    print(f"     Response: {response}")
            except:
                pass
            
            print(f"     Did the routing change? (waiting...)")
            await asyncio.sleep(1)
        
        writer.close()
        await writer.wait_closed()
        
    except Exception as ex:
        print(f"  ✗ Error: {ex}")
        return False
    
    return True

async def main():
    if len(sys.argv) < 2:
        print("Usage: python test_all_formats.py <matrix_ip>")
        sys.exit(1)
    
    host = sys.argv[1]
    port = 23
    preset = 1
    
    print(f"\n{'='*60}")
    print(f"OREI Matrix Command Format Tester")
    print(f"{'='*60}")
    print(f"Target: {host}:{port}")
    print(f"Testing Preset {preset}")
    print(f"\nWATCH YOUR MATRIX for routing changes!")
    print(f"We'll test multiple command formats...")
    print(f"{'='*60}")
    
    input("\nPress Enter to start testing...")
    
    # All possible command formats to try
    test_cases = [
        (f"preset {preset}", "Lowercase 'preset N'"),
        (f"PRESET {preset}", "Uppercase 'PRESET N'"),
        (f"Preset {preset}", "Capitalized 'Preset N'"),
        (f"preset{preset}", "No space 'presetN'"),
        (f"PRESET{preset}", "No space 'PRESETN'"),
        (f"load preset {preset}", "Load preset N"),
        (f"recall preset {preset}", "Recall preset N"),
        (f"call preset {preset}", "Call preset N"),
        (f"scene {preset}", "Scene N"),
        (f"SCENE{preset}", "SCENEN"),
        (f"MT00PR0{preset}", "MT protocol PR (preset)"),
        (f"MT00SW0{preset}", "MT protocol SW (switch)"),
        (f"MT00SC0{preset}", "MT protocol SC (scene)"),
        (f"s recall preset {preset}", "S recall preset N"),
        (f"s load preset {preset}", "S load preset N"),
        (f"SET#0{preset}", "SET#0N format"),
        (f"@PRESET{preset}", "@PRESETN format"),
        (f"#PRESET{preset}", "#PRESETN format"),
        (f"$PRESET{preset}", "$PRESETN format"),
        (f"PRE{preset}", "Short PREN"),
        (f"P{preset}", "Single P N"),
    ]
    
    for command, description in test_cases:
        await test_format(host, port, command, description)
        
        response = input("\n  ▶ Did the routing change? (y/n/q to quit): ").strip().lower()
        if response == 'y':
            print(f"\n  ✓✓✓ SUCCESS! This format works: '{command}'")
            print(f"  ✓✓✓ Description: {description}")
            print(f"\n  Now testing which terminator worked...")
            # Would need to test again to isolate terminator
            break
        elif response == 'q':
            print("\n  Stopping test.")
            break
        else:
            print("  Continuing to next format...")
    
    print(f"\n{'='*60}")
    print("Test complete!")
    print(f"{'='*60}")

if __name__ == "__main__":
    asyncio.run(main())
