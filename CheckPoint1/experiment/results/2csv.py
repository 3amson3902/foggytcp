#!/usr/bin/env python3
"""
Simple log to CSV converter following UNIX philosophy:
- Do one thing well: convert results.log to CSV
- Work as a filter: read from file, output to stdout
- Be composable: output can be piped to other tools
"""

import re
import sys
import csv
from datetime import datetime
from pathlib import Path

SOC_DIR = Path(__file__).parent
LOG_FILE = SOC_DIR / 'results.log'

def parse_log_line(line):
    """Parse a log line and extract timestamp, test_id, and transmission_time"""
    # Pattern: [YYYY-MM-DD HH:MM:SS] [test_id] Complete transmission in X ms
    pattern = r'\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\] \[(\d+)\] Complete transmission in (\d+) ms'
    match = re.match(pattern, line.strip())
    
    if match:
        timestamp = match.group(1)
        test_id = int(match.group(2))
        transmission_time = int(match.group(3))
        return timestamp, test_id, transmission_time
    return None

def convert_log_to_csv(input_file=LOG_FILE, output_file=SOC_DIR / 'results.csv'):
    """Convert log file to CSV format"""
    
    # Open output (stdout if no file specified)
    if output_file:
        output = open(output_file, 'w', newline='')
    else:
        output = sys.stdout
    
    try:
        csv_writer = csv.writer(output)
        
        # Write header
        csv_writer.writerow(['timestamp', 'test_id', 'transmission_time_ms'])
        
        # Process log file
        with open(input_file, 'r') as f:
            for line in f:
                result = parse_log_line(line)
                if result:
                    csv_writer.writerow(result)
    
    finally:
        if output_file:
            output.close()

if __name__ == '__main__':
    convert_log_to_csv()