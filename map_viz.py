import plotly.graph_objects as go

# Hardcoded coordinates for the demo scenarios
# This ensures it works perfectly offline without needing a Geocoding API
LOCATIONS = {
    "BER": {"lat": 52.5200, "lon": 13.4050, "name": "Berlin (Hub)"},
    "MUC": {"lat": 48.1351, "lon": 11.5820, "name": "Munich (Dest)"},
    "HAM": {"lat": 53.5511, "lon": 9.9937, "name": "Hamburg (Port)"},
    "ROT": {"lat": 51.9244, "lon": 4.4777, "name": "Rotterdam (Partner)"},
    "FRA": {"lat": 50.1109, "lon": 8.6821, "name": "Frankfurt (Air)"},
    "PAR": {"lat": 48.8566, "lon": 2.3522, "name": "Paris (Pharma)"}
}


def render_map(route_name, is_disrupted=False, outsourced_vol=0):
    """
    Draws a connection map for the selected service lane.
    Colors the line RED if disrupted, GREEN if optimal.
    """

    # 1. Parse the Route (e.g., "BER-MUC")
    try:
        # Extract 3-letter codes
        origin_code = route_name[:3].upper()
        dest_code = route_name[4:7].upper()

        start = LOCATIONS.get(origin_code)
        end = LOCATIONS.get(dest_code)

        if not start or not end:
            return None  # Skip map if codes don't match known cities

    except:
        return None

    # 2. Define Visual Style based on Status
    line_color = '#2ca02c'  # Green (Normal)
    status_text = "Status: 🟢 Flowing"

    if is_disrupted:
        line_color = '#d62728'  # Red (Shock)
        status_text = "Status: 🔴 DISRUPTED (Port Strike)"
    elif outsourced_vol > 0:
        line_color = '#ff7f0e'  # Orange (Overflow)
        status_text = "Status: 🟡 Overflow > Partner Network"

    # 3. Build the Plotly Map
    fig = go.Figure()

    # Draw the Route Line
    fig.add_trace(go.Scattergeo(
        lon=[start['lon'], end['lon']],
        lat=[start['lat'], end['lat']],
        mode='lines',
        line=dict(width=4, color=line_color),
        name='Service Lane',
        hoverinfo='none'
    ))

    # Draw the Nodes (Cities)
    fig.add_trace(go.Scattergeo(
        lon=[start['lon'], end['lon']],
        lat=[start['lat'], end['lat']],
        mode='markers+text',
        text=[start['name'], end['name']],
        textposition=["top center", "bottom center"],
        marker=dict(size=12, color='#1f77b4', line=dict(width=2, color='white')),
        name='Hubs'
    ))

    # 4. Map Layout (Focused on Europe)
    fig.update_layout(
        title_text=f"📍 Network Visibility: {route_name} | {status_text}",
        geo=dict(
            scope='europe',
            projection_type='mercator',
            showland=True,
            landcolor="rgb(250, 250, 250)",
            subunitcolor="rgb(217, 217, 217)",
            countrycolor="rgb(217, 217, 217)",
            countrywidth=0.5,
            subunitwidth=0.5
        ),
        margin={"r": 0, "t": 40, "l": 0, "b": 0},
        height=350
    )

    return fig