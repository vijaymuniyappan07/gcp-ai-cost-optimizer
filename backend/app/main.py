import sys
import os
from fastapi import FastAPI
from fastapi.responses import JSONResponse

# Ensure api module is importable for both script and package execution
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from api import gcp_resources
from api import recommendations

# Import GCP credential validation
from utils import auth

app = FastAPI()

app.include_router(gcp_resources.router)
app.include_router(recommendations.router)

@app.get("/health")
def health_check():
    """
    Health check endpoint for the backend API.
    Returns 200 OK with a status message.
    """
    return JSONResponse(content={"status": "ok"})

@app.get("/auth/check")
def check_gcp_credentials():
    """
    Endpoint to validate GCP credentials.
    Returns JSON with success and message.
    """
    success, message = auth.validate_gcp_credentials()
    return JSONResponse(content={"success": success, "message": message})
