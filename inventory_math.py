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


# --- WALLENBURG RESEARCH MODULES ---

def calculate_horizontal_sharing(total_demand, internal_capacity, partner_surcharge, base_holding_cost):
    """
    Models the financial impact of Horizontal Cooperation (Outsourcing).
    """
    overflow_volume = max(0, total_demand - internal_capacity)
    internal_volume = total_demand - overflow_volume

    # Costs
    cost_internal = internal_volume * base_holding_cost
    cost_outsourced = overflow_volume * (base_holding_cost + partner_surcharge)
    total_cost = cost_internal + cost_outsourced

    # Dependency Ratio
    dependency_ratio = (overflow_volume / total_demand) if total_demand > 0 else 0

    return {
        "overflow_vol": int(overflow_volume),
        "internal_vol": int(internal_volume),
        "total_cost": round(total_cost, 2),
        "dependency_ratio": round(dependency_ratio * 100, 1)
    }


def calculate_resilience_score(safety_stock, combined_volatility, dependency_ratio):
    """
    Calculates 'Resilience Index' (0-100).
    """
    # 1. Coverage Score (Max 50 pts)
    if combined_volatility > 0:
        sigma_coverage = safety_stock / combined_volatility
        coverage_score = min(50, (sigma_coverage / 2.0) * 50)
    else:
        coverage_score = 50

    # 2. Independence Score (Max 50 pts)
    independence_score = 50 - (dependency_ratio / 2)

    total_resilience = coverage_score + independence_score
    return round(total_resilience, 1)


def calculate_service_implications(demand_mean, demand_std, target_sla, stockout_cost):
    """
    Calculates Service Failure metrics (Fill Rate & Penalty).
    """
    if demand_std == 0: return {"expected_shortage": 0, "penalty_cost": 0, "reliability_score": 100}

    z_score = stats.norm.ppf(target_sla)
    pdf_z = stats.norm.pdf(z_score)
    cdf_z = stats.norm.cdf(z_score)
    standard_loss = pdf_z - (z_score * (1 - cdf_z))

    expected_shortage_units = demand_std * standard_loss
    expected_penalty_cost = expected_shortage_units * stockout_cost

    if demand_mean > 0:
        service_reliability_score = 100 * (1 - (expected_shortage_units / demand_mean))
    else:
        service_reliability_score = 100

    return {
        "expected_shortage": round(expected_shortage_units, 2),
        "penalty_cost": round(expected_penalty_cost, 2),
        "reliability_score": round(service_reliability_score, 2)
    }


# --- NEW: GREEN & LOYALTY MODULES (v3.3) ---

def calculate_sustainability_impact(internal_vol, outsourced_vol):
    """
    Calculates Carbon Footprint (Scope 3 Emissions).
    Research Logic: Horizontal Cooperation reduces empty runs (efficiency),
    so outsourced volume has a lower CO2 factor per unit.
    """
    CO2_PER_UNIT_INTERNAL = 12.5  # kg (Standard Solo Logistics)
    CO2_PER_UNIT_SHARED = 10.0  # kg (Optimized Shared Network)

    total_emissions = (internal_vol * CO2_PER_UNIT_INTERNAL) + (outsourced_vol * CO2_PER_UNIT_SHARED)

    # Baseline: What if we did it all internally (inefficiently)?
    baseline_emissions = (internal_vol + outsourced_vol) * CO2_PER_UNIT_INTERNAL

    savings = max(0, baseline_emissions - total_emissions)

    return {
        "total_emissions": round(total_emissions, 2),
        "co2_saved": round(savings, 2),
        "is_green_optimized": savings > 0
    }


def calculate_loyalty_index(sla_target, actual_reliability):
    """
    Calculates 'LSP Customer Loyalty Index'.
    Ref: Wallenburg (2011) - Proactive improvement (Goal Exceedance) drives loyalty.
    """
    # Gap between Promise (SLA) and Reality (Reliability)
    gap = actual_reliability - (sla_target * 100)

    base_loyalty = 75.0  # Neutral starting point

    if gap >= 0:
        # Goal Exceedance: Bonus multiplier (Delight Factor)
        loyalty = base_loyalty + (gap * 1.5)
    else:
        # Goal Failure: Penalty multiplier (Disappointment Factor)
        loyalty = base_loyalty + (gap * 2.5)  # Penalty is harsher than reward

    return min(100, max(0, round(loyalty, 1)))