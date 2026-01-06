"""
main.py
Digital Capacity Optimizer v6.0 - The Oracle Edition (Predictive)
"""
from inventory_math import calculate_newsvendor_target, calculate_required_inventory
from data_loader import load_data
from forecaster import generate_forecast
from visualizer import plot_forecast
import config

def run_simulation():
    print("--- 🔮 Digital Capacity Optimizer v6.0 (Predictive Mode) ---")

    # 1. Load History
    df = load_data('mock_data.csv')
    if df.empty: return

    # 2. Generate Forecast (Look 3 months ahead)
    print("Step 1: Training Forecasting Model...")
    forecast_result = generate_forecast(df, months_ahead=3)
    forecast_values = forecast_result['forecast_values']

    # 3. Visualize
    plot_forecast(df, forecast_values)

    # 4. Decision Logic (Proactive)
    # We don't care about last year's average anymore.
    # We care about NEXT MONTH'S prediction.
    next_month_demand = forecast_values.iloc[0]
    std_dev_demand = df['demand'].std() # We assume volatility stays similar

    print(f"\n📊 PROACTIVE ANALYSIS")
    print(f"   -> Historical Avg Demand: {round(df['demand'].mean(), 1)}")
    print(f"   -> Predicted Next Month:  {round(next_month_demand, 1)} (Growth Trend)")

    # 5. Optimize for Future
    optimal_sla = calculate_newsvendor_target(config.HOLDING_COST, config.STOCKOUT_COST)
    required_inventory = calculate_required_inventory(next_month_demand, std_dev_demand, optimal_sla)

    print("-" * 60)
    print(f"🔮 RECOMMENDATION (For Month 13):")
    print(f"   Buy {required_inventory} units.")
    print(f"   (Based on {round(optimal_sla*100, 1)}% Service Level against FORECASTED demand)")
    print("-" * 60)

if __name__ == "__main__":
    run_simulation()