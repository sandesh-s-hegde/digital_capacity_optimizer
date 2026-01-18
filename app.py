import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from sqlalchemy.orm import Session
from database_schema import engine, DemandLog
from datetime import date

# Import Custom Logic Modules
import config
import inventory_math
import ai_brain

# --- CONFIGURATION ---
st.set_page_config(page_title="Digital Capacity Optimizer", layout="wide")


# --- DATABASE FUNCTIONS ---
def load_data_from_db():
    try:
        query = "SELECT * FROM demand_logs ORDER BY date ASC"
        df = pd.read_sql(query, engine)
        if not df.empty:
            df['date'] = pd.to_datetime(df['date'])
        return df
    except Exception as e:
        st.error(f"Database Error: {e}")
        return None


def add_new_order(log_date, demand_qty):
    try:
        with Session(engine) as session:
            new_log = DemandLog(
                date=log_date,
                demand=demand_qty,
                region="Global",
                unit_price=config.HOLDING_COST
            )
            session.add(new_log)
            session.commit()
            return True
    except Exception as e:
        st.error(f"Failed to write to DB: {e}")
        return False


# --- CSV LOADER ---
def load_data_from_csv(uploaded_file):
    try:
        df = pd.read_csv(uploaded_file)
        df.columns = df.columns.str.strip().str.lower()
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
        return df
    except Exception as e:
        st.error(f"Error reading CSV: {e}")
        return None


# --- SIDEBAR ---
st.sidebar.header("⚙️ Data Source")
source_option = st.sidebar.radio("Mode:", ("🔌 Live Database", "📂 Sandbox (CSV)"))
st.sidebar.markdown("---")

if source_option == "🔌 Live Database":
    st.sidebar.subheader("📝 Log New Inventory")
    with st.sidebar.form("entry_form"):
        new_date = st.date_input("Transaction Date", value=date.today())
        new_demand = st.number_input("📦 Order Quantity", min_value=1, value=100)
        if st.form_submit_button("💾 Save"):
            if add_new_order(new_date, new_demand):
                st.sidebar.success("✅ Saved!")
                st.rerun()

st.sidebar.markdown("---")
st.sidebar.header("🔧 Parameters")
holding_cost = st.sidebar.number_input("Holding Cost ($)", value=config.HOLDING_COST)
stockout_cost = st.sidebar.number_input("Stockout Cost ($)", value=config.STOCKOUT_COST)

# --- ABOUT ---
st.sidebar.markdown("---")
st.sidebar.info("Capacity Optimizer v2.1\nAI: Gemini Flash")

# --- MAIN PAGE ---
st.title("📦 Digital Capacity Optimizer")

df = None
if source_option == "🔌 Live Database":
    df = load_data_from_db()
elif uploaded_file := st.file_uploader("Upload CSV", type=["csv"]):
    df = load_data_from_csv(uploaded_file)

if df is not None and not df.empty:
    # A. Chart
    st.subheader("📈 Inventory Trends")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['date'], y=df['demand'], mode='lines+markers', name='Demand'))
    st.plotly_chart(fig, use_container_width=True)

    # B. Math
    avg_demand = df['demand'].mean()
    std_dev = df['demand'].std()

    eoq = inventory_math.calculate_eoq(avg_demand * 12, config.ORDER_COST, holding_cost)
    target_sla = inventory_math.calculate_newsvendor_target(holding_cost, stockout_cost)

    # ✅ FIX: Using keyword args to ensure absolute safety with the new math file
    safety_stock = inventory_math.calculate_safety_stock(
        std_dev_demand=std_dev,
        service_level_z=target_sla,
        lead_time=1.0
    )

    # C. Metrics
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Avg Demand", f"{int(avg_demand)}")
    c2.metric("Target SLA", f"{target_sla * 100:.1f}%")
    c3.metric("Safety Stock", f"{int(safety_stock)}")
    c4.metric("EOQ", f"{int(eoq)}")

    st.markdown("---")

    # --- CHAT ---
    col_t, col_b = st.columns([5, 1])
    with col_t:
        st.subheader("💬 Chat with Data")
    with col_b:
        if st.button("🗑️ Clear"):
            st.session_state.messages = []
            st.rerun()

    if "messages" not in st.session_state: st.session_state.messages = []

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]): st.markdown(msg["content"])

    if prompt := st.chat_input("Ask about inventory..."):
        with st.chat_message("user"): st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        gemini_hist = [{"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]}
                       for m in st.session_state.messages[:-1]]

        ctx = {
            "avg_demand": int(avg_demand),
            "std_dev": int(std_dev),
            "eoq": int(eoq),
            "safety_stock": int(safety_stock),
            "sla": target_sla
        }

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = ai_brain.chat_with_data(prompt, gemini_hist, df, ctx)
                st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})

else:
    if source_option == "🔌 Live Database":
        st.warning("Database empty. Add data!")

st.markdown("---")
st.caption("© 2026 Digital Capacity Inc.")