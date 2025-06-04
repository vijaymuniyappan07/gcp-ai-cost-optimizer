import sys
import os
from fastapi import FastAPI
from fastapi.responses import JSONResponse

# Ensure api module is importable for both script and package execution
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from api import gcp_resources

app = FastAPI()

app.include_router(gcp_resources.router)

@app.get("/health")
def health_check():
    """
    Health check endpoint for the backend API.
    Returns 200 OK with a status message.
    """
    return JSONResponse(content={"status": "ok"})
