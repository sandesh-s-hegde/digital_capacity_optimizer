import streamlit as st
import matplotlib.pyplot as plt
import time
from services.dispatcher import EcosystemDispatcher


def render_chat_ui(df, metrics, ai_brain, extra_context="", key="default_chat"):
    """Renders the AI chat interface and manages session state history."""
    st.divider()
    st.subheader("💬 LSP Strategy Assistant")

    if "messages" not in st.session_state:
        st.session_state.messages = []

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
                history = [
                    {"role": m["role"], "parts": [m["content"]]}
                    for m in st.session_state.messages
                ]

                response = ai_brain.chat_with_data(full_query, history, df, metrics)

            st.chat_message("assistant").markdown(response)

        st.session_state.messages.append({"role": "assistant", "content": response})
        st.rerun()


def render_research_lab_ui(opt_ss, curr_ss, avg_b, delta, loss_prob_b, var_95_b, p_a, p_b):
    """Renders the metric visualizations and distribution plots for the Research Lab."""
    st.divider()

    k1, k2, k3 = st.columns(3)
    k1.metric("Optimal Safety Stock", f"{int(opt_ss)} Units", f"vs Current {curr_ss}")
    k2.metric("Daily Net Profit", f"${avg_b:,.2f}", f"{delta:,.2f} vs Current")
    k3.metric("Projected Annual Gain", f"${delta * 365:,.0f}", "Capital Release", delta_color="normal")

    r1, r2, r3 = st.columns(3)
    r1.metric("📉 Loss Probability", f"{loss_prob_b:.1f}%", "Downside Risk", delta_color="inverse")
    r2.metric("⚠️ Value at Risk (VaR 95%)", f"${var_95_b:,.0f}", "Worst Case Scenario")
    r3.metric("Risk Profile", "STABLE" if loss_prob_b < 5 else "ELEVATED", "Simulation Rating")

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.hist(p_a, bins=50, alpha=0.4, label='Current Strategy', color='gray', density=True)
    ax.hist(p_b, bins=50, alpha=0.6, label='Optimal Strategy', color='#004562', density=True)
    ax.axvline(0, color='red', linestyle='--', linewidth=1)
    ax.legend()
    ax.set_title("Profit & Loss Distribution")
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    st.pyplot(fig)


def render_tactical_execution_ui():
    """Renders the execution widget to dispatch AI decisions to external APIs."""
    st.divider()
    st.subheader("⚡ Tactical Ecosystem Execution")
    st.caption("Bridge the gap between predictive analytics and real-world procurement.")

    col1, col2 = st.columns(2)
    with col1:
        supplier_type = st.radio("Target Ecosystem Route:", ["Modern B2B (API)", "Legacy Carrier (RPA)"])
    with col2:
        assets_needed = st.number_input("Assets to Procure", min_value=1, value=5)

    if st.button("🚀 Dispatch Booking Webhook", type="primary"):
        with st.spinner("Cryptographically signing payload and routing to middleware..."):

            is_legacy = supplier_type == "Legacy Carrier (RPA)"
            payload = {
                "transaction_id": f"tx-{int(time.time())}",
                "carrier_name": "MAERSK" if is_legacy else "ENTERPRISE",
                "assets_required": assets_needed,
                "max_budget_eur": assets_needed * 150.0,
                "is_legacy_system": is_legacy
            }

            dispatcher = EcosystemDispatcher()
            success = dispatcher.dispatch_sync(payload)

            if success:
                st.success(f"✅ Webhook successfully dispatched to the {'RPA Bridge' if is_legacy else 'B2B API'}!")
                st.balloons()
            else:
                st.error("❌ Dispatch failed. Check API connection and logs.")
