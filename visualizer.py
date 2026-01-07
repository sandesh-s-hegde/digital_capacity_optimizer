"""
visualizer.py
Generates supply chain performance charts for management reporting.
Updated for Streamlit Web Rendering.
"""
import matplotlib.pyplot as plt
import pandas as pd

def plot_scenario_comparison(df_baseline: pd.DataFrame, df_scenario: pd.DataFrame, scenario_name: str):
    """
    Saves a comparison chart of Baseline vs. Scenario Demand.
    (Kept as-is for backward compatibility with main.py)
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

def plot_forecast(df_history: pd.DataFrame, forecast_values: pd.Series):
    """
    Plots historical data vs. predicted future demand.
    RETURNS the figure object for Streamlit rendering.
    """
    # CHANGE 1: Create figure and axes explicitly using subplots
    fig, ax = plt.subplots(figsize=(12, 6))

    # 1. Plot History (Solid Blue Line)
    # CHANGE 2: Use 'ax.plot' instead of 'plt.plot'
    ax.plot(df_history.index, df_history['demand'],
             marker='o', linestyle='-', color='#0078D4', label='Historical Data')

    # 2. Plot Forecast (Dashed Green Line)
    last_index = df_history.index[-1]
    future_indices = range(last_index + 1, last_index + 1 + len(forecast_values))

    ax.plot(future_indices, forecast_values,
             marker='x', linestyle='--', color='#107C10', label='Forecast (AI Prediction)')

    # CHANGE 3: Use 'ax.set_title' instead of 'plt.title'
    ax.set_title('Demand Forecast: Next Quarter Prediction', fontsize=14)
    ax.set_xlabel('Time Period (Month Index)', fontsize=12)
    ax.set_ylabel('Demand', fontsize=12)
    ax.grid(True, linestyle=':', alpha=0.6)
    ax.legend()

    # CHANGE 4: Return 'fig' instead of saving/closing
    return fig