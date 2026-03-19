import os
import logging
from datetime import datetime, timedelta
from typing import List, Tuple

import pandas as pd
import numpy as np
from dotenv import load_dotenv

import db_manager

# Configure enterprise-grade logging
load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def generate_complex_scenarios() -> List[Tuple[datetime.date, str, int]]:
    """
    Generates a high-volume, fully vectorized dataset representing 10 strategic
    global supply chain lanes over a 5-year horizon (approx. 18,250 records).
    """
    logger.info("Initializing 5-year vectorized macroeconomic scenario generation...")
    np.random.seed(42)

    # 5-Year Time Horizon
    end_date = datetime.today()
    start_date = end_date - timedelta(days=1825)
    dates = pd.date_range(start=start_date, end=end_date, freq='D')
    days_arr = np.arange(len(dates))

    # Pre-calculate date features for rapid vectorization
    months = dates.month
    days = dates.day
    is_weekend = dates.weekday >= 5

    raw_data = []

    # --- Scenario Dictionary: [Name, Base Demand, Growth Rate, Volatility] ---
    scenarios = {
        "SHG-ROT (Ocean/Tech + CBAM)": {"base": 250, "growth": 0.05, "vol": 25},
        "IST-MUC (Nearshore/Auto)": {"base": 100, "growth": 0.15, "vol": 12},
        "SCL-FRA (Air/Lithium EV)": {"base": 50, "growth": 0.25, "vol": 35},
        "BOM-LHR (Air/Pharma)": {"base": 120, "growth": 0.08, "vol": 10},
        "SGP-LAX (Ocean/Semiconductors)": {"base": 300, "growth": 0.10, "vol": 40},
        "MEX-DTW (Rail/Nearshore Mfg)": {"base": 180, "growth": 0.20, "vol": 15},
        "VNM-SEA (Ocean/Apparel C+1)": {"base": 140, "growth": 0.18, "vol": 20},
        "DXB-CDG (Air/Luxury)": {"base": 40, "growth": 0.02, "vol": 5},
        "SAO-MIA (Air/Agriculture)": {"base": 200, "growth": 0.05, "vol": 30},
        "TPE-NRT (Air/Components)": {"base": 220, "growth": 0.04, "vol": 45}
    }

    logger.info("Computing vectorized demand matrices for %d global lanes...", len(scenarios))

    for lane, params in scenarios.items():
        # 1. Base Trend & Noise
        trend = days_arr * params["growth"] + params["base"]
        noise = np.random.normal(0, params["vol"], len(dates))

        # 2. Universal Seasonality (Sine wave)
        seasonality = (params["base"] * 0.15) * np.sin(2 * np.pi * days_arr / 365)

        # 3. Vectorized Shocks & Surges
        surge = np.where(np.isin(months, [10, 11]), params["base"] * 0.3, 0)
        q_end_push = np.where((days > 25) & np.isin(months, [3, 6, 9, 12]), params["base"] * 0.2, 0)

        # Macro-shocks (1% chance of severe disruption)
        shock_matrix = np.where(np.random.random(len(dates)) > 0.99, -params["base"] * 0.6, 0)

        # 4. Final Matrix Calculation
        total_demand = trend + seasonality + noise + surge + q_end_push + shock_matrix
        total_demand = np.maximum(0, np.round(total_demand)).astype(int)

        # 5. Append to dataset
        lane_data = list(zip(dates.date, [lane] * len(dates), total_demand.tolist()))
        raw_data.extend(lane_data)

    return raw_data


def seed_database() -> None:
    """Executes a high-performance batch insertion into the cloud PostgreSQL instance."""
    if not os.getenv("DATABASE_URL"):
        logger.error("DATABASE_URL not found in environment variables.")
        return

    try:
        conn = db_manager.get_db_connection()
        if not conn:
            logger.error("Failed to connect via db_manager. Check URL credentials.")
            return

        with conn.cursor() as cur:
            logger.info("Verifying/Creating schema for 'inventory' table...")
            cur.execute("""
                CREATE TABLE IF NOT EXISTS inventory (
                    id SERIAL PRIMARY KEY,
                    date DATE NOT NULL,
                    product_name TEXT NOT NULL,
                    demand INTEGER NOT NULL
                );
            """)

            logger.info("Flushing legacy transactional data from 'inventory' table...")
            cur.execute("TRUNCATE TABLE inventory RESTART IDENTITY;")  # Faster than DELETE

            raw_data = generate_complex_scenarios()

            logger.info("Executing batch insertion of %d records...", len(raw_data))

            # Using executemany for safe, parameterized batch inserts
            query = "INSERT INTO inventory (date, product_name, demand) VALUES (%s, %s, %s)"
            cur.executemany(query, raw_data)
            conn.commit()

        logger.info("Stress test injection complete. Database is armed and ready.")

    except Exception as e:
        logger.error("Critical error during database seeding: %s", e)
        if conn:
            conn.rollback()
    finally:
        if 'conn' in locals() and conn:
            conn.close()


if __name__ == "__main__":
    logger.warning("Executing this script will OVERWRITE the production database.")
    confirm = input("Type 'yes' to proceed with High-Volume Data Injection: ")

    if confirm.lower().strip() == "yes":
        seed_database()
    else:
        logger.info("Operation safely aborted.")
