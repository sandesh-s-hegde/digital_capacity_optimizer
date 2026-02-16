import pandas as pd
import numpy as np
import plotly.graph_objects as go


def solve_center_of_gravity(customers):
    """
    Calculates the demand-weighted Center of Gravity (CoG).
    Mathematical Logic:
    Lat_opt = Σ(Lat_i * Demand_i) / Σ(Demand_i)
    Lon_opt = Σ(Lon_i * Demand_i) / Σ(Demand_i)
    """
    df = pd.DataFrame(customers)

    if df['demand'].sum() == 0:
        return 0, 0

    # Vectorized calculation for speed
    total_demand = df['demand'].sum()
    cg_lat = (df['lat'] * df['demand']).sum() / total_demand
    cg_lon = (df['lon'] * df['demand']).sum() / total_demand

    return cg_lat, cg_lon


def generate_network_map(customers, hub_lat, hub_lon):
    """Generates a professional supply chain map."""
    df = pd.DataFrame(customers)

    fig = go.Figure()

    # 1. Demand Clusters (Customers)
    fig.add_trace(go.Scattermapbox(
        lat=df['lat'], lon=df['lon'],
        mode='markers+text',
        marker=go.scattermapbox.Marker(
            size=df['demand'] / 100,  # Scaled size
            color='rgb(50, 100, 200)',
            opacity=0.8
        ),
        text=df['name'],
        name='Demand Nodes'
    ))

    # 2. The Optimal Hub (Red Star)
    fig.add_trace(go.Scattermapbox(
        lat=[hub_lat], lon=[hub_lon],
        mode='markers',
        marker=go.scattermapbox.Marker(
            size=20, color='red', symbol='star'
        ),
        name='Optimal DC Location'
    ))

    # 3. Connectivity Lines (Spokes)
    for _, row in df.iterrows():
        fig.add_trace(go.Scattermapbox(
            mode="lines",
            lon=[hub_lon, row['lon']],
            lat=[hub_lat, row['lat']],
            line=dict(width=1, color='gray'),
            hoverinfo='none',
            showlegend=False
        ))

    fig.update_layout(
        mapbox_style="carto-positron",
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        height=500,
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01)
    )

    return fig
