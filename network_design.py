import pandas as pd
import numpy as np
import plotly.graph_objects as go
from geopy.distance import geodesic
import requests

# --- 1. THE "INSTANT" CACHE (Top Global Logistics Hubs) ---
# Format: "City, Country": {"lat": ..., "lon": ...}
CITY_DATABASE = {
    # ASIA
    "Shanghai, CN": {"lat": 31.2304, "lon": 121.4737},
    "Singapore, SG": {"lat": 1.3521, "lon": 103.8198},
    "Beijing, CN": {"lat": 39.9042, "lon": 116.4074},
    "Bengaluru, IN": {"lat": 12.9716, "lon": 77.5946},
    "Tokyo, JP": {"lat": 35.6762, "lon": 139.6503},
    "Hong Kong, HK": {"lat": 22.3193, "lon": 114.1694},
    "Mumbai, IN": {"lat": 19.0760, "lon": 72.8777},
    "Seoul, KR": {"lat": 37.5665, "lon": 126.9780},
    "Bangkok, TH": {"lat": 13.7563, "lon": 100.5018},
    "Dubai, AE": {"lat": 25.2769, "lon": 55.2962},
    "Shenzhen, CN": {"lat": 22.5431, "lon": 114.0579},
    "Guangzhou, CN": {"lat": 23.1291, "lon": 113.2644},
    "New Delhi, IN": {"lat": 28.6139, "lon": 77.2090},
    "Jakarta, ID": {"lat": -6.2088, "lon": 106.8456},
    "Ho Chi Minh City, VN": {"lat": 10.8231, "lon": 106.6297},
    "Taipei, TW": {"lat": 25.0330, "lon": 121.5654},
    "Kuala Lumpur, MY": {"lat": 3.1390, "lon": 101.6869},
    "Chennai, IN": {"lat": 13.0827, "lon": 80.2707},
    "Osaka, JP": {"lat": 34.6937, "lon": 135.5023},

    # EUROPE
    "London, UK": {"lat": 51.5074, "lon": -0.1278},
    "Paris, FR": {"lat": 48.8566, "lon": 2.3522},
    "Berlin, DE": {"lat": 52.5200, "lon": 13.4050},
    "Frankfurt, DE": {"lat": 50.1109, "lon": 8.6821},
    "Rotterdam, NL": {"lat": 51.9244, "lon": 4.4777},
    "Antwerp, BE": {"lat": 51.2194, "lon": 4.4025},
    "Hamburg, DE": {"lat": 53.5511, "lon": 9.9937},
    "Amsterdam, NL": {"lat": 52.3676, "lon": 4.9041},
    "Milan, IT": {"lat": 45.4642, "lon": 9.1900},
    "Madrid, ES": {"lat": 40.4168, "lon": -3.7038},
    "Barcelona, ES": {"lat": 41.3851, "lon": 2.1734},
    "Munich, DE": {"lat": 48.1351, "lon": 11.5820},
    "Zurich, CH": {"lat": 47.3769, "lon": 8.5417},
    "Dublin, IE": {"lat": 53.3498, "lon": -6.2603},
    "Warsaw, PL": {"lat": 52.2297, "lon": 21.0122},
    "Istanbul, TR": {"lat": 41.0082, "lon": 28.9784},
    "Cork, IE": {"lat": 51.8985, "lon": -8.4756},

    # AMERICAS
    "New York, US": {"lat": 40.7128, "lon": -74.0060},
    "Los Angeles, US": {"lat": 34.0522, "lon": -118.2437},
    "Chicago, US": {"lat": 41.8781, "lon": -87.6298},
    "Toronto, CA": {"lat": 43.6510, "lon": -79.3470},
    "Mexico City, MX": {"lat": 19.4326, "lon": -99.1332},
    "Sao Paulo, BR": {"lat": -23.5505, "lon": -46.6333},
    "Buenos Aires, AR": {"lat": -34.6037, "lon": -58.3816},
    "Miami, US": {"lat": 25.7617, "lon": -80.1918},
    "San Francisco, US": {"lat": 37.7749, "lon": -122.4194},
    "Dallas, US": {"lat": 32.7767, "lon": -96.7970},  # FIXED HERE
    "Atlanta, US": {"lat": 33.7490, "lon": -84.3880},
    "Houston, US": {"lat": 29.7604, "lon": -95.3698},
    "Vancouver, CA": {"lat": 49.2827, "lon": -123.1207},

    # OTHER
    "Sydney, AU": {"lat": -33.8688, "lon": 151.2093},
    "Melbourne, AU": {"lat": -37.8136, "lon": 144.9631},
    "Cape Town, ZA": {"lat": -33.9249, "lon": 18.4241},
    "Lagos, NG": {"lat": 6.5244, "lon": 3.3792},
}

# DHL Hub Database
DHL_HUBS = [
    {"code": "LEJ", "name": "Leipzig (Global)", "lat": 51.4239, "lon": 12.2363},
    {"code": "CVG", "name": "Cincinnati (US)", "lat": 39.0461, "lon": -84.6621},
    {"code": "HKG", "name": "Hong Kong (Asia)", "lat": 22.3080, "lon": 113.9185},
    {"code": "EMA", "name": "East Midlands (UK)", "lat": 52.8311, "lon": -1.3280},
    {"code": "MIA", "name": "Miami (LatAm)", "lat": 25.7959, "lon": -80.2870},
    {"code": "BAH", "name": "Bahrain (ME)", "lat": 26.2708, "lon": 50.6336},
    {"code": "BRU", "name": "Brussels (Euro)", "lat": 50.9014, "lon": 4.4844},
    {"code": "DXB", "name": "Dubai (Global)", "lat": 25.2532, "lon": 55.3657},
    {"code": "SIN", "name": "Singapore (APAC)", "lat": 1.3644, "lon": 103.9915},
    {"code": "JFK", "name": "New York (East)", "lat": 40.6413, "lon": -73.7781}
]


def get_city_list():
    """Returns a sorted list of city names for the dropdown."""
    return sorted(list(CITY_DATABASE.keys()))


def get_coords(city_name):
    """Returns dict {lat, lon, name} for a given city."""
    if city_name in CITY_DATABASE:
        data = CITY_DATABASE[city_name].copy()
        data['name'] = city_name
        return data

    # Fallback Geocoder (Only runs if user types a custom city not in list)
    try:
        url = "https://nominatim.openstreetmap.org/search"
        params = {"q": city_name, "format": "json", "limit": 1}
        headers = {"User-Agent": "LSP_Twin_Fallback"}
        res = requests.get(url, params=params, headers=headers, timeout=2)
        if res.status_code == 200 and res.json():
            place = res.json()[0]
            return {
                "name": city_name,
                "lat": float(place['lat']),
                "lon": float(place['lon'])
            }
    except:
        pass
    return None


def find_nearest_hub(lat, lon):
    nearest = None
    min_dist = float('inf')
    for hub in DHL_HUBS:
        dist = geodesic((lat, lon), (hub['lat'], hub['lon'])).km
        if dist < min_dist:
            min_dist = dist
            nearest = hub
    return nearest, min_dist


def analyze_route(origin_name, dest_name):
    """
    Main Logic: Calculates route between two named cities.
    """
    # 1. Look up coordinates
    origin_data = get_coords(origin_name)
    dest_data = get_coords(dest_name)

    if not origin_data or not dest_data: return None

    lat_a, lon_a = origin_data['lat'], origin_data['lon']
    lat_b, lon_b = dest_data['lat'], dest_data['lon']

    # 2. Direct Distance
    direct_km = geodesic((lat_a, lon_a), (lat_b, lon_b)).km

    # 3. Network Routing (Hub A -> Hub B)
    hub_a, dist_to_hub_a = find_nearest_hub(lat_a, lon_a)
    hub_b, dist_to_hub_b = find_nearest_hub(lat_b, lon_b)

    inter_hub_dist = geodesic((hub_a['lat'], hub_a['lon']), (hub_b['lat'], hub_b['lon'])).km
    total_air_km = dist_to_hub_a + inter_hub_dist + dist_to_hub_b

    return {
        "origin": origin_data,
        "dest": dest_data,
        "hub_origin": hub_a,
        "hub_dest": hub_b,
        "metrics": {
            "direct_km": direct_km,
            "network_km": total_air_km,
            "road_cost": direct_km * 1.5,
            "road_time": direct_km / 65 / 24,
            "air_cost": total_air_km * 4.2,
            "air_time": (total_air_km / 800 / 24) + 1.0,
        }
    }


def plot_route_map(data):
    """
    Visualizes the Route.
    Logic: Only draws the RED Air Network line if distance > 400km.
    """
    if not data: return go.Figure()

    o = data['origin']
    d = data['dest']
    h1 = data['hub_origin']
    h2 = data['hub_dest']
    dist_km = data['metrics']['direct_km']  # Get the total distance

    fig = go.Figure()

    # 1. Endpoints (Always Show)
    fig.add_trace(go.Scattermapbox(
        lat=[o['lat'], d['lat']], lon=[o['lon'], d['lon']],
        mode='markers+text',
        marker=dict(size=12, color='#004562'),
        text=[o['name'], d['name']], textposition="bottom center", name='Location'
    ))

    # 2. Direct Road Path (Always Show - Grey)
    fig.add_trace(go.Scattermapbox(
        mode="lines", lon=[o['lon'], d['lon']], lat=[o['lat'], d['lat']],
        line=dict(width=2, color='grey'), name='Direct Road'
    ))

    # 3. SMART AIR LOGIC: Only show Hubs & Flight Path if > 400km
    if dist_km > 400:
        # Plot Hubs
        fig.add_trace(go.Scattermapbox(
            lat=[h1['lat'], h2['lat']], lon=[h1['lon'], h2['lon']],
            mode='markers+text',
            marker=dict(size=18, color='#D40511', symbol='airport'),
            text=[h1['code'], h2['code']], textposition="top center", name='DHL Hub'
        ))

        # Plot Flight Path (Red)
        path_lats = [o['lat'], h1['lat'], h2['lat'], d['lat']]
        path_lons = [o['lon'], h1['lon'], h2['lon'], d['lon']]

        fig.add_trace(go.Scattermapbox(
            mode="lines", lon=path_lons, lat=path_lats,
            line=dict(width=3, color='#D40511'), name='Express Air'
        ))

    fig.update_layout(
        mapbox_style="carto-positron", margin={"r": 0, "t": 0, "l": 0, "b": 0}, height=500,
        legend=dict(orientation="h", y=0.01, x=0.01),
        title=f"Strategic Routing: {o['name']} ➡ {d['name']}"
    )
    return fig
