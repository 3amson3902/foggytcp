import subprocess
import os
import time
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

BINARY = "./bin/server"  # Path to server binary on server VM
SERVER_IP = "10.0.1.1"
SERVER_PORT = 3120
OUTPUT_DIR = "./results/"

def listener(output_dir=OUTPUT_DIR, binary=BINARY, server_ip=SERVER_IP, server_port=SERVER_PORT):
    print("Listener started")
    try:
        cmd = [binary, server_ip, str(server_port), output_dir + "test.out"]
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

def main():
    cleanup_results_file(OUTPUT_DIR)
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