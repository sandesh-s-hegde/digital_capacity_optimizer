from typing import Optional
import numpy as np
import pandas as pd


def generate_forecast(df: pd.DataFrame, months: int = 3) -> Optional[pd.DataFrame]:
    """Projects future demand using linear trend regression and 95% confidence intervals."""
    if len(df) < 3:
        return None

    df_clean = df.copy().sort_values('date')
    x = df_clean['date'].map(pd.Timestamp.toordinal).values
    y = df_clean['demand'].values

    slope, intercept = np.polyfit(x, y, 1)
    trend_line = np.poly1d([slope, intercept])

    residuals = y - trend_line(x)
    std_error = np.std(residuals)

    last_date = df_clean['date'].max()
    future_dates = [last_date + pd.DateOffset(months=i) for i in range(1, months + 1)]
    future_ordinals = np.array([d.toordinal() for d in future_dates])

    predicted_demand = trend_line(future_ordinals)

    return pd.DataFrame({
        'date': future_dates,
        'demand': np.maximum(0, predicted_demand),
        'demand_upper': np.maximum(0, predicted_demand + (1.96 * std_error)),
        'demand_lower': np.maximum(0, predicted_demand - (1.96 * std_error)),
        'type': 'Forecast'
    })
