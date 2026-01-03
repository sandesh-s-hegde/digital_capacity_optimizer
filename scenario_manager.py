"""
scenario_manager.py
Utilities for generating stress-test scenarios from baseline data.
"""
import pandas as pd

def create_stress_test(df: pd.DataFrame,
                       demand_multiplier: float = 1.0,
                       lead_time_multiplier: float = 1.0) -> pd.DataFrame:
    """
    Creates a new DataFrame with adjusted demand or lead times.

    Args:
        df (pd.DataFrame): The baseline data.
        demand_multiplier (float): Factor to increase/decrease demand (e.g., 1.2 = +20%).
        lead_time_multiplier (float): Factor to delay supply (e.g., 1.5 = +50% delay).

    Returns:
        pd.DataFrame: A modified copy of the dataset.
    """
    # Create a deep copy so we don't mess up the original data
    scenario_df = df.copy()

    # Apply Stress Factors
    scenario_df['demand'] = scenario_df['demand'] * demand_multiplier
    scenario_df['lead_time_days'] = scenario_df['lead_time_days'] * lead_time_multiplier

    print(f"⚠️ Generated Scenario: Demand x{demand_multiplier}, Lead Time x{lead_time_multiplier}")
    return scenario_df