from locust import HttpUser, task, between
import uuid
import random

class SupplyChainShockSimulator(HttpUser):
    """
    Simulates a massive macroeconomic shock (e.g., Suez Canal blockage).
    Fires high-velocity stochastic capacity requests to stress-test the Tripartite Ecosystem.
    """
    wait_time = between(0.1, 0.5)

    @task(3)
    def simulate_modern_b2b_surge(self):
        payload = {
            "transaction_id": f"tx-{uuid.uuid4().hex[:8]}",
            "carrier_name": random.choice(["ENTERPRISE", "RYDER", "HERTZ"]),
            "vehicle_type": "EV_VAN_LARGE",
            "max_budget_eur": random.uniform(150.0, 450.0),
            "is_legacy_system": False
        }
        # In a real environment, this hits the AI Brain's ingestion endpoint
        self.client.post("/api/v1/simulate-decision", json=payload, name="B2B Capacity Surge")

    @task(1)
    def simulate_legacy_rpa_surge(self):
        payload = {
            "transaction_id": f"tx-{uuid.uuid4().hex[:8]}",
            "carrier_name": random.choice(["MAERSK", "HAPAG-LLOYD", "DB_SCHENKER"]),
            "vehicle_type": "OCEAN_TEU_20",
            "max_budget_eur": random.uniform(1200.0, 3500.0),
            "is_legacy_system": True
        }
        self.client.post("/api/v1/simulate-decision", json=payload, name="Legacy RPA Surge")
