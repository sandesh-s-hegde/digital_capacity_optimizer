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

    if "messages" not in st.session_state: st.session_state.messages = []

    chat_container = st.container(height=400, border=True)

    with chat_container:
        for msg in st.session_state.messages:
            st.chat_message(msg["role"]).markdown(msg["content"])

    if prompt := st.chat_input("Ask about capacity sharing, risk, or profit...", key=key):
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

# Financials
st.sidebar.subheader("💰 Unit Economics")
uc = st.sidebar.number_input("Handling Cost ($)", value=50.0)
sp = st.sidebar.number_input("Service Revenue ($)", value=85.0)

# --- NEW: STRESS TEST MODULE ---
st.sidebar.subheader("🌪️ Risk Simulation")
disruption_mode = st.sidebar.checkbox("🔥 Simulate Supplier Shock",
                                      help="Simulates a port strike: Doubles Lead Time & Variance.")

if disruption_mode:
    st.sidebar.error("⚠️ SHOCK EVENT ACTIVE")
    # Force high values during shock
    holding_cost = st.sidebar.number_input("Warehousing Cost ($/pallet)", value=config.HOLDING_COST)
    stockout_cost = st.sidebar.number_input("SLA Penalty Cost ($/pallet)", value=config.STOCKOUT_COST)

    # Visual feedback only - logic uses multipliers below
    st.sidebar.slider("Lead Time (Months)", 0.5, 6.0, 3.0, disabled=True)
    st.sidebar.slider("Supply Variance (σ_LT)", 0.0, 2.0, 1.5, disabled=True)

    # The actual values passed to the math engine
    lead_time_months = 3.0
    lead_time_volatility = 1.5

else:
    # Normal Mode
    holding_cost = st.sidebar.number_input("Warehousing Cost ($/pallet)", value=config.HOLDING_COST)
    stockout_cost = st.sidebar.number_input("SLA Penalty Cost ($/pallet)", value=config.STOCKOUT_COST)
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
st.sidebar.caption("🟢 LSP Digital Twin | v3.1.0 Resilience Module")

# --- ACADEMIC LABELING ---
st.sidebar.info(
    """
    **LSP Optimization Engine**

    *Research Modules:*
    * 🌪️ **Disruption Simulation**
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
    reverse_logistics_vol = raw_avg_demand * (return_rate / 100.0)
    total_workload = raw_avg_demand + reverse_logistics_vol
    std_dev_demand = df['demand'].std() if len(df) > 1 else 0

    # 2. SAFETY STOCK CALCULATION
    actual_sla = inventory_math.calculate_newsvendor_target(holding_cost, stockout_cost)
    sim_safety_stock = inventory_math.calculate_advanced_safety_stock(
        total_workload, std_dev_demand, lead_time_months, lead_time_volatility, sim_sla / 100.0
    )

    # 3. CAPACITY SHARING LOGIC
    total_required_capacity = total_workload + sim_safety_stock
    cooperation_metrics = inventory_math.calculate_horizontal_sharing(
        total_required_capacity, warehouse_cap, partner_cost, holding_cost
    )
    outsourced_vol = cooperation_metrics["overflow_vol"]
    dependency_pct = cooperation_metrics["dependency_ratio"]

    # 4. RESILIENCE
    combined_volatility_est = (lead_time_months * (std_dev_demand ** 2) + (raw_avg_demand ** 2) * (
                lead_time_volatility ** 2)) ** 0.5
    resilience_score = inventory_math.calculate_resilience_score(
        sim_safety_stock, combined_volatility_est, dependency_pct
    )

    metrics = {
        "avg_demand": int(total_workload),
        "std_dev": int(std_dev_demand),
        "lead_time": lead_time_months,
        "safety_stock": int(sim_safety_stock),
        "sla": sim_sla / 100.0,
        "product_name": selected_sku if selected_sku else "Aggregate",
        "return_vol": int(reverse_logistics_vol),
        "outsourced": int(outsourced_vol),
        "resilience_score": resilience_score,
        "dependency_ratio": dependency_pct,
        "lead_time_risk": lead_time_volatility,
        "unit_cost": uc,
        "selling_price": sp,
        "holding_cost": holding_cost,
        "stockout_cost": stockout_cost
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

            # Forecast
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
            fig.add_hline(y=warehouse_cap, line_dash="dot", line_color="red", annotation_text="Internal Capacity Limit")

            if f_df is not None:
                last_pt = pd.DataFrame({'date': [df['date'].max()], 'demand': [df.iloc[-1]['demand']]})
                combined_f = pd.concat([last_pt, f_df])
                fig.add_trace(go.Scatter(x=combined_f['date'], y=combined_f['demand'], mode='lines', name='Forecast',
                                         line=dict(dash='dash', color='blue')))

            st.plotly_chart(fig, use_container_width=True)

            # Metrics
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Total Throughput", f"{int(total_workload)}", f"+{int(reverse_logistics_vol)} Returns")

            # Conditional Color for Resilience
            res_delta = "off"
            if metrics['resilience_score'] < 50: res_delta = "- Critical Vulnerability"
            c2.metric("Network Resilience", f"{metrics['resilience_score']}/100",
                      res_delta if disruption_mode else "Risk Robustness")

            if outsourced_vol > 0:
                c3.metric("⚠️ Partner Dependency", f"{metrics['dependency_ratio']}%",
                          f"{int(outsourced_vol)} Outsourced", delta_color="inverse")
            else:
                c3.metric("Capacity Status", "Optimal", "100% Internal")

            # Safety Stock Highlight in Shock Mode
            c4.metric("Safety Buffer", f"{metrics['safety_stock']}", "Pallets",
                      delta="Surge!" if disruption_mode else None)

            # PDF Report
            st.divider()
            col_pdf1, col_pdf2 = st.columns([1, 4])
            with col_pdf1:
                if st.button("📄 Generate Research Report"):
                    with st.spinner("Compiling Resilience & Cooperation Data..."):
                        summary = ai_brain.chat_with_data(
                            f"Write a strategic executive summary for service lane {metrics['product_name']}. Focus on resilience and capacity sharing.",
                            [], df, metrics
                        )
                        pdf_bytes = report_gen.generate_pdf(metrics, summary)
                        st.download_button(
                            label="⬇️ Download PDF Artifact",
                            data=pdf_bytes,
                            file_name=f"LSP_Resilience_Report_{metrics['product_name']}.pdf",
                            mime="application/pdf"
                        )

            ai_context = f"Analysis for Logistics Service Provider. Total Load: {total_workload}. Warehouse Cap: {warehouse_cap}. Forecast: {forecast_text}. SHOCK MODE: {disruption_mode}"
            render_chat_ui(df, metrics, extra_context=ai_context, key="ops_chat")

        # --- TAB 2: FINANCIAL ENGINE ---
        with tab2:
            st.subheader("💰 Financial Optimization")

            if sp > uc:
                st.markdown("#### 📉 Cost-Service Convexity")
                try:
                    st.plotly_chart(profit_optimizer.plot_cost_tradeoff(
                        total_workload, std_dev_demand, holding_cost, stockout_cost, uc, sp
                    ), use_container_width=True)
                except:
                    st.warning("Update profit_optimizer.py for charts")

                st.markdown("#### 🗺️ Risk Sensitivity")
                st.plotly_chart(profit_optimizer.calculate_profit_scenarios(
                    total_workload, std_dev_demand, holding_cost, stockout_cost, uc, sp
                ), use_container_width=True)

                st.info(f"💡 The AI Analyst can now explain these charts directly.")
                render_chat_ui(df, metrics, extra_context="User is looking at Profit Heatmaps.", key="fin_chat")
            else:
                st.error("Revenue must exceed Cost.")

# --- FOOTER ---
st.markdown("---")
st.caption(f"© 2026 Logistics Research Lab | v3.1.0 | Stress Test Module Active")

if source_option == "🔌 Live WMS Database" and df is not None:
    with st.expander("🔍 Inspect Warehouse Logs"):
        st.dataframe(df, use_container_width=True)