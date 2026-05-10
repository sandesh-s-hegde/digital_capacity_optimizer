# 🚛 LSP Digital Capacity Twin: Multi-Modal Stochastic Engine

**Author:** Sandesh Hegde

**Version:** v5.0.0 (Serverless Edition)

## 🚀 Live Demo

**[Click here to launch the Research Artifact](https://digital-capacity-optimizer.onrender.com/)** *(Note: Hosted on Render Free Tier. Please allow 30s for cold start.)*

---

## 📖 Executive Summary

This artifact operationalizes the **"Pixels to Premiums"** research framework, serving as a comprehensive **Decision Support System (DSS)** for Logistics Service Providers (LSPs). In its v5.0.0 iteration, it combines advanced **Risk Quantification**, **Geospatial Network Design**, **Global Observability**, and **Zero-Trust Tactical Execution** to solve for the "China Plus One" strategy, multi-modal routing constraints, and real-time operational bottlenecks.

---

## 🧮 Methodological Framework

### 1. Multi-Modal Trade-off Logic

The engine applies strategic multipliers to simulate mode-specific constraints. The "Iron Triangle" of Logistics is modeled as:

* **Lead Time ($L_m$):** $L_{base} \times M_{time}$ (e.g., Air = 0.2x, Rail = 1.5x)
* **Unit Cost ($C_m$):** $C_{base} \times M_{cost}$ (e.g., Air = 3.0x, Rail = 0.7x)
* **Emissions ($E_m$):** $E_{base} \times M_{co2}$ (e.g., Air = 5.0x, Rail = 0.3x)

### 2. Geospatial & Geopolitical Routing

The Network Designer utilizes a deterministic logic engine to validate commercial viability:

* **Geodesic Distance:** Calculated using Vincenty’s formulae via `geopy`.
* **Geopolitical Filtering:** Automatically blocks routes through conflict zones and enforces "Open Border" logic for long-haul trucking.
* **Intermodal Realism:** Adds penalty factors for Drayage, Port Handling, and Driver Rest Limits.

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

## 🚀 Key Features

### 📊 1. Global Observability & Capacity Hub

* **Embedded Observability Dashboard:** Real-time visualization of macro-network telemetry natively integrated into the user interface.
* **Semantic Data Compression:** Summarizes 'Global Briefing' statistics to securely pass macro-network insights into the AI without exceeding token limits.

### 🤖 2. AI Strategy Assistant (Upgraded)

* **Gemini 2.5 Flash Engine:** Upgraded RAG pipeline to Google's latest high-speed multimodal model.
* **Time-Series Ingestion:** Dynamically injects the most recent 30 rows of operational, financial, and strategic data for granular, day-to-day trend analysis.
* **Robust API Handling:** Implemented exponential backoff and retry logic to seamlessly handle rate limits.

### 🗺️ 3. Network Designer

* **Real-World Routing:** Integrates **Google Maps Platform** via secure HTTPS endpoints to visualize live trade lanes.
* **Smart Mode Selection:** Automatically determines feasibility of Road vs. Sea vs. Air based on geographic constraints.

### 🌏 4. Global Sourcing & Trade Strategy

* **"China Plus One" Simulator:** Compares Domestic/Nearshore against Offshore sourcing.
* **Trade Policy Lever:** Interactive Tariff and CBAM (Carbon Tax) sliders to test the viability of Free Trade Agreements vs. Green Trade Barriers.

### 🌪️ 5. Resilience Simulator

* **"Stress Test" Mode:** Simulates a Supply Chain Shock and instantly quantifies the crash in Resilience Scores based on current safety buffers.

### ⚡ 6. Tactical Ecosystem Execution

* **Zero-Trust Webhooks:** Cryptographically signs outbound payloads (HMAC SHA-256) to bridge predictive analytics directly to external procurement APIs and legacy RPA bots.

---

## ⚙️ Technical Architecture

* **Core Logic:** `numpy` (Monte Carlo) & `scipy.stats` (Stochastic Calculus).
* **Intelligence Layer:** Google Gemini 2.5 Flash (via `ai_brain.py`) with semantic context injection.
* **Security Layer:** Cryptographic HMAC SHA-256 Payload Signer.
* **Visualization:** `plotly.graph_objects` (Geospatial & Risk Histograms).
* **CI/CD:** Automated Python 3.12+ testing matrix via GitHub Actions.
* **Frontend:** Streamlit (React-based) structured for optimized UI rendering.
* **Database:** Serverless PostgreSQL via Neon.

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

# 3. Set your API Keys (Create a `.env` file in the root directory with the following keys:)
# GEMINI_API_KEY="AIzaSy..."                | Your Google AI Studio Key (For Chat).
# GOOGLE_API_KEY="AIzaSy..."                | Your Google Maps API Key (For Network Design).
# DATABASE_URL="postgresql://..."           | Your Neon PostgreSQL connection string.
# B2B_API_URL="[https://webhook.site/](https://webhook.site/)..."    | Endpoint for modern API routing.
# RPA_BRIDGE_URL="[https://webhook.site/](https://webhook.site/)..." | Endpoint for legacy system routing.
# API_SECRET_KEY="your_secret_key"          | Secret key for Zero-Trust webhook signing.

# 4. Generate Research Data (Optional)
python seed_data.py

# 5. Launch the Digital Twin
streamlit run app.py
```

---

## ☁️ Production Infrastructure (Multi-Cloud)
To bypass standard cloud-provider limitations and ensure high availability, this application utilizes a decoupled, multi-cloud architecture:
* **Compute/Hosting:** Render (Frankfurt Region)
* **Storage/Database:** Neon Serverless PostgreSQL (Frankfurt Region)

### 💾 Data Hydration
The production database is hydrated using a custom vectorized NumPy simulation generating 5-years of global supply chain telemetry (18,000+ records).
To re-seed the database:
```bash
python database_schema.py
python seed_data.py

```

### 🧠 Autonomous Tool Calling Architecture
This repository utilizes the `gemini-2.5-flash` model functioning as an autonomous agent. Instead of relying solely on static training data, the AI is equipped with external **Tools**.

### 🌱 The Sustainability Protocol
The AI is strictly bound by a system prompt that mandates environmental checks prior to routing. When a user requests a dispatch, the AI autonomously pauses text generation, executes the `check_grid_emissions` python function to query the external **ESG Grid Oracle**, parses the JSON response, and resumes generation to formulate a carbon-aware routing strategy.

---

## 📄 Citation

If you use this software in your research, please cite it as follows:

**Harvard Style:**

> Hegde, S.S. (2026). LSP Digital Capacity Twin: Multi-Modal Stochastic Engine (Version 5.0.0) [Software]. Available at: [https://github.com/sandesh-s-hegde/digital_capacity_optimizer](https://github.com/sandesh-s-hegde/digital_capacity_optimizer)

**BibTeX:**

```bibtex
@software {Hegde_LSP_Digital_Twin_2026,
  author = {Hegde, Sandesh Subramanya},
  month = apr,
  title = {LSP Digital Capacity Twin: Multi-Modal Stochastic Engine},
  url = {([https://github.com/sandesh-s-hegde/digital_capacity_optimizer](https://github.com/sandesh-s-hegde/digital_capacity_optimizer))},
  version = {5.0.0},
  year = {2026}
}

```

---

### 🚀 Deployment Notes

* **Python Version:** 3.12+ (configured via CI/CD matrix)
* **Database:** Serverless PostgreSQL (Neon)
* **Dependency Management:** Flexible top-level requirements for better cloud compatibility.

---

## 🔮 Roadmap & Project Status

*This repository has reached its planned maturity and serves as the finalized Macro-Strategy layer of the supply chain architecture.*

| Phase | Maturity Level | Key Capabilities                                    | Status |
| --- | --- |-----------------------------------------------------| --- |
| Phase 1 | Descriptive | Static Rule-Based Logic (EOQ)                       | ✅ Done |
| Phase 2 | Predictive | Cloud Database + Forecasting                        | ✅ Done |
| Phase 3 | Stochastic | Multi-Modal, Monte Carlo & Resilience               | ✅ Done |
| Phase 4 | Strategic | Global Sourcing & Geospatial Network Design         | ✅ Done |
| Phase 5 | Observability | Distributed Telemetry & AI Context Optimization     | ✅ Done |
| Phase 6 | Execution | **Zero-Trust Tactical API & RPA Webhook Routing** | ✅ **Stable (v5.1)** |

---

> ➡️ **Next Evolution:** The project has expanded into the **Tactical Execution Layer**. Strategic capacity shortfalls identified by this Twin are now automatically routed to the [B2B Fleet Aggregator API](https://github.com/sandesh-s-hegde/b2b-fleet-aggregator-api). This middleware bridges the gap between macro-forecasting and real-world fulfillment by aggregating commercial vehicle inventory from third-party rental suppliers.
