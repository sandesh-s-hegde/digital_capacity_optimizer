import unittest
import inventory_math

class TestInventoryLogic(unittest.TestCase):

    def test_eoq_calculation(self):
        """Test the Economic Order Quantity formula."""
        # Demand=1000, Setup=$10, Holding=$2 -> EOQ = sqrt(2*1000*10/2) = 100
        result = inventory_math.calculate_eoq(1000, 10, 2)
        self.assertEqual(int(result), 100)

    def test_safety_stock_logic(self):
        """Test that higher service level increases safety stock."""
        # Low service level (50%) vs High service level (95%)
        # Note: At 50% service level (Z=0), safety stock should be 0 or very low
        low_sla = inventory_math.calculate_advanced_safety_stock(100, 10, 1, 0, 0.50)
        high_sla = inventory_math.calculate_advanced_safety_stock(100, 10, 1, 0, 0.95)
        self.assertTrue(high_sla > low_sla)

if __name__ == '__main__':
    unittest.main()