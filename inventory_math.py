import math


# --- HELPER: Pure Python Normal Distribution Inverse (Abramowitz & Stegun approx) ---
# This removes the need for scipy or statistics modules completely.
def norm_inv(p):
    """
    Approximates the Inverse Standard Normal CDF (Z-Score).
    Accurate enough for supply chain calculations.
    """
    if p <= 0.0: return -3.0  # Guardrail for 0%
    if p >= 1.0: return 3.0  # Guardrail for 100%

    # If p < 0.5, use symmetry
    if p < 0.5:
        return -norm_inv(1.0 - p)

    t = math.sqrt(-2.0 * math.log(1.0 - p))
    numerator = (0.010328 * t + 0.802853) * t + 2.515517
    denominator = ((0.001308 * t + 0.189269) * t + 1.432788) * t + 1.0

    return t - (numerator / denominator)


# --- MAIN FUNCTIONS ---

def calculate_eoq(annual_demand, ordering_cost, holding_cost):
    if annual_demand <= 0 or ordering_cost <= 0 or holding_cost <= 0:
        return 0
    return math.sqrt((2 * annual_demand * ordering_cost) / holding_cost)


def calculate_newsvendor_target(holding_cost, stockout_cost):
    if (holding_cost + stockout_cost) == 0:
        return 0.5
    return stockout_cost / (holding_cost + stockout_cost)


def calculate_advanced_safety_stock(avg_demand, std_dev_demand, avg_lead_time, std_dev_lead_time, target_service_level):
    # Safety Bounds
    if target_service_level >= 0.999: target_service_level = 0.999
    if target_service_level <= 0.001: target_service_level = 0.001

    # 1. Get Z-Score using our manual function
    z_score = norm_inv(target_service_level)

    # 2. Variance due to Demand Fluctuations
    demand_risk = avg_lead_time * (std_dev_demand ** 2)

    # 3. Variance due to Supplier Delays
    supply_risk = (avg_demand ** 2) * (std_dev_lead_time ** 2)

    # 4. Combined Risk
    combined_sigma = math.sqrt(demand_risk + supply_risk)

    return z_score * combined_sigma