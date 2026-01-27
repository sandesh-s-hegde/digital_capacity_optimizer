# Security Policy

## Supported Versions

As this is a research artifact submitted for academic assessment, active security maintenance is prioritized for the current major release version only.

| Version | Supported          |
| ------- | ------------------ |
| 2.x     | :white_check_mark: |
| 1.x     | :x:                |

## Reporting a Vulnerability

This project utilizes `dotenv` for environment variable management to secure credentials (API Keys, Database URLs).

If you discover a security vulnerability (e.g., exposed endpoints, SQL injection risk), please do **not** open a public issue.

Instead, please report it via email to the repository owner. As this is a proof-of-concept digital twin, patches will be applied on a best-effort basis consistent with the research timeline.

### Critical Considerations for Reviewers
* **API Keys:** The `GOOGLE_API_KEY` is not committed to the repository and must be injected via the environment.
* **Database:** The PostgreSQL instance uses SSL-required connections (`sslmode=require`) in production.