# MVP Task List: GCP AI Cost Optimizer

This document contains a granular, step-by-step plan to build the MVP for the GCP AI Cost Optimizer. Each task is atomic, testable, and focused on a single concern, following TDD principles.

---

## 1. Project Initialization

1. **[COMPLETED] Create project root structure**
   - Start: No project folders exist.
   - End: All top-level folders (`frontend/`, `backend/`, `scripts/`, `.clinerules/`, `tests/`) and placeholder `.gitkeep` files are present.

2. **[COMPLETED] Initialize Python environment and requirements**
   - Start: No `requirements.txt`.
   - End: `requirements.txt` with FastAPI, Flask, GCP SDK, pytest, black, flake8, isort, etc.

3. **[COMPLETED] Create `.env` and add to `.gitignore`**
   - Start: No `.env` or `.gitignore`.
   - End: `.env` exists with placeholder variables; `.gitignore` excludes `.env`.

---

## 2. Backend API Foundation

4. **[COMPLETED] Scaffold backend FastAPI app**
   - Start: No backend code.
   - End: `backend/app/main.py` with a minimal FastAPI app and a health check endpoint.

5. **[COMPLETED] Write and pass test for backend health check**
   - Start: No test for health check.
   - End: `backend/tests/test_backend.py` with a test that verifies the health check endpoint.

6. **[COMPLETED] Set up backend folder structure**
   - Start: Only `main.py` exists.
   - End: `api/`, `services/`, `utils/`, `types/` subfolders with `__init__.py` files.

---

## 3. GCP Integration (Backend)

7. **[COMPLETED] Implement GCP authentication utility**
   - Start: No GCP auth code.
   - End: `backend/app/utils/auth.py` with a function to load credentials from `.env`.

8. **[COMPLETED] Write and pass test for GCP authentication**
   - Start: No test for auth utility.
   - End: Test that mocks `.env` and checks credential loading.

9. **[COMPLETED] Scaffold GCP client service**
   - Start: No GCP client.
   - End: `backend/app/services/gcp_client.py` with a class stub for GCP API calls.

10. **[COMPLETED] Write and pass test for GCP client initialization**
    - Start: No test for GCP client.
    - End: Test that instantiates the client with mock credentials.

---

## 4. Resource Data Endpoints

11. **[COMPLETED] Implement `/resources/vms` endpoint (stub)**
    - Start: No endpoint for VMs.
    - End: `backend/app/api/gcp_resources.py` with a GET endpoint returning mock VM data.

12. **[COMPLETED] Write and pass test for `/resources/vms` endpoint**
    - Start: No test for endpoint.
    - End: Test that calls endpoint and checks response format.

13. **[COMPLETED] Repeat for Cloud SQL, GKE, Filestore, Cloud Storage**
    - Each: Implement stub endpoint and test for each resource type.

---

## 5. Cost Analysis & AI Recommendation

14. **Implement cost analysis service (stub)**
    - Start: No cost analysis logic.
    - End: `backend/app/services/cost_analysis.py` with a function stub.

15. **Write and pass test for cost analysis service**
    - Start: No test for cost analysis.
    - End: Test that calls the stub and checks output.

16. **Implement AI service (stub)**
    - Start: No AI service.
    - End: `backend/app/services/ai_service.py` with a function stub.

17. **Write and pass test for AI service**
    - Start: No test for AI service.
    - End: Test that calls the stub and checks output.

18. **Implement `/recommendations` endpoint (stub)**
    - Start: No recommendations endpoint.
    - End: `backend/app/api/recommendations.py` with a POST endpoint returning mock recommendations.

19. **Write and pass test for `/recommendations` endpoint**
    - Start: No test for recommendations endpoint.
    - End: Test that posts sample data and checks response.

---

## 6. Frontend Foundation

20. **Scaffold frontend app (Flask/FastAPI/Streamlit)**
    - Start: No frontend code.
    - End: `frontend/app/main.py` with a minimal app and root route.

21. **Write and pass test for frontend root route**
    - Start: No test for frontend.
    - End: `frontend/tests/test_frontend.py` with a test for the root route.

22. **Set up frontend folder structure**
    - Start: Only `main.py` exists.
    - End: `templates/`, `static/`, `components/`, `utils/` subfolders with placeholder files.

---

## 7. Frontend UI Components (Stubs)

23. **Create dashboard component (stub)**
    - Start: No dashboard.
    - End: `frontend/app/components/dashboard.py` with a stub class/function.

24. **Write and pass test for dashboard component**
    - Start: No test for dashboard.
    - End: Test that imports and instantiates the dashboard.

25. **Repeat for resource summary, recommendation list, action panel, cost trends chart**
    - Each: Create stub and test for each component.

---

## 8. Dockerization

26. **Create Dockerfile for backend**
    - Start: No Dockerfile.
    - End: `Dockerfile` builds backend app.

27. **Write and pass test: build and run backend container**
    - Start: No test for Docker build.
    - End: Backend container builds and health check passes.

28. **Create Dockerfile for frontend (if separate)**
    - Start: No frontend Dockerfile.
    - End: Dockerfile builds frontend app.

29. **Write and pass test: build and run frontend container**
    - Start: No test for frontend Docker build.
    - End: Frontend container builds and root route passes.

30. **Create docker-compose.yml**
    - Start: No compose file.
    - End: `docker-compose.yml` runs backend, frontend, and (optional) db.

31. **Write and pass test: docker-compose up brings up all services**
    - Start: No integration test.
    - End: All containers start and health checks pass.

---

## 9. Documentation & Linting

32. **Add and test README.md**
    - Start: No README.
    - End: `README.md` with setup and usage instructions.

33. **Set up and test linting/formatting**
    - Start: No linting.
    - End: `flake8`, `black`, and `isort` configs; test that code passes linting.

---

Each of these tasks is atomic, testable, and focused on a single concern. This plan enables incremental, TDD-driven development and easy validation at every step.
