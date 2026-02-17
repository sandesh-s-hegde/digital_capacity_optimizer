# 🚛 LSP Digital Capacity Twin: Multi-Modal Stochastic Engine

**Author:** Sandesh Hegde  
**Version:** v4.2.0 (Network Designer Edition)

![Python](https://img.shields.io/badge/Python-3.11-blue?style=for-the-badge&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-v1.31-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Research_Artifact-orange?style=for-the-badge)
![Cloud](https://img.shields.io/badge/Deployed_on-Render-46E3B7?style=for-the-badge&logo=render&logoColor=white)

## 🚀 Live Demo

**[Click here to launch the Research Artifact](https://digital-capacity-optimizer.onrender.com/)** *(Note: Hosted on Render Free Tier. Please allow 30s for cold start.)*

---

## 📖 Executive Summary
This artifact operationalizes the **"Pixels to Premiums"** research framework, serving as a **Decision Support System (DSS)** for Logistics Service Providers (LSPs). It provides advanced **Risk Quantification**, **Resilience Simulation**, and now **Geospatial Network Design** to solve for the "China Plus One" strategy, the impact of Free Trade Agreements (FTAs), and complex multi-modal routing constraints.

---

## 🧮 Methodological Framework

### 1. Multi-Modal Trade-off Logic
The engine applies strategic multipliers to simulate mode-specific constraints. The "Iron Triangle" of Logistics is modeled as:

* **Lead Time ($L_m$):** $L_{base} \times M_{time}$ (e.g., Air = 0.2x, Rail = 1.5x)
* **Unit Cost ($C_m$):** $C_{base} \times M_{cost}$ (e.g., Air = 3.0x, Rail = 0.7x)
* **Emissions ($E_m$):** $E_{base} \times M_{co2}$ (e.g., Air = 5.0x, Rail = 0.3x)

### 2. Geospatial & Geopolitical Routing (New!)
The Network Designer utilizes a deterministic logic engine to validate commercial viability:
* **Geodesic Distance:** Calculated using Vincenty’s formulae via `geopy`.
* **Geopolitical Filtering:** Automatically blocks routes through conflict zones (e.g., India-Pakistan borders) and enforces "Open Border" logic for long-haul trucking (EU/NAFTA).
* **Intermodal Realism:** Adds penalty factors for Drayage (Truck-to-Port), Port Handling (8 days), and Driver Rest Limits (500km/day).

### 3. Total Landed Cost (TLC) Model
To compare Domestic vs. Offshore sourcing, the system calculates the hidden cost of risk:

$$\text{TLC} = \text{Base Price} + \text{Freight} + \text{Duty} + \left( \frac{\text{Lead Time}}{365} \times \text{Demand} \times \text{Holding Rate} \right)$$

### 4. Monte Carlo Risk Engine
To quantify financial tail risk, the system runs **10,000 stochastic iterations** for every scenario. Instead of a single "average" profit, we generate a probability distribution:

$$P_{sim} = (D_{stoch} \cdot SP) - (Q_{order} \cdot UC_{mode}) - (I_{safety} \cdot H) - (S_{missed} \cdot \pi)$$

* **Metric:** Value at Risk (VaR 95%) = The worst 5% financial outcome.

### 5. Volatility Modelling (RSS)
The system calculates **Risk-Adjusted Safety Stock** using a Root Sum of Squares approach, integrating demand variability ($\sigma_{D}$) and lead time variability ($\sigma_{LT}$):

$$\text{Safety Stock} = Z_{\alpha}\sqrt{(\overline{L}\sigma_{D}^{2})+(\overline{D}^{2}\sigma_{LT}^{2})}$$

---

## 🚀 Key Features (v4.2.0)

### 🗺️ 1. Network Designer (New!)
* **Real-World Routing:** Integrates **Google Maps Platform** to visualize live trade lanes.
* **Smart Mode Selection:** Automatically determines feasibility of Road vs. Sea vs. Air based on distance caps (e.g., Road < 3,500km) and Landlocked country constraints (e.g., Nepal).
* **AI Consultant:** Embedded **Gemini AI** companion that explains the *why* behind routing decisions (e.g., "Why is the sea route 18 days?").

### 🚚 2. Multi-Modal Transport Engine
* **Mode Selection:** Toggle between **Road** (Standard), **Rail** (Green/Slow), and **Air** (Express/Costly).
* **Impact Analysis:** Real-time visibility into how switching to Rail affects stockout risk due to slower replenishment cycles.

### 🌏 3. Global Sourcing & Trade Strategy
* **"China Plus One" Simulator:** Compares **Domestic/Nearshore** sourcing against **Offshore (e.g., India)** sourcing.
* **Trade Policy Lever:** Interactive Tariff and CBAM (Carbon Tax) sliders to test the viability of Free Trade Agreements vs. Green Trade Barriers.

### 🌍 4. Strategic Scorecard (Triple Bottom Line)
* **Sustainability:** Tracks **CO2 Emissions (kg)** and calculates "Green Savings" from modal shifts.
* **Customer Loyalty:** Dynamic score based on Fill Rate reliability vs. SLA targets (Wallenburg 2011).

### 🌪️ 5. Resilience Simulator
* **"Stress Test" Mode:** Simulates a **Supply Chain Shock** (e.g., Port Strike).
* **Recovery Analysis:** Instantly quantifies the crash in Resilience Scores based on current safety buffers and modal flexibility.

---

## ⚙️ Technical Architecture

* **Core Logic:** `numpy` (Monte Carlo) & `scipy.stats` (Stochastic Calculus).
* **Intelligence Layer:** Google Gemini Flash Latest (via `ai_brain.py`) for strategic context.
* **Visualization:** `plotly.graph_objects` (Geospatial & Risk Histograms).
* **CI/CD:** GitHub Actions (Automated Testing & Deployment).
* **Frontend:** Streamlit (React-based) for interactive simulation.

---

## 🚀 Installation & Usage

### Prerequisites
You need a [Google AI Studio API Key](https://aistudio.google.com/), and a [Google Maps API Key](https://console.cloud.google.com/).

### Option A: Run Locally (Python)

```bash
# 1. Clone the repository
git clone https://github.com/sandesh-s-hegde/digital_capacity_optimizer.git
cd digital_capacity_optimizer

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set your API Key (Create a `.env` file in the root directory with the following keys:)
# GEMINI_API_KEY="AIzaSy..."  | Your Google AI Studio Key (For Chat).
# GOOGLE_API_KEY="AIzaSy..."  | Your Google Maps API Key (For Network Design).
# DATABASE_URL="postgresql://..."  | Your Render PostgreSQL connection string.

# 4. Generate Research Data (Optional)
python seed_data.py

# 5. Launch the Digital Twin
streamlit run app.py

```

---

## 📄 Citation

If you use this software in your research, please cite it as follows:

**Harvard Style:**

> Hegde, S.S. (2026). LSP Digital Capacity Twin: Multi-Modal Stochastic Engine (Version 4.2.0) [Software]. Available at: https://github.com/sandesh-s-hegde/digital_capacity_optimizer

**BibTeX:**

```bibtex
@software {Hegde_LSP_Digital_Twin_2026,
  author = {Hegde, Sandesh Subramanya},
  month = feb,
  title = {LSP Digital Capacity Twin: Multi-Modal Stochastic Engine},
  url = {(https://github.com/sandesh-s-hegde/digital_capacity_optimizer)},
  version = {4.2.0},
  year = {2026}
}

```

---

### 🚀 Deployment Notes
- **Python Version:** 3.11 (configured via `runtime.txt`)
- **Database:** PostgreSQL 16 (Render Frankfurt)
- **Dependency Management:** Flexible top-level requirements for better cloud compatibility.

---

## 🔮 Roadmap

| Phase   | Maturity Level | Key Capabilities                                    | Status              |
|---------| --- |-----------------------------------------------------|---------------------|
| Phase 1 | Descriptive | Static Rule-Based Logic (EOQ)                       | ✅ Done              |
| Phase 2 | Predictive | Cloud Database + Forecasting                        | ✅ Done              |
| Phase 3 | Stochastic | **Multi-Modal, Monte Carlo & Resilience, Research** | ✅ **Stable (v4.0)** |
| Phase 4 | Strategic | Global Sourcing & Network Design (Geospatial)                | ✅ **Stable (v4.2)** |
| Phase 5 | Autonomous | Multi-Echelon Reinforcement Learning                | 🚧 Planned          |
