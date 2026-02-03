import scipy.stats as stats
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px


def run_simulation(avg_demand, std_dev, capacity_limit, unit_cost, selling_price, holding_cost, stockout_cost,
                   num_simulations=1000):
    """
    Runs a Monte Carlo simulation (1,000 iterations) to determine financial risk profile.
    Returns a dataframe of results and a Plotly Histogram.
    """

    # 1. Generate Stochastic Demand (Normal Distribution)
    # We ensure demand doesn't drop below 0
    simulated_demands = stats.norm.rvs(loc=avg_demand, scale=std_dev, size=num_simulations)
    simulated_demands = [max(0, int(d)) for d in simulated_demands]

    results = []

    # 2. Iterate through each theoretical month
    for demand in simulated_demands:
        # Flow Logic
        sold_units = min(demand, capacity_limit)
        lost_sales = max(0, demand - capacity_limit)
        unsold_inventory = max(0, capacity_limit - demand)

        # Financial Logic
        revenue = sold_units * selling_price

        # Costs
        handling_c = sold_units * unit_cost
        holding_c = unsold_inventory * holding_cost
        penalty_c = lost_sales * stockout_cost

        profit = revenue - handling_c - holding_c - penalty_c

        results.append(profit)

    # 3. Create DataFrame
    sim_df = pd.DataFrame(results, columns=["Simulated Profit"])

    # 4. Calculate Risk Metrics
    avg_profit = sim_df["Simulated Profit"].mean()
    loss_probability = (sim_df[sim_df["Simulated Profit"] < 0].shape[0] / num_simulations) * 100
    var_95 = sim_df["Simulated Profit"].quantile(0.05)  # Value at Risk (5th percentile)

    # 5. Create Visualization (Histogram)
    fig = px.histogram(
        sim_df,
        x="Simulated Profit",
        nbins=50,
        title="Distribution of Financial Outcomes (N=1,000 Simulations)",
        color_discrete_sequence=['#1f77b4']
    )

    # Add vertical line for Mean
    fig.add_vline(x=avg_profit, line_dash="dash", line_color="green", annotation_text="Expected Profit")

    # Add vertical line for VaR (Risk Floor)
    fig.add_vline(x=var_95, line_dash="dot", line_color="red", annotation_text="VaR (95%)")

    fig.update_layout(
        xaxis_title="Monthly Profit ($)",
        yaxis_title="Frequency (Probability)",
        showlegend=False,
        margin={"r": 0, "t": 40, "l": 0, "b": 0},
        height=350
    )

    return fig, {
        "avg_profit": int(avg_profit),
        "loss_prob": round(loss_probability, 1),
        "var_95": int(var_95)
    }