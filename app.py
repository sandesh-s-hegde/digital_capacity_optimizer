import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import date
from dotenv import load_dotenv

# Import Custom Logic Modules
import config
import db_manager  # Refactored Manager
import inventory_math
import ai_brain
import report_gen
import forecast
import profit_optimizer

# --- LOAD SECRETS ---
load_dotenv()

# --- CONFIGURATION ---
st.set_page_config(page_title="Digital Capacity Optimizer", layout="wide")

# --- SIDEBAR: CONTROLS ---
st.sidebar.header("⚙️ Data Source")
source_option = st.sidebar.radio("Mode:", ("🔌 Live Database", "📂 Sandbox (CSV)"))

st.sidebar.markdown("---")

# 1. LIVE DATABASE CONTROLS
selected_sku = None

if source_option == "🔌 Live Database":

    # A. SINGLE ENTRY
    st.sidebar.subheader("📝 Log Inventory")
    with st.sidebar.expander("Add Single Record", expanded=False):
        with st.form("entry_form"):
            new_product = st.text_input("Product Name (SKU)", value="Widget A")
            new_date = st.date_input("Date", value=date.today())
            new_demand = st.number_input("Order Qty", min_value=1, value=100)

            if st.form_submit_button("💾 Save"):
                if db_manager.add_record(new_date, new_product, new_demand):
                    st.success("Saved!")
                    st.rerun()

    # B. BULK UPLOAD
    with st.sidebar.expander("📂 Bulk Upload (CSV)"):
        st.info("Columns needed: date, product_name, demand")
        upload_csv = st.file_uploader("Upload History", type=["csv"])

        if upload_csv:
            if st.button("🚀 Import to Database"):
                try:
                    bulk_df = pd.read_csv(upload_csv)
                    # Clean headers
                    bulk_df.columns = bulk_df.columns.str.strip().str.lower().str.replace(' ', '_')

                    if {'date', 'product_name', 'demand'}.issubset(bulk_df.columns):
                        success, msg = db_manager.bulk_import_csv(bulk_df)
                        if success:
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(f"Import Failed: {msg}")
                    else:
                        st.error("CSV missing columns: date, product_name, demand")
                except Exception as e:
                    st.error(f"File Error: {e}")

    # C. FILTER
    st.sidebar.markdown("---")
    st.sidebar.header("🔍 Filter Dashboard")
    all_products = db_manager.get_unique_products()

    if all_products:
        selected_sku = st.sidebar.selectbox("Select Product:", all_products)
    else:
        st.sidebar.caption("No data yet.")

    # D. DANGER ZONE (RESET)
    st.sidebar.markdown("---")
    st.sidebar.header("⚠️ Danger Zone")
    if st.sidebar.button("🧨 Factory Reset (Wipe All Data)"):
        if db_manager.reset_database():
            st.sidebar.success("Database wiped! IDs reset to 1.")
            st.rerun()
        else:
            st.sidebar.error("Reset failed.")

st.sidebar.markdown("---")

# 2. PARAMETERS (Financials & Risk)
st.sidebar.header("🔧 Settings")
holding_cost = st.sidebar.number_input("Holding Cost ($)", value=config.HOLDING_COST)
stockout_cost = st.sidebar.number_input("Stockout Cost ($)", value=config.STOCKOUT_COST)

st.sidebar.subheader("🚢 Supplier Risk")
lead_time_months = st.sidebar.slider("Avg Lead Time (Months)", 0.5, 6.0, 1.0, 0.5)
lead_time_volatility = st.sidebar.slider("Lead Time Variance", 0.0, 2.0, 0.0, 0.1)
sim_sla = st.sidebar.slider("Target Service Level (%)", 50, 99, 95, 1)

# --- SIDEBAR: ABOUT SECTION ---
st.sidebar.markdown("---")
st.sidebar.markdown("### ℹ️ About")
st.sidebar.info(
    """
    **Capacity Optimizer v2.6**

    *Current Build:* Beta
    *Modules:* Multi-SKU, Risk Engine, Profit AI
    """
)

# --- MAIN PAGE ---
st.title("📦 Digital Capacity Optimizer")

# 1. LOAD DATA
df = None
if source_option == "🔌 Live Database":
    df = db_manager.load_data(selected_sku)
else:
    # Sandbox Mode
    st.info("Sandbox Mode: Upload a CSV to simulate.")
    uploaded_file = st.file_uploader("Upload CSV", type=["csv"], key="sandbox")
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        df.columns = df.columns.str.strip().str.lower()
        if 'date' in df.columns: df['date'] = pd.to_datetime(df['date'])

# 2. EXECUTIVE SUMMARY
if source_option == "🔌 Live Database":
    st.markdown("### 🚁 Executive Command Center")
    full_df = db_manager.load_data(None)

    if full_df is not None and not full_df.empty:
        summary_data = []
        for p in full_df['product_name'].unique():
            p_data = full_df[full_df['product_name'] == p]
            last = p_data.iloc[-1]
            avg = p_data['demand'].mean()

            status = "🟢 Normal"
            if last['demand'] > avg * 1.5:
                status = "🔴 Surge Alert"
            elif last['demand'] < avg * 0.5:
                status = "🟡 Low Velocity"

            summary_data.append({
                "Product": p, "Last Update": last['date'],
                "Latest": int(last['demand']), "Status": status
            })

        summ_df = pd.DataFrame(summary_data)
        if not summ_df.empty:
            st.dataframe(
                summ_df.style.map(lambda v: 'color: red' if 'Surge' in v else 'color: green', subset=['Status']),
                use_container_width=True, hide_index=True
            )
    st.divider()

# 3. ANALYSIS TABS
if df is not None and not df.empty:

    # --- CALCULATIONS ---
    avg_demand = df['demand'].mean()
    std_dev_demand = df['demand'].std() if len(df) > 1 else 0
    actual_sla = inventory_math.calculate_newsvendor_target(holding_cost, stockout_cost)

    sim_safety_stock = inventory_math.calculate_advanced_safety_stock(
        avg_demand, std_dev_demand, lead_time_months, lead_time_volatility, sim_sla / 100.0
    )
    eoq = inventory_math.calculate_eoq(avg_demand * 12, config.ORDER_COST, holding_cost)

    metrics = {
        "avg_demand": int(avg_demand), "std_dev": int(std_dev_demand),
        "lead_time": lead_time_months, "lead_time_risk": lead_time_volatility,
        "eoq": int(eoq), "safety_stock": int(sim_safety_stock),
        "product_name": selected_sku if selected_sku else "Data"
    }

    if source_option == "🔌 Live Database" and not selected_sku:
        st.warning("Please select a product from the sidebar.")
    else:
        tab1, tab2 = st.tabs(["📊 Dashboard", "💰 Profit Optimizer"])

        with tab1:
            st.subheader(f"Analysis: {metrics['product_name']}")

            # Chart
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=df['date'], y=df['demand'], mode='lines+markers', name='Actual',
                                     line=dict(color='#2ca02c', width=3)))

            if st.checkbox("Show Forecast", value=True):
                f_df = forecast.generate_forecast(df)
                if f_df is not None:
                    # Bridge the gap visually
                    last_pt = pd.DataFrame({'date': [df['date'].max()], 'demand': [df.iloc[-1]['demand']]})
                    fig.add_trace(
                        go.Scatter(x=pd.concat([last_pt, f_df])['date'], y=pd.concat([last_pt, f_df])['demand'],
                                   mode='lines+markers', name='Forecast', line=dict(dash='dash', color='#1f77b4')))

            st.plotly_chart(fig, use_container_width=True)

            # Metrics
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Avg Demand", f"{int(avg_demand)}")
            c2.metric("Optimal SLA", f"{actual_sla * 100:.1f}%")
            c3.metric("Safety Stock", f"{int(sim_safety_stock)}", "Risk Adjusted")
            c4.metric("EOQ Order", f"{int(eoq)}")

            # AI Chat
            st.divider()
            if "messages" not in st.session_state: st.session_state.messages = []

            for msg in st.session_state.messages:
                st.chat_message(msg["role"]).markdown(msg["content"])

            if prompt := st.chat_input("Ask about this product..."):
                st.session_state.messages.append({"role": "user", "content": prompt})
                st.chat_message("user").markdown(prompt)

                with st.spinner("Analyzing..."):
                    history = [{"role": m["role"], "parts": [m["content"]]} for m in st.session_state.messages]
                    response = ai_brain.chat_with_data(prompt, history, df, metrics)

                st.chat_message("assistant").markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})

        with tab2:
            st.subheader("Profit Heatmap")
            uc = st.number_input("Unit Cost", 50.0)
            sp = st.number_input("Selling Price", 85.0)
            if sp > uc:
                st.plotly_chart(profit_optimizer.calculate_profit_scenarios(
                    avg_demand, std_dev_demand, holding_cost, stockout_cost, uc, sp
                ), use_container_width=True)

    # DELETE SECTION
    if source_option == "🔌 Live Database":
        st.divider()
        with st.expander("🗑️ Manage Records"):
            st.dataframe(df[['id', 'date', 'product_name', 'demand']].sort_values('date', ascending=False),
                         use_container_width=True, hide_index=True)
            del_id = st.number_input("ID to Delete", min_value=1, step=1)
            if st.button("Delete"):
                if db_manager.delete_record(del_id):
                    st.success("Deleted!")
                    st.rerun()

# --- FOOTER ---
st.markdown("---")
st.caption("© 2026 Digital Capacity Inc. | v2.6 Beta")