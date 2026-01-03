"""
visualizer.py
Generates supply chain performance charts for management reporting.
"""
import matplotlib.pyplot as plt
import pandas as pd

def plot_scenario_comparison(df_baseline: pd.DataFrame, df_scenario: pd.DataFrame, scenario_name: str):
    """
    Saves a comparison chart of Baseline vs. Scenario Demand.
    """
    plt.figure(figsize=(10, 6))

    # Plot Baseline (Blue)
    plt.plot(df_baseline['month'], df_baseline['demand'],
             marker='o', linestyle='-', color='#0078D4', label='Baseline (Historical)')

    # Plot Scenario (Red Dashed)
    plt.plot(df_scenario['month'], df_scenario['demand'],
             marker='x', linestyle='--', color='#D13438', label=f'Scenario: {scenario_name}')

    plt.title(f'Capacity Planning: Baseline vs {scenario_name}', fontsize=14)
    plt.xlabel('Month', fontsize=12)
    plt.ylabel('Server Racks Needed', fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend()

    output_file = 'scenario_comparison.png'
    plt.savefig(output_file)
    print(f"📊 Comparison chart saved as '{output_file}'")
    plt.close()