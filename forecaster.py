"""
forecaster.py
Predictive analytics engine using Exponential Smoothing (Holt's Linear).
"""
import pandas as pd
from statsmodels.tsa.holtwinters import ExponentialSmoothing


def generate_forecast(df: pd.DataFrame, months_ahead: int = 3):
    """
    Predicts future demand using Holt's Linear Trend method.

    Args:
        df (pd.DataFrame): Historical data.
        months_ahead (int): How many months to predict.

    Returns:
        dict: Contains 'model' object and 'forecast' values.
    """
    # 1. Prepare Data (Extract demand series)
    # We use simple integer indexing for this mock dataset
    series = df['demand'].astype(float)

    # 2. Train Model (Holt's Linear Trend)
    # trend='add' means we expect demand to grow linearly (additive)
    model = ExponentialSmoothing(
        series,
        trend='add',
        seasonal=None,
        initialization_method="estimated"
    ).fit()

    # 3. Predict Future
    forecast_values = model.forecast(months_ahead)

    print(f"🔮 Forecast generated for next {months_ahead} months.")
    return {
        "model": model,
        "forecast_values": forecast_values
    }