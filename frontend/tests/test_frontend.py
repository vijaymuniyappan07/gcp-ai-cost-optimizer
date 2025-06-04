import sys
import os
import pytest

# Ensure the app module is importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'app')))

from main import app

def test_root_route():
    client = app.test_client()
    response = client.get("/")
    assert response.status_code == 200
    assert b"GCP AI Cost Optimizer Frontend" in response.data
    assert b"Welcome to the MVP Flask UI." in response.data
