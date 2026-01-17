import math

def calculate_eoq(annual_demand: float, order_cost: float, holding_cost: float) -> float:
    """
    Calculates the Economic Order Quantity (EOQ).
    
    Formula: sqrt((2 * Demand * Order_Cost) / Holding_Cost)
    
    Args:
        annual_demand (float): Total units needed per year.
        order_cost (float): Cost to place a single order.
        holding_cost (float): Cost to hold one unit for a year.
        
    Returns:
        float: The optimal number of units to order at once.
    """
    if holding_cost <= 0:
        return 0.0
    
    try:
        eoq = math.sqrt((2 * annual_demand * order_cost) / holding_cost)
        return eoq
    except ValueError:
        return 0.0

def calculate_safety_stock(lead_time: float, std_dev_demand: float, service_level_z: float = 1.645) -> float:
    """
    Calculates Safety Stock required to handle demand volatility.
    
    Args:
        lead_time (float): Time (in months) to receive goods.
        std_dev_demand (float): Standard deviation of monthly demand.
        service_level_z (float): Z-score for desired service level (default 95% = 1.645).
        
    Returns:
        float: Units of safety stock required.
    """
    # Safety Stock = Z * std_dev * sqrt(lead_time)
    # We assume lead_time is 1 month for simplicity in this dashboard
    return service_level_z * std_dev_demand * math.sqrt(lead_time)

def calculate_newsvendor_target(holding_cost: float, stockout_cost: float) -> float:
    """
    Calculates the critical ratio (Target Service Level) for the Newsvendor model.
    
    Returns:
        float: A percentage (e.g., 0.95 for 95%) representing optimal service level.
    """
    if (holding_cost + stockout_cost) == 0:
        return 0.0
        
    return stockout_cost / (holding_cost + stockout_cost)

def calculate_required_inventory(current_inventory: int, safety_stock: float, reorder_point: float) -> float:
    """
    Determines how much new inventory we need to buy right now.
    """
    target = safety_stock + reorder_point
    if current_inventory >= target:
        return 0.0
    return target - current_inventory