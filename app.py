import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from sqlalchemy.orm import Session
from database_schema import engine, DemandLog
from datetime import date
from dotenv import load_dotenv

# Import Custom Logic Modules
import config
import inventory_math
import ai_brain
import report_gen
import forecast  # Forecast Engine
import profit_optimizer  # Profit Engine

# --- LOAD SECRETS ---
load_dotenv()

# --- CONFIGURATION ---
st.set_page_config(page_title="Digital Capacity Optimizer", layout="wide")


# --- DATABASE FUNCTIONS ---

def get_unique_products():
    """Fetches a list of all unique product names from the DB for the sidebar dropdown."""
    try:
        query = "SELECT DISTINCT product_name FROM demand_logs_v2 ORDER BY product_name"
        df = pd.read_sql(query, engine)
        return df['product_name'].tolist() if not df.empty else []
    except Exception as e:
        return []


def load_data_from_db(selected_product=None):
    """Connects to the Cloud Database and fetches records, optionally filtering by Product."""
    try:
        if selected_product:
            # Filter query for specific product
            query = f"SELECT * FROM demand_logs_v2 WHERE product_name = '{selected_product}' ORDER BY date ASC"
        else:
            # Fallback (mostly for debug)
            query = "SELECT * FROM demand_logs_v2 ORDER BY date ASC"

        df = pd.read_sql(query, engine)
        if not df.empty:
            df['date'] = pd.to_datetime(df['date'])
        return df
    except Exception as e:
        st.error(f"Database Error: {e}")
        return None


def add_new_order(log_date, product_name, demand_qty):
    """Writes a new record to the Cloud Database safely."""
    try:
        with Session(engine) as session:
            new_log = DemandLog(
                date=log_date,
                product_name=product_name,
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


def delete_order(record_id):
    """Deletes a record from the database by its ID."""
    try:
        with Session(engine) as session:
            # Find the record
            record = session.get(DemandLog, int(record_id))
            if record:
                session.delete(record)
                session.commit()
                return True
            else:
                st.error("❌ ID not found.")
                return False
    except Exception as e:
        st.error(f"Failed to delete: {e}")
        return False


def get_inventory_summary():
    """
    Scans ALL products to build a high-level status report.
    Returns a DataFrame customized for the Executive Dashboard.
    """
    try:
        # Get all raw data
        query = "SELECT * FROM demand_logs_v2 ORDER BY date ASC"
        df = pd.read_sql(query, engine)

        if df.empty:
            return pd.DataFrame()

        summary_data = []
        unique_products = df['product_name'].unique()

        for product in unique_products:
            # Filter for this specific product
            p_df = df[df['product_name'] == product]

            # Get latest stats
            if not p_df.empty:
                last_record = p_df.iloc[-1]
                avg_demand = p_df['demand'].mean()

                # Simple Health Check Logic
                status = "🟢 Normal"
                if last_record['demand'] > (avg_demand * 1.5):
                    status = "🔴 Surge Alert"
                elif last_record['demand'] < (avg_demand * 0.5):
                    status = "🟡 Low Velocity"

                summary_data.append({
                    "Product": product,
                    "Last Update": last_record['date'],
                    "Latest Demand": int(last_record['demand']),
                    "Avg Demand": int(avg_demand),
                    "Status": status
                })

        return pd.DataFrame(summary_data)
    except Exception as e:
        return pd.DataFrame()


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
selected_sku = None  # Variable to store what user selects

if source_option == "🔌 Live Database":
    st.sidebar.subheader("📝 Log New Inventory")

    with st.sidebar.form("entry_form"):
        # NEW: Product Name Input
        new_product = st.text_input("Product Name (SKU)", value="Widget A", help="E.g., Laptop Pro, Widget X")
        new_date = st.date_input("Transaction Date", value=date.today())
        new_demand = st.number_input(
            "📦 Order Quantity (Units)",
            min_value=1,
            value=100,
            step=1,
            format="%d"
        )

        submitted = st.form_submit_button("💾 Save to Database")

        if submitted:
            if add_new_order(new_date, new_product, new_demand):
                st.sidebar.success("✅ Saved!")
                st.rerun()

    # --- NEW: DASHBOARD FILTER ---
    st.sidebar.markdown("---")
    st.sidebar.header("🔍 Filter Dashboard")

    all_products = get_unique_products()

    if all_products:
        selected_sku = st.sidebar.selectbox("Select Product to Analyze:", all_products)
    else:
        st.sidebar.caption("No products found yet. Add one above!")

st.sidebar.markdown("---")

# 1. Cost Parameters
st.sidebar.header("🔧 Financials")
holding_cost = st.sidebar.number_input("Holding Cost ($)", value=config.HOLDING_COST)
stockout_cost = st.sidebar.number_input("Stockout Cost ($)", value=config.STOCKOUT_COST)

# 2. Supplier Reliability
st.sidebar.markdown("---")
st.sidebar.header("🚢 Supplier Reliability")

lead_time_months = st.sidebar.slider(
    "Avg Lead Time (Months)",
    min_value=0.5, max_value=6.0, value=1.0, step=0.5
)

lead_time_volatility = st.sidebar.slider(
    "Lead Time Variance (Months)",
    min_value=0.0, max_value=2.0, value=0.0, step=0.1,
    help="High variance = Unpredictable supplier (Chaos Factor)."
)

# 3. Service Level Target
st.sidebar.markdown("---")
st.sidebar.subheader("🎛️ Scenario Planning")
sim_sla = st.sidebar.slider(
    "Target Service Level (%)",
    min_value=50, max_value=99, value=95, step=1
)

# --- SIDEBAR: ABOUT SECTION ---
st.sidebar.markdown("---")
st.sidebar.markdown("### ℹ️ About")
st.sidebar.info(
    """
    **Capacity Optimizer v3.1**

    🤖 AI Model: Gemini 1.5 Flash
    ☁️ Database: Neon PostgreSQL
    🔮 Forecasting: Linear Regression
    💰 Optimization: Profit Heatmap
    🚢 Risk Engine: Stochastic RSS

    *Built by Sandesh Hegde*
    """
)

# --- MAIN PAGE ---
st.title("📦 Digital Capacity Optimizer")

# 1. LOAD DATA
df = None
if source_option == "🔌 Live Database":
    # If we have a selected SKU, filter by it.
    if selected_sku:
        df = load_data_from_db(selected_sku)
    else:
        df = pd.DataFrame()
else:
    # Sandbox Mode
    st.info("Sandbox Mode: Upload a CSV to simulate different demand scenarios.")
    uploaded_file = st.file_uploader("Upload CSV", type=["csv"])
    if uploaded_file:
        df = load_data_from_csv(uploaded_file)

# --- EXECUTIVE COMMAND CENTER (Always Visible if DB Connected) ---
if source_option == "🔌 Live Database":
    st.markdown("### 🚁 Executive Command Center")
    summary_df = get_inventory_summary()

    if not summary_df.empty:
        # Style the Data (Highlight Alerts)
        def highlight_risk(val):
            if 'Surge' in str(val): return 'color: red; font-weight: bold'
            if 'Normal' in str(val): return 'color: green; font-weight: bold'
            return 'color: orange'


        styled_df = summary_df.style.map(highlight_risk, subset=['Status'])

        st.dataframe(
            styled_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Last Update": st.column_config.DateColumn("Last Update"),
                "Latest Demand": st.column_config.ProgressColumn("Latest Demand", format="%d", min_value=0,
                                                                 max_value=int(summary_df['Latest Demand'].max() + 10)),
            }
        )
    else:
        st.info("No data found. Add your first product in the sidebar!")

    st.divider()

# --- MAIN ANALYSIS TABS ---
if df is not None and not df.empty:

    # --- MATH ENGINE (Advanced) ---
    avg_demand = df['demand'].mean()
    std_dev_demand = df['demand'].std()
    if pd.isna(std_dev_demand): std_dev_demand = 0.0

    # A. Optimal SLA (Cost-Based)
    actual_sla = inventory_math.calculate_newsvendor_target(holding_cost, stockout_cost)

    # B. Safety Stock (Risk-Adjusted)
    sim_safety_stock = inventory_math.calculate_advanced_safety_stock(
        avg_demand,
        std_dev_demand,
        lead_time_months,
        lead_time_volatility,
        sim_sla / 100.0
    )

    # C. EOQ
    eoq = inventory_math.calculate_eoq(avg_demand * 12, config.ORDER_COST, holding_cost)

    metrics_context = {
        "avg_demand": int(avg_demand),
        "std_dev": int(std_dev_demand),
        "lead_time": lead_time_months,
        "lead_time_risk": lead_time_volatility,
        "eoq": int(eoq),
        "safety_stock": int(sim_safety_stock),
        "sla": sim_sla / 100.0,
        "actual_sla": actual_sla,
        "product_name": selected_sku if selected_sku else "Sandbox Data"
    }

    if source_option == "🔌 Live Database" and not selected_sku:
        st.warning("Please select a product from the sidebar to view detailed analytics.")
    else:
        # --- CREATE TABS ---
        tab1, tab2 = st.tabs(["📊 Inventory Dashboard", "💰 Profit Optimizer"])

        # ==========================
        # TAB 1: EXISTING DASHBOARD
        # ==========================
        with tab1:
            st.subheader(f"📈 Demand Trends: {metrics_context['product_name']}")

            col_chart_1, col_chart_2 = st.columns([3, 1])
            with col_chart_2:
                show_forecast = st.checkbox("🔮 Show AI Demand Forecast", value=True, key="forecast_toggle")

            fig = go.Figure()

            # 1. Plot Historical Data (Solid Green Line)
            fig.add_trace(go.Scatter(
                x=df['date'], y=df['demand'],
                mode='lines+markers', name='Actual History',
                line=dict(color='#2ca02c', width=3)
            ))

            # 2. Calculate & Plot Forecast (Dashed Blue Line)
            if show_forecast:
                forecast_df = forecast.generate_forecast(df)

                if forecast_df is not None:
                    # Connect lines
                    last_hist_date = df['date'].max()
                    last_hist_val = df.loc[df['date'] == last_hist_date, 'demand'].values[0]
                    bridge_df = pd.DataFrame({'date': [last_hist_date], 'demand': [last_hist_val]})
                    plot_forecast = pd.concat([bridge_df, forecast_df])

                    fig.add_trace(go.Scatter(
                        x=plot_forecast['date'], y=plot_forecast['demand'],
                        mode='lines+markers', name='Projected Forecast',
                        line=dict(color='#1f77b4', width=3, dash='dash')
                    ))
                else:
                    st.warning("Not enough data to generate a forecast yet (Need 2+ points).")

            st.plotly_chart(fig, use_container_width=True)

            # B. Display Key Metrics
            st.markdown("### 🔮 Planning Engine")

            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Avg Monthly Demand", f"{int(avg_demand)}")
            c2.metric("Optimal SLA (Cost-Based)", f"{actual_sla * 100:.1f}%")

            c3.metric(
                label=f"Safety Stock ({sim_sla}%)",
                value=f"{int(sim_safety_stock)}",
                delta="Includes Lead Time Risk",
                delta_color="off"
            )

            c4.metric("Optimal Order (EOQ)", f"{int(eoq)}")

            st.markdown("---")

            # C. Executive Reporting
            st.subheader("📑 Executive Reporting")

            col_rep_1, col_rep_2 = st.columns([3, 1])

            with col_rep_1:
                st.caption("Generate a PDF summary of the current simulation parameters and AI risk assessment.")

            with col_rep_2:
                if st.button("📄 Generate Report"):
                    with st.spinner("Asking AI to write summary..."):
                        summary_prompt = f"Write a 4-sentence executive summary for product '{metrics_context['product_name']}'. Be professional."
                        ai_summary = ai_brain.chat_with_data(summary_prompt, [], df, metrics_context)

                    with st.spinner("Rendering PDF..."):
                        pdf_bytes = report_gen.generate_pdf(metrics_context, ai_summary)

                        st.download_button(
                            label="⬇️ Download PDF",
                            data=pdf_bytes,
                            file_name=f"inventory_report_{metrics_context['product_name']}.pdf",
                            mime="application/pdf"
                        )

            st.markdown("---")

            # D. The Conversational AI
            col_title, col_btn = st.columns([5, 1])

            with col_title:
                st.subheader(f"💬 Chat about {metrics_context['product_name']}")

            with col_btn:
                if st.button("🗑️ Clear", help="Reset Chat History"):
                    st.session_state.messages = []
                    st.rerun()

            if "messages" not in st.session_state:
                st.session_state.messages = []

            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

            if prompt := st.chat_input("Ask about your inventory..."):

                with st.chat_message("user"):
                    st.markdown(prompt)
                st.session_state.messages.append({"role": "user", "content": prompt})

                gemini_history = []
                for msg in st.session_state.messages[:-1]:
                    role = "user" if msg["role"] == "user" else "model"
                    gemini_history.append({"role": role, "parts": [msg["content"]]})

                with st.chat_message("assistant"):
                    with st.spinner("Thinking..."):
                        response_text = ai_brain.chat_with_data(prompt, gemini_history, df, metrics_context)
                        st.markdown(response_text)

                st.session_state.messages.append({"role": "assistant", "content": response_text})

        # ==========================
        # TAB 2: PROFIT OPTIMIZER
        # ==========================
        with tab2:
            st.subheader(f"💸 Profit Simulator: {metrics_context['product_name']}")

            st.markdown("Use this tool to find the 'Sweet Spot' between ordering too much and too little.")

            c_input1, c_input2 = st.columns(2)
            unit_cost = c_input1.number_input("Manufacturing Unit Cost ($)", value=50.0, step=1.0)
            selling_price = c_input2.number_input("Retail Selling Price ($)", value=85.0, step=1.0)

            if selling_price <= unit_cost:
                st.error("⚠️ Selling Price must be higher than Unit Cost to generate profit!")
            else:
                heatmap_fig = profit_optimizer.calculate_profit_scenarios(
                    avg_demand, std_dev_demand, holding_cost, stockout_cost, unit_cost, selling_price
                )
                st.plotly_chart(heatmap_fig, use_container_width=True)

                st.info(
                    """
                    **How to read this Heatmap:**
                    * **Blue Areas 🔵:** High Profit zones.
                    * **Red Areas 🔴:** Loss zones (Overstocking or Stockouts).
                    """
                )

    # --- NEW: DATA MANAGEMENT SECTION ---
    if source_option == "🔌 Live Database":
        st.markdown("---")
        with st.expander("🗑️ Manage Records (Delete Data)"):
            st.warning("⚠️ Warning: Deleting records is permanent.")

            # Show Raw Data with IDs
            if df is not None:
                display_df = df[['id', 'date', 'product_name', 'demand']].sort_values('date', ascending=False)
                st.dataframe(display_df, use_container_width=True, hide_index=True)

            # Delete Interface
            c_del_1, c_del_2 = st.columns([1, 4])
            with c_del_1:
                id_to_delete = st.number_input("Enter ID to Delete", min_value=1, step=1)
            with c_del_2:
                st.write("")
                st.write("")
                if st.button("🗑️ Delete Record"):
                    if delete_order(id_to_delete):
                        st.success(f"✅ Record #{id_to_delete} deleted!")
                        st.rerun()

# --- FOOTER ---
st.markdown("---")
st.caption("© 2026 Digital Capacity Inc. | Powered by SQL, Neon & Google Gemini 🧠")