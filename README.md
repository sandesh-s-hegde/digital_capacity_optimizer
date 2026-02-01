# 🚛 LSP Digital Capacity Twin: Stochastic Optimization Engine

**Author:** Sandesh Hegde  
**Version:** v3.0.0 (LSP & Resilience Edition)

![Python](https://img.shields.io/badge/Python-3.11-blue?style=for-the-badge&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-v1.31-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Research_Artifact-orange?style=for-the-badge)
![Cloud](https://img.shields.io/badge/Deployed_on-Render-46E3B7?style=for-the-badge&logo=render&logoColor=white)

## 🚀 Live Demo

**[Click here to launch the Research Artifact](https://digital-capacity-optimizer.onrender.com/)** *(Note: Hosted on Render Free Tier. Please allow 30s for cold start.)*

---

## 📖 Executive Summary
This artifact operationalizes the **"Pixels to Premiums"** research framework, serving as a **Decision Support System (DSS)** for Logistics Service Providers (LSPs). Unlike traditional manufacturing-centric models, this Digital Twin specifically addresses **Horizontal Cooperation**, **Reverse Logistics**, and **Supply Chain Resilience** in capacity-constrained networks.

---

## 🧮 Methodological Framework

### 1. The Newsvendor Logic (Service Level)
The core engine determines the **Critical Ratio** ($\alpha^*$) to optimize the trade-off between the Cost of Underage (Penalty/Lost Service) and Cost of Overage (Warehousing):

$$\alpha^{*} = \frac{C_{u}}{C_{u} + C_{o}}$$

### 2. Volatility Modelling (RSS)
To account for supply chain entropy, the system calculates **Risk-Adjusted Safety Stock** using a Root Sum of Squares approach, integrating demand variability ($\sigma_{D}$) and lead time variability ($\sigma_{LT}$):

$$\text{Safety Stock} = Z_{\alpha}\sqrt{(\overline{L}\sigma_{D}^{2})+(\overline{D}^{2}\sigma_{LT}^{2})}$$

### 3. Horizontal Cooperation Logic
The system models capacity sharing between competitors. When required capacity ($C_{req}$) exceeds internal limits ($C_{max}$), the algorithm triggers an outsourcing event with a friction cost (Surcharge $S$):

$$Cost_{total} = (C_{max} \cdot H) + ((C_{req} - C_{max}) \cdot (H + S))$$

### 4. Network Resilience Index
A composite score (0-100) quantifying the robustness of a Service Lane, derived from **Buffer Coverage** ($\beta$) and **Partner Dependency** ($\delta$):

$$Score_{res} = \beta(\text{Coverage}) + (1 - \delta(\text{Dependency}))$$

---

## 🚀 Key Features (v3.0.0)

### 🚛 1. LSP Operations Hub
* **Service Lane Tracking:** Monitors distinct flows (e.g., "BER-MUC", "HAM-ROT") rather than generic SKUs.
* **Reverse Logistics:** Sidebar slider to model the capacity impact of **Product Returns** (e.g., E-commerce scenarios).
* **Forecast Integration:** Projects future capacity requirements using linear demand trends.

### 🤝 2. Horizontal Cooperation Module
* **Capacity Overflow:** Automatically flags when internal warehousing is breached.
* **Outsourcing Calculator:** Computes the financial penalty of relying on competitor capacity.
* **Dependency Ratio:** Measures % of throughput dependent on external partners.

### 📉 3. Risk & Resilience Engine
* **Resilience Scoring:** Assigns a "Shock-Proof" score (0-100) to each lane based on volatility and dependency.
* **Service Reliability:** Calculates expected **Fill Rate** and **SLA Penalty Costs**.
* **Cost Convexity Curve:** Visualizes the "U-Shaped" cost trade-off to mathematically prove the optimal service level.

### 💰 4. Financial Optimization
* **Scenario Heatmaps:** Visualizes the "Sweet Spot" between Holding Cost and Stockout Risk.
* **Unit Economics:** Real-time calculation of margins vs. operational costs.

### 🛠️ 5. Research Tools
* **Synthetic Data Generator:** Includes `seed_data.py` to generate PhD-grade test scenarios (Seasonal, Industrial, Shock).
* **Unit Test Suite:** Validated logic via `tests.py` ensuring mathematical accuracy.

---

## ⚙️ Technical Architecture

* **Core Logic:** `scipy.stats` for Stochastic Calculus & Normal Distribution modeling.
* **Intelligence Layer:** Google Gemini 2.0 Flash (via `ai_brain.py`) for contextual volatility analysis.
* **Database:** PostgreSQL (Cloud) for persistent transaction logging.
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

> Hegde, S.S. (2026). *LSP Digital Capacity Twin: Stochastic Optimization Engine* (Version 3.0.0) [Software]. Available at: https://github.com/sandesh-s-hegde/digital_capacity_optimizer

**BibTeX:**

```bibtex
@software{Hegde_LSP_Digital_Twin_2026,
  author = {Hegde, Sandesh Subramanya},
  month = feb,
  title = {{LSP Digital Capacity Twin: Stochastic Optimization Engine}},
  url = {[https://github.com/sandesh-s-hegde/digital_capacity_optimizer](https://github.com/sandesh-s-hegde/digital_capacity_optimizer)},
  version = {3.0.0},
  year = {2026}
}

```

---

## 🔮 Roadmap

| Phase | Maturity Level | Key Capabilities | Status |
| --- | --- | --- | --- |
| Phase 1 | Descriptive | Static Rule-Based Logic (EOQ) | ✅ Done |
| Phase 2 | Predictive | Cloud Database + Forecasting | ✅ Done |
| Phase 3 | Stochastic | **Resilience Index & Horizontal Cooperation** | ✅ **Released (v3.0)** |
| Phase 4 | Autonomous | Multi-Echelon Reinforcement Learning | 🚧 Planned |