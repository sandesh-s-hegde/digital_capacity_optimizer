import pytest
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

import climate_finance
import profit_optimizer
import forecast

def test_gbm_carbon_simulation_integrity():
    """Validates the Stochastic EU ETS Carbon Pricing model."""
    current_price = 85.0
    volatility = 0.40
    days = 365
    simulations = 2000

    res = climate_finance.simulate_ets_carbon_pricing(
        current_price=current_price,
        volatility=volatility,
        days=days,
        simulations=simulations
    )

    assert res["paths"].shape == (days, simulations), "GBM matrix dimensions collapsed."
    assert res["cvar_95"] > res["expected_price"], "CVaR boundary failed to exceed expected mean."
    assert np.all(res["paths"] > 0), "GBM produced negative asset prices."

def test_forecast_rmse_confidence_intervals():
    """Validates linear trend forecasting and RMSE-based confidence intervals."""
    dates = pd.date_range(start="2025-01-01", periods=10, freq='D')
    demand = [100, 105, 110, 108, 115, 120, 118, 125, 130, 135]
    df = pd.DataFrame({'date': dates, 'demand': demand})

    res_df = forecast.generate_forecast(df, months=3)

    assert res_df is not None, "Forecaster returned None on valid dataframe."
    assert len(res_df) == 3, "Forecaster failed to project the requested horizon."
    assert all(res_df['demand_upper'] >= res_df['demand_lower']), "RMSE confidence intervals inverted."
    assert all(res_df['demand'] >= 0), "Demand clamped below absolute zero."

def test_profit_optimizer_vectorization():
    """Stress-tests the NumPy meshgrid implementation for the Newsvendor model."""
    try:
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
        pytest.fail(f"Vectorized matrix broadcasting failed: {e}")
