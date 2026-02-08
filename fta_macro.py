import pandas as pd
import numpy as np
import plotly.graph_objects as go


def calculate_landed_cost(base_price, freight, tariff_rate, lead_time_days, holding_cost_annual, demand_annual):
    """
    Calculates Total Landed Cost (TLC) including Inventory Carrying Cost due to lead time.
    """
    # 1. Direct Costs
    tariff_amt = base_price * (tariff_rate / 100.0)
    landed_unit_cost = base_price + freight + tariff_amt

    # 2. Inventory (Risk) Costs
    # Longer lead time = More safety stock & pipeline inventory needed
    # Formula: (Lead Time / 365) * Annual Demand * Unit Cost * Holding Rate
    # Note: This is a simplified "Pipeline Inventory" cost
    pipeline_inventory_cost = (lead_time_days / 365.0) * demand_annual * landed_unit_cost * (
                holding_cost_annual / 100.0)

    per_unit_risk_cost = pipeline_inventory_cost / demand_annual

    total_cost_per_unit = landed_unit_cost + per_unit_risk_cost

    return {
        "Base Price": base_price,
        "Freight": freight,
        "Tariff": tariff_amt,
        "Risk (Holding)": per_unit_risk_cost,
        "Total Landed Cost": total_cost_per_unit
    }


def render_fta_comparison(demand=10000):
    # Scenario A: EU Supplier (High Cost, Low Risk)
    eu_data = calculate_landed_cost(
        base_price=85.0,  # Expensive labor
        freight=5.0,  # Trucking is cheap
        tariff_rate=0.0,  # Single market
        lead_time_days=3,  # Fast
        holding_cost_annual=20,
        demand_annual=demand
    )

    return eu_data