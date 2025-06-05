# HOWTO: Run GCP AI Cost Optimizer (Backend & Frontend, No Docker)

## Prerequisites

- Python 3.9+ installed
- `requirements.txt` dependencies installed
- `.env` file with GCP credentials (see `.env.example` or `README.md`)

---

## 1. Install Dependencies

From the project root:

```sh
pip install -r requirements.txt
```

---

## 2. Set Up Environment

- Ensure `.env` is present in the project root and contains valid GCP credentials and other required variables.

---

## 3. Run the Backend (FastAPI)

From the project root:

```sh
uvicorn backend.app.main:app --reload
```

- Access backend at: [http://localhost:8000/health](http://localhost:8000/health)
- Other endpoints: `/resources/vms`, `/resources/cloudsql`, etc.

---

## 4. Run the Frontend (Flask)

From the project root:

```sh
cd frontend/app
flask run
```

- Access frontend at: [http://localhost:5000/](http://localhost:5000/)

---

## 5. Run Tests

- **Backend unit/integration:**  
  `pytest backend/tests/`
- **Frontend unit:**  
  `pytest frontend/tests/`

---

## 6. Troubleshooting

- Ensure `.env` is present and valid.
- If ports are in use, stop other services or change the port in the run command.
- For import errors, ensure you are running commands from the project root.

---

If you need more granular instructions for a specific workflow, let me know!
