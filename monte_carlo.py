from typing import Dict, Tuple, Union
import numpy as np
import pandas as pd
import plotly.express as px
from plotly.graph_objs import Figure


def run_simulation(
    avg_demand: float,
    std_dev: float,
    capacity_limit: int,
    unit_cost: float,
    selling_price: float,
    holding_cost: float,
    stockout_cost: float,
    num_simulations: int = 10000
) -> Tuple[Figure, Dict[str, Union[int, float]]]:
    """Executes a vectorized Monte Carlo simulation to evaluate financial risk profiles."""
    np.random.seed(42)

    raw_demands = np.random.normal(loc=avg_demand, scale=std_dev, size=num_simulations)
    demands = np.maximum(0, np.round(raw_demands)).astype(int)

    sold_units = np.minimum(demands, capacity_limit)
    lost_sales = np.maximum(0, demands - capacity_limit)
    unsold_inventory = np.maximum(0, capacity_limit - demands)

    revenue = sold_units * selling_price
    handling_cost_total = sold_units * unit_cost
    holding_cost_total = unsold_inventory * holding_cost
    penalty_cost_total = lost_sales * stockout_cost

    profits = revenue - handling_cost_total - holding_cost_total - penalty_cost_total
    sim_df = pd.DataFrame({"profit": profits})

    avg_profit = float(sim_df["profit"].mean())
    loss_probability = float((sim_df[sim_df["profit"] < 0].shape[0] / num_simulations) * 100)
    var_95 = float(sim_df["profit"].quantile(0.05))

    q_low = float(sim_df["profit"].quantile(0.01))
    q_high = float(sim_df["profit"].quantile(0.99))
    plot_df = sim_df[(sim_df["profit"] > q_low) & (sim_df["profit"] < q_high)]

    fig = px.histogram(
        plot_df,
        x="profit",
        nbins=50,
        title=f"Monte Carlo Risk Distribution ({num_simulations:,} Iterations)",
        color_discrete_sequence=['#1f77b4']
    )

    fig.add_vrect(
        x0=q_low, x1=0,
        fillcolor="red", opacity=0.1,
        layer="below", line_width=0,
        annotation_text="Loss Zone", annotation_position="top left"
    )

    fig.add_vline(x=avg_profit, line_dash="dash", line_color="green")
    fig.add_annotation(
        x=avg_profit, y=1.05, yref="paper",
        text="Expected Profit", showarrow=False, font=dict(color="green")
    )

    fig.add_vline(x=var_95, line_dash="dot", line_color="red")
    fig.add_annotation(
        x=var_95, y=0.95, yref="paper",
        text="VaR (95%)", showarrow=False, font=dict(color="red")
    )

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
