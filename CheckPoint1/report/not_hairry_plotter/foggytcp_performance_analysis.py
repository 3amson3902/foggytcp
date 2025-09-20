#!/usr/bin/env python3
"""
FoggyTCP Performance Analysis - Academic Figure Generation
Generates a 2x2 subplot figure comparing theoretical vs experimental results.

This script plots each experimental run as an individual line to show
the variability and reproducibility of the experimental data.
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os

# Configure matplotlib for academic publication
plt.rcParams.update({
    'text.usetex': True,  # Enable LaTeX rendering for professional appearance
    'font.family': 'serif',
    'font.serif': ['Times', 'DejaVu Serif'],
    'font.size': 10,
    'axes.labelsize': 10,
    'axes.titlesize': 11,
    'legend.fontsize': 9,
    'xtick.labelsize': 9,
    'ytick.labelsize': 9,
    'figure.titlesize': 12
})


def plot_comparison(ax, x_data, y_theoretical, y_experimental_runs, 
                   x_label, y_label, title, x_scale='linear', y_scale='linear'):
    """
    Reusable helper function for plotting theoretical vs experimental comparisons.
    
    Parameters:
    -----------
    ax : matplotlib.axes.Axes
        The subplot axes to plot on
    x_data : array-like
        X-axis data points
    y_theoretical : array-like
        Theoretical y values
    y_experimental_runs : list of array-like
        List of experimental y values for each run
    x_label : str
        X-axis label (LaTeX formatted)
    y_label : str
        Y-axis label (LaTeX formatted)
    title : str
        Subplot title (LaTeX formatted)
    x_scale : str, optional
        X-axis scale ('linear' or 'log')
    y_scale : str, optional
        Y-axis scale ('linear' or 'log')
    """
    # Plot theoretical results
    ax.plot(x_data, y_theoretical, 'o-', color='blue', linewidth=2.0, 
            markersize=5, label='Theoretical', markerfacecolor='white', 
            markeredgecolor='blue', markeredgewidth=1.5, zorder=3)
    
    # Plot experimental results - each run as a separate line
    colors = ['red', 'darkred', 'crimson', 'indianred']  # Different shades for runs
    linestyles = ['-', '--', '-.', ':']
    markers = ['s', '^', 'v', 'D']
    
    for i, y_exp in enumerate(y_experimental_runs):
        color = colors[i % len(colors)]
        linestyle = linestyles[i % len(linestyles)]
        marker = markers[i % len(markers)]
        alpha = 0.7 if i > 0 else 1.0  # First run more prominent
        
        label = f'Experimental Run {i+1}' if len(y_experimental_runs) > 1 else 'Experimental'
        
        ax.plot(x_data, y_exp, marker=marker, linestyle=linestyle, 
                color=color, linewidth=1.5, markersize=4, 
                label=label, markerfacecolor='white', 
                markeredgecolor=color, markeredgewidth=1, 
                alpha=alpha, zorder=2)
    
    # Set axis scales
    ax.set_xscale(x_scale)
    ax.set_yscale(y_scale)
    
    # Set labels and title
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    ax.set_title(title)
    
    # Add legend
    ax.legend(loc='best', frameon=True, fancybox=False, shadow=False, fontsize=8)
    
    # Grid for better readability
    ax.grid(True, alpha=0.3, linestyle='-', linewidth=0.5, zorder=1)
    
    # Ensure tight axis limits
    ax.margins(0.05)

def load_data():
    """
    Load and process experimental and theoretical data from CSV files.
    
    Returns:
    --------
    dict: Dictionary containing processed data for all three tests
    """
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Load CSV files from the script directory
    test_params = pd.read_csv(os.path.join(script_dir, 'test_parameters.csv'))
    test_results = pd.read_csv(os.path.join(script_dir, 'test_results.csv'))
    theory_results = pd.read_csv(os.path.join(script_dir, 'theory_results.csv'))
    
    # Group experimental results by test_id to get all runs
    grouped_results = test_results.groupby('test_id')['transmission_time_ms'].apply(list).reset_index()
    grouped_results.columns = ['test_id', 'transmission_times']
    
    # Merge with test parameters
    merged_data = pd.merge(test_params, grouped_results, on='test_id')
    
    # Parse file sizes to numeric values in KB
    def parse_file_size(size_str):
        if 'KB' in size_str:
            return float(size_str.replace('KB', ''))
        elif 'MB' in size_str:
            return float(size_str.replace('MB', '')) * 1024
        return float(size_str)
    
    # Parse bandwidth to numeric values in Mbps
    def parse_bandwidth(bw_str):
        return float(bw_str.replace('Mbps', ''))
    
    # Parse delay to numeric values in ms
    def parse_delay(delay_str):
        return float(delay_str.replace('ms', ''))
    
    merged_data['file_size_kb'] = merged_data['file_size'].apply(parse_file_size)
    merged_data['bandwidth_mbps'] = merged_data['bandwidth'].apply(parse_bandwidth)
    merged_data['delay_ms'] = merged_data['delay'].apply(parse_delay)
    
    # Extract data for each test
    test1_data = merged_data[merged_data['test_name'].str.contains('TEST 1')].copy()
    test2_data = merged_data[merged_data['test_name'].str.contains('TEST 2')].copy()
    test3_data = merged_data[merged_data['test_name'].str.contains('TEST 3')].copy()
    
    # Sort data
    test1_data = test1_data.sort_values('file_size_kb')
    test2_data = test2_data.sort_values('bandwidth_mbps')
    test3_data = test3_data.sort_values('delay_ms')
    
    # Get theoretical data
    theory_test1 = theory_results[theory_results['Test_Type'] == 'Test_1_FileSize'].copy()
    theory_test2 = theory_results[theory_results['Test_Type'] == 'Test_2_Bandwidth'].copy()
    theory_test3 = theory_results[theory_results['Test_Type'] == 'Test_3_PropagationDelay'].copy()
    
    # Extract theoretical values for specific test points
    def get_theory_value(theory_df, param_values):
        result = []
        for val in param_values:
            closest_match = theory_df[theory_df['Parameter_Value'].round(3) == round(val, 3)]
            if not closest_match.empty:
                result.append(closest_match['Time_ms'].iloc[0])
            else:
                # Find closest value
                closest_idx = (theory_df['Parameter_Value'] - val).abs().idxmin()
                result.append(theory_df.loc[closest_idx, 'Time_ms'])
        return np.array(result)
    
    # Get theoretical values for each test
    test1_theory = get_theory_value(theory_test1, test1_data['file_size_kb'].values)
    test2_theory = get_theory_value(theory_test2, test2_data['bandwidth_mbps'].values)
    test3_theory = get_theory_value(theory_test3, test3_data['delay_ms'].values)
    
    # Organize experimental runs for each test
    def organize_experimental_runs(test_data):
        """Organize experimental data into separate runs."""
        if len(test_data) == 0:
            return []
        
        # Get the number of runs (assuming all test points have same number of runs)
        num_runs = len(test_data.iloc[0]['transmission_times'])
        runs = []
        
        for run_idx in range(num_runs):
            run_data = []
            for _, row in test_data.iterrows():
                if run_idx < len(row['transmission_times']):
                    run_data.append(row['transmission_times'][run_idx])
                else:
                    run_data.append(np.nan)  # Handle missing data
            runs.append(np.array(run_data))
        
        return runs
    
    test1_exp_runs = organize_experimental_runs(test1_data)
    test2_exp_runs = organize_experimental_runs(test2_data)
    test3_exp_runs = organize_experimental_runs(test3_data)
    
    return {
        'test1': {
            'x': test1_data['file_size_kb'].values,
            'experimental_runs': test1_exp_runs,
            'theoretical': test1_theory,
            'x_label': r'File Size (KB)',
            'y_label': r'Transmission Time (ms)',
            'title': r'Test 1: File Size Impact (10 Mbps, 10 ms delay)',
            'x_scale': 'log',
            'y_scale': 'log'
        },
        'test2': {
            'x': test2_data['bandwidth_mbps'].values,
            'experimental_runs': test2_exp_runs,
            'theoretical': test2_theory,
            'x_label': r'Bandwidth (Mbps)',
            'y_label': r'Transmission Time (ms)',
            'title': r'Test 2: Bandwidth Impact (1 MB file, 10 ms delay)',
            'x_scale': 'linear',
            'y_scale': 'log'
        },
        'test3': {
            'x': test3_data['delay_ms'].values,
            'experimental_runs': test3_exp_runs,
            'theoretical': test3_theory,
            'x_label': r'Propagation Delay (ms)',
            'y_label': r'Transmission Time (ms)',
            'title': r'Test 3: Delay Impact (1 MB file, 10 Mbps)',
            'x_scale': 'linear',
            'y_scale': 'linear'
        }
    }

def generate_performance_figure():
    """
    Generate the complete FoggyTCP performance analysis figure.
    """
    # Load data from CSV files
    data = load_data()
    
    # Create figure and subplots
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(10, 8))
    
    # Test 1: File Size Impact
    plot_comparison(ax1, 
                   data['test1']['x'], 
                   data['test1']['theoretical'], 
                   data['test1']['experimental_runs'],
                   data['test1']['x_label'], 
                   data['test1']['y_label'],
                   data['test1']['title'],
                   x_scale=data['test1']['x_scale'], 
                   y_scale=data['test1']['y_scale'])
    
    # Test 2: Bandwidth Impact
    plot_comparison(ax2, 
                   data['test2']['x'], 
                   data['test2']['theoretical'], 
                   data['test2']['experimental_runs'],
                   data['test2']['x_label'], 
                   data['test2']['y_label'],
                   data['test2']['title'],
                   x_scale=data['test2']['x_scale'], 
                   y_scale=data['test2']['y_scale'])
    
    # Test 3: Delay Impact
    plot_comparison(ax3, 
                   data['test3']['x'], 
                   data['test3']['theoretical'], 
                   data['test3']['experimental_runs'],
                   data['test3']['x_label'], 
                   data['test3']['y_label'],
                   data['test3']['title'],
                   x_scale=data['test3']['x_scale'], 
                   y_scale=data['test3']['y_scale'])
    
    # Remove the bottom-right subplot (leave empty)
    ax4.axis('off')
    
    # Add figure-wide title
    fig.suptitle(r'FoggyTCP Performance Analysis: Theoretical vs Experimental Results',
                fontsize=12, y=0.95)
    
    # Adjust layout to accommodate suptitle
    plt.tight_layout(rect=(0, 0, 1, 0.92))
    
    return fig

def main():
    """
    Main function to generate and display/save the figure.
    """
    try:
        print("Loading data and generating performance analysis figure...")
        
        # Get the directory where this script is located
        script_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Generate the figure
        fig = generate_performance_figure()
        
        # Save the figure in high quality to the script directory
        pdf_path = os.path.join(script_dir, 'foggytcp_performance_analysis.pdf')
        png_path = os.path.join(script_dir, 'foggytcp_performance_analysis.png')
        
        fig.savefig(pdf_path, dpi=300, bbox_inches='tight',
                    facecolor='white', edgecolor='none')
        fig.savefig(png_path, dpi=300, bbox_inches='tight',
                    facecolor='white', edgecolor='none')
        
        print("Figure generated successfully!")
        print(f"Saved as: {pdf_path}")
        print(f"          {png_path}")
        print("Each experimental run is plotted as an individual line to show data variability.")
        
        # Display the figure
        plt.show()
        
    except FileNotFoundError as e:
        print(f"Error: CSV file not found - {e}")
        print("Please ensure test_parameters.csv, test_results.csv, and theory_results.csv are in the script directory.")
    except ImportError as e:
        if "usetex" in str(e) or "latex" in str(e).lower():
            print("LaTeX not available. Disabling LaTeX rendering and retrying...")
            plt.rcParams['text.usetex'] = False
            main()  # Retry without LaTeX
        else:
            print(f"Import error: {e}")
    except Exception as e:
        print(f"Error generating figure: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()