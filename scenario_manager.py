import logging
import pandas as pd

# Configure enterprise-grade logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def create_stress_test(
    df: pd.DataFrame,
    demand_multiplier: float = 1.0,
    lead_time_multiplier: float = 1.0
) -> pd.DataFrame:
    """Generates a stress-test scenario by applying multiplier vectors to baseline data."""
    scenario_df = df.copy()

    if 'demand' in scenario_df.columns:
        scenario_df['demand'] *= demand_multiplier

    if 'lead_time_days' in scenario_df.columns:
        scenario_df['lead_time_days'] *= lead_time_multiplier

    logger.info(
        "Generated stress scenario: Demand x%.2f, Lead Time x%.2f",
        demand_multiplier,
        lead_time_multiplier
    )

    return scenario_df
