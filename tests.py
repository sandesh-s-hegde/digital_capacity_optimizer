import unittest
from inventory_math import calculate_horizontal_sharing, calculate_resilience_score


class TestWallenburgLogic(unittest.TestCase):

    def test_horizontal_cooperation_overflow(self):
        """
        Test that cooperation logic correctly identifies overflow.
        Scenario: Demand (120) > Capacity (100) -> Overflow (20)
        """
        result = calculate_horizontal_sharing(
            total_demand=120,
            internal_capacity=100,
            partner_surcharge=5.0,
            base_holding_cost=10.0
        )
        self.assertEqual(result["overflow_vol"], 20)
        self.assertEqual(result["internal_vol"], 100)

        # Cost Check:
        # Internal: 100 units * $10 = $1000
        # Outsourced: 20 units * ($10 + $5) = $300
        # Total: $1300
        self.assertEqual(result["total_cost"], 1300.0)

    def test_horizontal_cooperation_under_capacity(self):
        """
        Test that no outsourcing happens when capacity is sufficient.
        Scenario: Demand (80) < Capacity (100) -> Overflow (0)
        """
        result = calculate_horizontal_sharing(
            total_demand=80,
            internal_capacity=100,
            partner_surcharge=5.0,
            base_holding_cost=10.0
        )
        self.assertEqual(result["overflow_vol"], 0)
        self.assertEqual(result["dependency_ratio"], 0.0)

    def test_resilience_score_perfect(self):
        """
        Test that a risk-free, independent lane gets a perfect score.
        """
        score = calculate_resilience_score(
            safety_stock=100,
            combined_volatility=0,  # No risk
            dependency_ratio=0  # No dependency
        )
        self.assertEqual(score, 100.0)

    def test_resilience_score_high_dependency(self):
        """
        Test that high dependency on a partner lowers the resilience score.
        """
        # Coverage Score (Max 50): Let's say we have good stock (50 pts)
        # Independence Score (Max 50): 100% Dependency = 0 pts
        # Total should be around 50
        score = calculate_resilience_score(
            safety_stock=100,
            combined_volatility=10,  # Good coverage
            dependency_ratio=100  # Bad dependency
        )
        self.assertEqual(score, 50.0)


if __name__ == '__main__':
    unittest.main()