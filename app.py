import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import date
from dotenv import load_dotenv

# --- IMPORT CUSTOM LOGIC MODULES ---
import config
import db_manager
import inventory_math
import ai_brain
import report_gen
import forecast
import profit_optimizer
import map_viz  # Handles the Geospatial Map
import monte_carlo  # Handles the Stochastic Risk Simulation

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

    if prompt := st.chat_input("Ask about Modal Shift, CO2, or Risk...", key=key):
        st.session_state.messages.append({"role": "user", "content": prompt})

        with chat_container:
            st.chat_message("user").markdown(prompt)

            with st.spinner("Simulating Multi-Modal Network..."):
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

# --- MULTI-MODAL SELECTOR (v3.5) ---
st.sidebar.subheader("🚚 Transport Mode")
transport_mode = st.sidebar.selectbox(
    "Select Mode:",
    ["Road (Standard)", "Rail (Green/Slow)", "Air (Express/Costly)"]
)

# Mode Logic Multipliers (The "Trade-offs")
time_mult = 1.0
cost_mult = 1.0
co2_mult = 1.0

if "Rail" in transport_mode:
    time_mult = 1.5  # Rail is Slower
    cost_mult = 0.7  # Rail is Cheaper
    co2_mult = 0.3  # Rail is Greener
elif "Air" in transport_mode:
    time_mult = 0.2  # Air is Fast
    cost_mult = 3.0  # Air is Expensive
    co2_mult = 5.0  # Air is Dirty
# ----------------------------------------

# Financials
st.sidebar.subheader("💰 Unit Economics")
base_uc = st.sidebar.number_input("Base Handling Cost ($)", value=50.0)
uc = base_uc * cost_mult  # Apply Mode Multiplier to Cost
sp = st.sidebar.number_input("Service Revenue ($)", value=85.0)

# --- STRESS TEST MODULE ---
st.sidebar.subheader("🌪️ Risk Simulation")
disruption_mode = st.sidebar.checkbox("🔥 Simulate Supplier Shock",
                                      help="Simulates a port strike: Doubles Lead Time & Variance.")

if disruption_mode:
    st.sidebar.error("⚠️ SHOCK EVENT ACTIVE")
    # Shock overrides Mode logic slightly (everything gets worse)
    lead_time_months = 3.0 * time_mult
    lead_time_volatility = 1.5
    holding_cost = config.HOLDING_COST * 1.5  # Costs rise during shock

else:
    # Normal Mode
    holding_cost = st.sidebar.number_input("Warehousing Cost ($/pallet)", value=config.HOLDING_COST)
    base_lt = st.sidebar.slider("Base Lead Time (Months)", 0.5, 6.0, 1.0, 0.5)

    # Apply Mode Multiplier to Time
    lead_time_months = base_lt * time_mult

    lead_time_volatility = st.sidebar.slider("Supply Variance (σ_LT)", 0.0, 2.0, 0.2, 0.1)

stockout_cost = st.sidebar.number_input("SLA Penalty Cost ($/pallet)", value=config.STOCKOUT_COST)

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
st.sidebar.caption("🟢 LSP Digital Twin | v3.5.0 Multi-Modal Edition")

# --- ACADEMIC LABELING ---
st.sidebar.info(
    f"""
    **Current Strategy: {transport_mode}**
    * Lead Time Factor: x{time_mult}
    * Cost Factor: x{cost_mult}
    * CO2 Factor: x{co2_mult}

    **Research Modules:**
    * 🎲 Monte Carlo Risk
    * 📍 Geospatial Control
    * 🌿 Green Logistics
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
    internal_vol = cooperation_metrics["internal_vol"]
    dependency_pct = cooperation_metrics["dependency_ratio"]

    # 4. RESILIENCE
    combined_volatility_est = (lead_time_months * (std_dev_demand ** 2) + (raw_avg_demand ** 2) * (
                lead_time_volatility ** 2)) ** 0.5
    resilience_score = inventory_math.calculate_resilience_score(
        sim_safety_stock, combined_volatility_est, dependency_pct
    )

    # 5. SERVICE & LOYALTY
    try:
        service_metrics = inventory_math.calculate_service_implications(
            total_workload, std_dev_demand, sim_sla / 100.0, stockout_cost
        )
    except:
        service_metrics = {"reliability_score": 100, "penalty_cost": 0}

    loyalty_score = inventory_math.calculate_loyalty_index(sim_sla / 100.0, service_metrics["reliability_score"])

    # 6. GREEN LOGISTICS (Applied Mode Multiplier)
    green_metrics = inventory_math.calculate_sustainability_impact(internal_vol, outsourced_vol)
    # Apply Mode Multiplier to CO2
    green_metrics["total_emissions"] = round(green_metrics["total_emissions"] * co2_mult, 2)
    green_metrics["co2_saved"] = round(green_metrics["co2_saved"] * co2_mult, 2)

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
        "stockout_cost": stockout_cost,
        "loyalty_score": loyalty_score,
        "co2_emissions": green_metrics["total_emissions"],
        "co2_saved": green_metrics["co2_saved"],
        "transport_mode": transport_mode  # Passed for AI context
    }
    metrics.update(service_metrics)

    if source_option == "🔌 Live WMS Database" and not selected_sku:
        st.warning("Please select a Service Lane.")
    else:
        # TABS
        tab1, tab2 = st.tabs(["📊 Capacity & Cooperation Hub", "💰 Profit & Risk Engine"])

        # --- TAB 1: LOGISTICS HUB ---
        with tab1:
            st.subheader(f"Operations: {metrics['product_name']} | Mode: {transport_mode}")

            # --- MAP VISUALIZATION ---
            with st.container(border=True):
                # Pass Mode to Map Viz
                map_fig = map_viz.render_map(
                    metrics['product_name'],
                    is_disrupted=disruption_mode,
                    outsourced_vol=metrics['outsourced'],
                    transport_mode=transport_mode
                )
                if map_fig:
                    st.plotly_chart(map_fig, use_container_width=True)
                else:
                    st.info("🗺️ Select a valid Route (e.g., BER-MUC) to visualize network topology.")
            # -------------------------

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

            # KPI ROW 1
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Total Throughput", f"{int(total_workload)}", f"+{int(reverse_logistics_vol)} Returns")

            res_delta = "off"
            if metrics['resilience_score'] < 50: res_delta = "- Critical Vulnerability"
            c2.metric("Network Resilience", f"{metrics['resilience_score']}/100",
                      res_delta if disruption_mode else "Risk Robustness",
                      delta_color="normal" if metrics['resilience_score'] > 50 else "inverse")

            if outsourced_vol > 0:
                c3.metric("⚠️ Partner Dependency", f"{metrics['dependency_ratio']}%",
                          f"{int(outsourced_vol)} Outsourced", delta_color="inverse")
            else:
                c3.metric("Capacity Status", "Optimal", "100% Internal")

            delta_msg = "Surge!" if disruption_mode else "Pallets"
            delta_col = "inverse" if disruption_mode else "off"
            c4.metric("Safety Buffer", f"{metrics['safety_stock']}", delta=delta_msg, delta_color=delta_col)

            st.divider()

            # --- STRATEGIC SCORECARD (ROW 2) ---
            st.markdown("#### 🌍 Strategic Scorecard (Triple Bottom Line)")
            k1, k2, k3, k4 = st.columns(4)

            # Green Logic Visuals
            green_label = "Standard"
            if "Rail" in transport_mode:
                green_label = "Eco-Mode"
            elif "Air" in transport_mode:
                green_label = "High Carbon"

            k1.metric("🌿 Sustainability", green_label, f"{green_metrics['total_emissions']} kg CO₂ (Est.)",
                      delta_color="inverse" if "Air" in transport_mode else "normal")
            k2.metric("CO₂ Saved (vs Road)", f"{green_metrics['co2_saved']} kg", "Mode Shift Impact")

            loyalty_delta = f"Goal Exceeded (+{round(service_metrics['reliability_score'] - sim_sla, 1)}%)" if \
            service_metrics['reliability_score'] >= sim_sla else "SLA Breach"
            k3.metric("❤️ Customer Loyalty", f"{loyalty_score}/100", loyalty_delta)

            k4.metric("Reliability (Fill Rate)", f"{service_metrics['reliability_score']}%", f"Target: {sim_sla}%")
            # ---------------------------------------------

            st.divider()
            col_pdf1, col_pdf2 = st.columns([1, 4])
            with col_pdf1:
                if st.button("📄 Generate Research Report"):
                    with st.spinner("Compiling Resilience & Cooperation Data..."):
                        # UPDATED PROMPT: Explicitly asks for Recommendations
                        prompt = f"""
                                    Analyze the service lane {metrics['product_name']} operating under {metrics['transport_mode']} mode.

                                    Structure your response into two distinct sections:
                                    1. **Executive Analysis**: Summarize the resilience score ({metrics['resilience_score']}/100), dependency ratio, and carbon footprint.
                                    2. **Strategic Recommendations**: Provide 3 specific, actionable bullet points on how to improve profitability or reduce risk based on these metrics.
                                    """

                        summary = ai_brain.chat_with_data(prompt, [], df, metrics)

                        pdf_bytes = report_gen.generate_pdf(metrics, summary)
                        st.download_button(
                            label="⬇️ Download PDF Artifact",
                            data=pdf_bytes,
                            file_name=f"LSP_Report_{metrics['product_name']}.pdf",
                            mime="application/pdf"
                        )

            ai_context = f"Analysis for LSP. Total Load: {total_workload}. Warehouse Cap: {warehouse_cap}. Mode: {transport_mode}. CO2: {green_metrics['total_emissions']}. Loyalty: {loyalty_score}. SHOCK: {disruption_mode}"
            render_chat_ui(df, metrics, extra_context=ai_context, key="ops_chat")

        # --- TAB 2: FINANCIAL ENGINE ---
        with tab2:
            st.subheader("💰 Financial Optimization")

            if sp > uc:
                # 1. Deterministic Charts
                c_chart1, c_chart2 = st.columns(2)
                with c_chart1:
                    st.markdown("#### 📉 Cost Convexity")
                    st.plotly_chart(profit_optimizer.plot_cost_tradeoff(
                        total_workload, std_dev_demand, holding_cost, stockout_cost, uc, sp
                    ), use_container_width=True)
                with c_chart2:
                    st.markdown("#### 🗺️ Risk Heatmap")
                    st.plotly_chart(profit_optimizer.calculate_profit_scenarios(
                        total_workload, std_dev_demand, holding_cost, stockout_cost, uc, sp
                    ), use_container_width=True)

                st.divider()

                # 2. Monte Carlo Simulation (Stochastic)
                st.markdown("### 🎲 Monte Carlo Risk Engine")
                st.caption(
                    f"Running 1,000 stochastic iterations based on Demand σ={metrics['std_dev']} and Lead Time σ_LT={lead_time_volatility}")

                # Run Simulation
                sim_fig, sim_metrics = monte_carlo.run_simulation(
                    avg_demand=total_workload,
                    std_dev=std_dev_demand,
                    capacity_limit=total_required_capacity,
                    unit_cost=uc,
                    selling_price=sp,
                    holding_cost=holding_cost,
                    stockout_cost=stockout_cost
                )

                m1, m2, m3 = st.columns(3)
                m1.metric("Expected Profit (Mean)", f"${sim_metrics['avg_profit']}", "Avg Outcome")
                m2.metric("Loss Probability", f"{sim_metrics['loss_prob']}%", "Chance of $ < 0", delta_color="inverse")
                m3.metric("Value at Risk (VaR 95%)", f"${sim_metrics['var_95']}", "Worst Case Scenario",
                          delta_color="off")

                st.plotly_chart(sim_fig, use_container_width=True)

                render_chat_ui(df, metrics,
                               extra_context=f"Monte Carlo Results: Avg Profit ${sim_metrics['avg_profit']}, VaR ${sim_metrics['var_95']}",
                               key="fin_chat")
            else:
                st.error("Revenue must exceed Cost.")

# --- FOOTER ---
st.markdown("---")
st.caption(f"© 2026 Logistics Research Lab | v3.5.0 | Multi-Modal Strategic Edition")

if source_option == "🔌 Live WMS Database" and df is not None:
    with st.expander("🔍 Inspect Warehouse Logs"):
        st.dataframe(df, use_container_width=True)