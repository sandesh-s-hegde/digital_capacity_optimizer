"""
LSP Digital Capacity Twin: inventory_math.py
Version: 4.0.0 (Stable Release)
===========================================
Core mathematical engine for stochastic optimization,
sustainability impact, and customer loyalty metrics.
"""

import scipy.stats as stats
import math
from scipy.stats import norm


def calculate_newsvendor_target(holding_cost, stockout_cost):
    """
    Calculates the Critical Fractile (Optimal Service Level) based on cost asymmetry.
    Newsvendor Model: Cu / (Cu + Co)
    """
    if holding_cost + stockout_cost == 0:
        return 0.95
    return stockout_cost / (holding_cost + stockout_cost)


def calculate_advanced_safety_stock(avg_demand, std_dev, lt, lt_sigma, sla):
    """
    Calculates Risk-Adjusted Safety Stock using the RSS (Root Sum of Squares) method.
    Harden version for v4.0.0 to prevent domain errors on zero demand or invalid SLAs.
    """
    if avg_demand <= 0 or sla >= 1.0 or sla <= 0:
        return 0  # Return 0 instead of crashing on edge cases or undefined Z-scores

    # Calculate Z-score for the target Service Level Agreement
    z = norm.ppf(sla)

    # Variance from Demand: Average Lead Time * (StdDev Demand)^2
    # Variance from Supply: (Avg Demand)^2 * (Lead Time Variance)^2
    # Combined: Z * sqrt( (LT * sigma_D^2) + (D^2 * sigma_LT^2) )
    safety_stock = z * ((lt * (std_dev ** 2)) + (avg_demand ** 2 * lt_sigma ** 2)) ** 0.5

    return max(0, int(round(safety_stock)))


def calculate_eoq(annual_demand, order_cost, holding_cost):
    """
    Economic Order Quantity (EOQ) Model.
    """
    if holding_cost <= 0: return int(annual_demand / 12)
    return int(math.sqrt((2 * annual_demand * order_cost) / holding_cost))


# --- STRATEGIC RESEARCH MODULES ---

def calculate_horizontal_sharing(total_demand, internal_capacity, partner_surcharge, base_holding_cost):
    """
    Models the financial impact of Horizontal Cooperation (Outsourcing).
    Determines how much volume should be shifted to partners when capacity is breached.
    """
    overflow_volume = max(0, total_demand - internal_capacity)
    internal_volume = max(0, total_demand - overflow_volume)

    # Costs
    cost_internal = internal_volume * base_holding_cost
    cost_outsourced = overflow_volume * (base_holding_cost + partner_surcharge)
    total_cost = cost_internal + cost_outsourced

    # Dependency Ratio: Metric for supply chain vulnerability
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
    Balances inventory coverage against partner dependency.
    """
    # 1. Coverage Score (Max 50 pts): Ability to absorb shocks
    if combined_volatility > 0:
        sigma_coverage = safety_stock / combined_volatility
        coverage_score = min(50, (sigma_coverage / 2.0) * 50)
    else:
        coverage_score = 50

    # 2. Independence Score (Max 50 pts): Ability to operate without heavy outsourcing
    independence_score = 50 - (dependency_ratio / 2)

    total_resilience = coverage_score + independence_score
    return round(total_resilience, 1)


def calculate_service_implications(demand_mean, demand_std, target_sla, stockout_cost):
    """
    Calculates Service Failure metrics (Fill Rate & Penalty).
    Uses the Unit Normal Loss Function to find expected units short.
    """
    if demand_std <= 0 or target_sla <= 0 or target_sla >= 1:
        return {"expected_shortage": 0, "penalty_cost": 0, "reliability_score": 100}

    z_score = norm.ppf(target_sla)
    pdf_z = norm.pdf(z_score)
    cdf_z = norm.cdf(z_score)

    # Unit Normal Loss Function: L(z) = f(z) - z * [1 - F(z)]
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


# --- SUSTAINABILITY & CUSTOMER LOYALTY MODULES ---

def calculate_sustainability_impact(internal_vol, outsourced_vol):
    """
    Calculates Carbon Footprint (Scope 3 Emissions).
    Ref: Green Logistics Optimization through collaborative networks.
    """
    CO2_PER_UNIT_INTERNAL = 12.5  # kg (Standard Solo Logistics)
    CO2_PER_UNIT_SHARED = 10.0  # kg (Optimized Shared Network)

    total_emissions = (internal_vol * CO2_PER_UNIT_INTERNAL) + (outsourced_vol * CO2_PER_UNIT_SHARED)

    # Baseline: Carbon footprint without horizontal cooperation
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
    Based on Wallenburg (2011) - Service Level Goal Exceedance.
    """
    # Gap between promised SLA and actual delivered reliability
    gap = actual_reliability - (sla_target * 100)
    base_loyalty = 75.0  # Industry baseline score

    if gap >= 0:
        # Delight Factor: 1.5x multiplier for exceeding expectations
        loyalty = base_loyalty + (gap * 1.5)
    else:
        # Disappointment Factor: 2.5x penalty for failing the SLA promise
        loyalty = base_loyalty + (gap * 2.5)

    return min(100, max(0, round(loyalty, 1)))
