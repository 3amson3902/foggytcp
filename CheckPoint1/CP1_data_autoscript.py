#!/usr/bin/env python3
import os
import sys
import time
import subprocess
from pathlib import Path

"""
Simple network testing script for foggy-TCP between two VMs.

Usage:
  Server VM: Run server binary manually and keep it running
  Client VM: Run this script to test different network conditions
  
This script:
1. Sets network parameters (delay/bandwidth) on client VM
2. Generates test files 
3. Sends files to server VM
4. Records results

Linux only. Follows Unix philosophy: do one thing well.
"""

# Configuration - adjust these for your setup
SERVER_IP = "10.0.1.1"  # IP of server VM
SERVER_PORT = 3120
CLIENT_BINARY = "./client"  # Path to client binary on client VM


def get_interface():
    """Get default network interface name."""
    try:
        cmd = "ip route show default | awk '/dev/ {print $5}'"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.stdout.strip()
    except Exception:
        return ""


def has_tcconfig():
    """Check if tcconfig tools are available."""
    try:
        subprocess.run(["which", "tcset"], check=True, capture_output=True)
        return True
    except Exception:
        return False


def apply_network_shaping(iface, delay, bandwidth):
    """Apply network shaping using tc or tcconfig."""
    if not iface:
        print(f"[WARN] No interface found, skipping shaping")
        return
        
    if has_tcconfig():
        cmd = ["sudo", "tcset", iface, "--overwrite", "--delay", delay, "--rate", bandwidth]
    else:
        print(f"[WARN] tcconfig not found, install with: pip install tcconfig")
        return
        
    print(f"[SHAPE] Setting {delay} delay, {bandwidth} bandwidth on {iface}")
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Failed to apply shaping: {e}")


def clear_network_shaping(iface):
    """Clear network shaping."""
    if not iface:
        return
        
    try:
        if has_tcconfig():
            subprocess.run(["sudo", "tcdel", iface, "--all"], check=False)
        else:
            subprocess.run(["sudo", "tc", "qdisc", "del", "dev", iface, "root"], check=False)
    except Exception:
        pass


def create_test_file(size, filename):
    """Create test file of specified size."""
    # Convert size format (1KB -> 1K, 1MB -> 1M)
    size_norm = size.replace("B", "").upper()
    
    try:
        subprocess.run(["truncate", "-s", size_norm, filename], check=True)
        print(f"[FILE] Created {filename} ({size})")
    except subprocess.CalledProcessError:
        print(f"[ERROR] Failed to create {filename}")


def run_client_test(server_ip, server_port, test_file):
    """Run client to send file to server."""
    cmd = [CLIENT_BINARY, server_ip, str(server_port), test_file]
    print(f"[TEST] Sending {test_file} to {server_ip}:{server_port}")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if result.returncode == 0:
            print(f"[OK] Transfer completed")
        else:
            print(f"[ERROR] Transfer failed: {result.stderr}")
    except subprocess.TimeoutExpired:
        print(f"[ERROR] Transfer timed out")
    except Exception as e:
        print(f"[ERROR] Transfer error: {e}")


def main():
    """Main testing function."""
    if not sys.platform.startswith("linux"):
        print("[ERROR] Linux only")
        sys.exit(1)
    
    if not Path(CLIENT_BINARY).exists():
        print(f"[ERROR] Client binary not found: {CLIENT_BINARY}")
        sys.exit(1)
    
    print(f"[INFO] Testing with server at {SERVER_IP}:{SERVER_PORT}")
    print(f"[INFO] Make sure server is running on server VM")
    
    interface = get_interface()
    if interface:
        print(f"[INFO] Using interface: {interface}")
    else:
        print(f"[WARN] Could not detect interface")
    
    # Test parameters
    bandwidths = ["10Mbps", "5Mbps", "1Mbps", "500Kbps", "100Kbps", "50Kbps", "10Kbps"]
    delays = ["10ms", "100ms", "1s"]
    file_sizes = ["1KB", "5KB", "25KB", "100KB", "1MB", "10MB"]
    
    # Create test files
    print(f"[SETUP] Creating test files...")
    for size in file_sizes:
        create_test_file(size, f"{size}.txt")
    
    # Run tests
    for bandwidth in bandwidths:
        for delay in delays:
            print(f"\n=== Testing: {bandwidth} / {delay} ===")
            apply_network_shaping(interface, delay, bandwidth)
            time.sleep(1)  # Let shaping settle
            
            for size in file_sizes:
                filename = f"{size}.txt"
                if Path(filename).exists():
                    run_client_test(SERVER_IP, SERVER_PORT, filename)
                    time.sleep(0.5)  # Brief pause between transfers
    
    # Cleanup
    clear_network_shaping(interface)
    print(f"\n[DONE] All tests completed")


if __name__ == "__main__":
    main()