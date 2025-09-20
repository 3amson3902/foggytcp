import subprocess
import os
import time
import hashlib
from pathlib import Path

"""
Simple network testing script for foggy-TCP between two VMs.

Usage:
  Server VM: Run server binary manually and keep it running
  Client VM: Run this script to test different network conditions
  
This script:
1. Listens for incoming connections and saves received files
2. Records results (output from server binary)

Linux only. Follows Unix philosophy: do one thing well.
"""

SERVER_IP = "10.0.1.1"  # IP of server VM
SERVER_PORT = 3120
# Use current directory as base for all operations
current_dir = Path(__file__).parent

BINARY = str(current_dir / "bin" / "server")  # Path to server binary on server VM
CLIENT_BINARY = str(current_dir / "bin" / "client")
OUTPUT_DIR = str(current_dir / "results") + "/"

def hash_the_bin(binary_path=BINARY):
    """
    Calculate SHA256 hash of the binary file to confirm its integrity.
    
    Args:
        binary_path: Path to the binary file to hash
        
    Returns:
        str: SHA256 hash of the binary file, or error message if file not found
    """
    try:
        binary_file = Path(binary_path)
        if not binary_file.exists():
            return f"Binary file not found: {binary_path}"
        
        # Calculate SHA256 hash
        sha256_hash = hashlib.sha256()
        with open(binary_file, "rb") as f:
            # Read file in chunks to handle large files efficiently
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)
        
        hash_value = sha256_hash.hexdigest()
        print(f"Binary hash (SHA256): {hash_value}")
        print(f"Binary path: {binary_path}")
        print(f"Binary size: {binary_file.stat().st_size} bytes")
        
        return hash_value
        
    except Exception as e:
        error_msg = f"Error hashing binary: {e}"
        print(error_msg)
        return error_msg
    
    
def listener(Output_Dir=OUTPUT_DIR, Binary=BINARY, Server_IP=SERVER_IP, Server_Port=SERVER_PORT):
    print("Listener started")
    try:
        cmd = [Binary, Server_IP, str(Server_Port), Output_Dir + "test.out"]
        result = subprocess.run(cmd, shell=False, capture_output=True, text=True)
        return result.stdout.strip()
    except Exception as e:
        print(f"Error occurred: {e}")
        return "Receive Error"

def record_results(output, filename="results.log", directory=OUTPUT_DIR):
    # Create directory if it doesn't exist
    Path(directory).mkdir(parents=True, exist_ok=True)
    
    with open(Path(directory) / filename, "a") as f:
        f.write(output + "\n")
        f.flush()
        os.fsync(f.fileno())
        
def cleanup_test_file(directory=OUTPUT_DIR):
    """Remove test.out file if it exists, following Unix philosophy of doing one thing well."""
    test_file = Path(directory) / "test.out"
    if test_file.exists():
        os.remove(test_file)

def cleanup_results_file(directory=OUTPUT_DIR):
    """Remove results.log file if it exists, following Unix philosophy of doing one thing well."""
    results_file = Path(directory) / "results.log"
    if results_file.exists():
        os.remove(results_file)

def setup_local_environment():
    """Setup the local directory structure and binaries."""
    # Create necessary directories
    bin_dir = current_dir / "bin"
    bin_dir.mkdir(parents=True, exist_ok=True)
    
    # Create results directory
    Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
    
    print(f"[SETUP] Created local directory structure:")
    print(f"[SETUP] - bin: {bin_dir}")
    print(f"[SETUP] - results: {OUTPUT_DIR}")
    
    # Check if server binary exists, if not try to find it in the project structure
    if not Path(BINARY).exists():
        # Try to find the server binary in the parent project structure
        project_root = current_dir.parent.parent
        source_binary = project_root / "foggytcp" / "bin" / "server"
        
        if source_binary.exists():
            import shutil
            shutil.copy2(source_binary, BINARY)
            print(f"[SETUP] Copied server binary from {source_binary}")
        else:
            print(f"[WARN] Server binary not found at {source_binary}")
            print(f"[WARN] You may need to build the project first or copy the binary manually to {BINARY}")
    else:
        print(f"[SETUP] Server binary found at {BINARY}")
    
    # Check if client binary exists for hash verification
    if not Path(CLIENT_BINARY).exists():
        # Try to find the client binary in the parent project structure
        project_root = current_dir.parent.parent
        source_client_binary = project_root / "foggytcp" / "bin" / "client"
        
        if source_client_binary.exists():
            import shutil
            shutil.copy2(source_client_binary, CLIENT_BINARY)
            print(f"[SETUP] Copied client binary from {source_client_binary}")
        else:
            print(f"[WARN] Client binary not found at {source_client_binary}")
            print(f"[WARN] Client binary hash verification will be skipped")
    else:
        print(f"[SETUP] Client binary found at {CLIENT_BINARY}")

def main():
    # Setup local environment first
    print(f"[SETUP] Setting up local environment...")
    setup_local_environment()
    
    # cleanup_results_file(OUTPUT_DIR)
    record_results(f"Binary Hash: {hash_the_bin()}")
    record_results(f"Client Binary Hash: {hash_the_bin(CLIENT_BINARY)}")
    index = 0
    while True:
        result = listener()
        print(f"Listener result: {result}")
        # Record the result with a timestamp and index
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
        record_results(f"[{timestamp}] [{index}] {result}")
        index += 1
        cleanup_test_file(OUTPUT_DIR)
        time.sleep(0.1)
        
if __name__ == "__main__":
    main()