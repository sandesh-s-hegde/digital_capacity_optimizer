import os
import urllib.parse
from datetime import date

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from scipy.stats import norm
from dotenv import load_dotenv
from streamlit_searchbox import st_searchbox

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
import climate_finance
import ui_views

load_dotenv()

st.set_page_config(page_title="LSP Digital Capacity Twin", page_icon="🚛", layout="wide")

st.sidebar.header("LSP Data Feed")
source_option = st.sidebar.radio("Mode:", ("Live WMS Database", "Sandbox (CSV)"))
st.sidebar.divider()

selected_sku = None
if source_option == "Live WMS Database":
    with st.sidebar.expander("Log Service Lane"):
        with st.form("entry_form"):
            new_product = st.text_input("Service Lane ID", value="Route A")
            new_date = st.date_input("Date", value=date.today())
            new_demand = st.number_input("Volume", min_value=1, value=100)
            if st.form_submit_button("Save"):
                if db_manager.add_record(new_date, new_product, new_demand):
                    st.success("Saved")
                    st.rerun()

    with st.sidebar.expander("Correction"):
        del_id = st.number_input("Record ID", min_value=1, step=1)
        if st.button("Delete"):
            success, _ = db_manager.delete_record(del_id)
            if success:
                st.success("Deleted")
                st.rerun()

    with st.sidebar.expander("Bulk Import"):
        upload_csv = st.file_uploader("Upload CSV", type=["csv"])
        if upload_csv:
            if st.button("Import"):
                try:
                    bulk_df = pd.read_csv(upload_csv)
                    bulk_df.columns = bulk_df.columns.str.strip().str.lower().str.replace(' ', '_')
                    if {'date', 'product_name', 'demand'}.issubset(bulk_df.columns):
                        success, msg = db_manager.bulk_import_csv(bulk_df)
                        if success:
                            st.success(msg)
                            st.rerun()
                except Exception:
                    st.error("Invalid CSV")

    all_products = db_manager.get_unique_products()
    selected_sku = st.sidebar.selectbox("Select Lane:", all_products) if all_products else None

    with st.sidebar.expander("System Admin"):
        if st.button("Reset Database"):
            if db_manager.reset_database():
                st.success("Reset")
                st.rerun()

st.sidebar.divider()
st.sidebar.subheader("System Status")

conn = db_manager.get_db_connection()
if conn:
    st.sidebar.success("Database: Connected (v16)")
    conn.close()
else:
    st.sidebar.error("Database: Offline")

st.sidebar.divider()
st.sidebar.header("LSP Constraints")

transport_mode = st.sidebar.selectbox("Select Mode:", ["Road (Standard)", "Rail (Green/Slow)", "Air (Express/Costly)"])

time_mult, cost_mult, co2_mult = 1.0, 1.0, 1.0
if "Rail" in transport_mode:
    time_mult, cost_mult, co2_mult = 1.5, 0.7, 0.3
elif "Air" in transport_mode:
    time_mult, cost_mult, co2_mult = 0.2, 3.0, 5.0

st.sidebar.subheader("Unit Economics (USD)")
base_uc = st.sidebar.number_input("Base Handling Cost ($)", value=50.0)
uc = base_uc * cost_mult
sp = st.sidebar.number_input("Service Revenue ($)", value=85.0)

st.sidebar.subheader("Risk Simulation")
disruption_mode = st.sidebar.checkbox("Simulate Supplier Shock")

if disruption_mode:
    st.sidebar.error("SHOCK EVENT ACTIVE")
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

st.sidebar.subheader("Horizontal Cooperation")
warehouse_cap = st.sidebar.number_input("Internal Capacity Limit", value=150)
partner_cost = st.sidebar.number_input("Partner Surcharge ($)", value=5.0)
sim_sla = st.sidebar.slider("Target Service Level (%)", 50, 99, 95, 1)

st.sidebar.divider()
st.sidebar.caption("LSP Digital Twin | v4.2.6 | System: Frankfurt | Status: Online")

st.title("🚛 LSP Digital Capacity Twin")

df = None
if source_option == "Live WMS Database":
    df = db_manager.load_data(selected_sku)
    with st.expander("Network Command Center", expanded=False):
        full_df = db_manager.load_data(None)
        if full_df is not None and not full_df.empty:
            summary_data = []
            for p in full_df['product_name'].unique():
                p_data = full_df[full_df['product_name'] == p]
                if not p_data.empty:
                    last_val = p_data.iloc[-1]['demand']
                    avg_val = p_data['demand'].mean()
                    status = "🔴 Strain" if last_val > avg_val * 1.5 else "🟡 Idle" if last_val < avg_val * 0.5 else "🟢 Optimized"
                    summary_data.append({"Lane": p, "Vol": int(last_val), "Status": status})
            st.dataframe(pd.DataFrame(summary_data), use_container_width=True, hide_index=True)
    st.divider()
else:
    st.info("Sandbox Mode: Upload a CSV.")
    uploaded_file = st.file_uploader("Upload CSV", type=["csv"], key="sandbox")
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        df.columns = df.columns.str.strip().str.lower()
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])

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
    except Exception:
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

    if source_option == "Live WMS Database" and not selected_sku:
        st.warning("Please select a Service Lane.")
    else:
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📊 Capacity Hub", "💰 Profit Engine", "🔬 Research Lab", "🌏 Global Sourcing", "📍 Network Design"
        ])

        with tab1:
            st.subheader(f"Operations: {metrics['product_name']} | Mode: {transport_mode}")
            with st.container(border=True):
                map_fig = map_viz.render_map(metrics['product_name'], disruption_mode, outsourced_vol, transport_mode)
                if map_fig:
                    st.plotly_chart(map_fig, use_container_width=True)
                else:
                    st.info("Select a valid Route (e.g., BER-MUC)")

            f_df = forecast.generate_forecast(df) if st.checkbox("Show Demand Forecast", value=True) else None

            fig = go.Figure()
            fig.add_trace(go.Scatter(x=df['date'], y=df['demand'], mode='lines+markers', name='Outbound Flow',
                                     line=dict(color='#2ca02c', width=3)))
            fig.add_hline(y=warehouse_cap, line_dash="dot", line_color="red", annotation_text="Limit")

            if f_df is not None:
                if 'demand_upper' in f_df.columns:
                    fig.add_trace(go.Scatter(x=f_df['date'], y=f_df['demand_upper'], mode='lines', line=dict(width=0),
                                             showlegend=False))
                    fig.add_trace(go.Scatter(
                        name='95% Confidence Interval', x=f_df['date'], y=f_df['demand_lower'],
                        mode='lines', line=dict(width=0), fill='tonexty', fillcolor='rgba(0, 0, 255, 0.1)',
                        showlegend=True
                    ))
                last_pt = pd.DataFrame({'date': [df['date'].max()], 'demand': [df.iloc[-1]['demand']]})
                combined_f = pd.concat([last_pt, f_df])
                fig.add_trace(
                    go.Scatter(x=combined_f['date'], y=combined_f['demand'], mode='lines', name='Forecast Trend',
                               line=dict(dash='dash', color='blue')))

            st.plotly_chart(fig, use_container_width=True)

            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Throughput", f"{int(total_workload)}", f"+{int(reverse_logistics_vol)} Ret")
            c2.metric("Resilience", f"{metrics['resilience_score']}/100",
                      "- Critical" if metrics['resilience_score'] < 50 else "Stable")
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
                if st.button("Generate Report"):
                    with st.spinner("Compiling..."):
                        prompt = f"Analyze {metrics['product_name']}. Resilience {metrics['resilience_score']}. Suggest 3 strategic fixes."
                        summary = ai_brain.chat_with_data(prompt, [], df, metrics)
                        pdf_bytes = report_gen.generate_pdf(metrics, summary)
                        st.download_button("Download PDF", pdf_bytes, f"Report_{metrics['product_name']}.pdf",
                                           "application/pdf")

            ui_views.render_chat_ui(df, metrics, ai_brain,
                                    extra_context=f"LSP Context: Resilience {metrics['resilience_score']}, Mode {transport_mode}",
                                    key="ops_chat")

        with tab2:
            st.subheader("Financial Optimization")
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
                st.markdown("### Monte Carlo Risk Engine")
                sim_fig, sim_metrics = monte_carlo.run_simulation(total_workload, std_dev_demand,
                                                                  total_required_capacity, uc, sp, holding_cost,
                                                                  stockout_cost)
                m1, m2, m3 = st.columns(3)
                m1.metric("Expected Profit", f"${sim_metrics['avg_profit']}", "Mean")
                m2.metric("Loss Probability", f"{sim_metrics['loss_prob']}%", "Risk", delta_color="inverse")
                m3.metric("VaR (95%)", f"${sim_metrics['var_95']}", "Worst Case")
                st.plotly_chart(sim_fig, use_container_width=True)

                ui_views.render_chat_ui(df, metrics, ai_brain,
                                        extra_context=f"Fin Context: Avg Profit ${sim_metrics['avg_profit']}",
                                        key="fin_chat")
            else:
                st.error("Revenue must exceed Cost.")

        with tab3:
            st.subheader("Research Laboratory: Stochastic Stress Test")
            st.markdown("Monte Carlo simulation (N=10,000) to quantify Profit Maximization vs Loss Predictability.")

            col1, col2, col3 = st.columns(3)
            with col1:
                current_ss = st.number_input("Current Safety Stock (Units)", value=int(metrics['safety_stock']))
            with col2:
                sim_days = st.slider("Simulation Horizon", 1000, 10000, 5000)
            with col3:
                margin = st.number_input("Unit Margin ($)", value=float(sp - uc), step=1.0, format="%.2f")

            if st.button("Run Risk/Reward Analysis", type="primary"):
                with st.spinner(f"Simulating {sim_days} operational days..."):
                    critical_ratio = margin / (margin + holding_cost)
                    z_score = norm.ppf(critical_ratio)
                    opt_ss = max(0, z_score * std_dev_demand)

                    np.random.seed(42)
                    # Vectorized Monte Carlo generation
                    demands = np.random.normal(total_workload, std_dev_demand, sim_days)

                    cap_a = total_workload + current_ss
                    cap_b = total_workload + opt_ss

                    sales_a = np.minimum(demands, cap_a)
                    loss_a = np.maximum(0, cap_a - demands) * holding_cost
                    profit_a = (sales_a * margin) - loss_a

                    sales_b = np.minimum(demands, cap_b)
                    loss_b = np.maximum(0, cap_b - demands) * holding_cost
                    profit_b = (sales_b * margin) - loss_b

                    st.session_state.sim_results = {
                        "profit_a": profit_a, "profit_b": profit_b,
                        "optimal_ss": opt_ss, "current_ss": current_ss, "margin": margin
                    }

            if st.session_state.get("sim_results"):
                res = st.session_state.sim_results
                p_a, p_b = np.array(res["profit_a"]), np.array(res["profit_b"])
                opt_ss, curr_ss = res["optimal_ss"], res["current_ss"]

                avg_a, avg_b = np.mean(p_a), np.mean(p_b)
                delta = avg_b - avg_a
                loss_prob_b = np.mean(p_b < 0) * 100
                var_95_b = np.percentile(p_b, 5)

                ui_views.render_research_lab_ui(opt_ss, curr_ss, avg_b, delta, loss_prob_b, var_95_b, p_a, p_b)

            sim_ctx = ""
            if st.session_state.get("sim_results"):
                res = st.session_state.sim_results
                sim_ctx = f"Simulation Run: Optimal SS {int(res['optimal_ss'])}, Margin ${res.get('margin', margin)}, Holding ${holding_cost}"

            ui_views.render_chat_ui(df, metrics, ai_brain, extra_context=sim_ctx, key="research_chat")

        with tab4:
            st.subheader("Global Sourcing Strategy (China Plus One)")
            st.markdown("Quantify the impact of Free Trade Agreements (FTA) vs. Green Trade Barriers (CBAM).")

            col1, col2 = st.columns(2)
            with col1:
                st.markdown("### Baseline: Domestic/Nearshore")
                eu_price = st.number_input("Unit Price ($)", value=85.0)
                eu_lead = st.number_input("Lead Time (Days)", value=4)
                eu_co2 = st.number_input("Carbon Footprint (kg CO₂/unit)", value=2.5)

            with col2:
                st.markdown("### Challenger: India (Offshore)")
                in_price = st.number_input("Offshore Unit Price ($)", value=50.0)
                in_freight = st.number_input("Freight & Logistics ($)", value=12.0)
                in_lead = st.slider("Offshore Lead Time (Days)", 20, 60, 45)
                in_co2 = st.number_input("Carbon Footprint (kg CO₂/unit)", value=8.0)

            st.divider()
            st.markdown("#### Policy Levers: Tariffs vs. Taxes")
            c_lev1, c_lev2 = st.columns(2)
            with c_lev1:
                tariff = st.slider("Import Tariff (%)", 0, 20, 0)
            with c_lev2:
                carbon_tax = st.slider("EU Carbon Price ($/tonne)", 0, 200, 85)

            demand = 15000
            holding_rate = 20

            ets_cost_eu = (eu_co2 / 1000) * carbon_tax
            cost_eu = eu_price + ets_cost_eu
            risk_eu = (eu_lead / 365) * demand * cost_eu * (holding_rate / 100) / demand
            total_eu = cost_eu + risk_eu

            duty = in_price * (tariff / 100)
            cbam_cost = (in_co2 / 1000) * carbon_tax

            cost_in = in_price + in_freight + duty + cbam_cost
            risk_in = (in_lead / 365) * demand * cost_in * (holding_rate / 100) / demand
            total_in = cost_in + risk_in

            c1, c2, c3 = st.columns(3)
            c1.metric("Domestic Landed Cost", f"${total_eu:.2f}", f"Incl. ${ets_cost_eu:.2f} Carbon Cost")
            delta = total_eu - total_in
            c2.metric("Offshore Landed Cost", f"${total_in:.2f}", f"Incl. ${cbam_cost:.2f} CBAM Tax")
            winner = "Offshore" if delta > 0 else "Domestic"
            c3.metric("Sourcing Advantage", f"${abs(delta):.2f} / unit", f"Winner: {winner}",
                      delta_color="normal" if delta > 0 else "inverse")

            fig = go.Figure(data=[
                go.Bar(name='Base Price', x=['Domestic', 'Offshore'], y=[eu_price, in_price], marker_color='#2E86C1'),
                go.Bar(name='Freight', x=['Domestic', 'Offshore'], y=[0, in_freight], marker_color='#28B463'),
                go.Bar(name='Tariff', x=['Domestic', 'Offshore'], y=[0, duty], marker_color='#E74C3C'),
                go.Bar(name='Carbon Tax', x=['Domestic', 'Offshore'], y=[ets_cost_eu, cbam_cost],
                       marker_color='#5D6D7E'),
                go.Bar(name='Risk', x=['Domestic', 'Offshore'], y=[risk_eu, risk_in], marker_color='#F1C40F')
            ])
            fig.update_layout(barmode='stack', title="Landed Cost: The Impact of Green Regulations (CBAM)", height=500)
            st.plotly_chart(fig, use_container_width=True)

            if delta > 0:
                st.success(
                    f"Strategy: Sourcing from India remains profitable. The Labor arbitrage (${eu_price - in_price:.2f}) absorbs the ${cbam_cost:.2f} Green Tax.")
            else:
                st.error("Strategy: Reshore to Europe. Logistics Risk and CBAM Tax negate the manufacturing savings.")

            st.divider()
            st.subheader("Strategic Robustness: Sensitivity Matrix")
            with st.expander("Configure Sensitivity Parameters", expanded=False):
                s1, s2 = st.columns(2)
                with s1:
                    max_freight = st.slider("Max Freight Scenario ($)", 10.0, 50.0, 25.0)
                with s2:
                    max_carbon = st.slider("Max Carbon Price ($/ton)", 50, 300, 200)

            if st.button("Run Sensitivity Heatmap"):
                with st.spinner("Calculating scenarios..."):
                    freight_range = np.linspace(5.0, max_freight, 20)
                    carbon_range = np.linspace(0, max_carbon, 20)

                    # Vectorized heat map generation
                    C, F = np.meshgrid(carbon_range, freight_range)
                    cost_eu_grid = eu_price + ((eu_co2 / 1000) * C)
                    total_eu_grid = cost_eu_grid + (
                            (eu_lead / 365) * demand * cost_eu_grid * (holding_rate / 100) / demand)

                    cost_in_grid = in_price + F + (in_price * (tariff / 100)) + ((in_co2 / 1000) * C)
                    total_in_grid = cost_in_grid + (
                            (in_lead / 365) * demand * cost_in_grid * (holding_rate / 100) / demand)

                    z_values = total_eu_grid - total_in_grid

                    fig_heat = go.Figure(
                        data=go.Heatmap(z=z_values, x=carbon_range, y=freight_range, colorscale='RdBu', zmid=0,
                                        colorbar=dict(title="Savings ($/unit)")))
                    fig_heat.update_layout(title="Global Sourcing Viability Frontier",
                                           xaxis_title="Carbon Price ($/tonne)",
                                           yaxis_title="Ocean Freight Cost ($/unit)", height=500)
                    st.plotly_chart(fig_heat, use_container_width=True)

            fta_context = f"Sourcing: {winner} is optimal by ${abs(delta):.2f}. CBAM penalty for offshore: ${cbam_cost:.2f}."
            ui_views.render_chat_ui(df, metrics, ai_brain, extra_context=fta_context, key="fta_chat")

            st.divider()
            st.subheader("FinTech Climate Risk Engine")
            st.markdown("Simulate regulatory transition risk using Geometric Brownian Motion (GBM).")

            with st.expander("Configure Financial Markets", expanded=False):
                fin1, fin2, fin3 = st.columns(3)
                with fin1:
                    current_ets = st.number_input("Current ETS Price ($)", value=85.0)
                with fin2:
                    ets_volatility = st.slider("Market Volatility (σ)", 0.10, 1.00, 0.40)
                with fin3:
                    total_emissions = green_metrics.get("total_emissions", 50000)
                    st.metric("Total Supply Chain Emissions", f"{int(total_emissions):,} kg")

            if st.button("Run Stochastic Carbon Simulation"):
                with st.spinner("Generating 2,000 market paths via Geometric Brownian Motion..."):
                    emissions_tonnes = total_emissions / 1000.0
                    cf_fig, cf_metrics = climate_finance.plot_carbon_risk_simulation(current_price=current_ets,
                                                                                     volatility=ets_volatility,
                                                                                     total_emissions_tons=emissions_tonnes)
                    st.plotly_chart(cf_fig, use_container_width=True)

                    cf1, cf2, cf3 = st.columns(3)
                    cf1.metric("Current Carbon Liability", f"${cf_metrics['current_exposure']:,.0f}")
                    cf2.metric("Expected Liability (1Y)", f"${cf_metrics['expected_exposure']:,.0f}",
                               f"{cf_metrics['expected_exposure'] - cf_metrics['current_exposure']:,.0f} Drift",
                               delta_color="inverse")
                    cf3.metric("Carbon Value at Risk (95%)", f"${cf_metrics['worst_case_exposure']:,.0f}",
                               f"{cf_metrics['worst_case_exposure'] - cf_metrics['current_exposure']:,.0f} Max Downside",
                               delta_color="inverse")

        with tab5:
            st.subheader("Logistics Digital Twin: Network Designer")
            col_left, col_right = st.columns([1.2, 2])

            with col_left:
                st.markdown("#### Define Trade Lane")
                with st.container(border=True):
                    origin = st_searchbox(network_design.search_google_places, key="tab5_origin_search_final",
                                          placeholder="Origin City")
                    dest = st_searchbox(network_design.search_google_places, key="tab5_dest_search_final",
                                        placeholder="Destination City")

                    if origin: st.session_state['origin_val'] = origin
                    if dest: st.session_state['dest_val'] = dest

                    if st.button("Analyze Route", type="primary", use_container_width=True):
                        if st.session_state.get('origin_val') and st.session_state.get('dest_val'):
                            with st.spinner("Calculating Logistics Path..."):
                                try:
                                    st.session_state['route_res'] = network_design.analyze_route(
                                        st.session_state['origin_val'], st.session_state['dest_val'])
                                except Exception as e:
                                    st.error(f"Analysis Error: {e}")
                        else:
                            st.error("Please select origin and destination.")

                if 'route_res' in st.session_state:
                    res = st.session_state['route_res']
                    if "error" in res:
                        st.error(res['error'])
                    else:
                        m = res['metrics']
                        st.divider()
                        st.markdown(f"### Strategy: {res['recommendation']}")
                        st.caption(f"Reasoning: {res['reason']}")

                        for mode, emoji in [('road', '🚛 ROAD'), ('sea', '🚢 SEA'), ('air', '✈️ AIR')]:
                            if m[mode]['possible']:
                                with st.container(border=True):
                                    st.write(f"**{emoji}**")
                                    c1, c2 = st.columns(2)
                                    c1.metric("Cost", f"${m[mode]['cost']:,.0f}")
                                    c2.metric("Time", f"{m[mode]['time']:.1f} Days")
                                    st.progress(min(m[mode]['co2'] / 5000, 1.0),
                                                text=f"Carbon: {int(m[mode]['co2'])}kg")

            with col_right:
                st.markdown("#### Live Transportation Route")
                if 'route_res' in st.session_state and 'error' not in st.session_state['route_res']:
                    res = st.session_state['route_res']
                    api_key = os.getenv("GOOGLE_API_KEY")
                    if not api_key:
                        st.error("Google API Key missing.")
                    else:
                        o_q = urllib.parse.quote(res['origin']['name'])
                        d_q = urllib.parse.quote(res['dest']['name'])
                        embed_url = f"https://www.google.com/maps/embed/v1/directions?key={api_key}&origin={o_q}&destination={d_q}&mode=driving"
                        st.components.v1.iframe(embed_url, height=700)
                else:
                    st.info("Enter origin and destination to visualize the trade lane.")

            st.divider()
            st.subheader("Network Strategy Assistant")

            if "logistics_chat_history" not in st.session_state:
                st.session_state.logistics_chat_history = []

            chat_container = st.container(height=400, border=True)
            with chat_container:
                for role, text in st.session_state.logistics_chat_history:
                    st.chat_message(role).markdown(text)

            if prompt := st.chat_input("Ask about this trade lane...", key="network_chat"):
                st.session_state.logistics_chat_history.append(("user", prompt))
                with chat_container:
                    st.chat_message("user").markdown(prompt)
                    if 'route_res' in st.session_state:
                        with st.chat_message("assistant"):
                            with st.spinner("Analyzing data..."):
                                try:
                                    response = network_design.ask_gemini_logistics(prompt,
                                                                                   st.session_state['route_res'])
                                    st.markdown(response)
                                    st.session_state.logistics_chat_history.append(("assistant", response))
                                except Exception as e:
                                    st.error(f"AI Error: {e}")
                    else:
                        with st.chat_message("assistant"):
                            warning_msg = "Please analyze a route first."
                            st.warning(warning_msg)
                            st.session_state.logistics_chat_history.append(("assistant", warning_msg))
                st.rerun()

st.markdown("---")
st.caption(f"© 2026 LSP Digital Twin | v4.2.6 | Network Designer Edition")

if source_option == "Live WMS Database" and df is not None:
    with st.expander("Inspect Warehouse Logs"):
        st.dataframe(df, use_container_width=True)
