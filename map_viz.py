import plotly.graph_objects as go

# Hardcoded coordinates for the demo scenarios
LOCATIONS = {
    "BER": {"lat": 52.5200, "lon": 13.4050, "name": "Berlin (Hub)"},
    "MUC": {"lat": 48.1351, "lon": 11.5820, "name": "Munich (Dest)"},
    "HAM": {"lat": 53.5511, "lon": 9.9937, "name": "Hamburg (Port)"},
    "ROT": {"lat": 51.9244, "lon": 4.4777, "name": "Rotterdam (Partner)"},
    "FRA": {"lat": 50.1109, "lon": 8.6821, "name": "Frankfurt (Air)"},
    "PAR": {"lat": 48.8566, "lon": 2.3522, "name": "Paris (Pharma)"}
}


def render_map(route_name, is_disrupted=False, outsourced_vol=0, transport_mode="Road"):
    """
    Draws a connection map.
    Visuals change based on:
    1. Disruption (Red)
    2. Outsourcing (Orange)
    3. Transport Mode (Line Style: Solid/Dash/Dot)
    """

    # 1. Parse Route
    try:
        origin_code = route_name[:3].upper()
        dest_code = route_name[4:7].upper()
        start = LOCATIONS.get(origin_code)
        end = LOCATIONS.get(dest_code)
        if not start or not end: return None
    except:
        return None

    # 2. Define Visual Style
    line_color = '#2ca02c'  # Green (Standard)
    line_dash = 'solid'  # Standard Truck
    status_text = f"Mode: {transport_mode}"

    # Mode Logic (Visuals)
    if "Rail" in transport_mode:
        line_dash = 'dash'  # Train tracks look
        line_color = '#7f7f7f'  # Industrial Grey/Black
    elif "Air" in transport_mode:
        line_dash = 'dot'  # Flight path look
        line_color = '#1f77b4'  # Sky Blue

    # Override for Events
    if is_disrupted:
        line_color = '#d62728'  # Red (Shock)
        status_text += " | 🔴 DISRUPTED"
    elif outsourced_vol > 0:
        line_color = '#ff7f0e'  # Orange (Overflow)
        status_text += " | 🟡 Horizontal Coop Active"

    # 3. Build Plotly Map
    fig = go.Figure()

    # Route Line
    fig.add_trace(go.Scattergeo(
        lon=[start['lon'], end['lon']],
        lat=[start['lat'], end['lat']],
        mode='lines',
        line=dict(width=3, color=line_color, dash=line_dash),
        name=transport_mode,
        hoverinfo='text',
        text=status_text
    ))

    # Hub Nodes
    fig.add_trace(go.Scattergeo(
        lon=[start['lon'], end['lon']],
        lat=[start['lat'], end['lat']],
        mode='markers+text',
        text=[start['name'], end['name']],
        textposition=["top center", "bottom center"],
        marker=dict(size=10, color='#333', line=dict(width=1, color='white')),
        name='Hubs'
    ))

    fig.update_layout(
        title_text=f"📍 Network: {route_name} [{transport_mode}]",
        geo=dict(
            scope='europe',
            projection_type='mercator',
            showland=True,
            landcolor="rgb(250, 250, 250)",
            countrycolor="rgb(200, 200, 200)",
        ),
        margin={"r": 0, "t": 30, "l": 0, "b": 0},
        height=300
    )

    return fig