import numpy as np
import os
from pathlib import Path
"""
# In this checkpoint, we hypothesize that transmission time via a point to point 
# network is modeled by the following equation:

This script is used to calculate theoretical transmission times data points
Time = \frac{File Size}{Bandwidth} + 2 \times Propagation Delay
"""

OUTPUT_DIR = Path(__file__).parent / "results"

def cleanup_test_file(directory=OUTPUT_DIR):
    """Remove results.log file if it exists, following Unix philosophy of doing one thing well."""
    results_file = Path(directory) / "results.log"
    if results_file.exists():
        os.remove(results_file)

def theoretical_time(file_size, bandwidth, propagation_delay):
    return (file_size / bandwidth) + (2 * propagation_delay)

def record_results(output, filename="results.log", directory=OUTPUT_DIR):
    # Create directory if it doesn't exist
    Path(directory).mkdir(parents=True, exist_ok=True)
    
    with open(Path(directory) / filename, "a") as f:
        f.write(output + "\n")
        f.flush()
        os.fsync(f.fileno())

def generate_data_file_size(
    bandwidth = 10 * 1024 * 1024 / 8,  # Defualt: 10 Mbps in bytes per second
    propagation_delay = 0.01,  # 10 ms in seconds
    total_num_files = 10240,
    size_increment = 1024 * 1,
    min_file_size = 1024
):
    file_sizes = np.zeros(total_num_files)
    
    for i in range(total_num_files):
        file_sizes[i] = min_file_size + size_increment * i
        
    for y in file_sizes:
        time = theoretical_time(y, bandwidth, propagation_delay) * 1000
        record_results(f"[Test 1] {y / 1024} KB; {time:.4f} ms")
        
def generate_data_bandwidth(
    file_size = 1024 * 1024,  # Fixed: 1 MB file size
    propagation_delay = 0.01,  # Fixed: 10 ms in seconds
    total_num_tests = 20,
    bandwidth_increment = 1024 * 1024 / 8,  # 1 Mbps increment in bytes per second
    min_bandwidth = 1024 * 1024 / 8  # 1 Mbps in bytes per second
):
    bandwidths = np.zeros(total_num_tests)
    
    for i in range(total_num_tests):
        bandwidths[i] = min_bandwidth + bandwidth_increment * i
        
    for bandwidth in bandwidths:
        time = theoretical_time(file_size, bandwidth, propagation_delay) * 1000
        record_results(f"[Test 2] {bandwidth * 8 / (1024 * 1024):.1f} Mbps; {time:.4f} ms")
        
def generate_data_propagation_delay(
    file_size = 1024 * 1024,  # Fixed: 1 MB file size
    bandwidth = 10 * 1024 * 1024 / 8,  # Fixed: 10 Mbps in bytes per second
    total_num_tests = 100,
    delay_increment = 0.001,  # 1 ms increment in seconds
    min_delay = 0.001  # 1 ms in seconds
):
    delays = np.zeros(total_num_tests)
            
    for i in range(total_num_tests):
        delays[i] = min_delay + delay_increment * i
                
    for delay in delays:
        time = theoretical_time(file_size, bandwidth, delay) * 1000
        record_results(f"[Test 3] {delay * 1000:.1f} ms delay; {time:.4f} ms")



if __name__ == "__main__":
    cleanup_test_file()
    generate_data_file_size()
    generate_data_bandwidth()
    generate_data_propagation_delay()
    
    
