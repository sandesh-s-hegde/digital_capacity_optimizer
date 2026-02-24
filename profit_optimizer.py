import scipy.stats as stats
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px


def calculate_profit_scenarios(avg_demand: float, std_dev: float, holding_cost: float,
                               stockout_cost: float, unit_cost: float, selling_price: float):
    """
    Generates the Profit Heatmap using ultra-fast NumPy vectorization (meshgrid).
    """
    margin = selling_price - unit_cost

    # 1. Define Arrays (Vectorized)
    service_levels = np.linspace(0.50, 0.99, 20)
    lead_time_vars = np.linspace(0.0, 2.0, 20)

    z_scores = stats.norm.ppf(service_levels)

    # 2. Create 2D Grids for Matrix Math
    Z_grid, LT_grid = np.meshgrid(z_scores, lead_time_vars)

    # 3. Vectorized Financial Math (No 'for' loops)
    # RSS Safety Stock Formula: SS = Z * sqrt((1 * var_D) + (D^2 * var_LT))
    SS_grid = Z_grid * np.sqrt((1 * std_dev ** 2) + (avg_demand ** 2 * LT_grid ** 2))
    HC_grid = SS_grid * holding_cost

    # Standard Normal Loss Function: L(z) = pdf(z) - z * (1 - cdf(z))
    loss_grid = stats.norm.pdf(Z_grid) - Z_grid * (1 - stats.norm.cdf(Z_grid))
    ES_grid = std_dev * loss_grid  # Expected Shortage

    # Costs
    penalty_grid = ES_grid * (stockout_cost + margin)  # Penalty + Opportunity Cost
    gross_profit = avg_demand * margin

    # Net Profit Matrix
    profit_matrix = gross_profit - (HC_grid + penalty_grid)

    # 4. Build Visualization
    fig = go.Figure(data=go.Heatmap(
        z=profit_matrix,
        x=[f"{sl:.0%}" for sl in service_levels],
        y=[f"{lt:.1f}" for lt in lead_time_vars],
        colorscale='Viridis',
        hoverongaps=False,
        hovertemplate="Service Level: %{x}<br>Volatility: %{y}<br>Profit: $%{z:,.0f}<extra></extra>"
    ))

    fig.update_layout(
        title="Net Profit Landscape ($)",
        xaxis_title="Target Service Level (%)",
        yaxis_title=r"Supply Chain Volatility (\sigma_{LT})",
        height=400,
        margin={"r": 0, "t": 40, "l": 0, "b": 0}
    )

    return fig


def plot_cost_tradeoff(avg_demand: float, std_dev: float, holding_cost: float,
                       stockout_cost: float, unit_cost: float, selling_price: float):
    """
    Visualizes the Convexity of Supply Chain Costs.
    Vectorized for high-resolution plotting (100 data points).
    """
    margin = selling_price - unit_cost

    # 1. High-Resolution Arrays (100 points for a smooth curve)
    service_levels = np.linspace(0.50, 0.99, 100)
    z_scores = stats.norm.ppf(service_levels)

    # 2. Vectorized Math Operations
    safety_stock = z_scores * std_dev
    holding_costs = safety_stock * holding_cost

    loss_func = stats.norm.pdf(z_scores) - z_scores * (1 - stats.norm.cdf(z_scores))
    expected_shortage = std_dev * loss_func
    stockout_costs = expected_shortage * (stockout_cost + margin)

    total_costs = holding_costs + stockout_costs

    # 3. Find Optimal Point mathematically
    min_idx = np.argmin(total_costs)
    min_cost = total_costs[min_idx]
    optimal_sla = service_levels[min_idx]

    # 4. Build the Chart
    fig = go.Figure()

    # Trace 1: Holding Cost
    fig.add_trace(go.Scatter(x=service_levels, y=holding_costs, mode='lines',
                             name='Holding Cost', line=dict(color='red', dash='dot')))

    # Trace 2: Stockout Cost
    fig.add_trace(go.Scatter(x=service_levels, y=stockout_costs, mode='lines',
                             name='Stockout Cost', line=dict(color='orange', dash='dot')))

    # Trace 3: Total Cost
    fig.add_trace(go.Scatter(x=service_levels, y=total_costs, mode='lines',
                             name='Total Cost Impact', line=dict(color='green', width=4)))

    # Highlight Optimal Point
    fig.add_trace(go.Scatter(x=[optimal_sla], y=[min_cost], mode='markers',
                             name='Optimal Point', marker=dict(color='black', size=12, symbol='star')))

    fig.update_layout(
        title=f"The Optimization Curve (Optimal SLA: {optimal_sla:.1%})",
        xaxis_title="Target Service Level",
        yaxis_title="Financial Impact ($)",
        xaxis=dict(tickformat=".0%"),
        height=400,
        hovermode="x unified",
        margin={"r": 0, "t": 40, "l": 0, "b": 0}
    )

    return fig
