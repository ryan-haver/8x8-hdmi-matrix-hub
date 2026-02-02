#!/usr/bin/env python3
"""
OREI BK-808 Telnet Interface Test

This script tests the Telnet/TCP interface to see what status information
is available through the serial-over-IP protocol.
"""

import socket
import time
import sys

MATRIX_IP = "192.168.0.100"
TELNET_PORT = 23
TCP_PORT = 8000

import telnetlib

def test_telnet_proper(port: int):
    """Test Telnet connection using proper telnetlib."""
    print(f"\n[*] Testing port {port} with telnetlib...")
    
    try:
        tn = telnetlib.Telnet(MATRIX_IP, port, timeout=5)
        print(f"[+] Connected to {MATRIX_IP}:{port}")
        
        # Read welcome banner
        time.sleep(1.0)
        banner = tn.read_very_eager()
        if banner:
            print(f"[+] Banner: {banner}")
        
        # Try many different command format variations
        # Control4 driver uses command + "!\r\n" as terminator!
        commands = [
            # From Control4 driver - exact commands
            b"r status",
            b"r power",
            b"r input status",
            b"r output status",
            
            # Set commands from driver
            b"s power on",
            b"s power off",
            
            # Status read commands
            b"r output 1 hdcp",
            b"r output 1 video mode",
            b"r output 1 hdr",
            b"r output 1 in source",
            
            # Simple queries
            b"status",
            b"help",
            b"?",
        ]
        
        for cmd in commands:
            # Control4 driver uses cmd + "!\r\n" as terminator
            full_cmd = cmd + b"!\r\n"
            print(f"\n[>] Sending: {repr(full_cmd)}")
            tn.write(full_cmd)
            time.sleep(0.5)
            
            response = tn.read_very_eager()
            if response:
                decoded = response.decode('utf-8', errors='replace')
                print(f"[<] Response: {repr(decoded)}")
        
        # Listen for push data
        print("\n[*] Waiting 15 seconds for any push notifications...")
        print("    (Try connecting/disconnecting an HDMI cable NOW!)")
        
        start = time.time()
        while time.time() - start < 15:
            data = tn.read_very_eager()
            if data:
                print(f"\n[!] PUSH DATA: {data}")
                decoded = data.decode('utf-8', errors='replace')
                print(f"[!] Decoded: {repr(decoded)}")
            time.sleep(0.2)
        
        tn.close()
        return True
        
    except Exception as e:
        print(f"[-] Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_telnet(port: int):
    """Test Telnet connection and commands."""
    print(f"\n[*] Testing port {port}...")
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        sock.connect((MATRIX_IP, port))
        print(f"[+] Connected to {MATRIX_IP}:{port}")
        
        # Wait for initial response/banner
        time.sleep(1.0)
        try:
            initial = sock.recv(4096)
            if initial:
                print(f"[+] Initial response: {initial}")
        except socket.timeout:
            print("[*] No initial banner")
        
        # Only test commands that seemed valid (no E00)
        commands = [
            b"r output 1 in source\r\n",             # Query routing for output 1
            b"r input 1 status\r\n",                 # Input status query
            b"r all output status\r\n",              # All output status
            b"s output 1 hdcp 3\r\n",                # HDCP follow sink
        ]
        
        for cmd in commands:
            print(f"\n[>] Sending: {cmd.strip()}")
            sock.send(cmd)
            time.sleep(1.0)  # Wait longer for response
            
            # Try to read multiple times
            full_response = b""
            for _ in range(3):
                try:
                    sock.settimeout(0.5)
                    chunk = sock.recv(4096)
                    if chunk:
                        full_response += chunk
                except socket.timeout:
                    break
            
            if full_response:
                print(f"[<] Response: {full_response}")
                # Try to decode and show readable
                try:
                    decoded = full_response.decode('utf-8', errors='replace')
                    print(f"[<] Decoded: {repr(decoded)}")
                except:
                    pass
            else:
                print("[<] No response")
        
        sock.close()
        return True
        
    except socket.timeout:
        print(f"[-] Connection timeout to port {port}")
        return False
    except ConnectionRefusedError:
        print(f"[-] Connection refused on port {port}")
        return False
    except Exception as e:
        print(f"[-] Error: {e}")
        return False

def main():
    print("=" * 60)
    print("OREI BK-808 TELNET/TCP INTERFACE TEST")
    print("=" * 60)
    
    # Try Telnet port with proper telnetlib
    test_telnet_proper(TELNET_PORT)
    
    print("\n[*] Test complete!")

if __name__ == "__main__":
    main()
