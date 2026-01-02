# Digital Capacity Optimizer

**Author:** Sandesh Hegde
**Status:** Active Development (Jan 2026)
**License:** MIT

## 📌 Overview
This project explores the application of classical **Operations Management (OM)** principles—specifically **Inventory Control Theory**—to modern Cloud Infrastructure (IaaS).

While traditional OM focuses on physical stock (widgets), this tool treats "Server Capacity" as a stochastic inventory problem. It aims to minimize the Total Cost of Ownership (TCO) by balancing **Holding Costs** (Idle Capacity) against **Stockout Costs** (Service Outages).

## 🎯 Objectives
* **EOQ Implementation:** Adapting the Economic Order Quantity model for reserved instance procurement.
* **Safety Stock Modeling:** Calculating buffer capacity based on demand volatility ($\sigma$).
* **Data Visualization:** Automated generation of supply/demand curves from usage logs.

## 📊 Results (Simulation Output)
The system currently analyzes 12 months of synthetic Azure usage data to optimize procurement strategies.

### 1. Demand Visualization
![Demand Trend](demand_forecast.png)

### 2. Optimization Report
Running the simulation on the Munich Data Center dataset yields:

```text
✅ Optimal Order Quantity (EOQ): 848.53 units
   -> Strategy: Buy servers in batches of ~850 to minimize holding costs.

🛡️ Safety Stock Buffer: 299.07 units
   -> Reason: Buffers against 15.8-day average lead time volatility.