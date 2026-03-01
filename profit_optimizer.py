import numpy as np
import scipy.stats as stats
import plotly.graph_objects as go

def calculate_profit_scenarios(
    avg_demand: float,
    std_dev: float,
    holding_cost: float,
    stockout_cost: float,
    unit_cost: float,
    selling_price: float
) -> go.Figure:
    """Generates a Profit Heatmap using vectorized meshgrid optimization."""
    margin = selling_price - unit_cost

    service_levels = np.linspace(0.50, 0.99, 20)
    lead_time_vars = np.linspace(0.0, 2.0, 20)
    z_scores = stats.norm.ppf(service_levels)

    z_grid, lt_grid = np.meshgrid(z_scores, lead_time_vars)

    ss_grid = z_grid * np.sqrt((1.0 * std_dev ** 2) + (avg_demand ** 2 * lt_grid ** 2))
    hc_grid = ss_grid * holding_cost

    loss_grid = stats.norm.pdf(z_grid) - z_grid * (1.0 - stats.norm.cdf(z_grid))
    es_grid = std_dev * loss_grid

    penalty_grid = es_grid * (stockout_cost + margin)
    gross_profit = avg_demand * margin

    profit_matrix = gross_profit - (hc_grid + penalty_grid)

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
        yaxis_title="Supply Chain Volatility (σ_LT)",
        height=400,
        margin={"r": 0, "t": 40, "l": 0, "b": 0}
    )

    return fig

def plot_cost_tradeoff(
    avg_demand: float,
    std_dev: float,
    holding_cost: float,
    stockout_cost: float,
    unit_cost: float,
    selling_price: float
) -> go.Figure:
    """Visualizes the convexity of supply chain costs to find the optimal service level."""
    margin = selling_price - unit_cost

    service_levels = np.linspace(0.50, 0.99, 100)
    z_scores = stats.norm.ppf(service_levels)

    safety_stock = z_scores * std_dev
    holding_costs = safety_stock * holding_cost

    loss_func = stats.norm.pdf(z_scores) - z_scores * (1.0 - stats.norm.cdf(z_scores))
    expected_shortage = std_dev * loss_func
    stockout_costs = expected_shortage * (stockout_cost + margin)

    total_costs = holding_costs + stockout_costs

    min_idx = int(np.argmin(total_costs))
    min_cost = float(total_costs[min_idx])
    optimal_sla = float(service_levels[min_idx])

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=service_levels, y=holding_costs, mode='lines',
        name='Holding Cost', line=dict(color='red', dash='dot')
    ))

    fig.add_trace(go.Scatter(
        x=service_levels, y=stockout_costs, mode='lines',
        name='Stockout Cost', line=dict(color='orange', dash='dot')
    ))

    fig.add_trace(go.Scatter(
        x=service_levels, y=total_costs, mode='lines',
        name='Total Cost Impact', line=dict(color='green', width=4)
    ))

    fig.add_trace(go.Scatter(
        x=[optimal_sla], y=[min_cost], mode='markers',
        name='Optimal Point', marker=dict(color='black', size=12, symbol='star')
    ))

    fig.update_layout(
        title=f"Optimization Curve (Optimal SLA: {optimal_sla:.1%})",
        xaxis_title="Target Service Level",
        yaxis_title="Financial Impact ($)",
        xaxis=dict(tickformat=".0%"),
        height=400,
        hovermode="x unified",
        margin={"r": 0, "t": 40, "l": 0, "b": 0}
    )

    return fig
