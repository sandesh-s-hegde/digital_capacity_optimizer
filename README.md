# 🧠 AI-Powered Digital Capacity Optimizer

**Author:** Sandesh Hegde

**Version:** v2.6.0 (Stochastic Edition)

**License:** MIT

## 🚀 Live Demo

**[Click here to launch the App](https://digital-capacity-optimizer.onrender.com/)** *(Note: Hosted on Render Free Tier. Please allow 30s for cold start.)*

---

## 📌 Overview

The **Digital Capacity Optimizer** is a production-grade SaaS platform for Supply Chain Intelligence. It has evolved from a simple calculator into a **Multi-Tenant Inventory System** capable of managing hundreds of products simultaneously.

It combines **Stochastic Math** (to handle supplier risk) with **Generative AI** (to explain the data), helping managers balance the fine line between "Stockouts" and "Overstocking."

### 🖥️ The Executive Command Center

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

## 🎯 Key Features

### 🧠 Cognitive Intelligence

* **🚁 Executive Command Center:** A "Watchtower" view that scans the entire database to flag products as **🟢 Normal**, **🔴 Surge Alert**, or **🟡 Low Velocity**.
* **📄 Executive PDF Reporting:** One-click generation of professional summaries using AI to explain the "Why" behind the numbers.
* **💬 Chat with Data:** Ask natural language questions like *"Why is safety stock so high for Widget A?"*

### 🚢 Stochastic Risk Engine (New)

* **⚡ Supplier Chaos Factor:** Models "Lead Time Variance" (e.g., shipping delays). The system calculates how much extra stock you need if your supplier is unreliable.
* **📉 AI Demand Forecasting:** Uses Linear Regression to project demand trends 3 months into the future.
* **💰 Profit Heatmaps:** Visualizes the exact "Sweet Spot" for order quantity based on unit economics.

### 🏭 Core Operations

* **📦 Multi-Product Support:** Track distinct SKUs ("Widget A", "Widget B") with isolated data streams.
* **🚚 Bulk Import:** Drag-and-drop CSV upload to ingest historical data in seconds.
* **🧨 Factory Reset:** "Danger Zone" tools to wipe data and reset ID counters for clean testing.

---

## 📊 How It Works

The system utilizes a hybrid approach of **Deterministic Math** and **Probabilistic AI**:

1. **The Math:** Uses the **Root Sum of Squares (RSS)** formula to combine Demand Uncertainty and Lead Time Uncertainty into a single Risk Metric.
2. **The Optimization:** Solves the **Newsvendor Problem** to find the mathematically optimal order quantity that maximizes profit margins.
3. **The AI:** Acts as the analyst, translating these complex deviations into actionable business advice.

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
| Phase 3 (Done) | Stochastic | **Risk Engine, Multi-SKU, Bulk Import** | Scipy, Numpy, Plotly |
| Phase 4 | Autonomous | Self-Healing Supply Chain | Reinforcement Learning |