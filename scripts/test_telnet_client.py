#!/usr/bin/env python3
"""
Test the TelnetClient implementation with the real OREI matrix.
"""

import asyncio
import logging
import sys

# Add src to path
sys.path.insert(0, 'src')

from telnet_client import TelnetClient, TelnetState

# Enable debug logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
_LOG = logging.getLogger(__name__)

MATRIX_IP = "192.168.0.100"


async def main():
    print("=" * 60)
    print("OREI BK-808 Telnet Client Test")
    print("=" * 60)
    
    # Create client
    client = TelnetClient(host=MATRIX_IP, port=23)
    
    # Connect
    print("\n[1] Testing connection...")
    if await client.connect():
        print(f"✓ Connected! Firmware: {client.firmware_version}")
    else:
        print("✗ Connection failed!")
        return
    
    # Test full status
    print("\n[2] Testing full status query...")
    try:
        # Get raw response for debugging
        raw_response = await client._send_raw("status")
        print(f"   Raw response length: {len(raw_response)} chars")
        
        status = await client.get_full_status()
        print(f"✓ Status retrieved:")
        print(f"   Power: {status.power}")
        print(f"   Beep: {status.beep}")
        print(f"   Panel Lock: {status.panel_lock}")
        print(f"   LCD Timeout: {status.lcd_timeout}s")
        print(f"   Inputs: {[(p, 'connected' if i.connected else 'disconnected') for p, i in status.inputs.items()]}")
        print(f"   Outputs: {[(p, 'connected' if o.connected else 'disconnected') for p, o in status.outputs.items()]}")
        print(f"   Routing: {dict(status.routing)}")
    except Exception as e:
        print(f"✗ Status failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Test individual input connection
    print("\n[3] Testing input cable detection...")
    for i in range(1, 9):
        try:
            connected = await client.get_input_connection(i)
            symbol = "🔌" if connected else "❌"
            print(f"   Input {i}: {symbol} {'connected' if connected else 'disconnected'}")
        except Exception as e:
            print(f"   Input {i}: error - {e}")
    
    # Test individual output connection
    print("\n[4] Testing output cable detection...")
    for i in range(1, 9):
        try:
            connected = await client.get_output_connection(i)
            symbol = "🔌" if connected else "❌"
            print(f"   Output {i}: {symbol} {'connected' if connected else 'disconnected'}")
        except Exception as e:
            print(f"   Output {i}: error - {e}")
    
    # Test CEC command (power on input 1 - safe command)
    print("\n[5] Testing CEC command (input 1 power on)...")
    try:
        success = await client.cec_input_power_on(1)
        if success:
            print("✓ CEC power on sent to input 1")
        else:
            print("✗ CEC command failed")
    except Exception as e:
        print(f"✗ CEC error: {e}")
    
    # Disconnect
    print("\n[6] Disconnecting...")
    await client.disconnect()
    print("✓ Disconnected")
    
    print("\n" + "=" * 60)
    print("Test complete!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
