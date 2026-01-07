"""
app.py
The Web Interface for the Digital Capacity Optimizer.
Run with: streamlit run app.py
"""
import streamlit as st
import pandas as pd
from inventory_math import calculate_newsvendor_target, calculate_required_inventory
from forecaster import generate_forecast
from visualizer import plot_forecast
import config

# --- 1. Page Configuration ---
st.set_page_config(page_title="Digital Capacity Optimizer", page_icon="🏭")

st.title("🏭 Digital Capacity Optimizer")
st.markdown("""
**AI-Powered Supply Chain Planning** Upload your demand logs to generate forecasts and optimized procurement plans.
""")

# --- 2. Sidebar (Settings) ---
st.sidebar.header("⚙️ Configuration")
holding_cost = st.sidebar.number_input("Holding Cost ($/Unit/Year)", value=config.HOLDING_COST)
stockout_cost = st.sidebar.number_input("Stockout Cost ($/Unit)", value=config.STOCKOUT_COST)

# --- 3. File Upload ---
uploaded_file = st.file_uploader("Upload CSV Usage Logs", type=["csv"])

if uploaded_file is not None:
    # Load Data
    df = pd.read_csv(uploaded_file)
    st.success(f"✅ Loaded {len(df)} months of data.")

    # Show Raw Data (Expandable)
    with st.expander("View Raw Data"):
        st.dataframe(df)

    # --- 4. Run Forecasting Engine ---
    st.subheader("🔮 Demand Forecast")

    months_to_predict = st.slider("Months to Forecast", min_value=1, max_value=6, value=3)

    with st.spinner("Training AI Model..."):
        forecast_result = generate_forecast(df, months_ahead=months_to_predict)
        forecast_values = forecast_result['forecast_values']

        # Display Chart
        fig = plot_forecast(df, forecast_values)
        st.pyplot(fig)

    # --- 5. Optimization Results ---
    st.subheader("📦 Procurement Recommendation")

    # Get Next Month's Prediction
    next_month_demand = forecast_values.iloc[0]
    std_dev_demand = df['demand'].std()

    # Calculate Math
    optimal_sla = calculate_newsvendor_target(holding_cost, stockout_cost)
    required_inventory = calculate_required_inventory(next_month_demand, std_dev_demand, optimal_sla)

    # Display Key Metrics in Columns
    col1, col2, col3 = st.columns(3)
    col1.metric("Predicted Demand", f"{int(next_month_demand)} units", delta="Next Month")
    col2.metric("Optimal Service Level", f"{optimal_sla * 100:.1f}%", help="Based on Cost Ratio")
    col3.metric("Recommended Order", f"{int(required_inventory)} units", delta="Final Decision")

    st.info(
        f"💡 **Insight:** To maintain a {optimal_sla * 100:.1f}% Service Level with current volatility, you need **{int(required_inventory)} units** in stock.")

else:
    st.info("👆 Please upload a CSV file to begin simulation. (Use 'mock_data.csv')")