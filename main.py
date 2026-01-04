"""
main.py
Digital Capacity Optimizer v3.0 - Scenario Analysis Edition
"""
from azure_model import REGIONS
from inventory_math import calculate_eoq, calculate_safety_stock
from data_loader import load_data
from visualizer import plot_scenario_comparison
from scenario_manager import create_stress_test
import config

def analyze_inventory(df, label):
    """
    Helper function to calculate metrics for a specific dataset.
    """
    total_annual_demand = df['demand'].sum()
    max_daily_demand = df['demand'].max() / 30
    avg_daily_demand = df['demand'].mean() / 30
    avg_lead_time = df['lead_time_days'].mean()

    eoq = calculate_eoq(total_annual_demand, config.ORDER_COST, config.HOLDING_COST)
    ss = calculate_safety_stock(max_daily_demand, avg_daily_demand, avg_lead_time)

    return {
        "label": label,
        "eoq": eoq,
        "safety_stock": round(ss, 2),
        "total_reserve": round(eoq + ss, 2)
    }

def run_simulation():
    print("--- 🏭 Digital Capacity Optimizer v4.0 (Azure Edition) ---")
    selected_region = "west-europe"
    region_info = REGIONS[selected_region]
    print(f"🌍 Target Region: {region_info['name']}")
    print(f"🚛 Shipping SLA: {region_info['shipping_delay_days']} days")

    # 1. Load Baseline Data
    df_baseline = load_data('mock_data.csv')
    if df_baseline.empty: return

    # 2. Create "High Growth" Scenario (20% Demand Increase)
    df_growth = create_stress_test(df_baseline, demand_multiplier=1.20, lead_time_multiplier=1.0)

    # 3. Visualize Comparison
    plot_scenario_comparison(df_baseline, df_growth, "High Growth (+20%)")

    # 4. Calculate & Compare Metrics
    stats_base = analyze_inventory(df_baseline, "Baseline")
    stats_growth = analyze_inventory(df_growth, "High Growth")

    # 5. Print Executive Report
    print(f"\n📊 SCENARIO COMPARISON REPORT")
    print(f"{'Metric':<20} | {'Baseline':<15} | {'High Growth':<15} | {'Delta'}")
    print("-" * 65)

    for key in ['eoq', 'safety_stock', 'total_reserve']:
        val_base = stats_base[key]
        val_growth = stats_growth[key]
        delta = round(val_growth - val_base, 2)
        print(f"{key:<20} | {val_base:<15} | {val_growth:<15} | {delta:+}")

    print("-" * 65)
    print("✅ Analysis Complete. Check 'scenario_comparison.png' for visuals.")

if __name__ == "__main__":
    run_simulation()