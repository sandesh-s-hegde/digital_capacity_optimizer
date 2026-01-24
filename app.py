import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import date
from dotenv import load_dotenv

# Import Custom Logic Modules
import config
import db_manager
import inventory_math
import ai_brain
import report_gen
import forecast
import profit_optimizer

# --- LOAD SECRETS ---
load_dotenv()

# --- CONFIGURATION ---
st.set_page_config(
    page_title="Digital Capacity Optimizer",
    page_icon="📦",
    layout="wide"
)


# --- HELPER: REUSABLE CHAT INTERFACE ---
def render_chat_ui(df, metrics, extra_context="", key="default_chat"):
    """
    Renders the Chat UI with specific context for the active tab.
    """
    st.divider()
    st.subheader("💬 AI Analyst")

    # 1. Initialize Chat History
    if "messages" not in st.session_state: st.session_state.messages = []

    # 2. Scrollable Container
    chat_container = st.container(height=400, border=True)

    with chat_container:
        for msg in st.session_state.messages:
            st.chat_message(msg["role"]).markdown(msg["content"])

    # 3. Input Area (Fixed: Added unique 'key')
    if prompt := st.chat_input("Ask a question...", key=key):
        st.session_state.messages.append({"role": "user", "content": prompt})

        with chat_container:
            st.chat_message("user").markdown(prompt)

            with st.spinner("Analyzing..."):
                # Combine General Metrics + Tab Specific Context
                full_query = f"{prompt}\n\n[CONTEXT OVERRIDE: {extra_context}]"

                history = [{"role": m["role"], "parts": [m["content"]]} for m in st.session_state.messages]
                response = ai_brain.chat_with_data(full_query, history, df, metrics)

            st.chat_message("assistant").markdown(response)

        st.session_state.messages.append({"role": "assistant", "content": response})
        st.rerun()


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
                    bulk_df.columns = bulk_df.columns.str.strip().str.lower().str.replace(' ', '_')
                    if {'date', 'product_name', 'demand'}.issubset(bulk_df.columns):
                        success, msg = db_manager.bulk_import_csv(bulk_df)
                        if success:
                            st.success(msg); st.rerun()
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

    # D. DANGER ZONE
    st.sidebar.markdown("---")
    with st.sidebar.expander("⚠️ Danger Zone"):
        if st.button("🧨 Factory Reset"):
            if db_manager.reset_database(): st.success("Reset Complete"); st.rerun()

st.sidebar.markdown("---")

# 2. PARAMETERS
st.sidebar.header("🔧 Settings")
holding_cost = st.sidebar.number_input("Holding Cost ($)", value=config.HOLDING_COST)
stockout_cost = st.sidebar.number_input("Stockout Cost ($)", value=config.STOCKOUT_COST)

st.sidebar.subheader("🚢 Supplier Risk")
lead_time_months = st.sidebar.slider("Avg Lead Time (Months)", 0.5, 6.0, 1.0, 0.5)
lead_time_volatility = st.sidebar.slider("Lead Time Variance", 0.0, 2.0, 0.0, 0.1)
sim_sla = st.sidebar.slider("Target Service Level (%)", 50, 99, 95, 1)

st.sidebar.markdown("---")
st.sidebar.caption("🟢 System Status: **Online** | v2.7.0 (Final Release)")

# --- ACADEMIC LABELING ---
st.sidebar.markdown("### ℹ️ About")
st.sidebar.info(
    """
    **Capacity Optimizer v2.7**

    *Methods Applied:*
    * 📊 Demand Forecasting (Linear)
    * 🚢 **Newsvendor Inventory Model**
    * 🔮 Stochastic Safety Stock (RSS)
    * 💰 Cost-Profit Optimization
    """
)

# --- MAIN PAGE ---
st.title("📦 Digital Capacity Optimizer")

# LOAD DATA
df = None
if source_option == "🔌 Live Database":
    df = db_manager.load_data(selected_sku)
else:
    st.info("Sandbox Mode: Upload a CSV to simulate.")
    uploaded_file = st.file_uploader("Upload CSV", type=["csv"], key="sandbox")
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        df.columns = df.columns.str.strip().str.lower()
        if 'date' in df.columns: df['date'] = pd.to_datetime(df['date'])

# EXECUTIVE SUMMARY
if source_option == "🔌 Live Database":
    with st.expander("🚁 Executive Command Center", expanded=False):
        full_df = db_manager.load_data(None)
        if full_df is not None and not full_df.empty:
            summary_data = []
            for p in full_df['product_name'].unique():
                p_data = full_df[full_df['product_name'] == p]
                if not p_data.empty:
                    last = p_data.iloc[-1]
                    avg = p_data['demand'].mean()
                    status = "🟢 Normal"
                    if last['demand'] > avg * 1.5:
                        status = "🔴 Surge Alert"
                    elif last['demand'] < avg * 0.5:
                        status = "🟡 Low Velocity"
                    summary_data.append({"Product": p, "Latest": int(last['demand']), "Status": status})
            st.dataframe(pd.DataFrame(summary_data), use_container_width=True, hide_index=True)
    st.divider()

# ANALYSIS TABS
if df is not None and not df.empty:

    # METRICS
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
        "sla": sim_sla / 100.0, "actual_sla": actual_sla,
        "product_name": selected_sku if selected_sku else "Data"
    }

    if source_option == "🔌 Live Database" and not selected_sku:
        st.warning("Please select a product from the sidebar.")
    else:
        tab1, tab2 = st.tabs(["📊 Dashboard", "💰 Profit Optimizer"])

        # --- TAB 1: DASHBOARD ---
        with tab1:
            st.subheader(f"Analysis: {metrics['product_name']}")

            # Chart
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=df['date'], y=df['demand'], mode='lines+markers', name='Actual',
                                     line=dict(color='#2ca02c', width=3)))
            if st.checkbox("Show Forecast", value=True):
                f_df = forecast.generate_forecast(df)
                if f_df is not None:
                    last_pt = pd.DataFrame({'date': [df['date'].max()], 'demand': [df.iloc[-1]['demand']]})
                    fig.add_trace(
                        go.Scatter(x=pd.concat([last_pt, f_df])['date'], y=pd.concat([last_pt, f_df])['demand'],
                                   mode='lines+markers', name='Forecast', line=dict(dash='dash', color='#1f77b4')))
            st.plotly_chart(fig, use_container_width=True)

            # KPI Metrics
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Avg Demand", f"{int(avg_demand)}")
            c2.metric("Optimal SLA", f"{actual_sla * 100:.1f}%")
            # ACADEMIC LABELING CHANGE HERE
            c3.metric("Safety Stock", f"{int(sim_safety_stock)}", "Newsvendor + RSS Model")
            c4.metric("EOQ Order", f"{int(eoq)}")

            # PDF Report
            if st.button("📄 Generate PDF Report"):
                with st.spinner("Writing..."):
                    summary = ai_brain.chat_with_data(f"Summary for {metrics['product_name']}", [], df, metrics)
                    pdf_bytes = report_gen.generate_pdf(metrics, summary)
                    st.download_button("⬇️ Download PDF", pdf_bytes, f"report.pdf", "application/pdf")

            # --- AI CHAT (DASHBOARD CONTEXT) ---
            render_chat_ui(df, metrics, extra_context="Focus on inventory levels and forecasting.",
                           key="dashboard_chat")

        # --- TAB 2: PROFIT OPTIMIZER ---
        with tab2:
            st.subheader("Profit Heatmap")

            # Inputs
            c_input1, c_input2 = st.columns(2)
            uc = c_input1.number_input("Unit Cost ($)", 50.0)
            sp = c_input2.number_input("Selling Price ($)", 85.0)

            if sp > uc:
                # 1. Show Heatmap
                st.plotly_chart(profit_optimizer.calculate_profit_scenarios(
                    avg_demand, std_dev_demand, holding_cost, stockout_cost, uc, sp
                ), use_container_width=True)

                # 2. Build Profit Context for AI
                margin = sp - uc
                margin_pct = (margin / sp) * 100
                profit_context = f"""
                PROFIT SCENARIO ACTIVE:
                - Unit Cost: ${uc}
                - Selling Price: ${sp}
                - Profit Margin: ${margin} ({margin_pct:.1f}%)
                - The user is looking at a heatmap showing profit vs risk.
                - Higher Service Levels increase costs but capture more revenue.
                """

                # --- AI CHAT (PROFIT CONTEXT) ---
                st.info("💡 Tip: Ask the AI to summarize this heatmap or find the break-even point.")
                render_chat_ui(df, metrics, extra_context=profit_context, key="profit_chat")
            else:
                st.error("Selling Price must be higher than Unit Cost.")

# --- FOOTER ---
st.markdown("---")
st.caption("© 2026 Digital Capacity Inc. | v2.7.0")