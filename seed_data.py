import db_manager
import pandas as pd
import numpy as np
from datetime import datetime, timedelta


def generate_research_data():
    """
    Generates stochastic demand patterns for 3 specific supply chain scenarios.
    Ref: 'Pixels to Premiums' Framework - Volatility & Seasonality Modeling.
    """
    print("🧪 Generating PhD-grade LSP datasets...")

    data = []
    # Generate data for the last 365 days
    end_date = datetime.today()
    start_date = end_date - timedelta(days=365)
    dates = pd.date_range(start=start_date, end=end_date, freq='D')

    # --- SCENARIO 1: BER-MUC (E-Commerce High Volatility) ---
    # Story: High noise, seasonal peaks (Q4), used for Return Logic
    base_demand = 100
    for d in dates:
        # Add Seasonality (Sine wave) + Random Noise
        day_index = d.dayofyear
        seasonality = 20 * np.sin(2 * np.pi * day_index / 365)
        noise = np.random.normal(0, 25)  # High variance

        # Christmas Spike (Nov-Dec)
        spike = 50 if d.month in [11, 12] else 0

        demand = int(max(0, base_demand + seasonality + noise + spike))
        data.append((d.date(), "BER-MUC (E-Com)", demand))

    # --- SCENARIO 2: HAM-ROT (Industrial Overflow) ---
    # Story: Stable but consistently OVER capacity to trigger Cooperation Logic
    # If your Warehouse Cap is 150, we aim for 160+ often
    base_demand = 160
    for d in dates:
        noise = np.random.normal(0, 10)  # Low variance (Industrial)
        demand = int(max(0, base_demand + noise))
        data.append((d.date(), "HAM-ROT (Indus)", demand))

    # --- SCENARIO 3: FRA-PAR (Pharma Shock) ---
    # Story: Low volume, but extreme 'shocks' for Resilience Scoring
    base_demand = 50
    for d in dates:
        # 5% chance of massive shock (e.g., pandemic spike or recall replacement)
        if np.random.random() > 0.95:
            shock = 100
        else:
            shock = 0

        noise = np.random.normal(0, 5)
        demand = int(max(0, base_demand + noise + shock))
        data.append((d.date(), "FRA-PAR (Pharma)", demand))

    return data


def seed_database():
    try:
        # Use our robust v4.0.0 connection manager (Handles SSL & Fallbacks)
        conn = db_manager.get_db_connection()
        if not conn:
            print("❌ Failed to connect via db_manager.")
            return

        cur = conn.cursor()
        print("🔌 Connected to Database via db_manager.")

        # 1. WIPE OLD DATA (Safe Reset)
        # We use DELETE instead of TRUNCATE to avoid permission issues on some cloud tiers
        print("🗑️  Clearing old simulation data...")
        cur.execute("DELETE FROM inventory;")

        # 2. GENERATE & PREPARE DATA
        raw_data = generate_research_data()

        # Convert to DataFrame for bulk upload if needed, or raw insert
        # We will use raw insert here for speed and simplicity
        print(f"💾 Injecting {len(raw_data)} records into 'inventory' table...")

        query = """
            INSERT INTO inventory (date, product_name, demand) 
            VALUES (%s, %s, %s)
        """

        cur.executemany(query, raw_data)
        conn.commit()

        print(f"✅ Success! {len(raw_data)} records inserted.")
        print("🚀 v4.0.0 is now populated with Multi-Modal Research Data.")

        cur.close()
        conn.close()

    except Exception as e:
        print(f"❌ Error during seeding: {e}")


if __name__ == "__main__":
    print("⚠️  WARNING: This will wipe the 'inventory' table on Render.")
    confirm = input("Type 'yes' to proceed with Research Data Injection: ")
    if confirm.lower().strip() == "yes":
        seed_database()
    else:
        print("❌ Operation cancelled.")
