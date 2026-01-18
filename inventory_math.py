import math

def calculate_eoq(annual_demand, order_cost, holding_cost):
    """Calculates Economic Order Quantity."""
    if holding_cost <= 0: return 0.0
    try:
        return math.sqrt((2 * annual_demand * order_cost) / holding_cost)
    except ValueError:
        return 0.0

def calculate_safety_stock(std_dev_demand, service_level_z=1.645, lead_time=1.0):
    """
    Calculates Safety Stock.
    Args:
        std_dev_demand: The standard deviation of demand.
        service_level_z: The Z-score (default 1.645).
        lead_time: The lead time in months (default 1.0).
    """
    return service_level_z * std_dev_demand * math.sqrt(lead_time)

def calculate_newsvendor_target(holding_cost, stockout_cost):
    """Calculates Critical Ratio."""
    if (holding_cost + stockout_cost) == 0: return 0.0
    return stockout_cost / (holding_cost + stockout_cost)

def calculate_required_inventory(current_inventory, safety_stock, reorder_point):
    """Calculates Net Inventory Requirement."""
    target = safety_stock + reorder_point
    return target - current_inventory