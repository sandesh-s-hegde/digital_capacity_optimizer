"""
config.py
Centralized configuration for simulation parameters.
"""

# Financial Parameters (USD)
ORDER_COST = 450.00         # Cost to place one Purchase Order
HOLDING_COST = 18.50        # Annual cost to store/power one unit

# NEW: Cost of being out of stock (Service Credits / Reputation Damage)
# This is usually much higher than holding cost.
STOCKOUT_COST = 2000.00

# Simulation Defaults
DEFAULT_LEAD_TIME = 14      # Days