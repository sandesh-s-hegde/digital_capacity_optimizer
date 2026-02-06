import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import norm


def render_research_lab(avg_demand, std_dev, margin, holding_cost):
    st.markdown("## 🔬 Research Laboratory: Stochastic Stress Test")
    st.info("Run a Monte Carlo simulation (N=10,000) to validate inventory assumptions against demand volatility.")

    col1, col2 = st.columns(2)
    with col1:
        current_ss = st.number_input("Current Safety Stock", value=66)
    with col2:
        sim_days = st.slider("Simulation Horizon (Days)", 1000, 10000, 5000)

    if st.button("Run Monte Carlo Simulation"):
        with st.spinner("Simulating supply chain scenarios..."):
            # 1. Theoretical Math
            critical_ratio = margin / (margin + holding_cost)
            z_score = norm.ppf(critical_ratio)
            optimal_ss = z_score * std_dev

            # 2. Simulation Engine
            np.random.seed(42)
            demands = np.random.normal(avg_demand, std_dev, sim_days)

            # Scenario A: Current
            cap_A = avg_demand + current_ss
            profit_A = []

            # Scenario B: Optimal
            cap_B = avg_demand + optimal_ss
            profit_B = []

            for d in demands:
                # Calc A
                sales_a = min(d, cap_A)
                loss_a = max(0, cap_A - d) * holding_cost
                profit_A.append((sales_a * margin) - loss_a)

                # Calc B
                sales_b = min(d, cap_B)
                loss_b = max(0, cap_B - d) * holding_cost
                profit_B.append((sales_b * margin) - loss_b)

            # 3. Results Visualization
            avg_A = np.mean(profit_A)
            avg_B = np.mean(profit_B)
            delta = avg_B - avg_A

            st.success(
                f"**Research Conclusion:** Optimizing Safety Stock yields **${delta:,.2f}** additional profit per day.")

            # Charting
            fig, ax = plt.subplots(figsize=(10, 4))
            ax.hist(profit_A, bins=50, alpha=0.5, label=f'Current (SS={current_ss})', color='gray')
            ax.hist(profit_B, bins=50, alpha=0.5, label=f'Optimal (SS={int(optimal_ss)})', color='#002D62')
            ax.set_xlabel("Daily Net Profit ($)")
            ax.set_ylabel("Frequency (Days)")
            ax.legend()
            ax.set_title("Profit Distribution: Current vs. Optimal Strategy")

            st.pyplot(fig)

            # Data Table
            res_data = {
                "Metric": ["Safety Stock", "Daily Profit (Avg)", "Risk (StdDev)", "Annual Impact"],
                "Current Strategy": [f"{current_ss}", f"${avg_A:,.2f}", f"${np.std(profit_A):,.2f}", "-"],
                "Optimal Strategy": [f"{int(optimal_ss)}", f"${avg_B:,.2f}", f"${np.std(profit_B):,.2f}",
                                     f"+${delta * 365:,.0f}"]
            }
            st.table(pd.DataFrame(res_data))