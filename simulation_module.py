import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from scipy.stats import norm


def render_research_lab(avg_demand: float, std_dev: float, margin: float, holding_cost: float):
    st.markdown("## 🔬 Research Laboratory: Stochastic Stress Test")
    st.info(
        "Run a vectorized Monte Carlo simulation (N=10,000) to validate inventory assumptions against demand volatility.")

    col1, col2 = st.columns(2)
    with col1:
        current_ss = st.number_input("Current Safety Stock", value=66)
    with col2:
        sim_days = st.slider("Simulation Horizon (Days)", 1000, 10000, 5000)

    if st.button("🚀 Run Vectorized Monte Carlo", type="primary"):
        with st.spinner(f"Simulating {sim_days:,} supply chain scenarios..."):
            # 1. Theoretical Math (Newsvendor)
            # Safe division guard against edge cases
            critical_ratio = margin / (margin + holding_cost) if (margin + holding_cost) > 0 else 0.95
            z_score = norm.ppf(critical_ratio)
            optimal_ss = max(0, z_score * std_dev)

            # 2. Vectorized Simulation Engine (Eliminated 'for' loop)
            np.random.seed(42)
            raw_demands = np.random.normal(avg_demand, std_dev, sim_days)
            demands = np.maximum(0, np.round(raw_demands))  # Clean to positive integers

            # Scenario A: Current Strategy (Matrix Math)
            cap_A = avg_demand + current_ss
            sales_A = np.minimum(demands, cap_A)
            loss_A = np.maximum(0, cap_A - demands) * holding_cost
            profit_A = (sales_A * margin) - loss_A

            # Scenario B: Optimal Strategy (Matrix Math)
            cap_B = avg_demand + optimal_ss
            sales_B = np.minimum(demands, cap_B)
            loss_B = np.maximum(0, cap_B - demands) * holding_cost
            profit_B = (sales_B * margin) - loss_B

            # 3. Results Metrics
            avg_A, std_A = np.mean(profit_A), np.std(profit_A)
            avg_B, std_B = np.mean(profit_B), np.std(profit_B)
            delta = avg_B - avg_A

            # Value at Risk calculation (Worst 5% of days)
            var_95_A = np.percentile(profit_A, 5)
            var_95_B = np.percentile(profit_B, 5)

            st.success(
                f"**Research Conclusion:** Optimizing Safety Stock to **{int(optimal_ss)} units** yields **${delta:,.2f}** additional profit per day.")

            # 4. Interactive Plotly Charting
            fig = go.Figure()
            fig.add_trace(go.Histogram(
                x=profit_A, nbinsx=50, opacity=0.6,
                name=f'Current (SS={current_ss})', marker_color='gray'
            ))
            fig.add_trace(go.Histogram(
                x=profit_B, nbinsx=50, opacity=0.75,
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

            # Add zero-profit risk line
            fig.add_vline(x=0, line_dash="dash", line_color="red", annotation_text="Loss Zone")

            st.plotly_chart(fig, use_container_width=True)

            # 5. Data Table
            res_data = {
                "Metric": ["Safety Stock (Units)", "Daily Profit (Avg)", "Volatility (StdDev)", "VaR (95% Downside)",
                           "Annual Impact"],
                "Current Strategy": [f"{current_ss}", f"${avg_A:,.2f}", f"${std_A:,.2f}", f"${var_95_A:,.2f}", "-"],
                "Optimal Strategy": [f"{int(optimal_ss)}", f"${avg_B:,.2f}", f"${std_B:,.2f}", f"${var_95_B:,.2f}",
                                     f"+${delta * 365:,.0f}"]
            }
            st.table(pd.DataFrame(res_data))
