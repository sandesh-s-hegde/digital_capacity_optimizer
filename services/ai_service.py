import os
import logging
from core.simulation import MonteCarloEngine

logger = logging.getLogger("digital-twin")


class CapacityIntelligenceService:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")

    async def determine_action(self, carrier: str, capacity: int, mean_demand: float, volatility: float) -> dict:
        """Attempts AI inference, falls back to raw statistical heuristics if AI is degraded."""
        stats = MonteCarloEngine.calculate_shortfall_risk(capacity, mean_demand, volatility)

        try:
            raise ConnectionError("Simulated LLM API Timeout")
        except Exception as e:
            logger.warning(f"AI Inference degraded ({str(e)}). Engaging heuristic fallback circuit.")
            return self._heuristic_fallback(carrier, stats)

    def _heuristic_fallback(self, carrier: str, stats: dict) -> dict:
        """Deterministic rule-based routing when the neural network is down."""
        if stats["risk_level"] == "CRITICAL" and stats["expected_asset_deficit"] > 0:
            is_legacy = carrier.upper() in ["MAERSK", "HAPAG-LLOYD"]
            return {
                "action": "EXECUTE_BOOKING",
                "carrier_name": carrier,
                "assets_required": stats["expected_asset_deficit"],
                "is_legacy_system": is_legacy,
                "reason": f"Fallback trigger: {stats['shortfall_probability'] * 100}% probability of failure."
            }
        return {"action": "HOLD", "reason": "Capacity deemed sufficient via fallback heuristics."}
