"""
test_suite.py
Unit tests to verify Operations Research logic before deployment.
"""
import unittest
from inventory_math import calculate_eoq, calculate_safety_stock

class TestInventoryLogic(unittest.TestCase):

    def test_eoq_calculation(self):
        # Case 1: Standard Values
        # D=1000, S=10, H=2 -> Sqrt(2*1000*10 / 2) = Sqrt(10000) = 100
        result = calculate_eoq(1000, 10, 2)
        self.assertEqual(result, 100.0)
        print("✅ EOQ Standard Test Passed")

    def test_eoq_zero_holding_cost(self):
        # Case 2: Division by Zero prevention
        result = calculate_eoq(1000, 10, 0)
        self.assertEqual(result, 0.0)
        print("✅ EOQ Zero-Division Test Passed")

    def test_safety_stock(self):
        # Case 3: Safety Stock
        # Max=50, Avg=40, LT=10 -> (50*10) - (40*10) = 500 - 400 = 100
        result = calculate_safety_stock(50, 40, 10)
        self.assertEqual(result, 100)
        print("✅ Safety Stock Test Passed")

if __name__ == '__main__':
    print("--- 🧪 Running Automated Diagnostics ---")
    unittest.main()