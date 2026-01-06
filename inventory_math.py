"""
inventory_math.py
Core optimization logic for inventory management.
Includes Stochastic models (Newsvendor) and Service Level logic.
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
    """
    return (max_daily_demand - avg_daily_demand) * lead_time

def calculate_service_level(avg_demand, std_dev_demand, total_inventory):
    """
    Calculates the probability (%) of NOT running out of stock (SLA).
    Uses Normal Distribution (Z-Score).
    """
    if std_dev_demand == 0:
        return 1.0 if total_inventory >= avg_demand else 0.0

    # Z = (Stock - Mean) / Volatility
    z_score = (total_inventory - avg_demand) / std_dev_demand

    # Convert Z-score to Percentage (0 to 1)
    probability = norm.cdf(z_score)
    return round(probability, 4)

def calculate_newsvendor_target(holding_cost, stockout_cost):
    """
    Calculates the Optimal Service Level (Critical Ratio) based on cost.
    Formula: Critical Ratio = Stockout_Cost / (Stockout_Cost + Holding_Cost)

    Returns:
        float: Optimal Service Level (e.g., 0.95 for 95%)
    """
    if (stockout_cost + holding_cost) == 0: return 0.0

    critical_ratio = stockout_cost / (stockout_cost + holding_cost)
    return round(critical_ratio, 4)

def calculate_required_inventory(avg_demand, std_dev_demand, target_sla):
    """
    Calculates how much stock is needed to achieve a specific SLA.
    Uses Inverse Normal Distribution (norm.ppf).
    """
    # Z-Score for the target SLA (e.g., 95% -> 1.645)
    z_score = norm.ppf(target_sla)

    required_safety_stock = z_score * std_dev_demand
    return round(avg_demand + required_safety_stock, 2)