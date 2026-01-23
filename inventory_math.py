import math
import statistics


def calculate_eoq(annual_demand, order_cost, holding_cost):
    """
    Economic Order Quantity (EOQ):
    Determines the optimal order size to minimize total inventory costs.
    Formula: sqrt((2 * Demand * OrderCost) / HoldingCost)
    """
    if holding_cost <= 0: return 0
    return math.sqrt((2 * annual_demand * order_cost) / holding_cost)


def calculate_newsvendor_target(holding_cost, stockout_cost):
    """
    Critical Ratio (Newsvendor Model):
    Calculates the optimal Service Level based on the cost of being wrong.
    Formula: StockoutCost / (StockoutCost + HoldingCost)
    """
    if (stockout_cost + holding_cost) == 0: return 0.5
    return stockout_cost / (stockout_cost + holding_cost)


def calculate_advanced_safety_stock(avg_demand, std_dev_demand, avg_lead_time, lead_time_var, service_level):
    """
    Stochastic Safety Stock:
    Uses 'Root Sum of Squares' to account for both Demand Volatility AND Supply Chain Risk.
    """
    # Z-Score (Standard Normal Distribution)
    try:
        z_score = statistics.NormalDist().inv_cdf(service_level)
    except:
        z_score = 1.65  # Fallback for 95%

    # Risk 1: Demand Variation during Lead Time
    demand_risk = avg_lead_time * (std_dev_demand ** 2)

    # Risk 2: Supply Chain Lead Time Variation
    supply_risk = (avg_demand ** 2) * (lead_time_var ** 2)

    # Combined Risk (Root Sum of Squares)
    combined_risk = math.sqrt(demand_risk + supply_risk)

    return z_score * combined_risk