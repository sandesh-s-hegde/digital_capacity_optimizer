import numpy as np
import scipy.stats as stats
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def run_simulation(avg_demand: float, std_dev: float, capacity_limit: int,
                   unit_cost: float, selling_price: float, holding_cost: float,
                   stockout_cost: float, num_simulations: int = 10000):
    """
    Runs a fully vectorized Monte Carlo simulation to determine financial risk profile.
    Returns a dataframe of results and a Plotly Histogram with Risk Zones.
    """

    # 1. Generate Stochastic Demand (Vectorized)
    np.random.seed(42)  # For consistent UI testing
    raw_demands = stats.norm.rvs(loc=avg_demand, scale=std_dev, size=num_simulations)
    # Clamp to 0 and convert to integers instantly
    demands = np.maximum(0, np.round(raw_demands)).astype(int)

    # 2. Vectorized Financial Math (Eliminates the slow 'for' loop)
    sold_units = np.minimum(demands, capacity_limit)
    lost_sales = np.maximum(0, demands - capacity_limit)
    unsold_inventory = np.maximum(0, capacity_limit - demands)

    # Matrix multiplication for instant cost calculation
    revenue = sold_units * selling_price
    handling_c = sold_units * unit_cost
    holding_c = unsold_inventory * holding_cost
    penalty_c = lost_sales * stockout_cost

    profits = revenue - handling_c - holding_c - penalty_c

    # 3. Create DataFrame
    sim_df = pd.DataFrame({"Simulated Profit": profits})

    # 4. Calculate Risk Metrics
    avg_profit = sim_df["Simulated Profit"].mean()
    loss_probability = (sim_df[sim_df["Simulated Profit"] < 0].shape[0] / num_simulations) * 100
    var_95 = sim_df["Simulated Profit"].quantile(0.05)  # Value at Risk

    # 5. UI CLEANUP: Filter Outliers for the Chart ONLY
    # Changed lower bound to 0.01 to show more of the dangerous tail risk
    q_low = sim_df["Simulated Profit"].quantile(0.01)
    q_high = sim_df["Simulated Profit"].quantile(0.99)
    plot_df = sim_df[(sim_df["Simulated Profit"] > q_low) & (sim_df["Simulated Profit"] < q_high)]

    # 6. Create Visualization (Histogram)
    fig = px.histogram(
        plot_df,
        x="Simulated Profit",
        nbins=50,
        title=f"Monte Carlo Risk Distribution ({num_simulations:,} Iterations)",
        color_discrete_sequence=['#1f77b4']
    )

    # NEW: Add a shaded red background for the "Loss Zone" (Profit < 0)
    fig.add_vrect(
        x0=q_low, x1=0,
        fillcolor="red", opacity=0.1,
        layer="below", line_width=0,
        annotation_text="Loss Zone", annotation_position="top left"
    )

    # Add Mean Line
    fig.add_vline(x=avg_profit, line_dash="dash", line_color="green")
    fig.add_annotation(x=avg_profit, y=1.05, yref="paper", text="Expected Profit", showarrow=False,
                       font=dict(color="green"))

    # Add VaR Line
    fig.add_vline(x=var_95, line_dash="dot", line_color="red")
    fig.add_annotation(x=var_95, y=0.95, yref="paper", text="VaR (95%)", showarrow=False, font=dict(color="red"))

    fig.update_layout(
        xaxis_title="Monthly Profit ($)",
        yaxis_title="Frequency",
        showlegend=False,
        margin={"r": 0, "t": 40, "l": 0, "b": 0},
        height=350
    )

    return fig, {
        "avg_profit": int(avg_profit),
        "loss_prob": round(loss_probability, 1),
        "var_95": int(var_95)
    }
