import pytest
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

# --- IMPORT LOCAL ACADEMIC MODULES ---
import climate_finance
import profit_optimizer
import forecast


# ==========================================
# 1. FINTECH: CLIMATE RISK & GBM VALIDATION
# ==========================================
def test_gbm_carbon_simulation_integrity():
    """
    Validates the Stochastic EU ETS Carbon Pricing model.
    Ensures Geometric Brownian Motion generates correct matrix dimensions
    and sensible Carbon Value at Risk (CVaR) boundaries.
    """
    current_price = 85.0
    volatility = 0.40
    days = 365
    simulations = 2000

    # Execute empirical simulation
    res = climate_finance.simulate_ets_carbon_pricing(
        current_price=current_price,
        volatility=volatility,
        days=days,
        simulations=simulations
    )

    # 1. Matrix Shape Validation (Time x Iterations)
    assert res["paths"].shape == (days, simulations), "GBM matrix dimensions collapsed."

    # 2. Financial Logic Validation
    # The 95th percentile worst-case cost MUST be strictly greater than the expected mean
    assert res["cvar_95"] > res["expected_price"], "CVaR boundary failed to exceed mean expected cost."

    # Prices cannot be negative in a standard GBM model
    assert np.all(res["paths"] > 0), "GBM produced impossible negative asset prices."


# ==========================================
# 2. STRATEGY: STOCHASTIC FORECASTING
# ==========================================
def test_forecast_rmse_confidence_intervals():
    """
    Validates linear trend forecasting and RMSE-based confidence intervals.
    """
    # Generate synthetic upward trend data
    dates = pd.date_range(start="2025-01-01", periods=10, freq='D')
    demand = [100, 105, 110, 108, 115, 120, 118, 125, 130, 135]
    df = pd.DataFrame({'date': dates, 'demand': demand})

    # Run forecast for 3 months
    res_df = forecast.generate_forecast(df, months=3)

    # 1. Output Validation
    assert res_df is not None, "Forecaster returned None on valid dataframe."
    assert len(res_df) == 3, "Forecaster failed to project the exact requested horizon."

    # 2. Statistical Bound Validation (Upper Bound >= Lower Bound)
    assert all(res_df['demand_upper'] >= res_df['demand_lower']), "RMSE confidence intervals inverted."
    assert all(res_df['demand'] >= 0), "Demand clamped below absolute zero boundary."


# ==========================================
# 3. OPERATIONS: VECTORIZED MATRIX MATH
# ==========================================
def test_profit_optimizer_vectorization():
    """
    Stress-tests the NumPy meshgrid implementation for the Newsvendor model.
    Validates that O(1) matrix math executes without broadcasting errors.
    """
    try:
        # Execute the high-resolution vectorization (100x100 grids)
        fig = profit_optimizer.calculate_profit_scenarios(
            avg_demand=15000,
            std_dev=3500,
            holding_cost=20.0,
            stockout_cost=150.0,
            unit_cost=50.0,
            selling_price=85.0
        )
        assert fig is not None, "Plotly figure failed to render from matrix data."
    except ValueError as e:
        pytest.fail(f"Vectorized matrix broadcasting failed with ValueError: {e}")
