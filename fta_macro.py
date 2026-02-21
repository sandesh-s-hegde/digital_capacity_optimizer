import pandas as pd
import numpy as np
import plotly.graph_objects as go
from typing import Dict, Any


def calculate_landed_cost(base_price: float, freight: float, tariff_rate: float,
                          lead_time_days: int, holding_cost_annual: float,
                          demand_annual: int, carbon_intensity_kg: float = 0.0,
                          carbon_price_ton: float = 0.0) -> Dict[str, float]:
    """
    Calculates Total Landed Cost (TLC) including Carbon Taxes (CBAM) and Pipeline Risk.
    """
    # 1. Direct Regulatory Costs
    tariff_amt = base_price * (tariff_rate / 100.0)
    cbam_tax = (carbon_intensity_kg / 1000.0) * carbon_price_ton

    # Base Landed Cost (Physical delivery + Taxes)
    landed_unit_cost = base_price + freight + tariff_amt + cbam_tax

    # 2. Inventory (Risk) Costs
    # Pipeline Risk = (Lead Time / 365) * Unit Cost * Holding Rate
    per_unit_risk_cost = (lead_time_days / 365.0) * landed_unit_cost * (holding_cost_annual / 100.0)

    # 3. Total Cost
    total_cost_per_unit = landed_unit_cost + per_unit_risk_cost

    return {
        "Base Price": float(base_price),
        "Freight": float(freight),
        "Tariff": float(tariff_amt),
        "Carbon Tax (CBAM)": float(cbam_tax),
        "Risk (Holding)": float(per_unit_risk_cost),
        "Total Landed Cost": float(total_cost_per_unit)
    }


def render_fta_comparison(demand: int = 15000, carbon_price: float = 85.0) -> go.Figure:
    """
    Generates a comparative Total Landed Cost analysis (Domestic vs Offshore).
    Returns a Plotly Stacked Bar Chart.
    """
    # Scenario A: Domestic / Nearshore (e.g., EU)
    # High base cost, low emissions, fast lead time.
    eu_data = calculate_landed_cost(
        base_price=85.0,
        freight=5.0,
        tariff_rate=0.0,
        lead_time_days=4,
        holding_cost_annual=20.0,
        demand_annual=demand,
        carbon_intensity_kg=2.5,
        carbon_price_ton=carbon_price
    )

    # Scenario B: Offshore / China Plus One (e.g., India)
    # Low base cost, high emissions, long lead time, subject to tariffs.
    in_data = calculate_landed_cost(
        base_price=50.0,
        freight=12.0,
        tariff_rate=5.0,  # 5% Import Tariff
        lead_time_days=45,
        holding_cost_annual=20.0,
        demand_annual=demand,
        carbon_intensity_kg=8.0,
        carbon_price_ton=carbon_price
    )

    # Build Stacked Bar Chart
    categories = ['Base Price', 'Freight', 'Tariff', 'Carbon Tax (CBAM)', 'Risk (Holding)']

    fig = go.Figure(data=[
        go.Bar(name='Base Price', x=['Domestic (EU)', 'Offshore (India)'],
               y=[eu_data['Base Price'], in_data['Base Price']], marker_color='#2E86C1'),
        go.Bar(name='Freight', x=['Domestic (EU)', 'Offshore (India)'],
               y=[eu_data['Freight'], in_data['Freight']], marker_color='#28B463'),
        go.Bar(name='Tariff (Trade)', x=['Domestic (EU)', 'Offshore (India)'],
               y=[eu_data['Tariff'], in_data['Tariff']], marker_color='#E74C3C'),
        go.Bar(name='Carbon Tax', x=['Domestic (EU)', 'Offshore (India)'],
               y=[eu_data['Carbon Tax (CBAM)'], in_data['Carbon Tax (CBAM)']], marker_color='#5D6D7E'),
        go.Bar(name='Risk (Inventory)', x=['Domestic (EU)', 'Offshore (India)'],
               y=[eu_data['Risk (Holding)'], in_data['Risk (Holding)']], marker_color='#F1C40F')
    ])

    fig.update_layout(
        barmode='stack',
        title=f"Total Landed Cost Comparison (CBAM @ ${carbon_price}/ton)",
        yaxis_title="Cost per Unit ($)",
        height=500,
        margin=dict(l=0, r=0, t=40, b=0)
    )

    return fig
