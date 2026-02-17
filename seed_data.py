import os
from dotenv import load_dotenv
import db_manager
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# 1. LOAD ENVIRONMENT VARIABLES
load_dotenv()


def generate_research_data():
    """
    Generates stochastic demand patterns for 3 specific supply chain scenarios.
    """
    print("🧪 Generating PhD-grade LSP datasets...")

    data = []
    end_date = datetime.today()
    start_date = end_date - timedelta(days=365)
    dates = pd.date_range(start=start_date, end=end_date, freq='D')

    # --- SCENARIO 1: BER-MUC (E-Commerce High Volatility) ---
    base_demand = 100
    for d in dates:
        day_index = d.dayofyear
        seasonality = 20 * np.sin(2 * np.pi * day_index / 365)
        noise = np.random.normal(0, 25)
        spike = 50 if d.month in [11, 12] else 0
        demand = int(max(0, base_demand + seasonality + noise + spike))
        data.append((d.date(), "BER-MUC (E-Com)", demand))

    # --- SCENARIO 2: HAM-ROT (Industrial Overflow) ---
    base_demand = 160
    for d in dates:
        noise = np.random.normal(0, 10)
        demand = int(max(0, base_demand + noise))
        data.append((d.date(), "HAM-ROT (Indus)", demand))

    # --- SCENARIO 3: FRA-PAR (Pharma Shock) ---
    base_demand = 50
    for d in dates:
        if np.random.random() > 0.95:
            shock = 100
        else:
            shock = 0
        noise = np.random.normal(0, 5)
        demand = int(max(0, base_demand + noise + shock))
        data.append((d.date(), "FRA-PAR (Pharma)", demand))

    return data


def seed_database():
    # DEBUG CHECK
    if not os.getenv("DATABASE_URL"):
        print("❌ Error: DATABASE_URL not found. Did you create a .env file?")
        return

    try:
        conn = db_manager.get_db_connection()
        if not conn:
            print("❌ Failed to connect via db_manager. Check your URL credentials.")
            return

        cur = conn.cursor()
        print("🔌 Connected to Database via db_manager.")

        print("🗑️  Clearing old simulation data...")
        cur.execute("DELETE FROM inventory;")

        raw_data = generate_research_data()

        print(f"💾 Injecting {len(raw_data)} records into 'inventory' table...")
        query = "INSERT INTO inventory (date, product_name, demand) VALUES (%s, %s, %s)"
        cur.executemany(query, raw_data)
        conn.commit()

        print(f"✅ Success! {len(raw_data)} records inserted.")
        print("🚀 v4.2.0 is now populated with Multi-Modal Research Data.")

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
