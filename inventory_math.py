"""
inventory_math.py
Core optimization logic for inventory management.
"""
import math
from scipy.stats import norm

def calculate_eoq(annual_demand, order_cost, holding_cost):
    """
    Calculates Economic Order Quantity (EOQ).
    Formula: Sqrt(2 * Demand * Order_Cost / Holding_Cost)
    """
    if holding_cost == 0: return 0.0
    return math.sqrt((2 * annual_demand * order_cost) / holding_cost)

def calculate_safety_stock(max_daily_demand, avg_daily_demand, lead_time):
    """
    Calculates Buffer Stock to survive delays.
    Formula: (Max_Daily_Usage * Max_Lead_Time) - (Avg_Daily_Usage * Avg_Lead_Time)
    Note: Simplistic version.
    """
    return (max_daily_demand - avg_daily_demand) * lead_time

def calculate_service_level(avg_demand, std_dev_demand, total_inventory): # <--- NEW FUNCTION
    """
    Calculates the probability (%) of NOT running out of stock (SLA).
    Uses Normal Distribution (Z-Score).

    Args:
        avg_demand (float): Average monthly demand
        std_dev_demand (float): Volatility of demand
        total_inventory (float): Stock on hand

    Returns:
        float: Service Level (e.g., 0.99 for 99%)
    """
    if std_dev_demand == 0:
        return 1.0 if total_inventory >= avg_demand else 0.0

    # Z = (Stock - Mean) / Volatility
    z_score = (total_inventory - avg_demand) / std_dev_demand

    # Convert Z-score to Percentage (0 to 1)
    probability = norm.cdf(z_score)
    return round(probability, 4)