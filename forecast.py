import pandas as pd
import numpy as np
from datetime import timedelta
from dateutil.relativedelta import relativedelta


def generate_forecast(df, months=3):
    """
    Takes the historical dataframe and projects 'months' into the future
    using a simple linear trend line (numpy polyfit).
    """
    if len(df) < 2:
        return None  # Not enough data to predict

    # 1. Prepare Data for Math (Convert Dates to Ordinal Numbers)
    df = df.sort_values('date')
    df['date_ordinal'] = df['date'].map(pd.Timestamp.toordinal)

    # 2. Calculate Trend Line (Linear Regression)
    # This finds the "slope" of your demand growth/shrinkage
    z = np.polyfit(df['date_ordinal'], df['demand'], 1)
    p = np.poly1d(z)

    # 3. Generate Future Dates
    last_date = df['date'].max()
    future_dates = []

    # We predict 1 point per month for the next N months
    current_date = last_date
    for _ in range(months):
        current_date = current_date + relativedelta(months=1)
        future_dates.append(current_date)

    # 4. Predict Values for those Future Dates
    future_ordinals = [d.toordinal() for d in future_dates]
    predicted_demand = p(future_ordinals)

    # 5. Create DataFrame for the Forecast
    forecast_df = pd.DataFrame({
        'date': future_dates,
        'demand': predicted_demand,
        'type': 'Forecast'
    })

    # Ensure no negative demand (impossible)
    forecast_df['demand'] = forecast_df['demand'].apply(lambda x: max(0, x))

    return forecast_df