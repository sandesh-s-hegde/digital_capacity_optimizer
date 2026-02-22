import plotly.graph_objects as go
from typing import Optional

# 1. EXPANDED GLOBAL COORDINATES
LOCATIONS = {
    "BER": {"lat": 52.5200, "lon": 13.4050, "name": "Berlin (Hub)"},
    "MUC": {"lat": 48.1351, "lon": 11.5820, "name": "Munich (Dest)"},
    "HAM": {"lat": 53.5511, "lon": 9.9937, "name": "Hamburg (Port)"},
    "ROT": {"lat": 51.9244, "lon": 4.4777, "name": "Rotterdam (Partner)"},
    "FRA": {"lat": 50.1109, "lon": 8.6821, "name": "Frankfurt (Air)"},
    "PAR": {"lat": 48.8566, "lon": 2.3522, "name": "Paris (Pharma)"},
    "SHG": {"lat": 31.2304, "lon": 121.4737, "name": "Shanghai (Origin)"}, # NEW: Ocean Lane
    "BOM": {"lat": 19.0760, "lon": 72.8777, "name": "Mumbai (Origin)"}   # NEW: Air Lane
}

def render_map(route_name: str, is_disrupted: bool = False,
               outsourced_vol: int = 0, transport_mode: str = "Road") -> Optional[go.Figure]:
    """
    Renders a dynamic geospatial trade lane.
    Auto-scales between European and Global projections based on origin/destination.
    """
    # 1. Parse Route Safely
    try:
        origin_code = route_name[:3].upper()
        dest_code = route_name[4:7].upper()
        start = LOCATIONS.get(origin_code)
        end = LOCATIONS.get(dest_code)
        if not start or not end:
            return None
    except Exception:
        return None

    # 2. Define Visual Style & Semantics
    line_color = '#2ca02c'  # Green (Standard)
    line_dash = 'solid'     # Standard Truck
    status_text = f"Mode: {transport_mode}"

    # Mode Logic (Visuals)
    if "Rail" in transport_mode:
        line_dash = 'dash'
        line_color = '#7f7f7f'  # Industrial Grey
    elif "Air" in transport_mode:
        line_dash = 'dot'
        line_color = '#1f77b4'  # Sky Blue
    elif "Ocean" in route_name or "Sea" in transport_mode: # Added Ocean support
        line_dash = 'longdash'
        line_color = '#000080'  # Navy Blue

    # Override for Risk Events
    if is_disrupted:
        line_color = '#d62728'  # Red (Shock)
        status_text += "<br>🔴 DISRUPTED (Route Blocked)"
    elif outsourced_vol > 0:
        line_color = '#ff7f0e'  # Orange (Overflow)
        status_text += f"<br>🟡 Horizontal Coop: {outsourced_vol} units outsourced"

    # 3. Dynamic Geospatial Scoping
    # If coordinates go beyond Europe (Longitude > 40), switch to Global View
    is_global = start['lon'] > 40 or end['lon'] > 40
    map_scope = 'world' if is_global else 'europe'
    projection_type = 'natural earth' if is_global else 'mercator'

    # 4. Build Plotly Figure
    fig = go.Figure()

    # Add Great Circle Route Line
    fig.add_trace(go.Scattergeo(
        lon=[start['lon'], end['lon']],
        lat=[start['lat'], end['lat']],
        mode='lines',
        line=dict(width=3, color=line_color, dash=line_dash),
        name=transport_mode,
        hoverinfo='text',
        text=status_text
    ))

    # Add Hub Nodes
    fig.add_trace(go.Scattergeo(
        lon=[start['lon'], end['lon']],
        lat=[start['lat'], end['lat']],
        mode='markers+text',
        text=[start['name'], end['name']],
        textposition=["top center", "bottom center"],
        textfont=dict(family="Arial", size=12, color="black"),
        marker=dict(size=12, color='#2C3E50', line=dict(width=2, color='white')),
        name='Logistics Hubs',
        hoverinfo='text'
    ))

    # Configure Layout
    fig.update_layout(
        title_text=f"📍 Trade Lane: {route_name}",
        geo=dict(
            scope=map_scope,
            projection_type=projection_type,
            showland=True,
            landcolor="rgb(245, 245, 245)",
            showocean=True,
            oceancolor="rgb(225, 235, 245)",
            countrycolor="rgb(200, 200, 200)",
            showcountries=True,
        ),
        margin={"r": 0, "t": 40, "l": 0, "b": 0},
        height=350,
        showlegend=False
    )

    return fig
