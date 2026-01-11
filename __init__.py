"""
Digital Capacity Optimizer
==========================

A supply chain intelligence package for cloud infrastructure.
"""

from .inventory_math import (
    calculate_eoq,
    calculate_safety_stock,
    calculate_service_level,
    calculate_newsvendor_target,
    calculate_required_inventory
)

__all__ = [
    "calculate_eoq",
    "calculate_safety_stock",
    "calculate_service_level",
    "calculate_newsvendor_target",
    "calculate_required_inventory"
]

__version__ = "1.0.0"
__author__ = "Sandesh Hegde"