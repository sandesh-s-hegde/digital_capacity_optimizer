"""
main.py
Advanced Simulation entry point using CSV Data and Visualization.
"""
from inventory_math import calculate_eoq, calculate_safety_stock
from data_loader import load_data
from visualizer import plot_demand_curve

# Global Parameters (Constants)
ORDER_COST = 450.00  # $ Admin cost per PO
HOLDING_COST = 18.50  # $ Cost to keep one drive powered/cooled for a year


def run_simulation():
    print("--- 🏭 Digital Capacity Optimizer v2.0 ---")

    # 1. Load Real Data
    print("Step 1: Loading Usage Logs...")
    df = load_data('mock_data.csv')

    # Stop if data is missing
    if df.empty:
        print("Stopping simulation due to missing data.")
        return

    # 2. Visualize Data
    print("Step 2: Generating Dashboard...")
    plot_demand_curve(df)

    # 3. Analyze Statistics from Data
    total_annual_demand = df['demand'].sum()

    # Calculate simple stats for Safety Stock logic
    # (Assuming 30 days per month for simplicity)
    max_daily_demand = df['demand'].max() / 30
    avg_daily_demand = df['demand'].mean() / 30
    avg_lead_time = df['lead_time_days'].mean()

    print(f"📈 Analyzed {len(df)} months of log data.")
    print(f"   -> Annual Demand: {total_annual_demand} units")
    print(f"   -> Avg Lead Time: {round(avg_lead_time, 1)} days")

    # 4. Calculate Optimization Metrics
    eoq = calculate_eoq(total_annual_demand, ORDER_COST, HOLDING_COST)
    ss = calculate_safety_stock(max_daily_demand, avg_daily_demand, avg_lead_time)

    print("-" * 40)
    print(f"✅ Optimal Order Quantity (EOQ): {eoq} units")
    print(f"🛡️ Safety Stock Buffer: {round(ss, 2)} units")
    print("-" * 40)


if __name__ == "__main__":
    run_simulation()