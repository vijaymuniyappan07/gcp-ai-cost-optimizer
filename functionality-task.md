# Functionality Task List: GCP AI Cost Optimizer (Next Phase)

This list prioritizes visual feedback and parallel backend/frontend progress.

---

## 1. Home Page (Frontend)

- **[COMPLETED] Create a Home Page**
  - Implement a homepage in the frontend (Flask) that visually references all major resources: VMs, Cloud SQL, GKE, Filestore, Cloud Storage.
  - The page should have clear navigation or links/cards for each resource type.
  - Test: Home page renders and all resource references are visible.
  - **Includes login mechanism:** Users must log in as admin or reader (credentials from .env) before accessing the homepage.

---

## 2. GCP Credential Validation (Backend)

- **[COMPLETED] Implement and Test GCP Credential Logic**
  - Update `backend/app/utils/auth.py` to validate real GCP credentials (load from `.env`, check file exists, attempt a simple GCP API call for validation).
  - Add a backend endpoint (e.g., `/auth/check`) to test credential validity.
  - Test: Endpoint returns success/failure for valid/invalid credentials.
  - (Optional) Add a frontend UI to display credential status.

---

## 3. VMs: Backend + Frontend

- **[COMPLETED] Backend:**
  - Refactor: Move VM logic to `backend/app/services/vm_service.py` and shared project/zone logic to `backend/app/services/gcp_client.py`.
  - API endpoints use resource-specific service files (e.g., `VMService` for `/resources/vms`).
  - Implement real GCP VM data fetching and wire to `/resources/vms`.
  - Test: Endpoint returns real (or mocked) VM data.

- **[COMPLETED] Frontend:**
  - Update `ResourceSummary` (or a dedicated VMs page) to fetch and display VM data from backend.
  - Add loading/error states for VM data.
  - Add sorting, pagination, and CSV download for all columns.
  - Test: UI shows live VM data.

---

## 4. Cloud SQL: Backend + Frontend

- **[COMPLETED] Backend:**
  - Refactor: Move Cloud SQL logic to `backend/app/services/cloudsql_service.py`.
  - API endpoint `/resources/cloudsql` uses `CloudSQLService` to return real Cloud SQL data.
  - Test: Endpoint returns real Cloud SQL data for the selected project.

- **[COMPLETED] Frontend:**
  - Add `/cloudsql` route and `cloudsql.html` template to display Cloud SQL data.
  - Add loading/error states for Cloud SQL.
  - Add "Cloud SQL" link to the home page.
  - Test: UI shows live Cloud SQL data.

---

## 5. GKE: Backend + Frontend

- **[COMPLETED] Backend:**
  - Implement GKE cluster data fetching in a dedicated service file and wire to `/resources/gke`.
  - Test: Endpoint returns real (or mocked) GKE data.

- **[COMPLETED] Frontend:**
  - Update `ResourceSummary` to display GKE data.
  - Add loading/error states for GKE.
  - Test: UI shows live GKE data.

---

## 6. Filestore: Backend + Frontend

- **[COMPLETED] Backend:**
  - Implement Filestore data fetching in a dedicated service file and wire to `/resources/filestore`.
  - Test: Endpoint returns real (or mocked) Filestore data.

- **[COMPLETED] Frontend:**
  - Add a new route and template to display Filestore data.
  - Add loading/error states for Filestore.
  - Add a "Filestore" link to the home page.
  - Add sorting and CSV download for all columns.
  - Test: UI shows live Filestore data.

---

## 7. Cloud Storage: Backend + Frontend

- **[COMPLETED] Backend:**
  - Implement Cloud Storage bucket data fetching in a dedicated service file and wire to `/resources/storage`.
  - Test: Endpoint returns real (or mocked) Storage data.

- **[COMPLETED] Frontend:**
  - Add a new route and template to display Storage data.
  - Add loading/error states for Storage.
  - Add sorting, pagination, and CSV download for all columns.
  - Test: UI shows live Storage data.

---

## 8. Cost Analysis: Backend + Frontend

- **Backend:**
  - Implement real cost analysis logic in `cost_analysis.py` and expose via `/cost-analysis`.
  - Test: Endpoint returns analysis for test data.

- **Frontend:**
  - Update dashboard to fetch and display cost analysis results.
  - Add loading/error states for cost analysis.
  - Test: UI shows live cost analysis.

---

## 9. AI/ML Recommendations: Backend + Frontend

### VMs

- **Backend:**
  - [ ] Implement `/recommendations` endpoint for VMs in `backend/app/api/recommendations.py`.
  - [ ] In `ai_service.py`, add logic to analyze VM data and return recommendations.
  - [ ] Test: Endpoint returns actionable recommendations for VMs.

- **Frontend:**
  - [ ] Add "Get AI Recommendation" button to the VMs page.
  - [ ] On click, send VM data to backend and display recommendations inline.
  - [ ] Add loading/error states for recommendations.
  - [ ] Test: UI shows live recommendations for VMs.

---

### Cloud SQL

- **Backend:**
  - [ ] Implement `/recommendations` endpoint for Cloud SQL.
  - [ ] In `ai_service.py`, add logic to analyze Cloud SQL data and return recommendations.
  - [ ] Test: Endpoint returns actionable recommendations for Cloud SQL.

- **Frontend:**
  - [ ] Add "Get AI Recommendation" button to the Cloud SQL page.
  - [ ] On click, send Cloud SQL data to backend and display recommendations inline.
  - [ ] Add loading/error states for recommendations.
  - [ ] Test: UI shows live recommendations for Cloud SQL.

---

### GKE

- **Backend:**
  - [ ] Implement `/recommendations` endpoint for GKE.
  - [ ] In `ai_service.py`, add logic to analyze GKE data and return recommendations.
  - [ ] Test: Endpoint returns actionable recommendations for GKE.

- **Frontend:**
  - [ ] Add "Get AI Recommendation" button to the GKE page.
  - [ ] On click, send GKE data to backend and display recommendations inline.
  - [ ] Add loading/error states for recommendations.
  - [ ] Test: UI shows live recommendations for GKE.

---

### Filestore

- **Backend:**
  - [ ] Implement `/recommendations` endpoint for Filestore.
  - [ ] In `ai_service.py`, add logic to analyze Filestore data and return recommendations.
  - [ ] Test: Endpoint returns actionable recommendations for Filestore.

- **Frontend:**
  - [ ] Add "Get AI Recommendation" button to the Filestore page.
  - [ ] On click, send Filestore data to backend and display recommendations inline.
  - [ ] Add loading/error states for recommendations.
  - [ ] Test: UI shows live recommendations for Filestore.

---

### Cloud Storage

- **Backend:**
  - [ ] Implement `/recommendations` endpoint for Cloud Storage.
  - [ ] In `ai_service.py`, add logic to analyze Storage data and return recommendations.
  - [ ] Test: Endpoint returns actionable recommendations for Storage.

- **Frontend:**
  - [ ] Add "Get AI Recommendation" button to the Storage page.
  - [ ] On click, send Storage data to backend and display recommendations inline.
  - [ ] Add loading/error states for recommendations.
  - [ ] Test: UI shows live recommendations for Storage.

---

## 10. User Actions & Polish

- **Frontend:**
  - Implement basic navigation and layout (dashboard, resource details, recommendations).
  - Add minimal CSS for usability.
  - Test: Visual check and navigation.

---

## 11. Documentation & DevOps

- **Update README and .env.example** as you add new features.
- **(Optional) Set up CI for tests and linting.**

---

If you want a more granular breakdown for any specific step, let me know!
