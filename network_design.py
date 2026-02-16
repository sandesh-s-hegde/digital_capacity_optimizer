import pandas as pd
import numpy as np
import plotly.graph_objects as go
from geopy.geocoders import Nominatim
from geopy.distance import geodesic

# --- STRATEGIC ASSET DATABASE: DHL NETWORK ---
DHL_HUBS = [
    {"code": "LEJ", "name": "Leipzig (Global Hub)", "lat": 51.4239, "lon": 12.2363, "region": "Europe"},
    {"code": "CVG", "name": "Cincinnati (Americas Hub)", "lat": 39.0461, "lon": -84.6621, "region": "Americas"},
    {"code": "HKG", "name": "Hong Kong (Asia Hub)", "lat": 22.3080, "lon": 113.9185, "region": "Asia"},
    {"code": "EMA", "name": "East Midlands (UK Hub)", "lat": 52.8311, "lon": -1.3280, "region": "Europe"},
    {"code": "BRU", "name": "Brussels (Euro Hub)", "lat": 50.9014, "lon": 4.4844, "region": "Europe"},
    {"code": "BGY", "name": "Bergamo (Southern Euro)", "lat": 45.6739, "lon": 9.7041, "region": "Europe"},
    {"code": "VGT", "name": "Vitoria (Iberian Hub)", "lat": 42.8828, "lon": -2.7245, "region": "Europe"},
    {"code": "CPH", "name": "Copenhagen (Nordic Hub)", "lat": 55.6180, "lon": 12.6508, "region": "Europe"},
]


def get_coordinates(city_name):
    """Geocodes a city name to Lat/Lon."""
    try:
        geolocator = Nominatim(user_agent="lsp_digital_twin_research_v4")
        location = geolocator.geocode(city_name)
        if location:
            return location.latitude, location.longitude
        else:
            return None, None
    except:
        return None, None


def solve_network(customers, transport_rate_per_km=1.5):
    """
    1. Calculates Mathematical Center of Gravity (Ideal).
    2. Snaps to the nearest DHL Hub (Real).
    """
    df = pd.DataFrame(customers)
    if df.empty or df['demand'].sum() == 0: return None

    # 1. Mathematical Optimization (The "Ideal" Point)
    total_demand = df['demand'].sum()
    ideal_lat = (df['lat'] * df['demand']).sum() / total_demand
    ideal_lon = (df['lon'] * df['demand']).sum() / total_demand

    # 2. Network Selection (The "Real" Point)
    nearest_hub = None
    min_dist = float('inf')

    for hub in DHL_HUBS:
        # Calculate geodesic distance (more accurate than euclidean)
        dist = geodesic((ideal_lat, ideal_lon), (hub['lat'], hub['lon'])).km
        if dist < min_dist:
            min_dist = dist
            nearest_hub = hub

    # 3. Calculate Final Costs based on the REAL HUB
    # We measure distance from customers to the DHL HUB, not the ideal point
    df['dist_to_hub_km'] = df.apply(
        lambda row: geodesic((row['lat'], row['lon']), (nearest_hub['lat'], nearest_hub['lon'])).km, axis=1
    )

    total_cost = (df['dist_to_hub_km'] * df['demand'] * (transport_rate_per_km / 1000)).sum()

    return {
        "ideal_lat": ideal_lat,
        "ideal_lon": ideal_lon,
        "hub_name": nearest_hub['name'],
        "hub_code": nearest_hub['code'],
        "hub_lat": nearest_hub['lat'],
        "hub_lon": nearest_hub['lon'],
        "deviation_km": min_dist,
        "total_cost": total_cost,
        "customer_df": df
    }


def plot_strategic_map(res):
    """Visualizes: Customers vs. Ideal CoG vs. Real DHL Hub."""
    if not res: return go.Figure()

    df = res['customer_df']

    fig = go.Figure()

    # 1. The Real DHL Hub (Operational Reality)
    fig.add_trace(go.Scattermapbox(
        lat=[res['hub_lat']], lon=[res['hub_lon']],
        mode='markers+text',
        marker=go.scattermapbox.Marker(size=30, color='#D40511', symbol='airport'),  # DHL Red
        text=[f"<b>{res['hub_code']}</b><br>{res['hub_name']}"],
        textposition="top center",
        name='Selected DHL Hub'
    ))

    # 2. The Mathematical Ideal (Theoretical Minimum)
    fig.add_trace(go.Scattermapbox(
        lat=[res['ideal_lat']], lon=[res['ideal_lon']],
        mode='markers',
        marker=go.scattermapbox.Marker(size=15, color='gray', opacity=0.5, symbol='circle'),
        text=["Theoretical Optimal Location"],
        name='Mathematical Ideal (CoG)'
    ))

    # 3. Connector: Ideal -> Real (Visualizing the Deviation)
    fig.add_trace(go.Scattermapbox(
        mode="lines",
        lon=[res['ideal_lon'], res['hub_lon']],
        lat=[res['ideal_lat'], res['hub_lat']],
        line=dict(width=2, color='red', dash='dot'),
        name=f"Deviation: {int(res['deviation_km'])}km"
    ))

    # 4. Demand Clusters
    fig.add_trace(go.Scattermapbox(
        lat=df['lat'], lon=df['lon'],
        mode='markers',
        marker=go.scattermapbox.Marker(size=df['demand'] / 100, color='#FFCC00', opacity=0.9),  # DHL Yellow
        text=df['name'],
        name='Demand Nodes'
    ))

    # 5. Spokes (Customer -> Hub)
    for _, row in df.iterrows():
        fig.add_trace(go.Scattermapbox(
            mode="lines",
            lon=[res['hub_lon'], row['lon']],
            lat=[res['hub_lat'], row['lat']],
            line=dict(width=1, color='gray'),
            showlegend=False,
            hoverinfo='skip'
        ))

    fig.update_layout(
        mapbox_style="carto-positron",
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        height=600,
        legend=dict(orientation="h", yanchor="bottom", y=0.02, xanchor="right", x=1)
    )
    return fig
