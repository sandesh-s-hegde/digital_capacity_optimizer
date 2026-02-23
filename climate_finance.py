import numpy as np
import pandas as pd
import plotly.graph_objects as go
from scipy.stats import norm


def simulate_ets_carbon_pricing(current_price: float = 85.0, volatility: float = 0.40,
                                drift: float = 0.05, days: int = 365,
                                simulations: int = 2000) -> dict:
    """
    Simulates European Union Emissions Trading System (EU ETS) carbon prices
    using vectorized Geometric Brownian Motion (GBM).
    """
    dt = 1 / 365
    np.random.seed(42)  # For deterministic academic review

    # 1. Initialize Price Matrix
    price_paths = np.zeros((days, simulations))
    price_paths[0] = current_price

    # 2. Vectorized GBM Simulation
    # Eliminates slow python loops for instant Monte Carlo generation
    for t in range(1, days):
        Z = np.random.standard_normal(simulations)
        # GBM Formula: S(t) = S(t-1) * exp((μ - 0.5 * σ^2)dt + σ * sqrt(dt) * Z)
        step = np.exp((drift - 0.5 * volatility ** 2) * dt + volatility * np.sqrt(dt) * Z)
        price_paths[t] = price_paths[t - 1] * step

    # 3. Extract Financial Risk Metrics (End of Year Prices)
    final_prices = price_paths[-1]
    expected_price = np.mean(final_prices)
    cvar_95 = np.percentile(final_prices, 95)  # 95th Percentile Worst-Case Cost

    return {
        "paths": price_paths,
        "expected_price": float(expected_price),
        "cvar_95": float(cvar_95)
    }


def plot_carbon_risk_simulation(current_price: float, volatility: float,
                                total_emissions_tons: float):
    """
    Generates a FinTech-grade Plotly visualization of Carbon Market Risk.
    """
    # Run the simulation
    sim_data = simulate_ets_carbon_pricing(current_price=current_price, volatility=volatility)
    paths = sim_data["paths"]

    # Calculate financial exposure
    current_exposure = current_price * total_emissions_tons
    expected_exposure = sim_data["expected_price"] * total_emissions_tons
    worst_case_exposure = sim_data["cvar_95"] * total_emissions_tons

    fig = go.Figure()

    # Plot a sample of 100 paths to prevent browser memory crashes
    sample_paths = paths[:, :100]
    time_steps = np.arange(365)

    for i in range(sample_paths.shape[1]):
        fig.add_trace(go.Scatter(
            x=time_steps, y=sample_paths[:, i],
            mode='lines', line=dict(color='rgba(93, 109, 126, 0.1)'),
            showlegend=False
        ))

    # Add Expected Mean Line
    mean_path = np.mean(paths, axis=1)
    fig.add_trace(go.Scatter(
        x=time_steps, y=mean_path,
        mode='lines', line=dict(color='#28B463', width=3),
        name=f"Expected Mean (${sim_data['expected_price']:.2f})"
    ))

    # Add 95% CVaR Line
    cvar_path = np.percentile(paths, 95, axis=1)
    fig.add_trace(go.Scatter(
        x=time_steps, y=cvar_path,
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
