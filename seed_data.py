import os
import psycopg2
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
DB_URL = os.getenv("DATABASE_URL")
if not DB_URL:
    raise ValueError("❌ DATABASE_URL is missing from .env")


def generate_research_data():
    print("🧪 Generating PhD-grade LSP datasets...")

    data = []
    end_date = datetime.today()
    start_date = end_date - timedelta(days=365)
    dates = pd.date_range(start=start_date, end=end_date, freq='D')

    # --- SCENARIO 1: BER-MUC (E-Commerce High Volatility) ---
    # Story: High noise, seasonal peaks (Q4), used for Return Logic
    base_demand = 100
    for d in dates:
        # Add Seasonality (Sine wave) + Random Noise
        seasonality = 20 * np.sin(2 * np.pi * d.dayofyear / 365)
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
        if np.random.random() > 0.95:  # 5% chance of massive shock
            shock = 100
        else:
            shock = 0

        noise = np.random.normal(0, 5)
        demand = int(max(0, base_demand + noise + shock))
        data.append((d.date(), "FRA-PAR (Pharma)", demand))

    return data


def seed_database():
    try:
        # Connect to Database
        conn = psycopg2.connect(DB_URL)
        cur = conn.cursor()

        print("🔌 Connected to Database.")

        # 1. CREATE TABLE IF MISSING (The Fix)
        print("🛠️  Checking table schema...")
        create_table_query = """
        CREATE TABLE IF NOT EXISTS inventory_logs (
            id SERIAL PRIMARY KEY,
            date DATE NOT NULL,
            product_name TEXT NOT NULL,
            demand INTEGER NOT NULL
        );
        """
        cur.execute(create_table_query)

        # 2. WIPE OLD DATA
        print("🗑️  Clearing old data...")
        cur.execute("DELETE FROM inventory_logs;")

        # 3. INSERT NEW DATA
        print("💾 Injecting new Service Lane data...")
        data = generate_research_data()

        query = "INSERT INTO inventory_logs (date, product_name, demand) VALUES (%s, %s, %s)"
        cur.executemany(query, data)

        conn.commit()
        print(f"✅ Success! {len(data)} records inserted.")
        print("🚀 Your LSP Digital Twin is now running on research data.")

        cur.close()
        conn.close()

    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    confirm = input("⚠️  This will DELETE all existing data. Type 'yes' to proceed: ")
    if confirm.lower() == "yes":
        seed_database()
    else:
        print("❌ Operation cancelled.")