import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from datetime import date
from dotenv import load_dotenv
from scipy.stats import norm

# --- IMPORT CUSTOM LOGIC MODULES ---
import config
import db_manager
import inventory_math
import ai_brain
import report_gen
import forecast
import profit_optimizer
import map_viz
import monte_carlo
import network_design

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

    if prompt := st.chat_input("Ask about Modal Shift, Cost Trade-offs, or Risk...", key=key):
        st.session_state.messages.append({"role": "user", "content": prompt})

        with chat_container:
            st.chat_message("user").markdown(prompt)

            with st.spinner("Simulating Network Strategy..."):
                full_query = f"{prompt}\n\n[CONTEXT OVERRIDE: {extra_context}]"
                history = [{"role": m["role"], "parts": [m["content"]]} for m in st.session_state.messages]
                response = ai_brain.chat_with_data(full_query, history, df, metrics)

            st.chat_message("assistant").markdown(response)

        st.session_state.messages.append({"role": "assistant", "content": response})
        st.rerun()


# --- HELPER: RESEARCH LAB RENDERER ---
def render_research_lab(avg_demand, std_dev, initial_margin, holding_cost, current_ss_default):
    st.subheader("🔬 Research Laboratory: Stochastic Stress Test")
    st.markdown("""
    **Methodology:** Monte Carlo simulation (N=10,000) to quantify the trade-off between **Profit Maximization** and **Loss Predictability**.
    """)

    col1, col2, col3 = st.columns(3)
    with col1:
        current_ss = st.number_input("Current Safety Stock (Units)", value=int(current_ss_default))
    with col2:
        sim_days = st.slider("Simulation Horizon", 1000, 10000, 5000)
    with col3:
        margin = st.number_input("Unit Margin ($)", value=float(initial_margin), step=1.0, format="%.2f",
                                 help="Selling Price - Unit Cost")

    if "sim_results" not in st.session_state:
        st.session_state.sim_results = None

    if st.button("🚀 Run Risk/Reward Analysis", type="primary"):
        with st.spinner(f"Simulating {sim_days} operational days..."):
            critical_ratio = margin / (margin + holding_cost)
            z_score = norm.ppf(critical_ratio)
            optimal_ss = max(0, z_score * std_dev)

            np.random.seed(42)
            demands = np.random.normal(avg_demand, std_dev, sim_days)

            cap_A = avg_demand + current_ss
            profit_A = []

            cap_B = avg_demand + optimal_ss
            profit_B = []

            for d in demands:
                sales_a = min(d, cap_A)
                loss_a = max(0, cap_A - d) * holding_cost
                profit_A.append((sales_a * margin) - loss_a)

                sales_b = min(d, cap_B)
                loss_b = max(0, cap_B - d) * holding_cost
                profit_B.append((sales_b * margin) - loss_b)

            st.session_state.sim_results = {
                "profit_A": profit_A, "profit_B": profit_B,
                "optimal_ss": optimal_ss, "current_ss": current_ss, "margin": margin
            }

    if st.session_state.sim_results:
        res = st.session_state.sim_results
        pA, pB = np.array(res["profit_A"]), np.array(res["profit_B"])
        opt_ss, curr_ss = res["optimal_ss"], res["current_ss"]

        avg_A, avg_B = np.mean(pA), np.mean(pB)
        delta = avg_B - avg_A
        loss_prob_B = np.mean(pB < 0) * 100
        var_95_B = np.percentile(pB, 5)

        st.divider()
        k1, k2, k3 = st.columns(3)
        k1.metric("Optimal Safety Stock", f"{int(opt_ss)} Units", f"vs Current {curr_ss}")
        k2.metric("Daily Net Profit", f"${avg_B:,.2f}", f"{delta:,.2f} vs Current")
        k3.metric("Projected Annual Gain", f"${delta * 365:,.0f}", "Capital Release", delta_color="normal")

        r1, r2, r3 = st.columns(3)
        r1.metric("📉 Loss Probability", f"{loss_prob_B:.1f}%", "Downside Risk", delta_color="inverse")
        r2.metric("⚠️ Value at Risk (VaR 95%)", f"${var_95_B:,.0f}", "Worst Case Scenario")
        r3.metric("Risk Profile", "STABLE" if loss_prob_B < 5 else "ELEVATED", "Simulation Rating")

        fig, ax = plt.subplots(figsize=(10, 5))
        ax.hist(pA, bins=50, alpha=0.4, label='Current Strategy', color='gray', density=True)
        ax.hist(pB, bins=50, alpha=0.6, label='Optimal Strategy', color='#004562', density=True)
        ax.axvline(0, color='red', linestyle='--', linewidth=1)
        ax.legend()
        ax.set_title("Profit & Loss Distribution")
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        st.pyplot(fig)


# --- SIDEBAR: CONTROLS ---
st.sidebar.header("⚙️ LSP Data Feed")
source_option = st.sidebar.radio("Mode:", ("🔌 Live WMS Database", "📂 Sandbox (CSV)"))
st.sidebar.markdown("---")

# 1. LIVE DATABASE CONTROLS
selected_sku = None
if source_option == "🔌 Live WMS Database":
    with st.sidebar.expander("📝 Log Service Lane"):
        with st.form("entry_form"):
            new_product = st.text_input("Service Lane ID", value="Route A")
            new_date = st.date_input("Date", value=date.today())
            new_demand = st.number_input("Volume", min_value=1, value=100)
            if st.form_submit_button("💾 Save"):
                if db_manager.add_record(new_date, new_product, new_demand):
                    st.success("Saved!");
                    st.rerun()

    with st.sidebar.expander("🗑️ Correction"):
        del_id = st.number_input("Record ID", min_value=1, step=1)
        if st.button("Delete"):
            success, msg = db_manager.delete_record(del_id)
            if success: st.success("Deleted!"); st.rerun()

    with st.sidebar.expander("📂 Bulk Import"):
        upload_csv = st.file_uploader("Upload CSV", type=["csv"])
        if upload_csv:
            if st.button("🚀 Import"):
                try:
                    bulk_df = pd.read_csv(upload_csv)
                    bulk_df.columns = bulk_df.columns.str.strip().str.lower().str.replace(' ', '_')
                    if {'date', 'product_name', 'demand'}.issubset(bulk_df.columns):
                        success, msg = db_manager.bulk_import_csv(bulk_df)
                        if success: st.success(msg); st.rerun()
                except:
                    st.error("Invalid CSV")

    st.sidebar.header("🔍 Lane Selector")
    all_products = db_manager.get_unique_products()
    selected_sku = st.sidebar.selectbox("Select Lane:", all_products) if all_products else None

    with st.sidebar.expander("🧪 Research Tools"):
        if st.button("🧹 Clear Simulation Cache"):
            st.session_state.sim_results = None
            st.rerun()

    with st.sidebar.expander("⚠️ System Admin"):
        if st.button("🧨 Reset Database"):
            if db_manager.reset_database(): st.success("Reset"); st.rerun()

# --- SYSTEM STATUS CHECK ---
st.sidebar.divider()
st.sidebar.subheader("📡 System Status")

# We use db_manager because the function is defined in that module
conn = db_manager.get_db_connection()

if conn:
    st.sidebar.success("Database: Connected (v16)")
    conn.close()
else:
    st.sidebar.error("Database: Offline")

st.sidebar.markdown("---")
st.sidebar.header("🔧 LSP Constraints")

# --- MULTI-MODAL SELECTOR ---
transport_mode = st.sidebar.selectbox("Select Mode:", ["Road (Standard)", "Rail (Green/Slow)", "Air (Express/Costly)"])

time_mult = 1.0;
cost_mult = 1.0;
co2_mult = 1.0
if "Rail" in transport_mode:
    time_mult = 1.5; cost_mult = 0.7; co2_mult = 0.3
elif "Air" in transport_mode:
    time_mult = 0.2; cost_mult = 3.0; co2_mult = 5.0

# Financials
st.sidebar.subheader("💰 Unit Economics (USD)")
base_uc = st.sidebar.number_input("Base Handling Cost ($)", value=50.0)
uc = base_uc * cost_mult
sp = st.sidebar.number_input("Service Revenue ($)", value=85.0)

# --- STRESS TEST MODULE ---
st.sidebar.subheader("🌪️ Risk Simulation")
disruption_mode = st.sidebar.checkbox("🔥 Simulate Supplier Shock")

if disruption_mode:
    st.sidebar.error("⚠️ SHOCK EVENT ACTIVE")
    lead_time_months = 3.0 * time_mult
    lead_time_volatility = 1.5
    holding_cost = config.HOLDING_COST * 1.5
else:
    holding_cost = st.sidebar.number_input("Warehousing Cost ($)", value=config.HOLDING_COST)
    base_lt = st.sidebar.slider("Base Lead Time (Mo)", 0.5, 6.0, 1.0, 0.5)
    lead_time_months = base_lt * time_mult
    lead_time_volatility = st.sidebar.slider("Supply Variance (σ)", 0.0, 2.0, 0.2, 0.1)

stockout_cost = st.sidebar.number_input("SLA Penalty ($)", value=config.STOCKOUT_COST)
return_rate = st.sidebar.slider("Return Rate %", 0, 30, 5, 1)

st.sidebar.subheader("🤝 Horizontal Cooperation")
warehouse_cap = st.sidebar.number_input("Internal Capacity Limit", value=150)
partner_cost = st.sidebar.number_input("Partner Surcharge ($)", value=5.0)
sim_sla = st.sidebar.slider("Target Service Level (%)", 50, 99, 95, 1)

st.sidebar.markdown("---")
st.sidebar.caption("🟢 LSP Digital Twin | v4.0.0 | System: Frankfurt | Status: Online")

# --- ACADEMIC LABELING ---
st.sidebar.info(
    f"""
    **Current Strategy: {transport_mode}**
    * Lead Time Factor: x{time_mult}
    * Cost Factor: x{cost_mult}
    * CO2 Factor: x{co2_mult}

    **Research Modules:**
    * 🌏 Sourcing Strategy (Global vs Local)
    * 🎲 Monte Carlo Risk
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
    st.info("Sandbox Mode: Upload a CSV.")
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
                        status = "🔴 Strain"
                    elif last['demand'] < avg * 0.5:
                        status = "🟡 Idle"
                    summary_data.append({"Lane": p, "Vol": int(last['demand']), "Status": status})
            st.dataframe(pd.DataFrame(summary_data), use_container_width=True, hide_index=True)
    st.divider()

# ANALYSIS TABS
if df is not None and not df.empty:
    raw_avg_demand = df['demand'].mean()
    reverse_logistics_vol = raw_avg_demand * (return_rate / 100.0)
    total_workload = raw_avg_demand + reverse_logistics_vol
    std_dev_demand = df['demand'].std() if len(df) > 1 else 0

    actual_sla = inventory_math.calculate_newsvendor_target(holding_cost, stockout_cost)
    sim_safety_stock = inventory_math.calculate_advanced_safety_stock(
        total_workload, std_dev_demand, lead_time_months, lead_time_volatility, sim_sla / 100.0
    )

    total_required_capacity = total_workload + sim_safety_stock
    cooperation_metrics = inventory_math.calculate_horizontal_sharing(
        total_required_capacity, warehouse_cap, partner_cost, holding_cost
    )
    outsourced_vol = cooperation_metrics["overflow_vol"]
    internal_vol = cooperation_metrics["internal_vol"]
    dependency_pct = cooperation_metrics["dependency_ratio"]

    combined_volatility_est = (lead_time_months * (std_dev_demand ** 2) + (raw_avg_demand ** 2) * (
                lead_time_volatility ** 2)) ** 0.5
    resilience_score = inventory_math.calculate_resilience_score(sim_safety_stock, combined_volatility_est,
                                                                 dependency_pct)

    try:
        service_metrics = inventory_math.calculate_service_implications(total_workload, std_dev_demand, sim_sla / 100.0,
                                                                        stockout_cost)
    except:
        service_metrics = {"reliability_score": 100, "penalty_cost": 0}

    loyalty_score = inventory_math.calculate_loyalty_index(sim_sla / 100.0, service_metrics["reliability_score"])
    green_metrics = inventory_math.calculate_sustainability_impact(internal_vol, outsourced_vol)
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
        "transport_mode": transport_mode
    }
    metrics.update(service_metrics)

    if source_option == "🔌 Live WMS Database" and not selected_sku:
        st.warning("Please select a Service Lane.")
    else:
        # TAB DEFINITIONS - v3.8.0 (Unified USD)
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["🚀 Control Tower", "📊 Risk Simulation", "🤖 AI Strategist", "📦 Inventory Policy", "🌍 Network Optimizer"])

        # --- TAB 1: OPERATIONS ---
        with tab1:
            st.subheader(f"Operations: {metrics['product_name']} | Mode: {transport_mode}")
            with st.container(border=True):
                map_fig = map_viz.render_map(metrics['product_name'], disruption_mode, outsourced_vol, transport_mode)
                if map_fig:
                    st.plotly_chart(map_fig, use_container_width=True)
                else:
                    st.info("🗺️ Select a valid Route (e.g., BER-MUC)")

            f_df = None
            if st.checkbox("Show Demand Forecast", value=True):
                f_df = forecast.generate_forecast(df)

            fig = go.Figure()
            fig.add_trace(go.Scatter(x=df['date'], y=df['demand'], mode='lines+markers', name='Outbound Flow',
                                     line=dict(color='#2ca02c', width=3)))
            fig.add_hline(y=warehouse_cap, line_dash="dot", line_color="red", annotation_text="Limit")
            if f_df is not None:
                last_pt = pd.DataFrame({'date': [df['date'].max()], 'demand': [df.iloc[-1]['demand']]})
                combined_f = pd.concat([last_pt, f_df])
                fig.add_trace(go.Scatter(x=combined_f['date'], y=combined_f['demand'], mode='lines', name='Forecast',
                                         line=dict(dash='dash', color='blue')))
            st.plotly_chart(fig, use_container_width=True)

            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Throughput", f"{int(total_workload)}", f"+{int(reverse_logistics_vol)} Ret")
            res_delta = "- Critical" if metrics['resilience_score'] < 50 else "Stable"
            c2.metric("Resilience", f"{metrics['resilience_score']}/100", res_delta)
            if outsourced_vol > 0:
                c3.metric("Dependency", f"{metrics['dependency_ratio']}%", f"{int(outsourced_vol)} Outsourced",
                          delta_color="inverse")
            else:
                c3.metric("Capacity", "Optimal", "Internal")
            c4.metric("Safety Stock", f"{metrics['safety_stock']}", "Pallets")

            st.divider()
            k1, k2, k3, k4 = st.columns(4)
            k1.metric("Sustainability", "Standard", f"{green_metrics['total_emissions']} kg CO₂")
            k2.metric("CO₂ Saved", f"{green_metrics['co2_saved']} kg", "vs Baseline")
            k3.metric("Loyalty", f"{loyalty_score}/100", "Index")
            k4.metric("Fill Rate", f"{service_metrics['reliability_score']}%", f"Target: {sim_sla}%")

            st.divider()
            col_pdf1, col_pdf2 = st.columns([1, 4])
            with col_pdf1:
                if st.button("📄 Generate Report"):
                    with st.spinner("Compiling..."):
                        prompt = f"Analyze {metrics['product_name']}. Resilience {metrics['resilience_score']}. Suggest 3 strategic fixes."
                        summary = ai_brain.chat_with_data(prompt, [], df, metrics)
                        pdf_bytes = report_gen.generate_pdf(metrics, summary)
                        st.download_button("⬇️ Download PDF", pdf_bytes, f"Report_{metrics['product_name']}.pdf",
                                           "application/pdf")
            render_chat_ui(df, metrics,
                           extra_context=f"LSP Context: Resilience {metrics['resilience_score']}, Mode {transport_mode}",
                           key="ops_chat")

        # --- TAB 2: FINANCIAL ---
        with tab2:
            st.subheader("💰 Financial Optimization")
            if sp > uc:
                c1, c2 = st.columns(2)
                with c1:
                    st.plotly_chart(
                        profit_optimizer.plot_cost_tradeoff(total_workload, std_dev_demand, holding_cost, stockout_cost,
                                                            uc, sp), use_container_width=True)
                with c2:
                    st.plotly_chart(
                        profit_optimizer.calculate_profit_scenarios(total_workload, std_dev_demand, holding_cost,
                                                                    stockout_cost, uc, sp), use_container_width=True)

                st.divider()
                st.markdown("### 🎲 Monte Carlo Risk Engine")
                sim_fig, sim_metrics = monte_carlo.run_simulation(total_workload, std_dev_demand,
                                                                  total_required_capacity, uc, sp, holding_cost,
                                                                  stockout_cost)
                m1, m2, m3 = st.columns(3)
                m1.metric("Expected Profit", f"${sim_metrics['avg_profit']}", "Mean")
                m2.metric("Loss Probability", f"{sim_metrics['loss_prob']}%", "Risk", delta_color="inverse")
                m3.metric("VaR (95%)", f"${sim_metrics['var_95']}", "Worst Case")
                st.plotly_chart(sim_fig, use_container_width=True)
                render_chat_ui(df, metrics, extra_context=f"Fin Context: Avg Profit ${sim_metrics['avg_profit']}",
                               key="fin_chat")
            else:
                st.error("Revenue must exceed Cost.")

        # --- TAB 3: RESEARCH LAB ---
        with tab3:
            unit_margin = sp - uc
            render_research_lab(total_workload, std_dev_demand, unit_margin, holding_cost, metrics['safety_stock'])
            sim_ctx = ""
            if "sim_results" in st.session_state and st.session_state.sim_results:
                res = st.session_state.sim_results
                sim_ctx = f"Simulation Run: Optimal SS {int(res['optimal_ss'])}, Margin ${res.get('margin', unit_margin)}, Holding ${holding_cost}"
            render_chat_ui(df, metrics, extra_context=sim_ctx, key="research_chat")

        # --- TAB 4: GLOBAL SOURCING (Unified USD + CBAM + Heatmap v5.3) ---
        with tab4:
            st.subheader("🌏 Global Sourcing Strategy (China Plus One)")
            st.markdown(
                "Quantify the impact of **Free Trade Agreements (FTA)** vs. **Green Trade Barriers (CBAM)** on sourcing strategy.")

            # 1. SCENARIO INPUTS
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("### 🏭 Baseline: Domestic/Nearshore")
                eu_price = st.number_input("Unit Price ($)", value=85.0, help="Higher Labor Cost")
                eu_lead = st.number_input("Lead Time (Days)", value=4, help="Fast Trucking")
                eu_co2 = st.number_input("Carbon Footprint (kg CO₂/unit)", value=2.5, help="Cleaner Grid")

            with col2:
                st.markdown("### 🚢 Challenger: India (Offshore)")
                in_price = st.number_input("Offshore Unit Price ($)", value=50.0, help="Arbitrage Advantage")
                in_freight = st.number_input("Freight & Logistics ($)", value=12.0)
                in_lead = st.slider("Offshore Lead Time (Days)", 20, 60, 45)
                in_co2 = st.number_input("Carbon Footprint (kg CO₂/unit)", value=8.0, help="Coal-heavy Grid")

            st.divider()

            # 2. POLICY LEVERS
            st.markdown("#### ⚖️ Policy Levers: The Clash of Tariffs vs. Taxes")
            c_lev1, c_lev2 = st.columns(2)
            with c_lev1:
                tariff = st.slider("Import Tariff (%)", 0, 20, 0, help="0% = Full Free Trade Agreement (FTA)")
            with c_lev2:
                carbon_tax = st.slider("EU Carbon Price ($/tonne)", 0, 200, 85, help="ETS / CBAM Price Forecast")

            # 3. CALCULATIONS
            demand = 15000
            holding_rate = 20

            # Domestic (EU) Calculation
            ets_cost_eu = (eu_co2 / 1000) * carbon_tax
            cost_eu = eu_price + ets_cost_eu
            risk_eu = (eu_lead / 365) * demand * cost_eu * (holding_rate / 100) / demand
            total_eu = cost_eu + risk_eu

            # Offshore (India) Calculation
            duty = in_price * (tariff / 100)
            cbam_cost = (in_co2 / 1000) * carbon_tax

            cost_in = in_price + in_freight + duty + cbam_cost
            risk_in = (in_lead / 365) * demand * cost_in * (holding_rate / 100) / demand
            total_in = cost_in + risk_in

            # 4. VISUALIZATION
            c1, c2, c3 = st.columns(3)
            c1.metric("Domestic Landed Cost", f"${total_eu:.2f}", f"Incl. ${ets_cost_eu:.2f} Carbon Cost")

            delta = total_eu - total_in
            c2.metric("Offshore Landed Cost", f"${total_in:.2f}", f"Incl. ${cbam_cost:.2f} CBAM Tax")

            winner = "Offshore" if delta > 0 else "Domestic"
            c3.metric("Sourcing Advantage", f"${abs(delta):.2f} / unit", f"Winner: {winner}",
                      delta_color="normal" if delta > 0 else "inverse")

            # Stacked Bar Chart
            fig = go.Figure(data=[
                go.Bar(name='Base Price', x=['Domestic', 'Offshore'], y=[eu_price, in_price],
                       marker_color='#2E86C1'),
                go.Bar(name='Freight', x=['Domestic', 'Offshore'], y=[0, in_freight], marker_color='#28B463'),
                go.Bar(name='Tariff (Trade)', x=['Domestic', 'Offshore'], y=[0, duty], marker_color='#E74C3C'),
                go.Bar(name='Carbon Tax (CBAM/ETS)', x=['Domestic', 'Offshore'], y=[ets_cost_eu, cbam_cost],
                       marker_color='#5D6D7E'),
                go.Bar(name='Risk (Inventory)', x=['Domestic', 'Offshore'], y=[risk_eu, risk_in],
                       marker_color='#F1C40F')
            ])
            fig.update_layout(barmode='stack', title="Landed Cost: The Impact of Green Regulations (CBAM)",
                              height=500)
            st.plotly_chart(fig, use_container_width=True)

            # 5. STRATEGIC INSIGHT (FIXED: Escaped Dollar Signs)
            labor_arbitrage = eu_price - in_price
            if delta > 0:
                st.success(
                    f"✅ **Strategy:** Sourcing from India remains profitable despite CBAM. The Labor arbitrage (\${labor_arbitrage:.2f}) is strong enough to absorb the **\${cbam_cost:.2f} Green Tax**.")
            else:
                st.error(
                    f"⚠️ **Strategy:** Reshore to Europe. The combined weight of **Logistics Risk** and **CBAM Tax** wipes out the manufacturing savings.")

            # 6. SENSITIVITY HEATMAP
            st.divider()
            st.subheader("🎛️ Strategic Robustness: The Sensitivity Matrix")
            st.markdown(
                "Identify the **'Tipping Point'**. At what combination of **Carbon Tax** and **Freight Cost** does the India advantage disappear?")

            with st.expander("🛠️ Configure Sensitivity Parameters", expanded=False):
                s1, s2 = st.columns(2)
                with s1:
                    max_freight = st.slider("Max Freight Scenario ($)", 10.0, 50.0, 25.0)
                with s2:
                    max_carbon = st.slider("Max Carbon Price ($/ton)", 50, 300, 200)

            if st.button("🔄 Run Sensitivity Heatmap"):
                with st.spinner("Calculating 400 strategic scenarios..."):
                    # Generate ranges
                    freight_range = np.linspace(5.0, max_freight, 20)  # Y-Axis
                    carbon_range = np.linspace(0, max_carbon, 20)  # X-Axis

                    z_values = []  # Profit Delta (Positive = India Wins, Negative = EU Wins)

                    for f in freight_range:
                        row = []
                        for c in carbon_range:
                            # Re-calculate costs dynamically

                            # 1. EU Cost (Domestic)
                            cost_eu_loop = eu_price + ((eu_co2 / 1000) * c)
                            risk_eu_loop = (eu_lead / 365) * demand * cost_eu_loop * (holding_rate / 100) / demand
                            total_eu_loop = cost_eu_loop + risk_eu_loop

                            # 2. India Cost (Offshore)
                            duty_loop = in_price * (tariff / 100)
                            cbam_loop = (in_co2 / 1000) * c

                            cost_in_loop = in_price + f + duty_loop + cbam_loop
                            risk_in_loop = (in_lead / 365) * demand * cost_in_loop * (holding_rate / 100) / demand
                            total_in_loop = cost_in_loop + risk_in_loop

                            # Calculate Advantage (EU - India)
                            advantage = total_eu_loop - total_in_loop
                            row.append(advantage)
                        z_values.append(row)

                    # PLOT HEATMAP
                    fig_heat = go.Figure(data=go.Heatmap(
                        z=z_values,
                        x=carbon_range,
                        y=freight_range,
                        colorscale='RdBu',  # Red = Negative (Reshore), Blue = Positive (Offshore)
                        zmid=0,  # The Tipping Point
                        colorbar=dict(title="Savings ($/unit)")
                    ))

                    fig_heat.update_layout(
                        title="Global Sourcing Viability Frontier",
                        xaxis_title="Carbon Price ($/tonne)",
                        yaxis_title="Ocean Freight Cost ($/unit)",
                        height=500
                    )

                    st.plotly_chart(fig_heat, use_container_width=True)

                    st.info("""
                        **How to read this Map:**
                        * 🔵 **Blue Zone:** India Sourcing is Profitable.
                        * 🔴 **Red Zone:** Reshoring to EU is Profitable.
                        * ⚪ **White Line:** The Strategic Tipping Point (Break-even).
                        """)

            # 7. AI CONTEXT
            fta_context = f"""
                Global Sourcing Context (CBAM Analysis):
                - Domestic Cost: ${total_eu:.2f} (Carbon Intensity: {eu_co2}kg).
                - Offshore Cost: ${total_in:.2f} (Carbon Intensity: {in_co2}kg).
                - Policy: Tariff {tariff}% | Carbon Price ${carbon_tax}/ton.
                - Impact: CBAM added ${cbam_cost:.2f} to Offshore cost.
                - Verdict: {winner} is the optimal choice by ${abs(delta):.2f}.
                """
            render_chat_ui(df, metrics, extra_context=fta_context, key="fta_chat")

        with tab5:
            st.header("🌍 Strategic Network Design")
            st.markdown(
                "Optimize the location of a **Central Distribution Center (DC)** to minimize weighted transport distance.")

            col1, col2 = st.columns([1, 2])

            with col1:
                st.subheader("📍 Demand Inputs")
                # Default scenario: Germany/Poland cluster
                default_data = [
                    {"name": "Berlin", "lat": 52.52, "lon": 13.40, "demand": 1500},
                    {"name": "Munich", "lat": 48.13, "lon": 11.58, "demand": 1200},
                    {"name": "Hamburg", "lat": 53.55, "lon": 9.99, "demand": 900},
                    {"name": "Warsaw", "lat": 52.22, "lon": 21.01, "demand": 1100},
                    {"name": "Prague", "lat": 50.07, "lon": 14.43, "demand": 850}
                ]

                # Editable Data Table
                input_df = st.data_editor(default_data, num_rows="dynamic", hide_index=True)

                if st.button("📍 Calculate Optimal Location", type="primary"):
                    # Run Optimization
                    opt_lat, opt_lon = network_design.solve_center_of_gravity(input_df)

                    st.success("Optimization Converged")
                    st.metric("Optimal Latitude", f"{opt_lat:.4f}")
                    st.metric("Optimal Longitude", f"{opt_lon:.4f}")

                    # Save for plotting
                    st.session_state['opt_coords'] = (opt_lat, opt_lon)
                    st.session_state['net_data'] = input_df

            with col2:
                if 'opt_coords' in st.session_state:
                    lat, lon = st.session_state['opt_coords']
                    fig = network_design.generate_network_map(st.session_state['net_data'], lat, lon)
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("👈 Edit demand volumes and click Calculate to visualize the network.")

st.markdown("---")
st.caption(f"© 2026 Logistics Research Lab | v4.0.0 | Robustness Analysis Edition")

if source_option == "🔌 Live WMS Database" and df is not None:
    with st.expander("🔍 Inspect Warehouse Logs"):
        st.dataframe(df, use_container_width=True)
