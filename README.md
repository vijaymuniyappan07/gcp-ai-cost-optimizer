# GCP AI Cost Optimizer

A Python-based, Dockerized web app that analyzes your Google Cloud Platform (GCP) usage (VMs, Cloud SQL, GKE, Filestore, Cloud Storage) and provides actionable recommendations to reduce costs.

---

## Architecture Overview

- **Backend:** FastAPI (Python 3.9+), provides REST API endpoints for GCP data, cost analysis, and AI recommendations.
- **Frontend:** Flask (Python 3.9+), serves a web UI for cost insights and recommendations.
- **Containerization:** Docker, docker-compose for orchestration.
- **Testing:** pytest, shell scripts for Docker/integration tests.
- **See:** `.clinerules/01_architecture.md` for full architecture.

---

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Python 3.9+ (for local development)
- GCP Service Account JSON (for real GCP integration)

### 1. Clone the Repository

```sh
git clone <repo-url>
cd gcp-ai-cost-optimizer
```

### 2. Set Up Environment

Copy `.env` and fill in your GCP credentials:

```sh
cp .env .env.local
# Edit .env.local as needed
```

### 3. Build & Run with Docker Compose

```sh
docker-compose up --build
```

- Backend: [http://localhost:8000/health](http://localhost:8000/health)
- Frontend: [http://localhost:5000/](http://localhost:5000/)

### 4. Run All Tests

- **Backend unit/integration:**  
  `pytest backend/tests/`
- **Frontend unit:**  
  `pytest frontend/tests/`
- **Docker Compose integration:**  
  `bash tests/test_compose_up.sh`

---

## Project Structure

- `backend/` - FastAPI app, API endpoints, services, tests
- `frontend/` - Flask app, UI components, tests
- `Dockerfile` - Backend Docker build
- `frontend/Dockerfile` - Frontend Docker build
- `docker-compose.yml` - Orchestration for backend & frontend
- `requirements.txt` - Python dependencies
- `.env` - Environment variables (not committed)
- `.clinerules/` - Architecture, coding policy, tech stack

---

## Development

- **TDD:** Write tests before code (see `.clinerules/02_coding_policy.md`)
- **Linting:**  
  `flake8 .`  
  `black .`  
  `isort .`
- **Run backend locally:**  
  `uvicorn backend.app.main:app --reload`
- **Run frontend locally:**  
  `cd frontend/app && flask run`

---

## Security

- Never commit secrets or credentials.
- Use `.env` for all sensitive config.

---

## License

MIT
