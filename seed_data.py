import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from dotenv import load_dotenv
import db_manager

# 1. LOAD ENVIRONMENT VARIABLES
load_dotenv()


def generate_research_data():
    """
    Generates stochastic demand patterns for 3 specific global supply chain scenarios.
    Upgraded for Production: Includes trend lines, DoW seasonality, and structural market shocks.
    """
    print("🧪 Generating Production-Grade Global Logistics Datasets (2 Years)...")

    data = []
    end_date = datetime.today()
    # Expanded to 2 years (730 days) to allow the Forecast module to detect yearly seasonality
    start_date = end_date - timedelta(days=730)
    dates = pd.date_range(start=start_date, end=end_date, freq='D')
    days_arr = np.arange(len(dates))

    # --- SCENARIO 1: SHG-ROT (Ocean Freight - Consumer Tech) ---
    # Profile: Steady macroeconomic growth, massive Q4 Holiday peaks, occasional port congestion.
    trend_1 = days_arr * 0.15 + 200  # Linear growth over 2 years
    seasonality_1 = 40 * np.sin(2 * np.pi * days_arr / 365)  # Yearly sine wave
    noise_1 = np.random.normal(0, 15, len(dates))

    for i, d in enumerate(dates):
        surge = 120 if d.month in [11, 12] else 0  # Black Friday / Christmas
        shock = -150 if np.random.random() > 0.99 else 0  # 1% chance of Port Strike/Blank Sailing
        demand = int(max(0, trend_1[i] + seasonality_1[i] + noise_1[i] + surge + shock))
        data.append((d.date(), "SHG-ROT (Ocean/Tech)", demand))

    # --- SCENARIO 2: BOM-FRA (China Plus One - Apparel/Pharma) ---
    # Profile: Aggressive growth trend (representing shifting supply chains), high volatility.
    trend_2 = days_arr * 0.35 + 80  # Steeper growth as sourcing shifts to India
    noise_2 = np.random.normal(0, 35, len(dates))  # Higher variance (emerging lane)

    for i, d in enumerate(dates):
        # Quarter-end push (The "Hockey Stick" effect common in B2B logistics)
        q_end_push = 80 if d.day > 25 and d.month in [3, 6, 9, 12] else 0
        demand = int(max(0, trend_2[i] + noise_2[i] + q_end_push))
        data.append((d.date(), "BOM-FRA (Air/Apparel)", demand))

    # --- SCENARIO 3: BER-MUC (Domestic Road - FMCG) ---
    # Profile: Flat macro trend, but EXTREME Day-of-Week (DoW) seasonality.
    trend_3 = np.full(len(dates), 300)  # Flat baseline

    for i, d in enumerate(dates):
        # 0=Mon, 6=Sun. Massive drops on weekends, surge on Mondays to clear backlog.
        if d.weekday() >= 5:
            dow_effect = -220
        elif d.weekday() == 0:
            dow_effect = 90
        else:
            dow_effect = 0

        noise_3 = np.random.normal(0, 12)
        demand = int(max(0, trend_3[i] + dow_effect + noise_3))
        data.append((d.date(), "BER-MUC (Road/FMCG)", demand))

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
        print("🚀 v4.2.6 is now populated with Production-Grade Multi-Modal Data.")

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
