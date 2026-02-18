# Changelog

All notable changes to the "Financial Digital Twin" research artifact will be documented in this file.

## [4.2.5] - 2026-02-18
### Added
- **Geospatial Network Designer:** Integration with Google Maps Platform for live trade lane visualization and interactive route analysis.
- **Geopolitical Logic Engine:** Automated filtering for blocked commercial borders (e.g., India-Pakistan) and conflict zones.
- **Logistics AI Companion:** Embedded Gemini 1.5 Flash consultant to explain routing constraints, customs delays, and supply chain trade-offs.
- **Intermodal Realism:** New deterministic logic accounting for port drayage, vessel frequency buffers (weekly sailings), and mandatory customs processing times.
- **Open Border Exceptions:** Specialized routing rules for EU Schengen and NAFTA zones allowing long-haul trucking (>3,500km) based on regional trade agreements.
- **Landlocked Validation:** Automated exclusion of Sea freight modes for landlocked nations (e.g., Nepal, Bhutan, Switzerland) to ensure model accuracy.

### Changed
- **UI Architecture:** Redesigned Tab 5 into a split-screen dashboard layout (Inputs & Metrics on Left | Interactive Map on Right).
- **State Management:** Implemented `st.session_state` persistence for Search Inputs and AI Chat history to prevent data loss on interface reruns.
- **Security:** Decoupled Maps and AI API authentication to support separate restriction policies for Google Cloud and AI Studio.

## [4.0.0] - 2026-02-12
### Added
- **Global Sourcing Simulator:** CBAM and FTA impact modeling.
- **Sensitivity Matrix:** Visualizing the sourcing tipping point.
- **Health Diagnostics:** New health_check.py for environment validation.

### Changed
- Standardized all financial metrics to USD ($).
- Optimized Monte Carlo engine to handle 10k iterations natively.

### Fixed
- Fixed LaTeX formatting issues in AI chat responses.
- Hardened math modules against zero-demand edge cases.

## [v3.0.0] - 2026-01-26
### Added
- **Monte Carlo Risk Engine:** Implemented 1,000-iteration stochastic simulation for profit forecasting.
- **Geospatial Logic:** Integrated `map_viz.py` for lane-specific network topology visualization.
- **Multi-Modal Selectors:** Added Air/Rail/Road logic with dynamic CO2 and lead-time multipliers.

### Changed
- **Research Refocus:** Shifted core logic from simple "EOQ" to "Supply Chain Resilience" (Wallenburg 2011 framework).
- **UI:** Redesigned Streamlit layout to a multi-tab architecture.

## [v2.7.0] - 2026-01-29
### Added
- **Governance:** Added Code of Conduct and Contributing Guidelines for academic compliance.
- **Documentation:** Implemented `CITATION.cff` for standardized research referencing.
- **Badges:** Added status indicators to README for quick assessment.

## [v2.6.5] - 2026-01-24
### Added
- **AI Intelligence Layer:** Integrated Google Gemini 2.0 Flash for real-time heatmap interpretation.
- **Profit Optimizer:** Added Critical Ratio ($\alpha^*$) calculation to the Streamlit sidebar.
- **Live Database:** Full migration from static CSV to Render PostgreSQL cloud infrastructure.

## [v2.5.0] - 2026-01-20
### Changed
- Refactored `db_manager.py` to support cloud-native connections.
- Updated Newsvendor logic to include "Stockout Cost" as a dynamic variable rather than a hardcoded constant.
- **Security:** Moved all API keys to `.env` environment handling.

## [v1.0.0] - 2025-12-15
### Initial Release
- Basic Streamlit interface for inventory simulation.
- Deterministic Safety Stock calculation (standard formula).
- Local CSV file support only.
