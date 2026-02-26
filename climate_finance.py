import numpy as np
import plotly.graph_objects as go


def simulate_ets_carbon_pricing(
    current_price: float = 85.0,
    volatility: float = 0.40,
    drift: float = 0.05,
    days: int = 365,
    simulations: int = 2000
) -> dict:
    """Simulates EU ETS carbon prices using fully vectorized Geometric Brownian Motion."""
    np.random.seed(42)
    dt = 1 / 365

    # Generate standard normal shocks for the entire matrix simultaneously
    Z = np.random.standard_normal((days, simulations))
    Z[0] = 0.0

    # Calculate Brownian paths (W_t) via cumulative sum
    W = np.cumsum(Z, axis=0) * np.sqrt(dt)

    # Generate time array and broadcast it to the matrix shape
    time_steps = np.linspace(0, 1, days)[:, np.newaxis]

    # Execute full GBM matrix calculation in O(1) Python time
    price_paths = current_price * np.exp((drift - 0.5 * volatility ** 2) * time_steps + volatility * W)

    final_prices = price_paths[-1]

    return {
        "paths": price_paths,
        "expected_price": float(np.mean(final_prices)),
        "cvar_95": float(np.percentile(final_prices, 95))
    }


def plot_carbon_risk_simulation(current_price: float, volatility: float, total_emissions_tons: float):
    """Generates an interactive Plotly visualization of stochastic carbon market risk."""
    sim_data = simulate_ets_carbon_pricing(current_price=current_price, volatility=volatility)
    paths = sim_data["paths"]

    current_exposure = current_price * total_emissions_tons
    expected_exposure = sim_data["expected_price"] * total_emissions_tons
    worst_case_exposure = sim_data["cvar_95"] * total_emissions_tons

    fig = go.Figure()
    time_steps = np.arange(365)
    sample_paths = paths[:, :100]

    for i in range(sample_paths.shape[1]):
        fig.add_trace(go.Scatter(
            x=time_steps, y=sample_paths[:, i],
            mode='lines', line=dict(color='rgba(93, 109, 126, 0.1)'),
            showlegend=False
        ))

    fig.add_trace(go.Scatter(
        x=time_steps, y=np.mean(paths, axis=1),
        mode='lines', line=dict(color='#28B463', width=3),
        name=f"Expected Mean (${sim_data['expected_price']:.2f})"
    ))

    fig.add_trace(go.Scatter(
        x=time_steps, y=np.percentile(paths, 95, axis=1),
        mode='lines', line=dict(color='#E74C3C', width=3, dash='dash'),
        name=f"95% Risk Bound (${sim_data['cvar_95']:.2f})"
    ))

    fig.update_layout(
        title="EU ETS Carbon Price Stochastic Simulation (GBM)",
        xaxis_title="Days (1 Year Horizon)",
        yaxis_title="Carbon Price ($ / tonne)",
        height=450,
        margin=dict(l=0, r=0, t=40, b=0),
        hovermode="x unified"
    )

    return fig, {
        "current_exposure": current_exposure,
        "expected_exposure": expected_exposure,
        "worst_case_exposure": worst_case_exposure
    }
