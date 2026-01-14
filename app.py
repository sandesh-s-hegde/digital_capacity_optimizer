import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
from database_schema import DATABASE_URL, DemandLog, engine
from datetime import datetime, date

# Import our custom logic modules
import config
import inventory_math

# --- CONFIGURATION ---
st.set_page_config(page_title="Digital Capacity Optimizer", layout="wide")


# --- DATABASE FUNCTIONS ---
def load_data_from_db():
    """Connects to the SQL Database."""
    try:
        # Use pandas to run a SELECT query
        query = "SELECT * FROM demand_logs ORDER BY date ASC"
        df = pd.read_sql(query, engine)
        if not df.empty:
            df['date'] = pd.to_datetime(df['date'])
        return df
    except Exception as e:
        st.error(f"Database Error: {e}")
        return None


def add_new_order(log_date, demand_qty):
    """Writes a new record to the PostgreSQL database safely."""
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


# --- CSV LOADER (Sandbox) ---
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


# --- SIDEBAR: CONTROLS ---
st.sidebar.header("⚙️ Data Source")
source_option = st.sidebar.radio("Mode:", ("🔌 Live Database", "📂 Sandbox (CSV)"))

st.sidebar.markdown("---")

# *** NEW: THE INPUT FORM (POLISHED) ***
if source_option == "🔌 Live Database":
    st.sidebar.subheader("📝 Log New Inventory")

    with st.sidebar.form("entry_form"):
        # Improved UI: Clear label, today's date default
        new_date = st.date_input("Transaction Date", value=date.today())

        # Improved UI: Integer only, no decimals, helpful tooltip
        new_demand = st.number_input(
            "📦 Order Quantity (Units)",
            min_value=1,
            value=100,
            step=1,
            format="%d",
            help="Enter the total number of units received into inventory."
        )

        submitted = st.form_submit_button("💾 Save to Database")

        if submitted:
            success = add_new_order(new_date, new_demand)
            if success:
                st.sidebar.success("✅ Saved! Refreshing...")
                st.rerun()

st.sidebar.markdown("---")
st.sidebar.header("🔧 Simulation Parameters")
holding_cost = st.sidebar.number_input("Holding Cost ($)", value=config.HOLDING_COST)
stockout_cost = st.sidebar.number_input("Stockout Cost ($)", value=config.STOCKOUT_COST)

# --- MAIN PAGE ---
st.title("📦 Digital Capacity Optimizer")

# 1. LOAD DATA
df = None
if source_option == "🔌 Live Database":
    df = load_data_from_db()
    if df is not None:
        st.caption(f"Connected to Production Database | {len(df)} Records Loaded")
else:
    uploaded_file = st.file_uploader("Upload CSV", type=["csv"])
    if uploaded_file:
        df = load_data_from_csv(uploaded_file)

# 2. VISUALIZE & ANALYZE
if df is not None and not df.empty:

    # Chart
    st.subheader("📈 Inventory & Demand Trends")
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df['date'], y=df['demand'],
        mode='lines+markers', name='Demand History',
        line=dict(color='#2ca02c', width=3)
    ))
    st.plotly_chart(fig, use_container_width=True)

    # Math
    avg_demand = df['demand'].mean()
    std_dev = df['demand'].std()
    target_sla = inventory_math.calculate_newsvendor_target(holding_cost, stockout_cost)
    safety_stock = inventory_math.calculate_required_inventory(0, std_dev, target_sla)

    # Metrics
    st.markdown("### 🔮 Planning Engine")
    c1, c2, c3 = st.columns(3)
    c1.metric("Avg Monthly Demand", f"{int(avg_demand)}")
    c2.metric("Target Service Level", f"{target_sla * 100:.1f}%")
    c3.metric("Rec. Safety Stock", f"{int(safety_stock)}")

    st.info(
        f"**AI Insight:** Based on a volatility of {int(std_dev)} units, you need **{int(safety_stock)} units** buffer stock.")

else:
    if source_option == "🔌 Live Database":
        st.warning("Database is empty. Use the sidebar form to add data!")