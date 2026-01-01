"""
inventory_math.py
Core Operations Research (OR) algorithms for inventory control.
"""
import math

def calculate_eoq(annual_demand: int, ordering_cost: float, holding_cost: float) -> float:
    """
    Calculates Economic Order Quantity (EOQ).
    Formula: Sqrt((2 * D * S) / H)
    """
    if holding_cost <= 0:
        return 0.0
    try:
        return round(math.sqrt((2 * annual_demand * ordering_cost) / holding_cost), 2)
    except ValueError:
        return 0.0

def calculate_safety_stock(max_daily_demand: int, avg_daily_demand: int, lead_time: int) -> int:
    """
    Calculates Safety Stock buffer against supply chain variability.
    Formula: (Max Demand * LT) - (Avg Demand * LT)
    """
    return max(0, (max_daily_demand * lead_time) - (avg_daily_demand * lead_time))