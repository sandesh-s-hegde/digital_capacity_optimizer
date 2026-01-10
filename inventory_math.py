"""
inventory_math.py
Core optimization logic for inventory management.
Includes Stochastic models (Newsvendor) and Service Level logic.
"""
import math
from scipy.stats import norm

def calculate_eoq(annual_demand: float, order_cost: float, holding_cost: float) -> float:
    """
    Calculates Economic Order Quantity (EOQ).
    """
    if holding_cost == 0: return 0.0
    return math.sqrt((2 * annual_demand * order_cost) / holding_cost)

def calculate_safety_stock(max_daily_demand: float, avg_daily_demand: float, lead_time: int) -> float:
    """
    Calculates Buffer Stock to survive delays.
    """
    return (max_daily_demand - avg_daily_demand) * lead_time

def calculate_service_level(avg_demand: float, std_dev_demand: float, total_inventory: float) -> float:
    """
    Calculates the probability (%) of NOT running out of stock (SLA).
    """
    if std_dev_demand == 0:
        return 1.0 if total_inventory >= avg_demand else 0.0

    z_score = (total_inventory - avg_demand) / std_dev_demand
    probability = norm.cdf(z_score)
    return round(float(probability), 4)

def calculate_newsvendor_target(holding_cost: float, stockout_cost: float) -> float:
    """
    Calculates the Optimal Service Level (Critical Ratio).
    """
    if (stockout_cost + holding_cost) == 0: return 0.0

    critical_ratio = stockout_cost / (stockout_cost + holding_cost)
    return round(critical_ratio, 4)

def calculate_required_inventory(avg_demand: float, std_dev_demand: float, target_sla: float) -> float:
    """
    Calculates stock needed for a specific SLA.
    """
    z_score = norm.ppf(target_sla)
    required_safety_stock = z_score * std_dev_demand
    return round(avg_demand + required_safety_stock, 2)