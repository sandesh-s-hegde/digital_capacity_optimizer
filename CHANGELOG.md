# Changelog

All notable changes to the "Financial Digital Twin" research artifact will be documented in this file.

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