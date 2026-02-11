"""
LSP Digital Capacity Twin
=========================

A stochastic digital twin for logistics service providers (LSPs) to optimize
capacity, inventory, and risk management.

This package operationalizes the "Pixels to Premiums" research framework.
"""

# Operational Core
from .inventory_math import (
    calculate_eoq,
    calculate_safety_stock,
    calculate_service_level,
    calculate_newsvendor_target,
    calculate_required_inventory
)

# Strategic Research Engines (New in v5.0)
from .monte_carlo import run_simulation
from .fta_macro import calculate_landed_cost

__all__ = [
    "calculate_eoq",
    "calculate_safety_stock",
    "calculate_service_level",
    "calculate_newsvendor_target",
    "calculate_required_inventory",
    "run_simulation",
    "calculate_landed_cost"
]

__version__ = "3.9.0"
__author__ = "Sandesh Hegde"
__license__ = "MIT"
__status__ = "Research Artifact"
__email__ = "s.sandesh.hegde@gmail.com"

def get_info():
    """Returns the research context for this artifact."""
    return {
        "Project": "LSP Digital Capacity Twin",
        "Framework": "Pixels to Premiums",
        "Version": __version__,
        "Author": __author__,
        "Status": __status__
    }
