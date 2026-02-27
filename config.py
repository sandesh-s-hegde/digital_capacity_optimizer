import os

ORDER_COST = float(os.getenv("ORDER_COST", 450.00))
HOLDING_COST = float(os.getenv("HOLDING_COST", 18.50))
STOCKOUT_COST = float(os.getenv("STOCKOUT_COST", 2000.00))

DEFAULT_LEAD_TIME = int(os.getenv("DEFAULT_LEAD_TIME", 14))
