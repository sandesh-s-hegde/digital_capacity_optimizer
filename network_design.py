import googlemaps
from geopy.distance import geodesic
import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")

# Configure APIs
try:
    gmaps = googlemaps.Client(key=API_KEY)
    genai.configure(api_key=API_KEY)
except:
    gmaps = None

# --- 1. GLOBAL CONFIGURATION ---

# A. Landlocked Countries (Cannot use Sea directly)
LANDLOCKED = {
    "NP", "BT", "AF", "KG", "TJ", "UZ", "KZ", "MN",  # Asia
    "CH", "AT", "HU", "SK", "CZ", "RS", "MK", "BY",  # Europe
    "RW", "UG", "ET", "SS", "BF", "NE", "ZM", "ZW",  # Africa
    "BO", "PY"  # South America
}

# B. Open Border / Free Trade Zones (Long-Haul Trucking Permitted > 3500km)
OPEN_BORDERS = {
    "FR", "DE", "ES", "IT", "PL", "NL", "BE", "AT", "DK", "SE", "NO", "FI",
    "PT", "GR", "CZ", "HU", "RO", "BG", "HR", "SI", "SK", "EE", "LV", "LT",
    "IE", "CH", "UK", "GB", "US", "CA", "MX", "AU"
}

# C. Blocked Geopolitical Borders (Trucking Impossible even if road exists)
# Using list of sets for bidirectional blocking
BLOCKED_PAIRS = [
    {"IN", "PK"},  # India - Pakistan (Blocks road to Middle East/Europe)
    {"IN", "CN"},  # India - China (Himalayan border closed for trucks)
    {"KR", "KP"},  # Korea
    {"UA", "RU"},  # Conflict Zone
    {"IL", "LB"}, {"IL", "SY"}  # Middle East closed borders
]


def search_google_places(search_term: str):
    """Auto-complete for the UI."""
    if not gmaps or not search_term or len(search_term) < 2: return []
    try:
        response = gmaps.places_autocomplete(input_text=search_term, types='(cities)')
        return [place['description'] for place in response]
    except:
        return []


def get_location_details(place_name):
    """Gets Lat/Lon and Country Code."""
    if not gmaps: return None
    try:
        res = gmaps.geocode(place_name)
        if res:
            data = res[0]
            loc = data['geometry']['location']
            country = "XX"
            for comp in data['address_components']:
                if 'country' in comp['types']:
                    country = comp['short_name']
                    break
            return {
                "name": data['formatted_address'],
                "lat": loc['lat'],
                "lon": loc['lng'],
                "country": country
            }
    except:
        return None


def get_real_road_distance(origin, dest):
    """Asks Google: Is there a road?"""
    try:
        directions = gmaps.directions(origin, dest, mode="driving")
        if directions:
            return directions[0]['legs'][0]['distance']['value'] / 1000
    except:
        pass
    return None


def analyze_route(origin_addr, dest_addr):
    """
    MASTER LOGIC ENGINE
    Calculates realistic time/cost for Road, Sea, and Air.
    """
    o_data = get_location_details(origin_addr)
    d_data = get_location_details(dest_addr)

    if not o_data or not d_data: return {"error": "Locations not found."}

    # 1. BASELINE DATA
    gc_dist = geodesic((o_data['lat'], o_data['lon']), (d_data['lat'], d_data['lon'])).km
    road_km = get_real_road_distance(o_data['name'], d_data['name'])

    # Identify Country Pair for blocking logic
    current_pair = {o_data['country'], d_data['country']}

    # --- 2. ROAD LOGIC ---
    road_possible = False
    road_metrics = {"cost": 0, "time": 0, "co2": 0}

    if road_km:
        road_possible = True

        # RULE 1: Max Distance Cap
        limit = 3500
        # Exception: Open Borders allow longer trucking
        if o_data['country'] in OPEN_BORDERS and d_data['country'] in OPEN_BORDERS:
            limit = 7000

        if road_km > limit:
            road_possible = False

        # RULE 2: Blocked Borders (Geopolitics)
        for blocked in BLOCKED_PAIRS:
            if blocked == current_pair:
                road_possible = False
                break

        # Specific India Rule: If routing West (not NP/BT/BD), usually blocked by PK logic
        if o_data['country'] == 'IN' and d_data['country'] not in ['IN', 'NP', 'BT', 'BD']:
            if road_km > 2000: road_possible = False

        if road_possible:
            # TIME: 500km/day (Driver Limits) + 1 day load + Border Penalty
            border_penalty = 0
            if o_data['country'] != d_data['country']:
                if o_data['country'] not in OPEN_BORDERS or d_data['country'] not in OPEN_BORDERS:
                    border_penalty = 2.0  # 2 days customs

            road_time = 1.0 + (road_km / 500) + border_penalty
            road_cost = 200 + (road_km * 1.1)
            road_metrics = {"cost": road_cost, "time": road_time, "co2": road_km * 0.105}

    # --- 3. SEA LOGIC ---
    sea_possible = True

    # RULE 1: Landlocked
    if o_data['country'] in LANDLOCKED or d_data['country'] in LANDLOCKED:
        sea_possible = False

    # RULE 2: Too Short
    if gc_dist < 800:
        sea_possible = False

    # RULE 3: Domestic (Unless huge coast)
    if o_data['country'] == d_data['country'] and gc_dist < 3000:
        sea_possible = False

    sea_metrics = {"cost": 0, "time": 0, "co2": 0}
    if sea_possible:
        sea_dist = gc_dist * 1.6

        # TIME: Port Handling (8 days) + Drayage (3 days) + Buffer (3 days) + Sailing
        drayage_time = 3.0
        port_handling = 8.0
        frequency_buffer = 3.0

        sea_time = port_handling + drayage_time + frequency_buffer + (sea_dist / 35 / 24)
        sea_cost = 600 + (sea_dist * 0.15)
        sea_metrics = {"cost": sea_cost, "time": sea_time, "co2": sea_dist * 0.015}

    # --- 4. AIR LOGIC ---
    air_possible = True
    if gc_dist < 400: air_possible = False  # Too short

    air_metrics = {"cost": 0, "time": 0, "co2": 0}
    if air_possible:
        air_dist = gc_dist * 1.05
        # TIME: 4 days processing + Flight
        air_time = 4.0 + (air_dist / 800 / 24)
        air_cost = 800 + (air_dist * 4.5)
        air_metrics = {"cost": air_cost, "time": air_time, "co2": air_dist * 0.600}

    # --- 5. RECOMMENDATION ---
    rec = "Road"
    reason = "Regional standard."

    if not road_possible and not sea_possible and not air_possible:
        rec = "None"
        reason = "No commercial route found."

    # Priority 1: Short Haul Road
    elif road_possible and road_km < 1200:
        rec = "Road"
        reason = "Short-Haul: Trucking is fastest."

    # Priority 2: Sea (Cost)
    elif sea_possible:
        rec = "Sea"
        reason = "Long-Haul: Ocean Freight (Cost Optimal)."

    # Priority 3: Air (Urgency/Landlocked)
    elif air_possible:
        rec = "Air"
        reason = "Landlocked/Urgent: Air Freight."

    # Priority 4: Long Haul Road (Open Borders)
    elif road_possible:
        rec = "Road"
        reason = "Long-Haul Trucking."

    return {
        "origin": o_data, "dest": d_data,
        "recommendation": rec, "reason": reason,
        "metrics": {
            "road": {"possible": road_possible, **road_metrics},
            "sea": {"possible": sea_possible, **sea_metrics},
            "air": {"possible": air_possible, **air_metrics}
        }
    }


def ask_gemini_logistics(user_question, route_context):
    """
    Sends the calculated route data + user question to Gemini for a realistic explanation.
    """
    try:
        # 1. LOAD THE SPECIFIC AI KEY (Not the Maps Key)
        ai_key = os.getenv("GEMINI_API_KEY")
        if not ai_key:
            return "⚠️ Error: Missing GEMINI_API_KEY in .env file."

        # 2. CONFIGURE WITH AI KEY
        genai.configure(api_key=ai_key)

        # 3. USE THE MODEL
        model = genai.GenerativeModel('gemini-flash-latest')

        # Feed calculated metrics into the prompt for grounding
        context_str = f"""
        You are a Logistics Expert AI. You are analyzing a route from {route_context['origin']['name']} to {route_context['dest']['name']}.

        DATA CONTEXT:
        - Recommended Mode: {route_context['recommendation']} ({route_context['reason']})
        - Road Data: {route_context['metrics']['road']}
        - Sea Data: {route_context['metrics']['sea']}
        - Air Data: {route_context['metrics']['air']}

        USER QUESTION: "{user_question}"

        INSTRUCTIONS:
        Answer strictly based on supply chain logic. Explain the data.
        If Road is impossible, explain why (e.g. "Too long for trucking" or "Geopolitical block").
        If Sea takes long, mention "Port congestion" or "Drayage".
        Keep it professional, concise, and helpful.
        """

        response = model.generate_content(context_str)
        return response.text
    except Exception as e:
        return f"⚠️ AI Service Unavailable: {str(e)}"
