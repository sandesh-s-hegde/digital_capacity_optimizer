import math


def calculate_eoq(annual_demand: float, order_cost: float, holding_cost: float) -> float:
    """
    Calculates the Economic Order Quantity (EOQ).
    """
    if holding_cost <= 0:
        return 0.0

    try:
        eoq = math.sqrt((2 * annual_demand * order_cost) / holding_cost)
        return eoq
    except ValueError:
        return 0.0


# REVERTED: lead_time is first again to satisfy old tests
def calculate_safety_stock(lead_time: float, std_dev_demand: float, service_level_z: float = 1.645) -> float:
    """
    Calculates Safety Stock.
    """
    return service_level_z * std_dev_demand * math.sqrt(lead_time)


def calculate_newsvendor_target(holding_cost: float, stockout_cost: float) -> float:
    """
    Calculates target service level (Critical Ratio).
    """
    if (holding_cost + stockout_cost) == 0:
        return 0.0

    return stockout_cost / (holding_cost + stockout_cost)


def calculate_required_inventory(current_inventory: int, safety_stock: float, reorder_point: float) -> float:
    """
    Determines how much new inventory to buy.
    """
    target = safety_stock + reorder_point
    if current_inventory >= target:
        return 0.0
    return target - current_inventory