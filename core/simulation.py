import numpy as np
import logging

logger = logging.getLogger("digital-twin")


class MonteCarloEngine:
    @staticmethod
    def calculate_shortfall_risk(current_capacity: int, historical_mean_demand: float, volatility_std: float,
                                 simulations: int = 10000) -> dict:
        """
        Runs a vectorized Monte Carlo simulation using a Log-Normal distribution
        to predict the probability of demand exceeding available physical capacity.
        """
        try:
            simulated_demand = np.random.lognormal(
                mean=np.log(historical_mean_demand ** 2 / np.sqrt(volatility_std ** 2 + historical_mean_demand ** 2)),
                sigma=np.sqrt(np.log(1 + (volatility_std ** 2 / historical_mean_demand ** 2))),
                size=simulations
            )

            shortfalls = simulated_demand[simulated_demand > current_capacity]
            shortfall_probability = len(shortfalls) / simulations
            expected_shortfall_volume = np.mean(shortfalls) - current_capacity if len(shortfalls) > 0 else 0.0

            return {
                "risk_level": "CRITICAL" if shortfall_probability > 0.15 else "STABLE",
                "shortfall_probability": round(shortfall_probability, 4),
                "expected_asset_deficit": int(np.ceil(expected_shortfall_volume)),
                "simulations_run": simulations
            }
        except Exception as e:
            logger.error(f"Monte Carlo simulation failed: {str(e)}")
            raise e
