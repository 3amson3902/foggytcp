#!/usr/bin/env python3
"""
FoggyTCP Performance Analysis Plotting Script
Generates academic-style plots for three test scenarios with theoretical vs experimental comparisons
"""

import matplotlib.pyplot as plt
import numpy as np
import matplotlib.patches as mpatches

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
colors = {
    'theoretical': '#1f77b4',  # Blue
    'experimental': '#d62728', # Red
    'grid': '#cccccc'
}

def extract_data_from_report():
    """Extract and organize data from the report with proper units"""
    
    # Test 1: Different File Sizes (Fixed: 10Mbps bandwidth, 10ms delay)
    # Units: File sizes in KB/MB, Times in ms
    test1_data = {
        'file_sizes': np.array([1, 5, 25, 100, 1024, 10240]),  # KB
        'file_labels': ['1KB', '5KB', '25KB', '100KB', '1MB', '10MB'],
        'theoretical': np.array([10.8, 14.0, 30.0, 90.0, 810, 8010]),  # ms
        'experimental': np.array([22, 24, 39, 105, 901, 9341])  # ms
    }
    
    # Test 2: Different Bandwidths (Fixed: 1MB file, 10ms delay)
    # Units: Bandwidth in Mbps, Times in ms
    test2_data = {
        'bandwidths': np.array([1, 5, 10, 20]),  # Mbps
        'theoretical': np.array([8394, 1679, 839, 420]),  # ms
        'experimental': np.array([6998, 1773, 901, 504])  # ms
    }
    
    # Test 3: Different Delays (Fixed: 1MB file, 10Mbps bandwidth)
    # Units: Delay in ms, Times in ms
    test3_data = {
        'delays': np.array([0, 5, 10, 20, 50, 100]),  # ms
        'theoretical': np.array([839, 844, 849, 859, 889, 939]),  # ms
        'experimental': np.array([889, 895, 900, 920, 1072, 1255])  # ms
    }
    
    return test1_data, test2_data, test3_data

def create_plots():
    """Create combined subplot figure with all three tests"""
    
    # Extract data
    test1, test2, test3 = extract_data_from_report()
    
    # Create figure with 2x2 subplot layout
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 10))
    fig.suptitle('FoggyTCP Performance Analysis: Theoretical vs Experimental Results', 
                 fontsize=14, fontweight='bold')
    
    # Test 1: File Size vs Transmission Time (Log scale for file sizes)
    ax1.loglog(test1['file_sizes'], test1['theoretical'], 'o-', 
               color=colors['theoretical'], label='Theoretical', markersize=6)
    ax1.loglog(test1['file_sizes'], test1['experimental'], 's-', 
               color=colors['experimental'], label='Experimental', markersize=6)
    
    ax1.set_xlabel('File Size (KB)')
    ax1.set_ylabel('Transmission Time (ms)')
    ax1.set_title('Test 1: File Size Impact\n(10 Mbps, 10ms delay)')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Custom x-axis labels for better readability
    ax1.set_xticks(test1['file_sizes'])
    ax1.set_xticklabels(test1['file_labels'])
    
    # Test 2: Bandwidth vs Transmission Time
    ax2.plot(test2['bandwidths'], test2['theoretical'], 'o-', 
             color=colors['theoretical'], label='Theoretical', markersize=6)
    ax2.plot(test2['bandwidths'], test2['experimental'], 's-', 
             color=colors['experimental'], label='Experimental', markersize=6)
    
    ax2.set_xlabel('Bandwidth (Mbps)')
    ax2.set_ylabel('Transmission Time (ms)')
    ax2.set_title('Test 2: Bandwidth Impact\n(1MB file, 10ms delay)')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    ax2.set_yscale('log')  # Log scale for better visualization of inverse relationship
    
    # Test 3: Delay vs Transmission Time
    ax3.plot(test3['delays'], test3['theoretical'], 'o-', 
             color=colors['theoretical'], label='Theoretical', markersize=6)
    ax3.plot(test3['delays'], test3['experimental'], 's-', 
             color=colors['experimental'], label='Experimental', markersize=6)
    
    ax3.set_xlabel('Propagation Delay (ms)')
    ax3.set_ylabel('Transmission Time (ms)')
    ax3.set_title('Test 3: Delay Impact\n(1MB file, 10 Mbps)')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # Test 4: Overhead Analysis (Experimental - Theoretical)
    overhead1 = test1['experimental'] - test1['theoretical']
    overhead2 = test2['experimental'] - test2['theoretical']
    overhead3 = test3['experimental'] - test3['theoretical']
    
    # Calculate relative overhead percentages
    rel_overhead1 = (overhead1 / test1['theoretical']) * 100
    rel_overhead2 = (overhead2 / test2['theoretical']) * 100
    rel_overhead3 = (overhead3 / test3['theoretical']) * 100
    
    # Plot relative overhead for each test
    x_pos = np.arange(len(test1['file_sizes']))
    width = 0.25
    
    ax4.bar(x_pos - width, rel_overhead1, width, label='File Size Test', alpha=0.8, color='#2ca02c')
    
    x_pos2 = np.arange(len(test2['bandwidths']))
    ax4_twin = ax4.twinx()
    ax4_twin.bar(x_pos2, rel_overhead2[:len(x_pos2)], width, label='Bandwidth Test', alpha=0.8, color='#ff7f0e')
    
    ax4.set_xlabel('Test Conditions')
    ax4.set_ylabel('TCP Overhead (%)', color='#2ca02c')
    ax4_twin.set_ylabel('TCP Overhead (%) - Bandwidth Test', color='#ff7f0e')
    ax4.set_title('TCP Protocol Overhead Analysis')
    
    # Combine legends
    lines1, labels1 = ax4.get_legend_handles_labels()
    lines2, labels2 = ax4_twin.get_legend_handles_labels()
    ax4.legend(lines1 + lines2, labels1 + labels2, loc='upper left')
    
    ax4.grid(True, alpha=0.3)
    ax4.set_xticks(range(max(len(test1['file_sizes']), len(test2['bandwidths']))))
    ax4.set_xticklabels([f'T{i+1}' for i in range(max(len(test1['file_sizes']), len(test2['bandwidths'])))])
    
    # Adjust layout to prevent overlap
    plt.tight_layout()
    
    return fig

def save_plots():
    """Generate and save the plots as PDF"""
    
    print("Generating FoggyTCP performance analysis plots...")
    
    # Create the plots
    fig = create_plots()
    
    # Save as PDF (best for LaTeX)
    output_file = 'foggytcp_performance_analysis.pdf'
    fig.savefig(output_file, format='pdf', dpi=300, bbox_inches='tight', 
                facecolor='white', edgecolor='none')
    
    print(f"✓ Plots saved as: {output_file}")
    
    # Also save as high-resolution PNG for presentations
    png_file = 'foggytcp_performance_analysis.png'
    fig.savefig(png_file, format='png', dpi=300, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    
    print(f"✓ High-res PNG saved as: {png_file}")
    
    # Display summary statistics
    test1, test2, test3 = extract_data_from_report()
    
    print("\n" + "="*60)
    print("PERFORMANCE ANALYSIS SUMMARY")
    print("="*60)
    
    # Calculate average overhead for each test
    avg_overhead1 = np.mean(test1['experimental'] - test1['theoretical'])
    avg_overhead2 = np.mean(test2['experimental'] - test2['theoretical'])
    avg_overhead3 = np.mean(test3['experimental'] - test3['theoretical'])
    
    print(f"Average TCP Overhead:")
    print(f"  File Size Test:  {avg_overhead1:.1f} ms")
    print(f"  Bandwidth Test:  {avg_overhead2:.1f} ms")
    print(f"  Delay Test:      {avg_overhead3:.1f} ms")
    
    # Calculate correlation coefficients
    corr1 = np.corrcoef(test1['theoretical'], test1['experimental'])[0,1]
    corr2 = np.corrcoef(test2['theoretical'], test2['experimental'])[0,1]
    corr3 = np.corrcoef(test3['theoretical'], test3['experimental'])[0,1]
    
    print(f"\nTheoretical vs Experimental Correlation:")
    print(f"  File Size Test:  {corr1:.3f}")
    print(f"  Bandwidth Test:  {corr2:.3f}")
    print(f"  Delay Test:      {corr3:.3f}")
    
    plt.show()

if __name__ == "__main__":
    save_plots()