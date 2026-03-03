import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from scipy.stats import norm


def render_research_lab(
    avg_demand: float,
    std_dev: float,
    margin: float,
    holding_cost: float
) -> None:
    """Renders the Stochastic Stress Test laboratory UI and executes the Monte Carlo simulation."""
    st.markdown("## Research Laboratory: Stochastic Stress Test")
    st.info(
        "Run a vectorized Monte Carlo simulation (N=10,000) to validate inventory assumptions against demand volatility.")

    col1, col2 = st.columns(2)
    with col1:
        current_ss = st.number_input("Current Safety Stock", value=66)
    with col2:
        sim_days = st.slider("Simulation Horizon (Days)", 1000, 10000, 5000)

    if st.button("Run Vectorized Monte Carlo", type="primary"):
        with st.spinner(f"Simulating {sim_days:,} supply chain scenarios..."):
            critical_ratio = margin / (margin + holding_cost) if (margin + holding_cost) > 0.0 else 0.95
            z_score = norm.ppf(critical_ratio)
            optimal_ss = max(0.0, z_score * std_dev)

            np.random.seed(42)
            raw_demands = np.random.normal(avg_demand, std_dev, sim_days)
            demands = np.maximum(0.0, np.round(raw_demands))

            cap_a = avg_demand + current_ss
            sales_a = np.minimum(demands, cap_a)
            loss_a = np.maximum(0.0, cap_a - demands) * holding_cost
            profit_a = (sales_a * margin) - loss_a

            cap_b = avg_demand + optimal_ss
            sales_b = np.minimum(demands, cap_b)
            loss_b = np.maximum(0.0, cap_b - demands) * holding_cost
            profit_b = (sales_b * margin) - loss_b

            avg_a, std_a = float(np.mean(profit_a)), float(np.std(profit_a))
            avg_b, std_b = float(np.mean(profit_b)), float(np.std(profit_b))
            delta = avg_b - avg_a

            var_95_a = float(np.percentile(profit_a, 5))
            var_95_b = float(np.percentile(profit_b, 5))

            st.success(
                f"**Research Conclusion:** Optimizing Safety Stock to **{int(optimal_ss)} units** yields **${delta:,.2f}** additional profit per day.")

            fig = go.Figure()
            fig.add_trace(go.Histogram(
                x=profit_a, nbinsx=50, opacity=0.6,
                name=f'Current (SS={current_ss})', marker_color='gray'
            ))
            fig.add_trace(go.Histogram(
                x=profit_b, nbinsx=50, opacity=0.75,
                name=f'Optimal (SS={int(optimal_ss)})', marker_color='#002D62'
            ))

            fig.update_layout(
                title="Profit Distribution: Current vs. Optimal Strategy",
                xaxis_title="Daily Net Profit ($)",
                yaxis_title="Frequency (Days)",
                barmode='overlay',
                height=450,
                margin=dict(l=0, r=0, t=40, b=0)
            )

            fig.add_vline(x=0, line_dash="dash", line_color="red", annotation_text="Loss Zone")

            st.plotly_chart(fig, use_container_width=True)

            res_data = {
                "Metric": [
                    "Safety Stock (Units)", "Daily Profit (Avg)",
                    "Volatility (StdDev)", "VaR (95% Downside)", "Annual Impact"
                ],
                "Current Strategy": [
                    f"{current_ss}", f"${avg_a:,.2f}",
                    f"${std_a:,.2f}", f"${var_95_a:,.2f}", "-"
                ],
                "Optimal Strategy": [
                    f"{int(optimal_ss)}", f"${avg_b:,.2f}",
                    f"${std_b:,.2f}", f"${var_95_b:,.2f}", f"+${delta * 365:,.0f}"
                ]
            }
            st.table(pd.DataFrame(res_data))
