"""
azure_model.py
Defines the physical infrastructure topology for the simulation.
"""

# Azure Regions & Their Characteristics
# Lead Time = Days to ship hardware to this location
REGIONS = {
    "west-europe": {
        "name": "West Europe (Netherlands)",
        "sla": 0.9999,
        "shipping_delay_days": 14,
        "risk_factor": 1.0
    },
    "north-europe": {
        "name": "North Europe (Ireland)",
        "sla": 0.9999,
        "shipping_delay_days": 18,  # Slower logistics
        "risk_factor": 1.2
    },
    "east-us": {
        "name": "East US (Virginia)",
        "sla": 0.9999,
        "shipping_delay_days": 7,   # Closer to suppliers
        "risk_factor": 0.8
    }
}

def get_region_delay(region_key: str) -> int:
    """Returns the shipping lead time for a specific Azure region."""
    return REGIONS.get(region_key, {}).get("shipping_delay_days", 14)