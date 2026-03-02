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


def generate_research_data() -> List[Tuple[datetime.date, str, int]]:
    """Generates stochastic demand patterns for global supply chain scenarios over a 2-year horizon."""
    logger.info("Generating production-grade global logistics datasets (2-year horizon)...")

    np.random.seed(42)  # Enforce determinism for academic reproducibility

    data = []
    end_date = datetime.today()
    start_date = end_date - timedelta(days=730)
    dates = pd.date_range(start=start_date, end=end_date, freq='D')
    days_arr = np.arange(len(dates))

    # --- Scenario 1: SHG-ROT (Ocean Freight - Consumer Tech) ---
    trend_1 = days_arr * 0.15 + 200
    seasonality_1 = 40 * np.sin(2 * np.pi * days_arr / 365)
    noise_1 = np.random.normal(0, 15, len(dates))

    for i, d in enumerate(dates):
        surge = 120 if d.month in [11, 12] else 0
        shock = -150 if np.random.random() > 0.99 else 0
        demand = int(max(0, trend_1[i] + seasonality_1[i] + noise_1[i] + surge + shock))
        data.append((d.date(), "SHG-ROT (Ocean/Tech)", demand))

    # --- Scenario 2: BOM-FRA (China Plus One - Apparel/Pharma) ---
    trend_2 = days_arr * 0.35 + 80
    noise_2 = np.random.normal(0, 35, len(dates))

    for i, d in enumerate(dates):
        q_end_push = 80 if d.day > 25 and d.month in [3, 6, 9, 12] else 0
        demand = int(max(0, trend_2[i] + noise_2[i] + q_end_push))
        data.append((d.date(), "BOM-FRA (Air/Apparel)", demand))

    # --- Scenario 3: BER-MUC (Domestic Road - FMCG) ---
    trend_3 = np.full(len(dates), 300)

    for i, d in enumerate(dates):
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


def seed_database() -> None:
    """Clears existing data and injects synthetic research records into the database."""
    if not os.getenv("DATABASE_URL"):
        logger.error("DATABASE_URL not found in environment variables.")
        return

    try:
        conn = db_manager.get_db_connection()
        if not conn:
            logger.error("Failed to connect via db_manager. Check URL credentials.")
            return

        logger.info("Connected to database.")

        with conn.cursor() as cur:
            logger.info("Clearing old simulation data...")
            cur.execute("DELETE FROM inventory;")

            raw_data = generate_research_data()

            logger.info("Injecting %d records into inventory table...", len(raw_data))
            query = "INSERT INTO inventory (date, product_name, demand) VALUES (%s, %s, %s)"
            cur.executemany(query, raw_data)
            conn.commit()

        logger.info("Successfully inserted %d records. System is now populated.", len(raw_data))

    except Exception as e:
        logger.error("Error during seeding: %s", e)
    finally:
        if 'conn' in locals() and conn:
            conn.close()


if __name__ == "__main__":
    logger.warning("This operation will wipe the 'inventory' table on the target database.")
    confirm = input("Type 'yes' to proceed with Research Data Injection: ")

    if confirm.lower().strip() == "yes":
        seed_database()
    else:
        logger.info("Operation cancelled.")
