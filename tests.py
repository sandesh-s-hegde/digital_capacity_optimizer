import unittest
from inventory_math import calculate_horizontal_sharing, calculate_resilience_score


class TestLogic(unittest.TestCase):

    def test_horizontal_cooperation_overflow(self) -> None:
        """Validates cooperation logic and cost allocation during capacity overflow constraints."""
        result = calculate_horizontal_sharing(
            total_demand=120.0,
            internal_capacity=100.0,
            partner_surcharge=5.0,
            base_holding_cost=10.0
        )

        self.assertEqual(result["overflow_vol"], 20.0)
        self.assertEqual(result["internal_vol"], 100.0)
        self.assertEqual(result["total_cost"], 1300.0)

    def test_horizontal_cooperation_under_capacity(self) -> None:
        """Verifies that no partner outsourcing is triggered when internal capacity is sufficient."""
        result = calculate_horizontal_sharing(
            total_demand=80.0,
            internal_capacity=100.0,
            partner_surcharge=5.0,
            base_holding_cost=10.0
        )

        self.assertEqual(result["overflow_vol"], 0.0)
        self.assertEqual(result["dependency_ratio"], 0.0)

    def test_resilience_score_perfect(self) -> None:
        """Asserts that a risk-free, fully independent operational lane achieves a maximum resilience score."""
        score = calculate_resilience_score(
            safety_stock=100.0,
            combined_volatility=0.0,
            dependency_ratio=0.0
        )

        self.assertEqual(score, 100.0)

    def test_resilience_score_high_dependency(self) -> None:
        """Validates that maximal partner dependency applies the correct mathematical penalty to the resilience index."""
        score = calculate_resilience_score(
            safety_stock=100.0,
            combined_volatility=10.0,
            dependency_ratio=100.0
        )

        self.assertEqual(score, 50.0)


if __name__ == '__main__':
    unittest.main()
