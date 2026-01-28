# 🧠 Financial Digital Twin: Stochastic Inventory Optimization Engine

**Author:** Sandesh Hegde

**Version:** v2.7.0 (Stochastic Edition)

![Python](https://img.shields.io/badge/Python-3.11-blue?style=for-the-badge&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-v1.31-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Research_Artifact-orange?style=for-the-badge)
![Cloud](https://img.shields.io/badge/Deployed_on-Render-46E3B7?style=for-the-badge&logo=render&logoColor=white)

## 🚀 Live Demo

**[Click here to launch the App](https://digital-capacity-optimizer.onrender.com/)** *(Note: Hosted on Render Free Tier. Please allow 30s for cold start.)*

---

## 🧮 Methodological Framework

### 1. The Newsvendor Logic
The core optimisation engine moves beyond static averages to determine the **Critical Ratio** ($\alpha^*$) based on cost asymmetry:

$$\alpha^{*} = \frac{C_{u}}{C_{u} + C_{o}}$$

Where:
* $C_{u}$: Cost of Underage (Lost Profit Margin)
* $C_{o}$: Cost of Overage (Holding Cost + Obsolescence)

### 2. Volatility Modelling
To account for supply chain volatility, the system calculates **Risk-Adjusted Safety Stock** using a Root Sum of Squares (RSS) approach, integrating both demand variability ($\sigma_{D}$) and lead time variability ($\sigma_{LT}$):

$$\text{Safety Stock} = Z_{\alpha}\sqrt{(\overline{L}\sigma_{D}^{2})+(\overline{D}^{2}\sigma_{LT}^{2})}$$

---

## 🚀 Key Features

### 📊 1. Intelligent Dashboard
* **Multi-Product Support:** Track distinct SKUs ("Widget A", "Widget B") with isolated data.
* **AI Forecasting:** Projects future demand using Linear Regression trend lines.
* **Visual Analytics:** Interactive charts built with Plotly.

### 🚁 2. Executive Command Center
* **"Watchtower" View:** Scans your entire database to flag products as **🟢 Normal**, **🔴 Surge Alert**, or **🟡 Low Velocity**.
* **Instant Health Check:** See the status of your entire inventory at a glance.

### 🚢 3. Stochastic Risk Engine
* **Lead Time Uncertainty:** Models "Supply Chain Chaos" (e.g., shipping delays) to calculate required Safety Stock.
* **Service Level Planning:** Adjust your desired SLA (e.g., 95% vs 99%) and see the cost impact instantly.

### 💰 4. Profit Optimizer
* **Scenario Heatmaps:** Visualizes the "Sweet Spot" between Ordering Too Much (Holding Cost) vs. Too Little (Stockout Cost).
* **Unit Economics:** Calculates profit margins based on manufacturing cost vs. retail price.

### 🛠️ 5. Data Management Tools
* **Bulk Importer:** Upload CSV files to ingest historical data in seconds.
* **Factory Reset:** "Danger Zone" feature to wipe the database and reset ID counters for testing.
* **CRUD Operations:** Add, View, and Delete individual records.

---

## ⚙️ Technical Architecture
The system is built on a cloud-native Python stack, designed for scalability and auditability.

* **Core Logic:** Stochastic calculus for Safety Stock (RSS method) & EOQ optimization.
* **Intelligence Layer:** Google Gemini AI (via `ai_brain.py`) for contextual volatility analysis.
* **Database:** PostgreSQL (Cloud) for persistent transaction logging.
* **Frontend:** Streamlit (React-based) for interactive simulation.

---

## 🛠️ Tech Stack

* **AI Model:** Google Gemini 1.5 Flash
* **Database:** PostgreSQL (Neon DB), SQLAlchemy ORM
* **Frontend:** Streamlit, Plotly Graph Objects
* **Math Engine:** Numpy, Statistics (Pure Python)
* **Reporting:** FPDF2
* **Language:** Python 3.10+

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
# GEMINI_API_KEY="AIzaSy..."
# DATABASE_URL="postgresql://..."

# 4. Launch the Dashboard
streamlit run app.py

```

### Option B: Bulk Upload Format

To import data via CSV, your file must have these headers:

```csv
date,product_name,demand
2024-01-01,Laptop Pro,120
2024-02-01,Laptop Pro,145
2024-03-01,Laptop Pro,130

```

---

## 🔮 Roadmap

| Phase | Maturity Level | Key Capabilities | Tech Stack |
| --- | --- | --- | --- |
| Phase 1 (Done) | Descriptive | Static Rule-Based Logic (EOQ) | Python, Pandas |
| Phase 2 (Done) | Predictive | Dockerized Web App + SQL Database | PostgreSQL, Docker |
| Phase 3 (Done) | Stochastic | **Risk Engine, Multi-SKU, Bulk Import** | **Numpy, Statistics, Plotly** |
| Phase 4 | Autonomous | Self-Healing Supply Chain | Reinforcement Learning |