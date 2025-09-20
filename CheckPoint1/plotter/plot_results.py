#!/usr/bin/env python3
"""
FoggyTCP Performance Analysis Plotting Script
Simple plotter following UNIX philosophy: do one thing and do it well
"""

import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
import json

# Configure matplotlib for academic/LaTeX output
# Do NOT edit this section
plt.rcParams.update({
    'font.family': 'serif',
    'font.serif': ['Times New Roman', 'DejaVu Serif'],
    'font.size': 10,
    'axes.labelsize': 11,
    'axes.titlesize': 12,
    'legend.fontsize': 9,
    'xtick.labelsize': 9,
    'ytick.labelsize': 9,
    'figure.titlesize': 14,
    'lines.linewidth': 2,
    'lines.markersize': 6,
    'grid.alpha': 0.3,
    'axes.grid': True,
    'grid.linestyle': '--'
})

# Academic color scheme
# Do NOT edit this section
colors = {
    'theoretical': '#1f77b4',  # Blue
    'experimental': '#d62728', # Red
    'grid': '#cccccc'
}

SOC_DIR = Path(__file__).parent

def process_theoretical_data(data, test_num):
    """Process theoretical data - return all theoretical values"""
    test = data['tests'][str(test_num)]
    theoretical = np.array(test['theoretical'])
    theoretical_params = np.array(test['theoretical_parameters'])
    
    # Return both theoretical values and their corresponding parameters
    return theoretical_params, theoretical

def process_experimental_data(data, test_num):
    """Process experimental data by averaging 5 runs per parameter - do one thing well"""
    test = data['tests'][str(test_num)]
    experimental = np.array(test['experimental'])
    num_params = len(test['parameters']['values'])
    runs_per_param = 5
    
    # Reshape and average: each parameter has 5 consecutive measurements
    reshaped = experimental[:num_params * runs_per_param].reshape(num_params, runs_per_param)
    averaged = np.mean(reshaped, axis=1)
    
    return averaged

def extract_test_parameters(data, test_num):
    """Extract parameters for a specific test - do one thing well"""
    test = data['tests'][str(test_num)]
    params = test['parameters']
    return {
        'values': params['values'],
        'labels': params.get('labels', [f"{v}{params['unit']}" for v in params['values']]),
        'unit': params['unit'],
        'name': params['name'],
        'description': params['description']
    }

def load_json_data(json_file_path):
    """Load JSON data from file - do one thing well"""
    try:
        with open(json_file_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: {json_file_path} not found")
        exit(1)

def create_single_plot(data, test_num=1):
    """Create one simple plot for specified test - do one thing well"""
    # Extract data using helper functions
    params = extract_test_parameters(data, test_num)
    experimental = process_experimental_data(data, test_num)
    theoretical_params, theoretical = process_theoretical_data(data, test_num)
    
    # Debug: Print data ranges
    print(f"Test {test_num} Data Summary:")
    print(f"Experimental params: {params['values']}")
    print(f"Experimental values: {experimental}")
    print(f"Theoretical params range: {theoretical_params[0]} to {theoretical_params[-1]} ({len(theoretical_params)} points)")
    print(f"Theoretical values range: {theoretical[0]} to {theoretical[-1]}")
    print()
    
    # Create figure
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Plot data - theoretical as continuous curve, experimental as points
    ax.loglog(theoretical_params, theoretical, '-', 
              color=colors['theoretical'], label='Theoretical', linewidth=2, alpha=0.8)
    ax.loglog(params['values'], experimental, 's', 
              color=colors['experimental'], label='Experimental', markersize=8, markerfacecolor='none', markeredgewidth=2)
    
    # Configure plot
    ax.set_xlabel(f"{params['name'].replace('_', ' ').title()} ({params['unit']})")
    ax.set_ylabel('Transmission Time (ms)')
    ax.set_title(f"FoggyTCP: {params['description']}")
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    return fig

def save_figure(fig, filename='foggytcp_plot.pdf'):
    """Save figure to file - do one thing well"""
    fig.savefig(filename, format='pdf', dpi=300, bbox_inches='tight', 
                facecolor='white', edgecolor='none')
    print(f"Plot saved as: {filename}")

def show_plot(fig):
    """Display plot - do one thing well"""
    plt.show()

def main(test_num=1):
    """Main execution - simple and linear"""
    # Load data
    json_file = SOC_DIR / 'index_based_results.json'
    data = load_json_data(json_file)
    
    # Create plot for specified test
    fig = create_single_plot(data, test_num)
    
    # Save and show
    save_figure(fig, f'foggytcp_test{test_num}_plot.pdf')
    show_plot(fig)

if __name__ == "__main__":
    # Default to test 1, but can be changed
    main(test_num=1)