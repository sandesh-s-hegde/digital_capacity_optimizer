"""
LSP Digital Capacity Twin
=========================

A stochastic digital twin for logistics service providers (LSPs) to optimize
capacity, inventory, and risk management.

This package operationalizes the "Pixels to Premiums" research framework.
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

__version__ = "3.9.0"
__author__ = "Sandesh Hegde"
