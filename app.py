import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from sqlalchemy import create_engine
from database_schema import DATABASE_URL
from datetime import datetime, timedelta

# Import our custom logic modules
import config
import inventory_math

# --- CONFIGURATION ---
st.set_page_config(page_title="Digital Capacity Optimizer", layout="wide")


# --- DATA LOADERS ---
@st.cache_data
def load_data_from_db():
    """Connects to the SQL Database."""
    try:
        engine = create_engine(DATABASE_URL)
        query = "SELECT * FROM demand_logs ORDER BY date ASC"
        df = pd.read_sql(query, engine)
        if not df.empty:
            df['date'] = pd.to_datetime(df['date'])
        return df
    except Exception as e:
        st.error(f"Database Error: {e}")
        return None


def load_data_from_csv(uploaded_file):
    """Parses an uploaded CSV file for simulation."""
    try:
        df = pd.read_csv(uploaded_file)

        # 1. Clean Column Names
        df.columns = df.columns.str.strip().str.lower()

        # 2. Map Columns
        if 'date' in df.columns:
            date_col = 'date'
        elif 'month' in df.columns:
            date_col = 'month'
        else:
            st.error("CSV must have a 'Date' or 'Month' column.")
            return None

        # 3. Standardize Dates (Handle "Jan", "Feb" or "2024-01-01")
        # We'll generate fake dates for simulation if simple month names are used
        clean_dates = []
        base_year = datetime.now().year
        month_map = {
            "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
            "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12
        }

        for _, row in df.iterrows():
            raw = str(row[date_col]).strip()
            # Try parsing real date
            try:
                dt = pd.to_datetime(raw).date()
            except:
                # Try parsing "Jan", "Feb"
                month_str = raw[:3].lower()
                month_num = month_map.get(month_str, 1)
                dt = datetime(base_year, month_num, 1).date()
            clean_dates.append(dt)

        df['date'] = clean_dates
        df['date'] = pd.to_datetime(df['date'])  # Ensure consistent type
        return df

    except Exception as e:
        st.error(f"Error reading CSV: {e}")
        return None


# --- SIDEBAR UI ---
st.sidebar.header("⚙️ Data Source")
source_option = st.sidebar.radio(
    "Select Input Mode:",
    ("🔌 Live Database", "📂 Upload CSV (Sandbox)")
)

st.sidebar.markdown("---")
st.sidebar.header("🔧 Simulation Parameters")
holding_cost = st.sidebar.number_input("Holding Cost ($/unit)", value=config.HOLDING_COST)
stockout_cost = st.sidebar.number_input("Stockout Penalty ($/unit)", value=config.STOCKOUT_COST)
lead_time = st.sidebar.number_input("Lead Time (Days)", value=config.DEFAULT_LEAD_TIME)

# --- MAIN LOGIC ---
st.title("📦 Digital Capacity Optimizer")

# 1. Load Data based on Selection
df = None

if source_option == "🔌 Live Database":
    df = load_data_from_db()
    if df is not None:
        st.success(f"Connected to Production Database. Loaded {len(df)} records.")
    else:
        st.warning("Database is empty. Try running the migration script.")

else:  # Upload CSV Mode
    st.info("Sandbox Mode: Upload a CSV to simulate different demand scenarios.")
    uploaded_file = st.file_uploader("Upload 'mock_data.csv'", type=["csv"])
    if uploaded_file is not None:
        df = load_data_from_csv(uploaded_file)
        if df is not None:
            st.success("Simulation Data Loaded Successfully.")

# 2. Visualize & Calculate (Only if data exists)
if df is not None and not df.empty:

    # VISUALIZE
    st.subheader("📈 Demand Trends")
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df['date'],
        y=df['demand'],
        mode='lines+markers',
        name='Demand',
        line=dict(color='#2ca02c', width=3)
    ))
    st.plotly_chart(fig, use_container_width=True)

    # CALCULATE
    latest_demand = df['demand'].iloc[-1]
    avg_demand = df['demand'].mean()
    std_dev = df['demand'].std()

    eoq = inventory_math.calculate_eoq(avg_demand * 12, config.ORDER_COST, holding_cost)
    target_sla = inventory_math.calculate_newsvendor_target(holding_cost, stockout_cost)
    safety_stock = inventory_math.calculate_required_inventory(0, std_dev, target_sla)

    total_needed = avg_demand + safety_stock

    # DISPLAY METRICS
    st.markdown("---")
    st.subheader("🔮 Optimization Engine")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Avg Monthly Demand", f"{int(avg_demand)} units")
    with col2:
        st.metric("Rec. Order Size (EOQ)", f"{int(eoq)} units")
    with col3:
        st.metric("Optimal Service Level", f"{target_sla * 100:.1f}%")
    with col4:
        st.metric("Safety Stock Buffer", f"{int(safety_stock)} units")

    st.info(f"""
    **🤖 Recommendation:** To maintain a **{target_sla * 100:.1f}% Service Level**, keep **{int(total_needed)} units** in stock.
    """)

elif source_option == "📂 Upload CSV (Sandbox)" and df is None:
    st.write("👈 *Waiting for file upload...*")