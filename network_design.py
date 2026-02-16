import googlemaps
from datetime import datetime
from geopy.distance import geodesic
import os
from dotenv import load_dotenv

load_dotenv()
gmaps = googlemaps.Client(key=os.getenv("GOOGLE_API_KEY"))


def search_google_places(search_term: str):
    """Provides dynamic city suggestions for the search box."""
    if not gmaps or not search_term or len(search_term) < 2:
        return []
    try:
        response = gmaps.places_autocomplete(input_text=search_term, types='(cities)')
        return [place['description'] for place in response]
    except:
        return []


def get_google_coords(place_name):
    """Converts location strings into coordinates."""
    try:
        res = gmaps.geocode(place_name)
        if res:
            loc = res[0]['geometry']['location']
            return {"name": res[0]['formatted_address'], "lat": loc['lat'], "lon": loc['lng']}
    except:
        return None


def analyze_route(origin_addr, dest_addr):
    """Calculates detailed logistics KPIs including Landed Cost and CO2."""
    o_data = get_google_coords(origin_addr)
    d_data = get_google_coords(dest_addr)

    if not o_data or not d_data:
        return {"error": "Locations not found."}

    # Great Circle Distance for baseline
    gc_dist = geodesic((o_data['lat'], o_data['lon']), (d_data['lat'], d_data['lon'])).km

    # Mode-Specific Detailing
    # Road (Trucking)
    road_dist = gc_dist * 1.25
    # Sea (Maritime Lanes)
    sea_dist = gc_dist * 1.6
    # Air (Direct flight path)
    air_dist = gc_dist * 1.05

    return {
        "origin": o_data,
        "dest": d_data,
        "recommendation": "Air" if gc_dist > 3500 else "Road",
        "metrics": {
            "road": {
                "possible": True if gc_dist < 4500 else False,
                "time": road_dist / 55 / 24,  # Days
                "cost": 200 + (road_dist * 0.95),
                "co2": road_dist * 0.08  # kg CO2
            },
            "sea": {
                "possible": True if gc_dist > 800 else False,
                "time": 7 + (sea_dist / 25 / 24),  # Handling + Days
                "cost": 350 + (sea_dist * 0.12),
                "co2": sea_dist * 0.01
            },
            "air": {
                "possible": True if gc_dist > 400 else False,
                "time": 1.5 + (air_dist / 800 / 24),  # Handling + Days
                "cost": 500 + (air_dist * 4.2),
                "co2": air_dist * 0.6
            }
        }
    }
