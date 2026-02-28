import math
from typing import Dict, Union
from scipy.stats import norm


def calculate_newsvendor_target(holding_cost: float, stockout_cost: float) -> float:
    """Calculates the Critical Fractile (Optimal Service Level) based on cost asymmetry."""
    if holding_cost + stockout_cost == 0.0:
        return 0.95
    return stockout_cost / (holding_cost + stockout_cost)


def calculate_advanced_safety_stock(
    avg_demand: float,
    std_dev: float,
    lt: float,
    lt_sigma: float,
    sla: float
) -> int:
    """Calculates Risk-Adjusted Safety Stock using the Root Sum of Squares (RSS) method."""
    if avg_demand <= 0.0 or sla >= 1.0 or sla <= 0.0:
        return 0

    z = norm.ppf(sla)
    variance_term = (lt * (std_dev ** 2)) + ((avg_demand ** 2) * (lt_sigma ** 2))
    safety_stock = z * math.sqrt(variance_term)

    return max(0, int(round(safety_stock)))


def calculate_eoq(annual_demand: float, order_cost: float, holding_cost: float) -> int:
    """Calculates the Economic Order Quantity (EOQ)."""
    if holding_cost <= 0.0:
        return int(annual_demand / 12)
    return int(math.sqrt((2.0 * annual_demand * order_cost) / holding_cost))


def calculate_horizontal_sharing(
    total_demand: float,
    internal_capacity: float,
    partner_surcharge: float,
    base_holding_cost: float
) -> Dict[str, float]:
    """Models the financial impact and volume shift of Horizontal Cooperation."""
    # Fixed the int vs float linter warning by using 0.0
    overflow_volume = max(0.0, total_demand - internal_capacity)
    internal_volume = max(0.0, total_demand - overflow_volume)

    cost_internal = internal_volume * base_holding_cost
    cost_outsourced = overflow_volume * (base_holding_cost + partner_surcharge)

    dependency_ratio = (overflow_volume / total_demand) if total_demand > 0.0 else 0.0

    return {
        "overflow_vol": float(overflow_volume),
        "internal_vol": float(internal_volume),
        "total_cost": round(cost_internal + cost_outsourced, 2),
        "dependency_ratio": round(dependency_ratio * 100.0, 1)
    }


def calculate_resilience_score(
    safety_stock: float,
    combined_volatility: float,
    dependency_ratio: float
) -> float:
    """Calculates a Resilience Index (0-100) balancing inventory coverage against partner dependency."""
    if combined_volatility > 0.0:
        sigma_coverage = safety_stock / combined_volatility
        coverage_score = min(50.0, (sigma_coverage / 2.0) * 50.0)
    else:
        coverage_score = 50.0

    independence_score = 50.0 - (dependency_ratio / 2.0)
    return round(coverage_score + independence_score, 1)


def calculate_service_implications(
    demand_mean: float,
    demand_std: float,
    target_sla: float,
    stockout_cost: float
) -> Dict[str, float]:
    """Calculates expected shortages and penalty costs using the Unit Normal Loss Function."""
    if demand_std <= 0.0 or target_sla <= 0.0 or target_sla >= 1.0:
        return {"expected_shortage": 0.0, "penalty_cost": 0.0, "reliability_score": 100.0}

    z_score = norm.ppf(target_sla)
    pdf_z = norm.pdf(z_score)
    cdf_z = norm.cdf(z_score)

    standard_loss = pdf_z - (z_score * (1.0 - cdf_z))
    expected_shortage_units = demand_std * standard_loss
    expected_penalty_cost = expected_shortage_units * stockout_cost

    if demand_mean > 0.0:
        service_reliability_score = 100.0 * (1.0 - (expected_shortage_units / demand_mean))
    else:
        service_reliability_score = 100.0

    return {
        "expected_shortage": round(expected_shortage_units, 2),
        "penalty_cost": round(expected_penalty_cost, 2),
        "reliability_score": round(service_reliability_score, 2)
    }


def calculate_sustainability_impact(
    internal_vol: float,
    outsourced_vol: float
) -> Dict[str, Union[float, bool]]:
    """Calculates Scope 3 Emissions footprint and savings from collaborative networks."""
    co2_per_unit_internal = 12.5
    co2_per_unit_shared = 10.0

    total_emissions = (internal_vol * co2_per_unit_internal) + (outsourced_vol * co2_per_unit_shared)
    baseline_emissions = (internal_vol + outsourced_vol) * co2_per_unit_internal

    # Fixed the int vs float linter warning by using 0.0
    savings = max(0.0, baseline_emissions - total_emissions)

    return {
        "total_emissions": round(total_emissions, 2),
        "co2_saved": round(savings, 2),
        "is_green_optimized": bool(savings > 0.0)
    }


def calculate_loyalty_index(sla_target: float, actual_reliability: float) -> float:
    """Calculates Customer Loyalty Index based on Service Level Goal Exceedance."""
    gap = actual_reliability - (sla_target * 100.0)
    base_loyalty = 75.0

    if gap >= 0.0:
        loyalty = base_loyalty + (gap * 1.5)
    else:
        loyalty = base_loyalty + (gap * 2.5)

    return min(100.0, max(0.0, round(loyalty, 1)))
