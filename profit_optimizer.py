import pandas as pd
import plotly.graph_objects as go
import numpy as np


def calculate_profit_scenarios(avg_demand, std_dev, holding_cost, stockout_cost, unit_cost, selling_price):
    """
    Simulates profit for a range of possible Order Quantities vs. Actual Demand scenarios.
    Returns a Heatmap figure.
    """

    # 1. Define Ranges
    # We test order sizes from 50% to 150% of average demand
    order_quantities = np.linspace(avg_demand * 0.5, avg_demand * 1.5, 50).astype(int)

    # We simulate actual demand occurring from -3 to +3 standard deviations
    possible_demands = np.linspace(max(0, avg_demand - 3 * std_dev), avg_demand + 3 * std_dev, 50).astype(int)

    z_matrix = []

    # 2. Run Grid Simulation
    for demand in possible_demands:
        row = []
        for order in order_quantities:
            # Units Sold = whatever is lower: what people want (demand) or what we have (order)
            units_sold = min(demand, order)

            # Unsold units (Overstock)
            unsold = max(0, order - demand)

            # Missed sales (Stockout)
            missed = max(0, demand - order)

            # --- THE PROFIT FORMULA ---
            revenue = units_sold * selling_price
            cost_of_goods = order * unit_cost
            holding_penalty = unsold * holding_cost
            stockout_penalty = missed * stockout_cost

            profit = revenue - cost_of_goods - holding_penalty - stockout_penalty
            row.append(profit)
        z_matrix.append(row)

    # 3. Build Heatmap
    fig = go.Figure(data=go.Heatmap(
        z=z_matrix,
        x=order_quantities,
        y=possible_demands,
        colorscale='RdBu',  # Red = Loss, Blue = Profit
        colorbar=dict(title='Net Profit ($)'),
        zmid=0  # Centers the colors so 0 profit is white
    ))

    fig.update_layout(
        title="💰 Profit Landscape (Order Qty vs. Actual Demand)",
        xaxis_title="If You Order (Units)",
        yaxis_title="And Actual Demand Is (Units)",
        height=500
    )

    return fig