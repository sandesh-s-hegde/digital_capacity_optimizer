import plotly.graph_objects as go
import numpy as np
import pandas as pd
import scipy.stats as stats


def calculate_profit_scenarios(avg_demand, std_dev, holding_cost, stockout_cost, unit_cost, selling_price):
    """
    Generates the Profit Heatmap (Existing Logic).
    """
    # Define ranges
    service_levels = np.linspace(0.50, 0.99, 20)
    lead_time_vars = np.linspace(0.0, 2.0, 20)

    z_scores = stats.norm.ppf(service_levels)

    profit_matrix = []

    margin = selling_price - unit_cost

    for lt_var in lead_time_vars:
        row = []
        for z in z_scores:
            # RSS Safety Stock Formula
            # Assuming Avg Lead Time = 1 for this heatmap abstraction
            safety_stock = z * np.sqrt((1 * std_dev ** 2) + (avg_demand ** 2 * lt_var ** 2))

            # Costs
            holding_cost_total = safety_stock * holding_cost

            # Expected Lost Sales (Standard Loss Function)
            # L(z) = pdf(z) - z * (1 - cdf(z))
            loss_func = stats.norm.pdf(z) - z * (1 - stats.norm.cdf(z))
            expected_shortage = std_dev * loss_func
            stockout_cost_total = expected_shortage * stockout_cost  # Penalty
            opportunity_cost = expected_shortage * margin  # Lost Profit

            # Total Profit = (Demand * Margin) - (Holding + Stockout + Opportunity)
            gross_profit = avg_demand * margin
            net_profit = gross_profit - (holding_cost_total + stockout_cost_total + opportunity_cost)

            row.append(net_profit)
        profit_matrix.append(row)

    fig = go.Figure(data=go.Heatmap(
        z=profit_matrix,
        x=[f"{sl:.0%}" for sl in service_levels],
        y=[f"{lt:.1f}" for lt in lead_time_vars],
        colorscale='Viridis',
        hoverongaps=False
    ))

    fig.update_layout(
        title="Net Profit Landscape ($)",
        xaxis_title="Target Service Level (%)",
        yaxis_title="Supply Chain Volatility (σ_LT)",
        height=400
    )

    return fig


def plot_cost_tradeoff(avg_demand, std_dev, holding_cost, stockout_cost, unit_cost, selling_price):
    """
    NEW FEATURE: Visualizes the 'Convexity' of Supply Chain Costs.
    Plots Holding Cost vs. Stockout Cost to find the mathematical minimum.
    """
    service_levels = np.linspace(0.50, 0.99, 50)
    z_scores = stats.norm.ppf(service_levels)

    holding_costs = []
    stockout_costs = []
    total_costs = []

    margin = selling_price - unit_cost

    for z in z_scores:
        # Simplified Safety Stock for this view (Focus on Service Level impact)
        safety_stock = z * std_dev

        # 1. Holding Cost (Linear Increase with Z)
        h_cost = safety_stock * holding_cost

        # 2. Stockout Cost (Exponential Decay with Z)
        loss_func = stats.norm.pdf(z) - z * (1 - stats.norm.cdf(z))
        expected_shortage = std_dev * loss_func

        # Total Shortage Impact = Penalty + Lost Margin
        s_cost = expected_shortage * (stockout_cost + margin)

        holding_costs.append(h_cost)
        stockout_costs.append(s_cost)
        total_costs.append(h_cost + s_cost)

    # Find Optimal Point (Minimum Total Cost)
    min_cost = min(total_costs)
    min_idx = total_costs.index(min_cost)
    optimal_sla = service_levels[min_idx]

    # Build the Chart
    fig = go.Figure()

    # Trace 1: Holding Cost (The Risk of Too Much)
    fig.add_trace(go.Scatter(x=service_levels, y=holding_costs, mode='lines', name='Holding Cost',
                             line=dict(color='red', dash='dot')))

    # Trace 2: Stockout Cost (The Risk of Too Little)
    fig.add_trace(go.Scatter(x=service_levels, y=stockout_costs, mode='lines', name='Stockout Cost',
                             line=dict(color='orange', dash='dot')))

    # Trace 3: Total Cost (The Optimization Curve)
    fig.add_trace(go.Scatter(x=service_levels, y=total_costs, mode='lines', name='Total Cost Impact',
                             line=dict(color='green', width=4)))

    # Highlight Optimal Point
    fig.add_trace(go.Scatter(x=[optimal_sla], y=[min_cost], mode='markers', name='Optimal Point',
                             marker=dict(color='black', size=12, symbol='star')))

    fig.update_layout(
        title=f"The Optimization Curve (Optimal SLA: {optimal_sla:.1%})",
        xaxis_title="Target Service Level",
        yaxis_title="Financial Impact ($)",
        xaxis=dict(tickformat=".0%"),
        height=400,
        hovermode="x unified"
    )

    return fig