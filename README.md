# 🧠 AI-Powered Digital Capacity Optimizer

**Author:** Sandesh Hegde

**Version:** v2.7.0 (Stochastic Edition)

**License:** MIT

## 🚀 Live Demo

**[Click here to launch the App](https://digital-capacity-optimizer.onrender.com/)** *(Note: Hosted on Render Free Tier. Please allow 30s for cold start.)*

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

## 🏗️ Architecture

The application follows a **Micro-Module Architecture** to ensure scalability:

1. **Presentation:** Streamlit (UI) + Plotly (Interactive Heatmaps)
2. **Logic Layer:** * `db_manager.py`: CRUD operations & Bulk Import logic.
   * `inventory_math.py`: Stochastic Engine (Z-Scores, Normal Distribution).
   * `forecast.py`: Linear Regression Forecasting.
3. **Intelligence:** Google Gemini 1.5 Flash (RAG - Chat with Data).
4. **Data:** PostgreSQL (Production) with Multi-SKU support.

**Data Flow:** `CSV/User Input` -> `DB Manager` -> `SQL` -> `Math Engine` -> `AI Context` -> `Strategic Report`

---

## 🧠 How It Works (The Math)

This is not a black-box AI. The optimization engine is built on standard Operations Research principles:

1.  **Newsvendor Model (Critical Ratio)**
    * Applies the **Single-Period Newsvendor Model** to determine the optimal service level.
    * *Formula:* `Critical Ratio = Cu / (Cu + Co)`
    * *Why:* Balances the cost of overstocking (Holding Cost) vs. the cost of understocking (Stockout Cost).

2.  **Stochastic Safety Stock**
    * Uses a **Root Sum of Squares (RSS)** approach to account for two distinct types of uncertainty:
        * **Demand Volatility:** Customer orders fluctuating month-to-month.
        * **Supply Chain Risk:** Supplier lead time variability (e.g., shipping delays).
    * *Result:* A mathematically robust buffer that protects service levels without bloating inventory.

3.  **Economic Order Quantity (EOQ)**
    * Calculates the optimal batch size to minimize total annual holding and ordering costs.

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
