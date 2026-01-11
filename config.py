"""
config.py
Centralized configuration for simulation parameters.
Reads from Environment Variables for Cloud/Docker overrides.
"""
import os

# Financial Parameters (USD)
# Uses os.getenv to allow server-side overrides
ORDER_COST = float(os.getenv("ORDER_COST", 450.00))
HOLDING_COST = float(os.getenv("HOLDING_COST", 18.50))
STOCKOUT_COST = float(os.getenv("STOCKOUT_COST", 2000.00))

# Simulation Defaults
DEFAULT_LEAD_TIME = int(os.getenv("DEFAULT_LEAD_TIME", 14))