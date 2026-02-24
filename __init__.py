"""
LSP Digital Capacity Twin
Version: 4.2.6
"""

__version__ = "4.2.6"

# 1. Core Operations & Math
from .inventory_math import (
    calculate_newsvendor_target,
    calculate_advanced_safety_stock,
    calculate_horizontal_sharing,
    calculate_resilience_score,
    calculate_service_implications,
    calculate_loyalty_index,
    calculate_sustainability_impact
)

# 2. FinTech & Risk
from .climate_finance import (
    simulate_ets_carbon_pricing,
    plot_carbon_risk_simulation
)

# 3. Strategy & Forecasting
from .profit_optimizer import calculate_profit_scenarios, plot_cost_tradeoff
from .forecast import generate_forecast

# 4. Geospatial
from .map_viz import render_map
