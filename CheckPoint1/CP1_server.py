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

Binary = "./bin/server"  # Path to server binary on server VM
Server_IP = "10.0.1.1"
Server_Port = 3120
Output_Dir = "./results/"
CLIENT_BINARY = "./bin/client"  # Path to client binary on client VM

def hash_the_bin(binary_path=Binary):
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
    
    
def listener(Output_Dir=Output_Dir, Binary=Binary, Server_IP=Server_IP, Server_Port=Server_Port):
    print("Listener started")
    try:
        cmd = [Binary, Server_IP, str(Server_Port), Output_Dir + "test.out"]
        result = subprocess.run(cmd, shell=False, capture_output=True, text=True)
        return result.stdout.strip()
    except Exception as e:
        print(f"Error occurred: {e}")
        return "Receive Error"

def record_results(output, filename="results.log", directory=Output_Dir):
    # Create directory if it doesn't exist
    Path(directory).mkdir(parents=True, exist_ok=True)
    
    with open(Path(directory) / filename, "a") as f:
        f.write(output + "\n")
        f.flush()
        os.fsync(f.fileno())
        
def cleanup_test_file(directory=Output_Dir):
    """Remove test.out file if it exists, following Unix philosophy of doing one thing well."""
    test_file = Path(directory) / "test.out"
    if test_file.exists():
        os.remove(test_file)

def cleanup_results_file(directory=Output_Dir):
    """Remove results.log file if it exists, following Unix philosophy of doing one thing well."""
    results_file = Path(directory) / "results.log"
    if results_file.exists():
        os.remove(results_file)

def main():
    cleanup_results_file(Output_Dir)
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
        cleanup_test_file(Output_Dir)
        time.sleep(0.1)
        
if __name__ == "__main__":
    main()