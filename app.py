import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from sqlalchemy.orm import Session
from database_schema import engine, DemandLog
from datetime import date

# Import Custom Logic Modules
import config
import inventory_math
import ai_brain  # <--- The AI Brain

# --- CONFIGURATION ---
st.set_page_config(page_title="Digital Capacity Optimizer", layout="wide")


# --- DATABASE FUNCTIONS ---
def load_data_from_db():
    """Connects to the SQL Database and fetches all records."""
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


# --- CSV LOADER (Sandbox Mode) ---
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

# Input Form (Only visible in Live Mode)
if source_option == "🔌 Live Database":
    st.sidebar.subheader("📝 Log New Inventory")

    with st.sidebar.form("entry_form"):
        new_date = st.date_input("Transaction Date", value=date.today())
        new_demand = st.number_input(
            "📦 Order Quantity (Units)",
            min_value=1,
            value=100,
            step=1,
            format="%d",
            help="Enter the total units received/demanded."
        )

        submitted = st.form_submit_button("💾 Save to Database")

        if submitted:
            if add_new_order(new_date, new_demand):
                st.sidebar.success("✅ Saved!")
                st.rerun()

st.sidebar.markdown("---")
st.sidebar.header("🔧 Simulation Parameters")
holding_cost = st.sidebar.number_input("Holding Cost ($)", value=config.HOLDING_COST)
stockout_cost = st.sidebar.number_input("Stockout Cost ($)", value=config.STOCKOUT_COST)

# --- SIDEBAR: ABOUT SECTION ---
st.sidebar.markdown("---")
st.sidebar.markdown("### ℹ️ About")
st.sidebar.info(
    """
    **Capacity Optimizer v2.1**

    🤖 AI Model: Gemini 1.5 Flash
    📊 Mode: Production

    *Built by Sandesh Hegde*
    """
)

# --- MAIN PAGE ---
st.title("📦 Digital Capacity Optimizer")

# 1. LOAD DATA
df = None
if source_option == "🔌 Live Database":
    df = load_data_from_db()
    if df is not None:
        st.caption(f"Connected to Production Database | {len(df)} Records Loaded")
else:
    # Sandbox Mode
    st.info("Sandbox Mode: Upload a CSV to simulate different demand scenarios.")
    uploaded_file = st.file_uploader("Upload CSV", type=["csv"])
    if uploaded_file:
        df = load_data_from_csv(uploaded_file)

# 2. VISUALIZE & ANALYZE
if df is not None and not df.empty:

    # A. Demand Chart
    st.subheader("📈 Inventory & Demand Trends")
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df['date'], y=df['demand'],
        mode='lines+markers', name='Demand History',
        line=dict(color='#2ca02c', width=3)
    ))
    st.plotly_chart(fig, use_container_width=True)

    # B. Math Calculations
    avg_demand = df['demand'].mean()
    std_dev = df['demand'].std()

    eoq = inventory_math.calculate_eoq(avg_demand * 12, config.ORDER_COST, holding_cost)
    target_sla = inventory_math.calculate_newsvendor_target(holding_cost, stockout_cost)
    safety_stock = inventory_math.calculate_required_inventory(0, std_dev, target_sla)

    # C. Display Key Metrics
    st.markdown("### 🔮 Planning Engine")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Avg Monthly Demand", f"{int(avg_demand)}")
    c2.metric("Target Service Level", f"{target_sla * 100:.1f}%")
    c3.metric("Safety Stock", f"{int(safety_stock)}")
    c4.metric("Optimal Order (EOQ)", f"{int(eoq)}")

    st.markdown("---")

    # --- 3. THE CONVERSATIONAL AI ---

    # Layout: Title left, Reset Button right
    col_title, col_btn = st.columns([5, 1])

    with col_title:
        st.subheader("💬 Chat with your Supply Chain Data")

    with col_btn:
        # The Reset Button logic
        if st.button("🗑️ Clear", help="Reset Chat History"):
            st.session_state.messages = []
            st.rerun()

    # A. Initialize Chat History in Session State
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # B. Display Previous Messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # C. Handle New Input
    if prompt := st.chat_input("Ask about your inventory (e.g., 'Why is safety stock high?')"):

        # 1. Display User Message immediately
        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        # 2. Convert memory format for Gemini
        gemini_history = []
        for msg in st.session_state.messages[:-1]:
            role = "user" if msg["role"] == "user" else "model"
            gemini_history.append({"role": role, "parts": [msg["content"]]})

        # 3. Define the Context (These variables come from your Math section above)
        metrics_context = {
            "avg_demand": int(avg_demand),
            "std_dev": int(std_dev),
            "eoq": int(eoq),
            "safety_stock": int(safety_stock),
            "sla": target_sla
        }

        # 4. Get AI Response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response_text = ai_brain.chat_with_data(prompt, gemini_history, df, metrics_context)
                st.markdown(response_text)

        # 5. Save AI Response to memory
        st.session_state.messages.append({"role": "assistant", "content": response_text})

else:
    if source_option == "🔌 Live Database":
        st.warning("Database is empty. Use the sidebar form to add data!")

# --- FOOTER ---
st.markdown("---")
st.caption("© 2026 Digital Capacity Inc. | Powered by SQL & Google Gemini 🧠")