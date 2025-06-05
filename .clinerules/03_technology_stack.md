# Technology Stack for GCP AI Cost Optimizer

This document clarifies the technology choices for all major components of the project. All contributors should adhere to these selections unless a change is explicitly approved.

---

## Backend

- **Language:** Python 3.9+
- **Framework:** FastAPI (primary)
- **API Modeling & Validation:** Pydantic
- **GCP Integration:** Google Cloud Python SDKs (e.g., google-cloud-compute, google-cloud-sql, google-cloud-storage, etc.)
- **Testing:** pytest, unittest.mock or pytest-mock
- **Linting & Formatting:** flake8, black, isort
- **Environment Variables:** python-dotenv

---

## Frontend

- **Language:** Python 3.9+
- **Framework:** Flask (primary for MVP)
    - *Alternatives (if needed):* FastAPI (with Jinja2 templates), Streamlit
- **Templating:** Jinja2 (for Flask/FastAPI)
- **Static Assets:** Standard CSS/JS (placed in `frontend/app/static/`)
- **Testing:** pytest

---

## Containerization & Orchestration

- **Containerization:** Docker (single and multi-stage builds)
- **Orchestration:** docker-compose

---

## General Tooling

- **Version Control:** git
- **Documentation:** Markdown (`README.md`, clinerules)
- **CI/CD:** (Recommended) GitHub Actions or similar for automated testing and linting

---

## Notes

- All code must follow PEP8 and the coding policy in `.clinerules/02_coding_policy.md`.
- All dependencies must be listed in `requirements.txt`.
- Use service accounts and `.env` files for secrets and configuration.
- All major technology changes must be discussed and approved.

---
