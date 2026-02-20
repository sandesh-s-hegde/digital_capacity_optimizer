import pandas as pd
import numpy as np

def generate_forecast(df: pd.DataFrame, months: int = 3) -> pd.DataFrame:
    """
    Takes the historical dataframe and projects 'months' into the future
    using linear trend projection, integrating standard error for 95% confidence intervals.
    """
    if len(df) < 3:
        return None  # Need at least 3 data points to calculate meaningful variance

    # 1. Prepare Data (Use copy to avoid SettingWithCopyWarning)
    df_clean = df.copy().sort_values('date')
    df_clean['date_ordinal'] = df_clean['date'].map(pd.Timestamp.toordinal)

    # 2. Calculate Trend Line (Linear Regression)
    x = df_clean['date_ordinal'].values
    y = df_clean['demand'].values
    slope, intercept = np.polyfit(x, y, 1)
    trend_line = np.poly1d([slope, intercept])

    # 3. Calculate Historical Error for Confidence Bounds
    # Root Mean Square Error (RMSE) to determine expected forecast drift
    historical_predictions = trend_line(x)
    residuals = y - historical_predictions
    std_error = np.std(residuals)

    # 4. Generate Future Dates (Pandas Vectorized Approach)
    last_date = df_clean['date'].max()
    future_dates = [last_date + pd.DateOffset(months=i) for i in range(1, months + 1)]

    # 5. Predict Values for Future Dates
    future_ordinals = np.array([d.toordinal() for d in future_dates])
    predicted_demand = trend_line(future_ordinals)

    # 6. Build DataFrame with 95% Confidence Intervals (Z = 1.96)
    forecast_df = pd.DataFrame({
        'date': future_dates,
        'demand': np.maximum(0, predicted_demand),  # Vectorized floor clamp
        'demand_upper': np.maximum(0, predicted_demand + (1.96 * std_error)),
        'demand_lower': np.maximum(0, predicted_demand - (1.96 * std_error)),
        'type': 'Forecast'
    })

    return forecast_df
