import unittest
import inventory_math


class TestInventoryLogic(unittest.TestCase):

    def test_eoq_calculation(self) -> None:
        """Validates the Economic Order Quantity (EOQ) mathematical constraint."""
        result = inventory_math.calculate_eoq(1000.0, 10.0, 2.0)
        self.assertEqual(result, 100)

    def test_safety_stock_logic(self) -> None:
        """Verifies that monotonic increases in Service Level Agreements (SLA) positively scale safety stock."""
        low_sla = inventory_math.calculate_advanced_safety_stock(100.0, 10.0, 1.0, 0.0, 0.50)
        high_sla = inventory_math.calculate_advanced_safety_stock(100.0, 10.0, 1.0, 0.0, 0.95)

        self.assertGreater(high_sla, low_sla)


if __name__ == '__main__':
    unittest.main()
