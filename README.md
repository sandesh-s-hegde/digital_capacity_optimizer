# 🚛 LSP Digital Capacity Twin: Multi-Modal Stochastic Engine

**Author:** Sandesh Hegde  
**Version:** v3.8.0 (Strategic Research Edition)

![Python](https://img.shields.io/badge/Python-3.11-blue?style=for-the-badge&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-v1.31-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Research_Artifact-orange?style=for-the-badge)
![Cloud](https://img.shields.io/badge/Deployed_on-Render-46E3B7?style=for-the-badge&logo=render&logoColor=white)

## 🚀 Live Demo

**[Click here to launch the Research Artifact](https://digital-capacity-optimizer.onrender.com/)** *(Note: Hosted on Render Free Tier. Please allow 30s for cold start.)*

---

## 📖 Executive Summary
This artifact operationalizes the **"Pixels to Premiums"** research framework, serving as a **Decision Support System (DSS)** for Logistics Service Providers (LSPs). It now includes a **Global Sourcing Simulator** to quantify the "China Plus One" strategy and the impact of Free Trade Agreements (FTAs). 

---

## 🧮 Methodological Framework

### 1. Multi-Modal Trade-off Logic
The engine applies strategic multipliers to simulate mode-specific constraints. The "Iron Triangle" of Logistics is modeled as:

* **Lead Time ($L_m$):** $L_{base} \times M_{time}$ (e.g., Air = 0.2x, Rail = 1.5x)
* **Unit Cost ($C_m$):** $C_{base} \times M_{cost}$ (e.g., Air = 3.0x, Rail = 0.7x)
* **Emissions ($E_m$):** $E_{base} \times M_{co2}$ (e.g., Air = 5.0x, Rail = 0.3x)

### 2. Total Landed Cost (TLC) Model (New!)
To compare Domestic vs. Offshore sourcing, the system calculates the hidden cost of risk:

$$\text{TLC} = \text{Base Price} + \text{Freight} + \text{Duty} + \left( \frac{\text{Lead Time}}{365} \times \text{Demand} \times \text{Holding Rate} \right)$$

### 3. Monte Carlo Risk Engine
To quantify financial tail risk, the system runs **10,000 stochastic iterations** for every scenario. Instead of a single "average" profit, we generate a probability distribution:

$$P_{sim} = (D_{stoch} \cdot SP) - (Q_{order} \cdot UC_{mode}) - (I_{safety} \cdot H) - (S_{missed} \cdot \pi)$$

* **Metric:** Value at Risk (VaR 95%) = The worst 5% financial outcome.

### 4. Volatility Modelling (RSS)
The system calculates **Risk-Adjusted Safety Stock** using a Root Sum of Squares approach, integrating demand variability ($\sigma_{D}$) and lead time variability ($\sigma_{LT}$):

$$\text{Safety Stock} = Z_{\alpha}\sqrt{(\overline{L}\sigma_{D}^{2})+(\overline{D}^{2}\sigma_{LT}^{2})}$$

---

## 🚀 Key Features (v3.8.0)

### 🚚 1. Multi-Modal Transport Engine
* **Mode Selection:** Toggle between **Road** (Standard), **Rail** (Green/Slow), and **Air** (Express/Costly).
* **Dynamic Economics:** "Air Mode" instantly triples costs and spikes CO2, but slashes lead time to near zero.
* **Impact Analysis:** See how switching to Rail affects your stockout risk due to slower replenishment.

### 🌏 2. Global Sourcing Strategy (New in v3.8!)
* **"China Plus One" Simulator:** Compares **Domestic/Nearshore** sourcing against **Offshore (e.g., India)** sourcing.
* **Trade Policy Lever:** Interactive Tariff slider (0-20%) to test the viability of Free Trade Agreements (FTAs).
* **Risk vs. Reward:** Visualizes the "tipping point" where logistics risk outweighs labor cost savings.

### 🌍 3. Strategic Scorecard (Triple Bottom Line)
* **Sustainability:** Tracks **CO2 Emissions (kg)** and calculates "Green Savings" from modal shifts.
* **Customer Loyalty:** Dynamic score based on Fill Rate reliability vs. SLA targets.
* **Resilience Score:** Composite index (0-100) measuring network robustness.

### 🌪️ 4. Disruption Simulator
* **"Stress Test" Mode:** Simulates a **Supply Chain Shock** (e.g., Port Strike).
* **Real-Time Impact:** Instantly doubles lead time variance ($\sigma_{LT}$), crashing Resilience Scores in real-time.

### 🔬 5. Research Laboratory (Enhanced)
* **Stochastic Validation:** Runs **10,000 iterations** to prove the "Newsvendor Optimal" strategy.
* **Loss Predictability:** New metric quantifying the **Probability of Loss (%)** to identify dangerous cost structures.
* **Profit Heatmaps:** Visualizes the "Zone of Profitability" across demand and volatility scenarios.

---

## ⚙️ Technical Architecture

* **Core Logic:** `numpy` (Monte Carlo) & `scipy.stats` (Stochastic Calculus).
* **Intelligence Layer:** Google Gemini 1.5 Flash (via `ai_brain.py`) for strategic context.
* **Visualization:** `plotly.graph_objects` (Geospatial & Risk Histograms).
* **CI/CD:** GitHub Actions (Automated Testing & Deployment).
* **Frontend:** Streamlit (React-based) for interactive simulation.

---

## 🚀 Installation & Usage

### Prerequisites
You need a [Google AI Studio API Key](https://aistudio.google.com/).

### Option A: Run Locally (Python)

```bash
# 1. Clone the repository
git clone https://github.com/sandesh-s-hegde/digital_capacity_optimizer.git
cd digital_capacity_optimizer

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set your API Key (Create a .env file)
# GOOGLE_API_KEY="AIzaSy..."
# DATABASE_URL="postgresql://..."

# 4. Generate Research Data (Optional)
python seed_data.py

# 5. Launch the Digital Twin
streamlit run app.py

```

---

## 📄 Citation

If you use this software in your research, please cite it as follows:

**Harvard Style:**

> Hegde, S.S. (2026). LSP Digital Capacity Twin: Multi-Modal Stochastic Engine (Version 3.8.0) [Software]. Available at: https://github.com/sandesh-s-hegde/digital_capacity_optimizer

**BibTeX:**

```bibtex
@software {Hegde_LSP_Digital_Twin_2026,
  author = {Hegde, Sandesh Subramanya},
  month = feb,
  title = {LSP Digital Capacity Twin: Multi-Modal Stochastic Engine},
  url = {(https://github.com/sandesh-s-hegde/digital_capacity_optimizer)},
  version = {3.8.0},
  year = {2026}
}

```

---

## 🔮 Roadmap

| Phase   | Maturity Level | Key Capabilities                                    | Status        |
|---------| --- |-----------------------------------------------------|---------------|
| Phase 1 | Descriptive | Static Rule-Based Logic (EOQ)                       | ✅ Done        |
| Phase 2 | Predictive | Cloud Database + Forecasting                        | ✅ Done        |
| Phase 3 | Stochastic | **Multi-Modal, Monte Carlo & Resilience, Research** | ✅ **Released (v3.8)** |
| Phase 4 | Strategic | Global Sourcing (FTA) & Trade Policy                | ✅ **Released (v3.8)** |
| Phase 5 | Autonomous | Multi-Echelon Reinforcement Learning                | 🚧 Planned    |