"""
main.py
Simulation entry point for Microsoft Munich Data Center scenario.
"""
from inventory_math import calculate_eoq, calculate_safety_stock

# Simulation Parameters (Munich Region)
ANNUAL_DEMAND = 12000       # Server Racks
ORDER_COST = 450.00         # Admin cost per PO
HOLDING_COST = 18.50        # Storage/Power cost per unit

# Risk Parameters
MAX_DAILY = 50
AVG_DAILY = 33
LEAD_TIME = 14              # Days

def run_simulation():
    print("--- 🏭 Digital Capacity Optimizer: Munich ---")

    # 1. EOQ Calculation
    eoq = calculate_eoq(ANNUAL_DEMAND, ORDER_COST, HOLDING_COST)
    print(f"✅ Optimal Order Quantity (EOQ): {eoq} units")

    # 2. Safety Stock Calculation
    ss = calculate_safety_stock(MAX_DAILY, AVG_DAILY, LEAD_TIME)
    print(f"🛡️ Safety Stock Buffer: {ss} units")

    # 3. Total Procurement
    total = eoq + ss
    print(f"🚀 TOTAL TARGET INVENTORY: {total} units")

if __name__ == "__main__":
    run_simulation()