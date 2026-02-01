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
    page_title="LSP Digital Capacity Twin",
    page_icon="🚛",
    layout="wide"
)


# --- HELPER: REUSABLE CHAT INTERFACE ---
def render_chat_ui(df, metrics, extra_context="", key="default_chat"):
    """
    Renders the Chat UI with specific context for the active tab.
    """
    st.divider()
    st.subheader("💬 LSP Strategy Assistant")

    # 1. Initialize Chat History
    if "messages" not in st.session_state: st.session_state.messages = []

    # 2. Scrollable Container
    chat_container = st.container(height=400, border=True)

    with chat_container:
        for msg in st.session_state.messages:
            st.chat_message(msg["role"]).markdown(msg["content"])

    # 3. Input Area
    if prompt := st.chat_input("Ask about capacity sharing or risk...", key=key):
        st.session_state.messages.append({"role": "user", "content": prompt})

        with chat_container:
            st.chat_message("user").markdown(prompt)

            with st.spinner("Analyzing Logistics Network..."):
                full_query = f"{prompt}\n\n[CONTEXT OVERRIDE: {extra_context}]"
                history = [{"role": m["role"], "parts": [m["content"]]} for m in st.session_state.messages]
                response = ai_brain.chat_with_data(full_query, history, df, metrics)

            st.chat_message("assistant").markdown(response)

        st.session_state.messages.append({"role": "assistant", "content": response})
        st.rerun()


# --- SIDEBAR: CONTROLS ---
st.sidebar.header("⚙️ LSP Data Feed")
source_option = st.sidebar.radio("Mode:", ("🔌 Live WMS Database", "📂 Sandbox (CSV)"))

st.sidebar.markdown("---")

# 1. LIVE DATABASE CONTROLS
selected_sku = None

if source_option == "🔌 Live WMS Database":
    # A. SINGLE ENTRY
    st.sidebar.subheader("📝 Log Service Lane")
    with st.sidebar.expander("Add Flow Record", expanded=False):
        with st.form("entry_form"):
            new_product = st.text_input("Service Lane ID (e.g. BER-MUC)", value="Route A")
            new_date = st.date_input("Date", value=date.today())
            new_demand = st.number_input("Volume (Pallets)", min_value=1, value=100)

            if st.form_submit_button("💾 Save to Cloud"):
                if db_manager.add_record(new_date, new_product, new_demand):
                    st.success("Log Updated!")
                    st.rerun()

    # B. DELETE RECORD
    with st.sidebar.expander("🗑️ Correction (Delete ID)"):
        del_id = st.number_input("Record ID", min_value=1, step=1)
        if st.button("Delete Transaction"):
            success, msg = db_manager.delete_record(del_id)
            if success:
                st.success(f"ID {del_id} Deleted!"); st.rerun()
            else:
                st.error(msg)

    # C. BULK UPLOAD
    with st.sidebar.expander("📂 Bulk Import"):
        upload_csv = st.file_uploader("Upload WMS History", type=["csv"])
        if upload_csv:
            if st.button("🚀 Import"):
                try:
                    bulk_df = pd.read_csv(upload_csv)
                    bulk_df.columns = bulk_df.columns.str.strip().str.lower().str.replace(' ', '_')
                    if {'date', 'product_name', 'demand'}.issubset(bulk_df.columns):
                        success, msg = db_manager.bulk_import_csv(bulk_df)
                        if success: st.success(msg); st.rerun()
                    else:
                        st.error("CSV must have: date, product_name, demand")
                except Exception as e:
                    st.error(f"Error: {e}")

    # D. FILTER
    st.sidebar.markdown("---")
    st.sidebar.header("🔍 Service Lane Selector")
    all_products = db_manager.get_unique_products()
    if all_products:
        selected_sku = st.sidebar.selectbox("Select Lane:", all_products)
    else:
        st.sidebar.caption("No data in WMS.")

    # E. DANGER ZONE
    st.sidebar.markdown("---")
    with st.sidebar.expander("⚠️ System Admin"):
        if st.button("🧨 Reset Database"):
            if db_manager.reset_database(): st.success("Reset Complete"); st.rerun()

st.sidebar.markdown("---")

# 2. PARAMETERS (LSP Operations)
st.sidebar.header("🔧 LSP Constraints")

# Rebranding Costs for Service Context
holding_cost = st.sidebar.number_input("Warehousing Cost ($/pallet)", value=config.HOLDING_COST)
stockout_cost = st.sidebar.number_input("SLA Penalty Cost ($/pallet)", value=config.STOCKOUT_COST)

st.sidebar.subheader("📉 Volatility Factors")
lead_time_months = st.sidebar.slider("Lead Time (Months)", 0.5, 6.0, 1.0, 0.5)
lead_time_volatility = st.sidebar.slider("Supply Variance (σ_LT)", 0.0, 2.0, 0.2, 0.1)

# Reverse Logistics Logic
return_rate = st.sidebar.slider("Return Rate % (Reverse Logistics)", 0, 30, 5, 1,
                                help="Impact of E-commerce Returns on Capacity")

# Horizontal Cooperation Logic
st.sidebar.subheader("🤝 Horizontal Cooperation")
warehouse_cap = st.sidebar.number_input("Internal Capacity Limit", value=150)
partner_cost = st.sidebar.number_input("Partner Surcharge ($)", value=5.0,
                                       help="Cost premium to outsource to competitor")

sim_sla = st.sidebar.slider("Target Service Level (%)", 50, 99, 95, 1)

st.sidebar.markdown("---")
st.sidebar.caption("🟢 LSP Digital Twin | v3.0.0 Production")

# --- ACADEMIC LABELING ---
st.sidebar.info(
    """
    **LSP Optimization Engine**

    *Research Modules:*
    * 🔄 **Reverse Logistics Load**
    * 🤝 **Horizontal Capacity Sharing**
    * 📉 **Newsvendor Risk Model**
    """
)

# --- MAIN PAGE ---
st.title("🚛 LSP Digital Capacity Twin")

# LOAD DATA
df = None
if source_option == "🔌 Live WMS Database":
    df = db_manager.load_data(selected_sku)
else:
    st.info("Sandbox Mode: Upload a CSV to simulate flows.")
    uploaded_file = st.file_uploader("Upload CSV", type=["csv"], key="sandbox")
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        df.columns = df.columns.str.strip().str.lower()
        if 'date' in df.columns: df['date'] = pd.to_datetime(df['date'])

# EXECUTIVE SUMMARY
if source_option == "🔌 Live WMS Database":
    with st.expander("🚁 Network Command Center", expanded=False):
        full_df = db_manager.load_data(None)
        if full_df is not None and not full_df.empty:
            summary_data = []
            for p in full_df['product_name'].unique():
                p_data = full_df[full_df['product_name'] == p]
                if not p_data.empty:
                    last = p_data.iloc[-1]
                    avg = p_data['demand'].mean()
                    status = "🟢 Optimized"
                    if last['demand'] > avg * 1.5:
                        status = "🔴 Capacity Strain"
                    elif last['demand'] < avg * 0.5:
                        status = "🟡 Underutilized"
                    summary_data.append({"Service Lane": p, "Latest Vol": int(last['demand']), "Status": status})
            st.dataframe(pd.DataFrame(summary_data), use_container_width=True, hide_index=True)
    st.divider()

# ANALYSIS TABS
if df is not None and not df.empty:

    # 1. BASE DEMAND CALCULATION
    raw_avg_demand = df['demand'].mean()

    # Impact of Returns on Workload
    # In LSPs, returns = MORE work (handling/storage), not less.
    reverse_logistics_vol = raw_avg_demand * (return_rate / 100.0)
    total_workload = raw_avg_demand + reverse_logistics_vol

    std_dev_demand = df['demand'].std() if len(df) > 1 else 0

    # 2. SAFETY STOCK CALCULATION (Using Total Workload)
    actual_sla = inventory_math.calculate_newsvendor_target(holding_cost, stockout_cost)
    sim_safety_stock = inventory_math.calculate_advanced_safety_stock(
        total_workload, std_dev_demand, lead_time_months, lead_time_volatility, sim_sla / 100.0
    )

    # 3. CAPACITY SHARING LOGIC
    total_required_capacity = total_workload + sim_safety_stock
    capacity_overflow = max(0, total_required_capacity - warehouse_cap)
    outsourced_vol = capacity_overflow
    internal_vol = total_required_capacity - outsourced_vol

    # Costs
    internal_cost = internal_vol * holding_cost
    cooperation_cost = outsourced_vol * (holding_cost + partner_cost)  # Base + Surcharge
    total_holding_cost = internal_cost + cooperation_cost

    metrics = {
        "avg_demand": int(total_workload),
        "std_dev": int(std_dev_demand),
        "lead_time": lead_time_months,
        "safety_stock": int(sim_safety_stock),
        "sla": sim_sla / 100.0,
        "product_name": selected_sku if selected_sku else "Aggregate",
        "return_vol": int(reverse_logistics_vol),
        "outsourced": int(outsourced_vol)
    }

    # Service Logic Integration
    try:
        service_metrics = inventory_math.calculate_service_implications(
            metrics["avg_demand"], metrics["std_dev"], metrics["sla"], stockout_cost
        )
        metrics.update(service_metrics)
    except:
        metrics.update({"reliability_score": "N/A", "penalty_cost": "N/A"})

    if source_option == "🔌 Live WMS Database" and not selected_sku:
        st.warning("Please select a Service Lane.")
    else:
        # TABS
        tab1, tab2 = st.tabs(["📊 Capacity & Cooperation Hub", "💰 Profit & Risk Engine"])

        # --- TAB 1: LOGISTICS HUB ---
        with tab1:
            st.subheader(f"Operations Analysis: {metrics['product_name']}")

            # Forecast Logic
            f_df = None
            forecast_text = ""
            if st.checkbox("Show Demand Forecast", value=True):
                f_df = forecast.generate_forecast(df)
                if f_df is not None:
                    forecast_text = f"Projected demand trend: {f_df.head(5)['demand'].tolist()}"

            # Chart
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=df['date'], y=df['demand'], mode='lines+markers', name='Outbound Flow',
                                     line=dict(color='#2ca02c', width=3)))

            # Visual: Show Capacity Ceiling
            fig.add_hline(y=warehouse_cap, line_dash="dot", line_color="red", annotation_text="Internal Capacity Limit")

            if f_df is not None:
                last_pt = pd.DataFrame({'date': [df['date'].max()], 'demand': [df.iloc[-1]['demand']]})
                combined_f = pd.concat([last_pt, f_df])
                fig.add_trace(go.Scatter(x=combined_f['date'], y=combined_f['demand'], mode='lines', name='Forecast',
                                         line=dict(dash='dash', color='blue')))

            st.plotly_chart(fig, use_container_width=True)

            # METRICS ROW 1: Operations
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Total Throughput", f"{int(total_workload)}", f"+{int(reverse_logistics_vol)} Returns")
            c2.metric("Reliability Score", f"{metrics.get('reliability_score', 'N/A')}%")

            # Metric: Horizontal Cooperation
            if outsourced_vol > 0:
                c3.metric("⚠️ Cooperation Triggered", f"{int(outsourced_vol)} Units", "Outsourced to Partner",
                          delta_color="inverse")
            else:
                c3.metric("Capacity Status", "Optimal", "Fully Internal")

            c4.metric("Safety Buffer", f"{metrics['safety_stock']}", "Pallets")

            # AI Context
            ai_context = f"""
            Analysis for Logistics Service Provider.
            - Total Load: {total_workload} (Includes {reverse_logistics_vol} from Returns).
            - Warehouse Cap: {warehouse_cap}. 
            - Outsourced Volume: {outsourced_vol} (Horizontal Cooperation).
            - Forecast: {forecast_text}
            """
            render_chat_ui(df, metrics, extra_context=ai_context, key="ops_chat")

        # --- TAB 2: FINANCIAL ENGINE ---
        with tab2:
            st.subheader("💰 Financial Optimization")

            c_input1, c_input2 = st.columns(2)
            uc = c_input1.number_input("Handling Cost ($)", 50.0)
            sp = c_input2.number_input("Service Revenue ($)", 85.0)

            if sp > uc:
                # 1. Cost Curve
                st.markdown("#### 📉 Cost-Service Convexity")
                try:
                    st.plotly_chart(profit_optimizer.plot_cost_tradeoff(
                        total_workload, std_dev_demand, holding_cost, stockout_cost, uc, sp
                    ), use_container_width=True)
                except:
                    st.warning("Update profit_optimizer.py for charts")

                # 2. Heatmap
                st.markdown("#### 🗺️ Risk Sensitivity")
                st.plotly_chart(profit_optimizer.calculate_profit_scenarios(
                    total_workload, std_dev_demand, holding_cost, stockout_cost, uc, sp
                ), use_container_width=True)

                # Context
                margin = sp - uc
                optimal_sla_math = margin / (margin + holding_cost)

                profit_context = f"""
                FINANCIALS:
                - Optimal Service Level: {optimal_sla_math:.1%}.
                - Impact of Returns: Added {reverse_logistics_vol} units to cost basis.
                - Cooperation Surcharges: ${outsourced_vol * partner_cost} extra cost due to capacity overflow.
                """

                st.info(f"💡 Optimal SLA for Max Margin: **{optimal_sla_math * 100:.1f}%**")
                render_chat_ui(df, metrics, extra_context=profit_context, key="fin_chat")
            else:
                st.error("Revenue must exceed Cost.")

# --- FOOTER ---
st.markdown("---")
st.caption(f"© 2026 Logistics Research Lab | v3.0.0 | Horizontal Cooperation Module Active")

if source_option == "🔌 Live WMS Database" and df is not None:
    with st.expander("🔍 Inspect Warehouse Logs"):
        st.dataframe(df, use_container_width=True)