#!/usr/bin/env python3
"""
Data Parser for FoggyTCP Performance Analysis
Converts .log output files to machine readable .json format for plotting

This script parses experimental and theoretical log files and extracts
transmission time data for different test scenarios:
- Test 1: Different file sizes (1KB, 5KB, 25KB, 100KB, 1MB, 10MB)
- Test 2: Different bandwidths (1, 5, 10, 20 Mbps)
- Test 3: Different delays (0, 5, 10, 20, 50, 100 ms)
"""

import json
import re
import os
from typing import Dict, List, Tuple, Optional
import argparse


class LogParser:
    """Parser for FoggyTCP log files"""
    
    def __init__(self):
        # Expected file sizes for Test 1 (in KB)
        self.file_sizes = [1, 5, 25, 100, 1024, 10240]  # 1KB to 10MB
        self.file_labels = ['1KB', '5KB', '25KB', '100KB', '1MB', '10MB']
        
        # Expected bandwidths for Test 2 (in Mbps)
        self.bandwidths = [1, 5, 10, 20]
        
        # Expected delays for Test 3 (in ms)
        self.delays = [0, 5, 10, 20, 50, 100]
        
    def parse_experimental_log(self, log_file: str) -> Dict[int, List[float]]:
        """
        Parse experimental log file and extract transmission times organized by test
        
        Expected format:
        [timestamp] [test_id] Complete transmission in XX ms
        Done: Transmitted "./results/test.out"
        
        Test boundaries based on index:
        - Index 0-5: Test 1 (File sizes)
        - Index 6-9: Test 2 (Bandwidths) 
        - Index 10-15: Test 3 (Delays)
        
        Args:
            log_file: Path to the experimental log file
            
        Returns:
            Dictionary with test numbers as keys and transmission times as values
        """
        test_data = {1: [], 2: [], 3: []}
        
        try:
            with open(log_file, 'r') as f:
                content = f.read()
                
            # Regex pattern to match transmission time lines with test index
            pattern = r'\[(\d+)\] Complete transmission in (\d+) ms'
            matches = re.findall(pattern, content)
            
            # Organize by test based on index ranges
            for index_str, time_str in matches:
                index = int(index_str)
                time = float(time_str)
                
                # Determine which test based on index
                if 0 <= index <= 5:
                    test_data[1].append(time)
                elif 6 <= index <= 9:
                    test_data[2].append(time)
                elif 10 <= index <= 15:
                    test_data[3].append(time)
                else:
                    print(f"Warning: Unknown test index {index} in {log_file}")
            
        except FileNotFoundError:
            print(f"Warning: File {log_file} not found")
        except Exception as e:
            print(f"Error parsing {log_file}: {e}")
            
        return test_data
    
    def parse_theoretical_log(self, log_file: str) -> Dict[str, List[Tuple[float, float]]]:
        """
        Parse theoretical log file and extract data points
        
        Expected formats:
        [Test 1] Y.Y KB; Z.Z ms
        [Test 2] Y.Y Mbps; Z.Z ms  
        [Test 3] Y.Y ms; Z.Z ms
        
        Args:
            log_file: Path to the theoretical log file
            
        Returns:
            Dictionary with test numbers as keys and (parameter, time) tuples as values
        """
        theoretical_data = {}
        
        try:
            with open(log_file, 'r') as f:
                lines = f.readlines()
                
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                    
                # Parse different formats for each test
                # Test 1: [Test 1] Y.Y KB; Z.Z ms
                pattern1 = r'\[Test (1)\] ([\d.]+) KB; ([\d.]+) ms'
                # Test 2: [Test 2] Y.Y Mbps; Z.Z ms
                pattern2 = r'\[Test (2)\] ([\d.]+) Mbps; ([\d.]+) ms'
                # Test 3: [Test 3] Y.Y ms delay; Z.Z ms
                pattern3 = r'\[Test (3)\] ([\d.]+) ms delay; ([\d.]+) ms'
                
                for pattern in [pattern1, pattern2, pattern3]:
                    match = re.match(pattern, line)
                    if match:
                        test_num = int(match.group(1))
                        param_value = float(match.group(2))
                        time_ms = float(match.group(3))
                        
                        if test_num not in theoretical_data:
                            theoretical_data[test_num] = []
                        
                        theoretical_data[test_num].append((param_value, time_ms))
                        break
                    
        except FileNotFoundError:
            print(f"Warning: File {log_file} not found")
        except Exception as e:
            print(f"Error parsing {log_file}: {e}")
            
        return theoretical_data
    
    def organize_test_data(self, experimental_data: Dict[int, List[float]], 
                          theoretical_data: Dict[str, List[Tuple[float, float]]],
                          test_type: int) -> Dict:
        """
        Organize parsed data into structured format for specific test type
        
        Args:
            experimental_data: Dictionary with test numbers as keys and transmission times as values
            theoretical_data: Dictionary of theoretical data points
            test_type: Test number (1, 2, or 3)
            
        Returns:
            Structured data dictionary for the test
        """
        experimental_times = experimental_data.get(test_type, [])
        
        result = {
            'test_type': test_type,
            'experimental': experimental_times,
            'theoretical': [],
            'theoretical_parameters': []
        }
        
        # Extract theoretical times and parameters for this test
        if test_type in theoretical_data:
            theoretical_points = theoretical_data[test_type]
            result['theoretical'] = [point[1] for point in theoretical_points]  # Extract time values
            result['theoretical_parameters'] = [point[0] for point in theoretical_points]  # Extract parameter values
            
            # Add parameter information based on test type
            if test_type == 1:
                result['parameters'] = {
                    'name': 'file_sizes',
                    'values': self.file_sizes,
                    'labels': self.file_labels,
                    'unit': 'KB',
                    'description': 'File sizes tested',
                    'expected_indices': '0-5'
                }
            elif test_type == 2:
                result['parameters'] = {
                    'name': 'bandwidths',
                    'values': self.bandwidths,
                    'unit': 'Mbps',
                    'description': 'Bandwidth settings tested',
                    'expected_indices': '6-9'
                }
            elif test_type == 3:
                result['parameters'] = {
                    'name': 'delays',
                    'values': self.delays,
                    'unit': 'ms',
                    'description': 'Network delay settings tested',
                    'expected_indices': '10-15'
                }
        
        return result
    
    def parse_all_results(self, results_dir: str = ".") -> Dict:
        """
        Parse all log files in the results directory
        
        Args:
            results_dir: Directory containing the log files
            
        Returns:
            Complete parsed data structure
        """
        parsed_data = {
            'metadata': {
                'description': 'FoggyTCP Performance Analysis Data',
                'test_index_mapping': {
                    '0-5': 'Test 1: File Size Impact (10 Mbps, 10ms delay)',
                    '6-9': 'Test 2: Bandwidth Impact (1MB file, 10ms delay)',
                    '10-15': 'Test 3: Delay Impact (1MB file, 10 Mbps)'
                },
                'tests': {
                    1: 'File Size Impact (10 Mbps, 10ms delay)',
                    2: 'Bandwidth Impact (1MB file, 10ms delay)', 
                    3: 'Delay Impact (1MB file, 10 Mbps)'
                }
            },
            'tests': {}
        }
        
        # Parse theoretical data
        theoretical_file = os.path.join(results_dir, 'theory', 'theo_results.log')
        theoretical_data = self.parse_theoretical_log(theoretical_file)
        
        # Parse experimental data files
        experiment_dir = os.path.join(results_dir, 'experiment')
        experimental_files = [
            'test_results.log',
            'results2.log',
            'results3.log', 
            'results4.log',
            'results5.log'
        ]
        
        # Aggregate all experimental data by test
        all_experimental_data = {1: [], 2: [], 3: []}
        
        for filename in experimental_files:
            exp_file = os.path.join(experiment_dir, filename)
            if os.path.exists(exp_file):
                file_exp_data = self.parse_experimental_log(exp_file)
                
                # Merge data from this file into aggregated data
                for test_num in [1, 2, 3]:
                    all_experimental_data[test_num].extend(file_exp_data.get(test_num, []))
        
        # Create organized data for each test
        for test_type in [1, 2, 3]:
            parsed_data['tests'][test_type] = self.organize_test_data(
                all_experimental_data, theoretical_data, test_type
            )
        
        return parsed_data
    
    def save_json(self, data: Dict, output_file: str):
        """Save parsed data to JSON file"""
        try:
            with open(output_file, 'w') as f:
                json.dump(data, f, indent=2)
            print(f"Successfully saved parsed data to {output_file}")
        except Exception as e:
            print(f"Error saving to {output_file}: {e}")
    
    def print_summary(self, data: Dict):
        """Print a summary of parsed data"""
        print("\n=== FoggyTCP Data Parser Summary ===")
        print(f"Description: {data['metadata']['description']}")
        print(f"Tests found: {len(data['tests'])}")
        
        # Show test index mapping
        if 'test_index_mapping' in data['metadata']:
            print("\nTest Index Mapping:")
            for indices, description in data['metadata']['test_index_mapping'].items():
                print(f"  Indices {indices}: {description}")
        
        for test_num, test_data in data['tests'].items():
            test_desc = data['metadata']['tests'].get(test_num, f"Test {test_num}")
            print(f"\nTest {test_num}: {test_desc}")
            print(f"  Experimental data points: {len(test_data.get('experimental', []))}")
            print(f"  Theoretical data points: {len(test_data.get('theoretical', []))}")
            
            if 'parameters' in test_data:
                params = test_data['parameters']
                print(f"  Parameter: {params['name']} ({params['unit']})")
                if 'expected_indices' in params:
                    print(f"  Expected indices: {params['expected_indices']}")
                if 'values' in params:
                    print(f"  Parameter values: {params['values']}")
                    
            # Show sample experimental data if available
            exp_data = test_data.get('experimental', [])
            if exp_data:
                print(f"  Sample experimental times: {exp_data[:6] if len(exp_data) > 6 else exp_data}")

    def get_test_subset(self, data: Dict, test_number: int, param_values: List[float]) -> Dict:
        """
        Extract a subset of data for specific parameter values
        
        Args:
            data: Full parsed data
            test_number: Test number (1, 2, or 3)
            param_values: List of parameter values to extract data for
            
        Returns:
            Subset of data for the specified parameters
        """
        if test_number not in data['tests']:
            return {}
            
        test_data = data['tests'][test_number]
        theoretical_params = test_data.get('theoretical_parameters', [])
        theoretical_times = test_data.get('theoretical', [])
        
        # Find indices of matching parameter values
        subset_theoretical = []
        subset_params = []
        
        for param_val in param_values:
            # Find closest match in theoretical parameters
            if theoretical_params:
                closest_idx = min(range(len(theoretical_params)), 
                                key=lambda i: abs(theoretical_params[i] - param_val))
                if abs(theoretical_params[closest_idx] - param_val) < 0.01:  # Tolerance
                    subset_theoretical.append(theoretical_times[closest_idx])
                    subset_params.append(theoretical_params[closest_idx])
        
        return {
            'test_type': test_number,
            'experimental': test_data.get('experimental', [])[:len(param_values)],
            'theoretical': subset_theoretical,
            'theoretical_parameters': subset_params,
            'parameters': test_data.get('parameters', {})
        }

    def export_csv(self, data: Dict, output_dir: str = '.'):
        """Export parsed data to CSV files for each test"""
        import csv
        
        for test_num, test_data in data['tests'].items():
            csv_file = os.path.join(output_dir, f'test_{test_num}_data.csv')
            
            try:
                with open(csv_file, 'w', newline='') as f:
                    writer = csv.writer(f)
                    
                    # Write header
                    params = test_data.get('parameters', {})
                    param_name = params.get('name', 'parameter')
                    writer.writerow([param_name, 'theoretical_time_ms', 'experimental_time_ms'])
                    
                    # Write data
                    theoretical = test_data.get('theoretical', [])
                    theoretical_params = test_data.get('theoretical_parameters', [])
                    experimental = test_data.get('experimental', [])
                    
                    # For theoretical data
                    for i, (param, time) in enumerate(zip(theoretical_params, theoretical)):
                        exp_time = experimental[i] if i < len(experimental) else ''
                        writer.writerow([param, time, exp_time])
                        
                print(f"Exported CSV: {csv_file}")
                
            except Exception as e:
                print(f"Error exporting CSV for test {test_num}: {e}")


def main():
    """Main function to run the parser"""
    parser = argparse.ArgumentParser(description='Parse FoggyTCP log files to JSON')
    parser.add_argument('--input-dir', '-i', default='.',
                        help='Input directory containing log files (default: current directory)')
    parser.add_argument('--output', '-o', default='parsed_results.json',
                        help='Output JSON file (default: parsed_results.json)')
    parser.add_argument('--summary', '-s', action='store_true',
                        help='Print summary of parsed data')
    
    args = parser.parse_args()
    
    # Initialize parser
    log_parser = LogParser()
    
    # Parse all results
    print(f"Parsing log files from: {args.input_dir}")
    parsed_data = log_parser.parse_all_results(args.input_dir)
    
    # Save to JSON
    log_parser.save_json(parsed_data, args.output)
    
    # Print summary if requested
    if args.summary:
        log_parser.print_summary(parsed_data)


if __name__ == "__main__":
    main()
