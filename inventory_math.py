import scipy.stats as stats
import math

def calculate_newsvendor_target(holding_cost, stockout_cost):
    """
    Calculates the Critical Fractile (Optimal Service Level) based on cost asymmetry.
    Newsvendor Model: Cu / (Cu + Co)
    """
    if holding_cost + stockout_cost == 0:
        return 0.95
    return stockout_cost / (holding_cost + stockout_cost)

def calculate_advanced_safety_stock(avg_demand, std_dev_demand, avg_lead_time, lead_time_volatility, target_sla):
    """
    Calculates Risk-Adjusted Safety Stock using the RSS (Root Sum of Squares) method.
    Accounts for both Demand Uncertainty and Supply (Lead Time) Uncertainty.
    """
    z_score = stats.norm.ppf(target_sla)

    # Variance from Demand: Average Lead Time * (StdDev Demand)^2
    demand_component = avg_lead_time * (std_dev_demand ** 2)

    # Variance from Supply: (Avg Demand)^2 * (Lead Time Variance)^2
    supply_component = (avg_demand ** 2) * (lead_time_volatility ** 2)

    # Combined Standard Deviation (RSS)
    combined_std_dev = math.sqrt(demand_component + supply_component)

    safety_stock = z_score * combined_std_dev
    return max(0, int(safety_stock))

def calculate_eoq(annual_demand, order_cost, holding_cost):
    """
    Economic Order Quantity (EOQ) Model.
    """
    if holding_cost == 0: return annual_demand / 12
    return math.sqrt((2 * annual_demand * order_cost) / holding_cost)

# --- NEW: WALLENBURG RESEARCH MODULES ---

def calculate_horizontal_sharing(total_demand, internal_capacity, partner_surcharge, base_holding_cost):
    """
    Models the financial impact of Horizontal Cooperation (Outsourcing to Competitors).

    Research Alignment:
    - Calculates the 'Overflow Volume' that must be routed to a partner.
    - Applies a 'Friction Cost' (Surcharge) which represents the transaction cost of cooperation.
    """
    overflow_volume = max(0, total_demand - internal_capacity)
    internal_volume = total_demand - overflow_volume

    # Internal Cost
    cost_internal = internal_volume * base_holding_cost

    # Cooperation Cost (Base + Surcharge)
    # In reality, partners often charge a premium for 'On-Demand' capacity
    cost_outsourced = overflow_volume * (base_holding_cost + partner_surcharge)

    total_cost = cost_internal + cost_outsourced

    # Dependency Ratio: What % of our flow relies on the partner?
    dependency_ratio = (overflow_volume / total_demand) if total_demand > 0 else 0

    return {
        "overflow_vol": int(overflow_volume),
        "internal_vol": int(internal_volume),
        "total_cost": round(total_cost, 2),
        "dependency_ratio": round(dependency_ratio * 100, 1) # Percentage
    }

def calculate_resilience_score(safety_stock, combined_volatility, dependency_ratio):
    """
    Calculates a 'Resilience Index' (0-100) for the Service Lane.

    Logic:
    1. Buffer Coverage: How many standard deviations of risk does our Safety Stock cover?
    2. Dependency Risk: High reliance on Horizontal Partners lowers resilience (Control Risk).
    """
    # 1. Coverage Score (Max 50 pts)
    # If Safety Stock covers > 2 Standard Deviations, we are very robust against shocks.
    if combined_volatility > 0:
        sigma_coverage = safety_stock / combined_volatility
        coverage_score = min(50, (sigma_coverage / 2.0) * 50)
    else:
        coverage_score = 50 # No volatility means perfect resilience

    # 2. Independence Score (Max 50 pts)
    # 0% Dependency = 50 pts. 100% Dependency = 0 pts.
    independence_score = 50 - (dependency_ratio / 2)

    total_resilience = coverage_score + independence_score
    return round(total_resilience, 1)

def calculate_service_implications(demand_mean, demand_std, target_sla, stockout_cost):
    """
    Calculates Service Failure metrics (Fill Rate & Penalty).
    """
    z_score = stats.norm.ppf(target_sla)

    # Standard Loss Function for Normal Distribution
    pdf_z = stats.norm.pdf(z_score)
    cdf_z = stats.norm.cdf(z_score)
    standard_loss = pdf_z - (z_score * (1 - cdf_z))

    expected_shortage_units = demand_std * standard_loss
    expected_penalty_cost = expected_shortage_units * stockout_cost

    # Reliability (Fill Rate)
    if demand_mean > 0:
        service_reliability_score = 100 * (1 - (expected_shortage_units / demand_mean))
    else:
        service_reliability_score = 100

    return {
        "expected_shortage": round(expected_shortage_units, 2),
        "penalty_cost": round(expected_penalty_cost, 2),
        "reliability_score": round(service_reliability_score, 2)
    }