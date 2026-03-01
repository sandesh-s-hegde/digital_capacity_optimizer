import os
import logging
from typing import List, Dict, Any, Optional
import googlemaps
from geopy.distance import geodesic
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

API_KEY = os.getenv("GOOGLE_API_KEY")

try:
    gmaps = googlemaps.Client(key=API_KEY) if API_KEY else None
except Exception as e:
    logger.error("Failed to initialize Google Maps client: %s", e)
    gmaps = None

LANDLOCKED = {
    "NP", "BT", "AF", "KG", "TJ", "UZ", "KZ", "MN",
    "CH", "AT", "HU", "SK", "CZ", "RS", "MK", "BY",
    "RW", "UG", "ET", "SS", "BF", "NE", "ZM", "ZW",
    "BO", "PY"
}

OPEN_BORDERS = {
    "FR", "DE", "ES", "IT", "PL", "NL", "BE", "AT", "DK", "SE", "NO", "FI",
    "PT", "GR", "CZ", "HU", "RO", "BG", "HR", "SI", "SK", "EE", "LV", "LT",
    "IE", "CH", "UK", "GB", "US", "CA", "MX", "AU"
}

BLOCKED_PAIRS = [
    {"IN", "PK"}, {"IN", "CN"}, {"KR", "KP"},
    {"UA", "RU"}, {"IL", "LB"}, {"IL", "SY"}
]


def search_google_places(search_term: str) -> List[str]:
    """Provides auto-complete suggestions for locations via Google Places API."""
    if not gmaps or not search_term or len(search_term) < 2:
        return []
    try:
        response = gmaps.places_autocomplete(input_text=search_term, types='(cities)')
        return [place['description'] for place in response]
    except Exception as e:
        logger.error("Places API error: %s", e)
        return []


def get_location_details(place_name: str) -> Optional[Dict[str, Any]]:
    """Retrieves geospatial coordinates and ISO country codes for a given location."""
    if not gmaps:
        return None
    try:
        res = gmaps.geocode(place_name)
        if not res:
            return None

        data = res[0]
        loc = data['geometry']['location']
        country_code = "XX"

        for comp in data['address_components']:
            if 'country' in comp['types']:
                country_code = comp['short_name']
                break

        return {
            "name": data['formatted_address'],
            "lat": loc['lat'],
            "lon": loc['lng'],
            "country": country_code
        }
    except Exception as e:
        logger.error("Geocoding error for %s: %s", place_name, e)
        return None


def get_real_road_distance(origin: str, dest: str) -> Optional[float]:
    """Queries Google Directions API to validate the existence of a physical road route."""
    if not gmaps:
        return None
    try:
        directions = gmaps.directions(origin, dest, mode="driving")
        if directions:
            return directions[0]['legs'][0]['distance']['value'] / 1000.0
    except Exception as e:
        logger.warning("No valid road found between %s and %s: %s", origin, dest, e)
    return None


def analyze_route(origin_addr: str, dest_addr: str) -> Dict[str, Any]:
    """Calculates multimodal transport viability, costs, and carbon emissions."""
    o_data = get_location_details(origin_addr)
    d_data = get_location_details(dest_addr)

    if not o_data or not d_data:
        return {"error": "Locations could not be resolved."}

    gc_dist = geodesic((o_data['lat'], o_data['lon']), (d_data['lat'], d_data['lon'])).km
    road_km = get_real_road_distance(o_data['name'], d_data['name'])
    current_pair = {o_data['country'], d_data['country']}

    # --- Road Logic ---
    road_possible = bool(road_km)
    road_metrics = {"cost": 0.0, "time": 0.0, "co2": 0.0}

    if road_possible and road_km:
        limit = 7000.0 if (o_data['country'] in OPEN_BORDERS and d_data['country'] in OPEN_BORDERS) else 3500.0

        if road_km > limit or current_pair in BLOCKED_PAIRS:
            road_possible = False

        if o_data['country'] == 'IN' and d_data['country'] not in ['IN', 'NP', 'BT', 'BD'] and road_km > 2000:
            road_possible = False

        if road_possible:
            border_penalty = 2.0 if (o_data['country'] != d_data['country'] and
                                     (o_data['country'] not in OPEN_BORDERS or d_data[
                                         'country'] not in OPEN_BORDERS)) else 0.0

            road_time = 1.0 + (road_km / 500.0) + border_penalty
            road_metrics = {
                "cost": 200.0 + (road_km * 1.1),
                "time": road_time,
                "co2": road_km * 0.105
            }

    # --- Sea Logic ---
    sea_possible = True
    if o_data['country'] in LANDLOCKED or d_data['country'] in LANDLOCKED or gc_dist < 800:
        sea_possible = False
    if o_data['country'] == d_data['country'] and gc_dist < 3000:
        sea_possible = False

    sea_metrics = {"cost": 0.0, "time": 0.0, "co2": 0.0}
    if sea_possible:
        sea_dist = gc_dist * 1.6
        sea_time = 8.0 + 3.0 + 3.0 + (sea_dist / 35.0 / 24.0)
        sea_metrics = {
            "cost": 600.0 + (sea_dist * 0.15),
            "time": sea_time,
            "co2": sea_dist * 0.015
        }

    # --- Air Logic ---
    air_possible = gc_dist >= 400
    air_metrics = {"cost": 0.0, "time": 0.0, "co2": 0.0}
    if air_possible:
        air_dist = gc_dist * 1.05
        air_metrics = {
            "cost": 800.0 + (air_dist * 4.5),
            "time": 4.0 + (air_dist / 800.0 / 24.0),
            "co2": air_dist * 0.600
        }

    # --- Strategy Recommendation ---
    rec, reason = "Road", "Regional standard."

    if not road_possible and not sea_possible and not air_possible:
        rec, reason = "None", "No commercial route found."
    elif road_possible and road_km and road_km < 1200:
        rec, reason = "Road", "Short-Haul: Trucking is fastest."
    elif sea_possible:
        rec, reason = "Sea", "Long-Haul: Ocean Freight (Cost Optimal)."
    elif air_possible:
        rec, reason = "Air", "Landlocked/Urgent: Air Freight."
    elif road_possible:
        rec, reason = "Road", "Long-Haul Trucking."

    return {
        "origin": o_data,
        "dest": d_data,
        "recommendation": rec,
        "reason": reason,
        "metrics": {
            "road": {"possible": road_possible, **road_metrics},
            "sea": {"possible": sea_possible, **sea_metrics},
            "air": {"possible": air_possible, **air_metrics}
        }
    }


def ask_gemini_logistics(user_question: str, route_context: Dict[str, Any]) -> str:
    """Interfaces with Gemini to provide qualitative context on multimodal routing decisions."""
    try:
        ai_key = os.getenv("GEMINI_API_KEY")
        if not ai_key:
            return "Error: Missing GEMINI_API_KEY in environment variables."

        genai.configure(api_key=ai_key)
        model = genai.GenerativeModel('gemini-flash-latest')

        context_str = f"""
        You are a quantitative Logistics Expert analyzing a trade lane from {route_context['origin']['name']} to {route_context['dest']['name']}.

        DATA CONTEXT:
        - Recommended Mode: {route_context['recommendation']} ({route_context['reason']})
        - Road Data: {route_context['metrics']['road']}
        - Sea Data: {route_context['metrics']['sea']}
        - Air Data: {route_context['metrics']['air']}

        USER QUESTION: "{user_question}"

        INSTRUCTIONS:
        Answer strictly based on operations research and supply chain logic. Explain the data objectively.
        If Road is impossible, explain the geopolitical or distance constraints.
        Maintain an academic, concise, and highly professional tone.
        """

        response = model.generate_content(context_str)
        return response.text
    except Exception as e:
        logger.error("AI Service Error: %s", e)
        return "AI Service Unavailable. Please check system logs."
