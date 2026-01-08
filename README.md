# Digital Capacity Optimizer

**Author:** Sandesh Hegde  
**Version:** v1.0.0 (Stable)  
**License:** MIT  
![Build Status](https://img.shields.io/badge/build-passing-brightgreen) ![Docker](https://img.shields.io/badge/docker-supported-blue)

---

## 📌 Overview

This project is a **Full-Stack Supply Chain Intelligence** platform for Cloud Infrastructure. It helps Data Center managers predict demand and optimize procurement using AI.

It moves beyond simple averages by using **Holt-Winters Exponential Smoothing** to forecast trends and **Newsvendor Logic** to financially justify inventory decisions.

### 🖥️ The Interactive Dashboard
![Dashboard UI](dashboard_ui.jpg)

---

## 🎯 Key Features

- **🔮 AI Forecasting Engine:** Uses `statsmodels` to predict future demand (Months 13-15) based on historical growth and seasonality.
- **💰 Financial Optimization:** Calculates the "Perfect Order Size" by balancing **Holding Costs** ($18.50) against **Stockout Penalties** ($2,000).
- **🛡️ Risk Modeling:** Automatically adjusts Safety Stock to meet a **99.1% Service Level Agreement (SLA)**.
- **🐳 Containerized:** Fully dockerized for consistent deployment across any environment.

---

## 📊 Results (v1.0 Release)

The system detected a strong growth trend in the Q4 dataset. Instead of using a reactive average, the **Oracle Engine** projected a demand surge:

```text
📊 PROACTIVE ANALYSIS
   -> Historical Avg Demand: 1,233 units
   -> Predicted Next Month:  1,950 units (Growth Trend)

🔮 RECOMMENDATION:
   Buy 2,561 units.
   (Includes safety buffer to maintain 99.1% SLA during growth phase)
```

---

## 🛠️ Tech Stack

- **Infrastructure:** Docker (Containerization)
- **Frontend:** Streamlit (Web Dashboard)
- **Core Logic:** Python 3.11
- **Forecasting:** Statsmodels (Holt-Winters)
- **Math:** SciPy (Normal Distribution / Z-Scores)

---

## 🚀 Usage

### Option A: Run with Docker (Recommended)
No Python installation required.

```bash
# 1. Build the container
docker build -t digital-capacity-optimizer .

# 2. Run the app
docker run -p 8501:8501 digital-capacity-optimizer
```
Access the dashboard at http://localhost:8501

### Option B: Run Locally (Python)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Launch the Dashboard
streamlit run app.py
```

---

## 🔮 Future Roadmap

This project is the foundational layer of a Digital Twin for Cloud Supply Chains.

| Phase             | Maturity Level | Key Capabilities                    | Tech Stack                |
|-------------------|----------------|-------------------------------------|---------------------------|
| Phase 1 (Done)    | Descriptive    | Static Rule-Based Logic (EOQ)       | Python, Pandas            |
| Phase 2 (Done)    | Predictive     | AI Forecasting & Web App            | Statsmodels, Streamlit    |
| Phase 3           | Cognitive      | "Chat with Data" (RAG)              | Llama-3, Vector DBs       |
| Phase 4           | Autonomous     | Self-Healing Supply Chain           | Reinforcement Learning    |