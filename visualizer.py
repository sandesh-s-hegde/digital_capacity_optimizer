"""
visualizer.py
Generates supply chain performance charts for management reporting.
"""
import matplotlib.pyplot as plt
import pandas as pd


def plot_demand_curve(df: pd.DataFrame):
    """
    Saves a trendline chart of server demand over time.

    Args:
        df (pd.DataFrame): The usage data containing 'month' and 'demand' columns.
    """
    # Create the figure size (10 inches wide, 6 inches tall)
    plt.figure(figsize=(10, 6))

    # Plot the data: X-axis = Month, Y-axis = Demand
    plt.plot(df['month'], df['demand'], marker='o', linestyle='-', color='#0078D4', linewidth=2)

    # Styling (Microsoft Blue)
    plt.title('Azure Capacity Demand Trend (2025)', fontsize=14)
    plt.xlabel('Month', fontsize=12)
    plt.ylabel('Server Racks Needed', fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.7)

    # Save to disk instead of popping up a window (better for automation)
    output_file = 'demand_forecast.png'
    plt.savefig(output_file)
    print(f"📊 Chart successfully saved as '{output_file}'")

    # Clear memory
    plt.close()