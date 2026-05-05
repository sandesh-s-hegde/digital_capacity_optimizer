from esg_client import fetch_carbon_intensity


def check_grid_emissions(region_code: str) -> dict:
    """
    Checks the real-time carbon intensity of a specific geographic energy grid.
    Use this tool BEFORE dispatching an electric vehicle (EV) or heavy asset to ensure
    the local grid is running on renewable energy (GREEN status).

    Args:
        region_code: The 2-letter country code (e.g., 'FR' for France, 'DE' for Germany).
    """
    return fetch_carbon_intensity(region_code)
