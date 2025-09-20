#!/usr/bin/env python3
import os
import sys
import time
import subprocess
import csv
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
# Use current directory as base for all operations
current_dir = Path(__file__).parent

CLIENT_BINARY = str(current_dir / "bin" / "client")
test_file_location = str(current_dir / "test_files")
output_dir = str(current_dir / "results")

# Global test counter for CSV tracking
test_id_counter = 0

def get_interface():
    """Get network interface that can reach the server IP."""
    try:
        # Use ip route to find interface that would be used to reach server
        cmd = f"ip route get {SERVER_IP} | grep -oP 'dev \\K[^ ]+' | head -n1"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        interface = result.stdout.strip()
        print(f"[INFO] Detected interface: {interface}")
        return interface
    except Exception:
        return ""


def init_test_params_csv(filename="test_parameters.csv"):
    """Initialize CSV file for test parameters."""
    csv_path = Path(output_dir) / filename
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    with open(csv_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['test_id', 'test_name', 'bandwidth', 'delay', 'file_size', 'file_path'])
    
    print(f"[CSV] Initialized test parameters CSV: {csv_path}")
    return csv_path


def log_test_params(test_id, test_name, bandwidth, delay, file_size, file_path, filename="test_parameters.csv"):
    """Log test parameters to CSV file."""
    csv_path = Path(output_dir) / filename
    
    with open(csv_path, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([test_id, test_name, bandwidth, delay, file_size, file_path])
    
    print(f"[CSV] Logged test {test_id}: {test_name}, {bandwidth}, {delay}, {file_size}")


def get_next_test_id():
    """Get next test ID and increment counter."""
    global test_id_counter
    current_id = test_id_counter
    test_id_counter += 1
    return current_id


def has_tcconfig():
    """Check if tcconfig tools are available."""
    try:
        # Try running tcset --version to check if it's available
        result = subprocess.run(["tcset", "--version"], check=True, capture_output=True, text=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        try:
            # Fallback: try with full path if installed via pip
            result = subprocess.run(["python3", "-m", "tcconfig.tcset", "--version"], check=True, capture_output=True, text=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False


def apply_network_shaping(iface, delay, bandwidth):
    """Apply network shaping using tc or tcconfig."""
    if not iface:
        print(f"[WARN] No interface found, skipping shaping")
        return
        
    if has_tcconfig():
        cmd = ["sudo", "tcset", iface, "--delay", delay, "--rate", bandwidth]
        print(f"[SHAPE] Setting {delay} delay, {bandwidth} bandwidth on {iface}")
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            print(f"[OK] Network shaping applied successfully")
        except subprocess.CalledProcessError as e:
            print(f"[ERROR] Failed to apply network shaping: {e.stderr}")
            
    else:
        print(f"[WARN] tcconfig not found, install with: pip install tcconfig")
        return


def clear_network_shaping(iface):
    """Clear network shaping."""
    try:
        if has_tcconfig():
            subprocess.run(["sudo", "tcdel", iface, "--all"], check=False)
    except Exception:
        pass


def create_test_file(size, filename, directory=test_file_location):
    """Create test file of specified size."""
    # Convert size format (1KB -> 1K, 1MB -> 1M)
    size_norm = size.replace("B", "").upper()
    file_path = Path(directory) / filename
    try:
        subprocess.run(["truncate", "-s", size_norm, str(file_path)], check=True)
        print(f"[FILE] Created {filename} ({size}) at {directory}")
    except subprocess.CalledProcessError:
        print(f"[ERROR] Failed to create {filename}")


def run_client_test(server_ip, server_port, test_file, test_name="", bandwidth="", delay="", file_size=""):
    """Run client to send file to server and log parameters."""
    cmd = [CLIENT_BINARY, server_ip, str(server_port), test_file]
    print(f"[TEST] Sending {test_file} to {server_ip}:{server_port}")
    
    # Get test ID and log parameters
    test_id = get_next_test_id()
    log_test_params(test_id, test_name, bandwidth, delay, file_size, test_file)
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if result.returncode == 0:
            print(f"[OK] Transfer completed (Test ID: {test_id})")
            return True
        else:
            print(f"[ERROR] Transfer failed: {result.stderr}")
            print(f"[FATAL] Transmission failed, exiting program")
            sys.exit(1)
    except subprocess.TimeoutExpired:
        print(f"[ERROR] Transfer timed out")
        print(f"[FATAL] Transmission failed, exiting program")
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR] Transfer error: {e}")
        print(f"[FATAL] Transmission failed, exiting program")
        sys.exit(1)


def make_test_directory(directory=test_file_location):
    """Create directory for test files if it doesn't exist."""
    Path(directory).mkdir(parents=True, exist_ok=True)
    print(f"[SETUP] Test files will be stored in: {directory}")


def setup_local_environment():
    """Setup the local directory structure and binaries."""
    # Create necessary directories
    bin_dir = current_dir / "bin"
    bin_dir.mkdir(parents=True, exist_ok=True)
    
    # Create test files directory
    Path(test_file_location).mkdir(parents=True, exist_ok=True)
    
    # Create results directory
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    print(f"[SETUP] Created local directory structure:")
    print(f"[SETUP] - bin: {bin_dir}")
    print(f"[SETUP] - test_files: {test_file_location}")
    print(f"[SETUP] - results: {output_dir}")
    
    # Check if client binary exists, if not try to find it in the project structure
    if not Path(CLIENT_BINARY).exists():
        # Try to find the client binary in the parent project structure
        project_root = current_dir.parent.parent
        source_binary = project_root / "foggytcp" / "bin" / "client"
        
        if source_binary.exists():
            import shutil
            shutil.copy2(source_binary, CLIENT_BINARY)
            print(f"[SETUP] Copied client binary from {source_binary}")
        else:
            print(f"[WARN] Client binary not found at {source_binary}")
            print(f"[WARN] You may need to build the project first or copy the binary manually to {CLIENT_BINARY}")
    else:
        print(f"[SETUP] Client binary found at {CLIENT_BINARY}")


def check_sudo_access():
    """Check if sudo access is available for network shaping."""
    try:
        result = subprocess.run(["sudo", "-n", "true"], capture_output=True)
        if result.returncode != 0:
            print("[ERROR] This script requires sudo privileges for network shaping")
            print("[INFO] Please run with: sudo python3 CP1_data_collector.py")
            sys.exit(1)
    except Exception:
        print("[WARN] Cannot verify sudo access, network shaping may fail")


def run_test_suite(interface, test_name, bandwidth, delay, file_sizes):
    """Run a test suite with given parameters."""
    print(f"\n" + "="*50)
    print(f"{test_name}")
    print(f"Bandwidth = {bandwidth}, Delay = {delay}")
    print(f"File sizes = {', '.join(file_sizes)}")
    print(f"="*50)
    
    # Clear any existing network shaping before applying new settings
    clear_network_shaping(interface)
    time.sleep(0.5)
    
    # Create test files
    for size in file_sizes:
        create_test_file(size, f"{size}.txt")
    
    # Apply network shaping once for this test
    apply_network_shaping(interface, delay, bandwidth)
    time.sleep(1)
    validate_network_settings(interface)
    # Run transfers
    for size in file_sizes:
        filename = f"{size}.txt"
        file_path = Path(test_file_location) / filename
        if file_path.exists():
            print(f"\n[{test_name.split(':')[0]}] Testing {size}")
            run_client_test(SERVER_IP, SERVER_PORT, str(file_path), 
                          test_name=test_name, bandwidth=bandwidth, delay=delay, file_size=size)
            time.sleep(1)


def run_variable_test(interface, test_name, fixed_params, variable_param, values):
    """Run a test varying one parameter while keeping others fixed."""
    print(f"\n" + "="*50)
    print(f"{test_name}")
    print(f"Fixed: {fixed_params}")
    print(f"Variable: {variable_param} = {', '.join(values)}")
    print(f"="*50)
    
    # Clear any existing network shaping before starting
    clear_network_shaping(interface)
    time.sleep(0.5)
    
    # Create test file if needed
    if 'file_size' in fixed_params:
        size = fixed_params['file_size']
        create_test_file(size, f"{size}.txt")
        file_path = Path(test_file_location) / f"{size}.txt"
        
        for value in values:
            print(f"\n[{test_name.split(':')[0]}] Testing {variable_param}={value}")
            
            # Clear previous settings before applying new ones
            clear_network_shaping(interface)
            time.sleep(0.5)
            
            # Set parameters based on what's being varied
            current_bandwidth = ""
            current_delay = ""
            
            if variable_param == 'bandwidth':
                current_bandwidth = value
                current_delay = fixed_params['delay']
                apply_network_shaping(interface, fixed_params['delay'], value)
            elif variable_param == 'delay':
                current_bandwidth = fixed_params['bandwidth']
                current_delay = value
                apply_network_shaping(interface, value, fixed_params['bandwidth'])
            
            validate_network_settings(interface)
            time.sleep(1)
            run_client_test(SERVER_IP, SERVER_PORT, str(file_path),
                          test_name=f"{test_name} ({variable_param}={value})",
                          bandwidth=current_bandwidth, delay=current_delay, file_size=size)
            time.sleep(1)


def validate_network_settings(interface=None):
    if interface is None:
        interface = get_interface()
    if has_tcconfig():
        print(f"[INFO] tcconfig tools found")
        print(f"[INFO] Current network settings:")
        cmd = [f"sudo tcshow {interface}"]
        subprocess.run(cmd, shell=True)
        return 
    else:
        print(f"[WARN] tcconfig not found, cannot display network settings")


def main():
    """Main testing function."""
    if not sys.platform.startswith("linux"):
        print("[ERROR] Linux only")
        sys.exit(1)
    
    # Setup local environment first
    print(f"[SETUP] Setting up local environment...")
    setup_local_environment()
    
    # Initialize CSV for test parameters
    init_test_params_csv()
    
    check_sudo_access()
    validate_client_binary_existence()
    
    print(f"[INFO] Testing with server at {SERVER_IP}:{SERVER_PORT}")
    print(f"[INFO] Make sure server is running on server VM")
    
    interface = get_interface()
    if interface:
        print(f"[INFO] Using interface: {interface}")
    else:
        print(f"[WARN] Could not detect interface")
    
    print(f"[SETUP] Preparing test file folder...")
    make_test_directory(test_file_location)
    
    # Clear any existing network shaping before starting tests
    print(f"[SETUP] Clearing any existing network shaping...")
    clear_network_shaping(interface)
    
    try:
        # Test 1: Different file sizes
        run_test_suite(
            interface, 
            "TEST 1: Different File Sizes",
            "10Mbps", "10ms", 
            ["1KB", "5KB", "25KB", "100KB", "1MB", "10MB"]
        )
        
        # Test 2: Different bandwidths  
        run_variable_test(
            interface,
            "TEST 2: Different Bandwidths",
            {"delay": "10ms", "file_size": "1MB"},
            "bandwidth",
            ["1Mbps", "2Mbps", "4Mbps", "5Mbps", "10Mbps", "20Mbps"]
        )
        
        # Test 3: Different delays
        run_variable_test(
            interface,
            "TEST 3: Different Delays", 
            {"bandwidth": "10Mbps", "file_size": "1MB"},
            "delay",
            ["0ms", "5ms", "10ms", "20ms", "50ms", "100ms"]
        )
        
        print(f"\n[DONE] All tests completed successfully!")
        
    finally:
        # Always cleanup network shaping, even if tests fail
        print(f"[CLEANUP] Clearing network shaping...")
        clear_network_shaping(interface)


def validate_client_binary_existence():
    if not Path(CLIENT_BINARY).exists():
        print(f"[ERROR] Client binary not found: {CLIENT_BINARY}")
        sys.exit(1)


def record_log(output, filename="client.log", directory=output_dir):
    # Create directory if it doesn't exist
    Path(directory).mkdir(parents=True, exist_ok=True)
    
    with open(Path(directory) / filename, "a") as f:
        f.write(output + "\n")
        f.flush()
        os.fsync(f.fileno())


if __name__ == "__main__":
    main()