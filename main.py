"""
main.py
Digital Capacity Optimizer v5.0 - Reliability Edition
"""
import pandas as pd
from inventory_math import calculate_eoq, calculate_safety_stock, calculate_service_level
from data_loader import load_data
from visualizer import plot_scenario_comparison
from scenario_manager import create_stress_test
import config

def analyze_risk(df, label, shock_factor=0.0):
    """
    Calculates Inventory Health and Service Level (SLA) under risk.
    """
    # 1. Basic Stats
    total_annual_demand = df['demand'].sum()
    avg_monthly_demand = df['demand'].mean()
    std_dev_demand = df['demand'].std() # Volatility

    # 2. Optimization
    eoq = calculate_eoq(total_annual_demand, config.ORDER_COST, config.HOLDING_COST)
    ss = calculate_safety_stock(df['demand'].max()/30, df['demand'].mean()/30, df['lead_time_days'].mean())

    # 3. Apply Shock (e.g., Zone Failure destroys inventory)
    total_inventory = (eoq + ss) * (1.0 - shock_factor)

    # 4. Calculate SLA (Probability of survival)
    sla = calculate_service_level(avg_monthly_demand, std_dev_demand, total_inventory)

    return {
        "label": label,
        "inventory": round(total_inventory, 2),
        "sla_percent": round(sla * 100, 2),
        "status": "✅ Safe" if sla > 0.99 else "❌ RISK"
    }

def run_simulation():
    print("--- 🏭 Digital Capacity Optimizer v5.0 (Reliability Mode) ---")

    df_baseline = load_data('mock_data.csv')
    if df_baseline.empty: return

    # Scenario 1: Normal Operations
    stats_normal = analyze_risk(df_baseline, "Normal Ops", shock_factor=0.0)

    # Scenario 2: Zone Failure (10% Capacity Loss)
    # Simulating a fire or power outage in one Availability Zone
    stats_shock = analyze_risk(df_baseline, "Zone Outage", shock_factor=0.10)

    # Print Report
    print(f"\n📊 RELIABILITY REPORT (Target SLA: 99.0%)")
    print(f"{'Scenario':<15} | {'Inventory':<15} | {'SLA %':<10} | {'Status'}")
    print("-" * 60)

    for stats in [stats_normal, stats_shock]:
        print(f"{stats['label']:<15} | {stats['inventory']:<15} | {stats['sla_percent']:<10} | {stats['status']}")

    print("-" * 60)

    # Alert Logic
    if stats_shock['sla_percent'] < 99.0:
        print("⚠️ CRITICAL ALERT: Resilience falls below 99% during Zone Outage.")
        print("   -> Recommendation: Increase Safety Stock by 15% to buffer risk.")

if __name__ == "__main__":
    run_simulation()