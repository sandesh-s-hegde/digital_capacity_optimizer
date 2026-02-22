# Security Policy

## Supported Versions

As this Decision Support System (DSS) is both an active research artifact and a production-grade proof-of-concept, security maintenance and patches are prioritized for the current major release tree.

| Version | Supported          |
| ------- | ------------------ |
| 4.2.x   | :white_check_mark: |
| 4.0.x   | :warning: (Critical patches only) |
| < 4.0   | :x:                |

## Reporting a Vulnerability

This project utilizes strict environment variable management (`dotenv`) to secure all credentials, cloud databases, and API keys.

If you discover a security vulnerability (e.g., SQL injection risks, exposed endpoints, or AI prompt injection vulnerabilities), please do **not** open a public GitHub issue.

Instead, please report it via email directly to the repository owner at **s.sandesh.hegde@gmail.com**. We will acknowledge receipt of the vulnerability within 48 hours and strive to issue a patch within 5 business days.

## Architecture Security Considerations

When deploying or reviewing this artifact, please note the following security implementations:

* **Decoupled Authentication:** The system uses distinct, strictly-scoped API keys for geospatial mapping (`GOOGLE_API_KEY`) and AI reasoning (`GEMINI_API_KEY`) to prevent cross-service privilege escalation and billing attacks.
* **Zero-Trust Secrets:** No keys or database credentials are ever committed to this repository. Users must supply their own keys via a local `.env` file or a cloud secrets manager (e.g., Streamlit Secrets / Render Environment Variables).
* **Database Encryption:** The PostgreSQL network twin enforces `sslmode=require` for all cloud connections, ensuring logistics and inventory data remain encrypted in transit.
* **Input Sanitization:** User inputs passed through the Streamlit UI and location search boxes are sanitized prior to backend execution to prevent malicious database queries.
