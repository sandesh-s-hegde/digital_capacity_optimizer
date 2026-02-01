import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_csv():
    print("🧪 Generating PhD-grade LSP dataset...")

    data = []
    end_date = datetime.today()
    start_date = end_date - timedelta(days=365)
    dates = pd.date_range(start=start_date, end=end_date, freq='D')

    # --- SCENARIO 1: BER-MUC (E-Commerce High Volatility) ---
    # Story: Seasonal peaks (Q4) + Random noise. Used for Reverse Logistics logic.
    base_demand = 100
    for d in dates:
        seasonality = 20 * np.sin(2 * np.pi * d.dayofyear / 365)
        noise = np.random.normal(0, 25)
        spike = 50 if d.month in [11, 12] else 0
        demand = int(max(0, base_demand + seasonality + noise + spike))
        data.append({"date": d.date(), "product_name": "BER-MUC (E-Com)", "demand": demand})

    # --- SCENARIO 2: HAM-ROT (Industrial Overflow) ---
    # Story: Consistently OVER capacity (Base 160 vs Cap 150). Triggers Horizontal Cooperation.
    base_demand = 160
    for d in dates:
        noise = np.random.normal(0, 10)
        demand = int(max(0, base_demand + noise))
        data.append({"date": d.date(), "product_name": "HAM-ROT (Indus)", "demand": demand})

    # --- SCENARIO 3: FRA-PAR (Pharma Shock) ---
    # Story: Low volume but massive shocks. Lowers Resilience Score.
    base_demand = 50
    for d in dates:
        shock = 100 if np.random.random() > 0.95 else 0
        noise = np.random.normal(0, 5)
        demand = int(max(0, base_demand + noise + shock))
        data.append({"date": d.date(), "product_name": "FRA-PAR (Pharma)", "demand": demand})

    # Save to CSV
    df = pd.DataFrame(data)
    filename = "research_data.csv"
    df.to_csv(filename, index=False)
    print(f"✅ Success! Generated {len(df)} rows in '{filename}'")


if __name__ == "__main__":
    generate_csv()