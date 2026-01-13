import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from sqlalchemy import create_engine
from database_schema import DATABASE_URL

# Import our custom logic modules
import config
import inventory_math

# --- CONFIGURATION ---
st.set_page_config(page_title="Digital Capacity Optimizer", layout="wide")

# --- DATABASE CONNECTION ---
@st.cache_data # Caches the data to make the app faster
def load_data_from_db():
    """
    Connects to SQLite and loads the demand logs.
    """
    try:
        engine = create_engine(DATABASE_URL)
        # Read the table into a Pandas DataFrame
        query = "SELECT * FROM demand_logs ORDER BY date ASC"
        df = pd.read_sql(query, engine)

        if df.empty:
            return None

        # Ensure 'date' is actually a datetime object
        df['date'] = pd.to_datetime(df['date'])
        return df
    except Exception as e:
        st.error(f"Database Error: {e}")
        return None

# --- SIDEBAR ---
st.sidebar.header("⚙️ Simulation Parameters")
holding_cost = st.sidebar.number_input("Holding Cost ($/unit)", value=config.HOLDING_COST)
stockout_cost = st.sidebar.number_input("Stockout Penalty ($/unit)", value=config.STOCKOUT_COST)
lead_time = st.sidebar.number_input("Lead Time (Days)", value=config.DEFAULT_LEAD_TIME)

# --- MAIN PAGE ---
st.title("📦 Digital Capacity Optimizer")
st.markdown(f"""
**System Status:** Connected to `inventory_system.db` 🟢
\nThis dashboard automatically loads historical demand from the central SQL database.
""")

# --- LOAD DATA AUTOMATICALLY ---
df = load_data_from_db()

if df is not None:
    # 1. VISUALIZE TRENDS
    st.subheader("📈 Demand Trends (Historical)")

    # Create the chart
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df['date'],
        y=df['demand'],
        mode='lines+markers',
        name='Actual Demand',
        line=dict(color='blue')
    ))
    st.plotly_chart(fig, use_container_width=True)

    # 2. RUN CALCULATIONS
    # Get latest data points for simulation
    latest_demand = df['demand'].iloc[-1]
    avg_demand = df['demand'].mean()
    std_dev = df['demand'].std()

    # Financial Math
    eoq = inventory_math.calculate_eoq(avg_demand * 12, config.ORDER_COST, holding_cost)
    target_sla = inventory_math.calculate_newsvendor_target(holding_cost, stockout_cost)
    safety_stock = inventory_math.calculate_required_inventory(0, std_dev, target_sla) # Base safety stock

    # 3. DISPLAY METRICS
    st.markdown("---")
    st.subheader("🔮 Optimization Engine")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Avg Monthly Demand", f"{int(avg_demand)} units")
    with col2:
        st.metric("Rec. Order Size (EOQ)", f"{int(eoq)} units")
    with col3:
        st.metric("Optimal Service Level", f"{target_sla*100:.1f}%")
    with col4:
        st.metric("Safety Stock Buffer", f"{int(safety_stock)} units")

    # 4. RECOMMENDATION LOGIC
    total_needed = avg_demand + safety_stock

    st.success(f"""
    **🤖 AI Recommendation:** To maintain a **{target_sla*100:.1f}% Service Level**, you should keep **{int(total_needed)} units** in stock.
    \nThis accounts for demand volatility ({int(std_dev)} variance) and the high cost of stockouts (${stockout_cost}).
    """)

else:
    st.warning("⚠️ The database is empty. Please run the migration script or contact IT.")