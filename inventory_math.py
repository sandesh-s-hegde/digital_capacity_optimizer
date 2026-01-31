"""
inventory_math.py
Core optimization logic for inventory management.
(Cloud-Optimized: Uses pure math instead of heavy scipy/numpy libraries)
"""
import math


# --- HELPER: Manual Normal Distribution Functions ---
# We write these manually to avoid installing the 100MB+ Scipy library

def norm_cdf(x):
    """Cumulative Distribution Function (CDF) approximation."""
    return (1.0 + math.erf(x / math.sqrt(2.0))) / 2.0


def norm_ppf(p):
    """Inverse CDF (Percent Point Function) approximation."""
    # Source: Abramowitz and Stegun approximation for standard normal distribution
    if p >= 1.0: return 5.0  # Guardrail
    if p <= 0.0: return -5.0  # Guardrail

    if p < 0.5:
        return -norm_ppf(1.0 - p)

    t = math.sqrt(-2.0 * math.log(1.0 - p))
    numerator = (0.010328 * t + 0.802853) * t + 2.515517
    denominator = ((0.001308 * t + 0.189269) * t + 1.432788) * t + 1.0

    return t - (numerator / denominator)


# --- MAIN LOGIC ---

def calculate_eoq(annual_demand: float, order_cost: float, holding_cost: float) -> float:
    """Calculates Economic Order Quantity (EOQ)."""
    if holding_cost == 0: return 0.0
    return math.sqrt((2 * annual_demand * order_cost) / holding_cost)


def calculate_safety_stock(max_daily_demand: float, avg_daily_demand: float, lead_time: int) -> float:
    """Calculates Buffer Stock to survive delays."""
    return (max_daily_demand - avg_daily_demand) * lead_time


def calculate_service_level(avg_demand: float, std_dev_demand: float, total_inventory: float) -> float:
    """Calculates the probability (%) of NOT running out of stock (SLA)."""
    if std_dev_demand == 0:
        return 1.0 if total_inventory >= avg_demand else 0.0

    z_score = (total_inventory - avg_demand) / std_dev_demand
    probability = norm_cdf(z_score)
    return round(float(probability), 4)


def calculate_newsvendor_target(holding_cost: float, stockout_cost: float) -> float:
    """Calculates the Optimal Service Level (Critical Ratio)."""
    if (stockout_cost + holding_cost) == 0: return 0.0
    critical_ratio = stockout_cost / (stockout_cost + holding_cost)
    return round(critical_ratio, 4)


def calculate_required_inventory(avg_demand: float, std_dev_demand: float, target_sla: float) -> float:
    """Calculates stock needed for a specific SLA."""
    z_score = norm_ppf(target_sla)
    required_safety_stock = z_score * std_dev_demand
    return round(avg_demand + required_safety_stock, 2)


def calculate_advanced_safety_stock(avg_demand, std_dev_demand, avg_lead_time, std_dev_lead_time, target_service_level):
    """Calculates Safety Stock accounting for Demand + Lead Time Risk."""
    z_score = norm_ppf(target_service_level)

    demand_risk = avg_lead_time * (std_dev_demand ** 2)
    supply_risk = (avg_demand ** 2) * (std_dev_lead_time ** 2)
    combined_sigma = math.sqrt(demand_risk + supply_risk)

    return z_score * combined_sigma


def calculate_service_implications(demand_mean, demand_std, target_sla, stockout_cost):
    """
    Calculates the Service Management implications of inventory decisions.
    Specifically focuses on 'Service Failure' (Stockouts) frequency and intensity.
    """
    import scipy.stats as stats

    # 1. Expected Fill Rate (Service Level)
    # Even if we aim for 95% probability of no stockout (Cycle Service Level),
    # the 'Fill Rate' (percent of demand met) is often higher.
    # We calculate the expected 'Unit Shortage' (Unmet Demand).

    z_score = stats.norm.ppf(target_sla)
    safety_stock = z_score * demand_std
    order_up_to = demand_mean + safety_stock

    # Standard Loss Function for Normal Distribution (E[z] = standard normal loss)
    # L(z) = pdf(z) - z * (1 - cdf(z))
    pdf_z = stats.norm.pdf(z_score)
    cdf_z = stats.norm.cdf(z_score)
    standard_loss = pdf_z - (z_score * (1 - cdf_z))

    expected_shortage_units = demand_std * standard_loss

    # 2. Service Failure Impact
    expected_penalty_cost = expected_shortage_units * stockout_cost
    service_reliability_score = 100 * (1 - (expected_shortage_units / demand_mean))

    return {
        "safety_stock": int(safety_stock),
        "expected_shortage": round(expected_shortage_units, 2),
        "penalty_cost": round(expected_penalty_cost, 2),
        "reliability_score": round(service_reliability_score, 2)
    }