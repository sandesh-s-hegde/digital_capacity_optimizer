import math
import scipy.stats as stats

def calculate_eoq(annual_demand, ordering_cost, holding_cost):
    """
    Economic Order Quantity (EOQ) Formula.
    Returns optimal order size to minimize total cost.
    """
    if annual_demand <= 0 or ordering_cost <= 0 or holding_cost <= 0:
        return 0
    return math.sqrt((2 * annual_demand * ordering_cost) / holding_cost)

def calculate_newsvendor_target(holding_cost, stockout_cost):
    """
    Critical Ratio (Newsvendor Model).
    Returns optimal Service Level (0.0 to 1.0).
    """
    if (holding_cost + stockout_cost) == 0:
        return 0.5
    return stockout_cost / (holding_cost + stockout_cost)

def calculate_advanced_safety_stock(avg_demand, std_dev_demand, avg_lead_time, std_dev_lead_time, target_service_level):
    """
    Calculates Safety Stock accounting for BOTH Demand Volatility AND Supplier Delay Risk.
    
    Formula: Z * sqrt( (Avg_Lead_Time * sigma_Demand^2) + (Avg_Demand^2 * sigma_Lead_Time^2) )
    """
    if target_service_level >= 1.0: target_service_level = 0.99
    if target_service_level <= 0.0: target_service_level = 0.01

    z_score = stats.norm.ppf(target_service_level)
    
    # Variance due to Demand Fluctuations
    demand_risk = avg_lead_time * (std_dev_demand ** 2)
    
    # Variance due to Supplier Delays
    supply_risk = (avg_demand ** 2) * (std_dev_lead_time ** 2)
    
    # Combined Risk (Standard Deviation of Lead Time Demand)
    combined_sigma = math.sqrt(demand_risk + supply_risk)
    
    return z_score * combined_sigma