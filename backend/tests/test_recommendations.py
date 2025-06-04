import sys
import os
import pytest
from fastapi.testclient import TestClient

# Ensure the app module is importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'app')))

from main import app

client = TestClient(app)

def test_post_recommendations():
    response = client.post("/recommendations", json={"analysis": "test"})
    assert response.status_code == 200
    data = response.json()
    assert "recommendations" in data
    assert isinstance(data["recommendations"], list)
    assert len(data["recommendations"]) > 0
