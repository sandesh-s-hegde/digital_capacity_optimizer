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
    # FIX: We pass 'random_state=42' here to fix the seed correctly (Optional: remove random_state=42 to restore fluctuations)
    simulated_demands = stats.norm.rvs(loc=avg_demand, scale=std_dev, size=num_simulations, random_state=42)
    simulated_demands = [max(0, int(d)) for d in simulated_demands]

    results = []

    # 2. Iterate through scenarios
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

    # 4. Calculate Risk Metrics (Using FULL Data for Accuracy)
    avg_profit = sim_df["Simulated Profit"].mean()
    loss_probability = (sim_df[sim_df["Simulated Profit"] < 0].shape[0] / num_simulations) * 100
    var_95 = sim_df["Simulated Profit"].quantile(0.05)  # Value at Risk

    # 5. UI CLEANUP: Filter Outliers for the Chart ONLY
    # FIX: We changed quantile from 0.01 to 0.05 (Cut bottom 5%)
    # This hides the heavy "Stockout Penalty" tails so the chart isn't squished
    q_low = sim_df["Simulated Profit"].quantile(0.05)
    q_high = sim_df["Simulated Profit"].quantile(0.99)
    plot_df = sim_df[(sim_df["Simulated Profit"] > q_low) & (sim_df["Simulated Profit"] < q_high)]

    # 6. Create Visualization (Histogram)
    fig = px.histogram(
        plot_df,
        x="Simulated Profit",
        nbins=40,
        title="Distribution of Financial Outcomes (Zoomed: 95% Confidence Interval)",
        color_discrete_sequence=['#1f77b4']
    )

    # Add Mean Line
    fig.add_vline(x=avg_profit, line_dash="dash", line_color="green")
    # Annotation at Top
    fig.add_annotation(x=avg_profit, y=1.05, yref="paper", text="Expected Profit", showarrow=False,
                       font=dict(color="green"))

    # Add VaR Line
    fig.add_vline(x=var_95, line_dash="dot", line_color="red")
    # Annotation slightly lower to prevent overlap
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