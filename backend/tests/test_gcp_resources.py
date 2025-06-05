import sys
import os
import pytest
from fastapi.testclient import TestClient

# Ensure the app module is importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'app')))

from main import app

client = TestClient(app)

def test_get_vms():
    response = client.get("/resources/vms")
    assert response.status_code == 200
    data = response.json()
    assert "vms" in data
    assert isinstance(data["vms"], list)
    assert len(data["vms"]) == 2
    assert all("id" in vm and "name" in vm and "status" in vm for vm in data["vms"])

def test_get_cloudsql():
    response = client.get("/resources/cloudsql")
    assert response.status_code == 200
    data = response.json()
    assert "cloudsql" in data
    assert isinstance(data["cloudsql"], list)
    assert len(data["cloudsql"]) == 2
    assert all("id" in sql and "name" in sql and "status" in sql for sql in data["cloudsql"])

def test_get_gke():
    response = client.get("/resources/gke")
    assert response.status_code == 200
    data = response.json()
    assert "gke" in data
    assert isinstance(data["gke"], list)
    assert len(data["gke"]) == 2
    assert all("id" in gke and "name" in gke and "status" in gke for gke in data["gke"])

def test_get_filestore():
    response = client.get("/resources/filestore")
    assert response.status_code == 200
    data = response.json()
    assert "filestore" in data
    assert isinstance(data["filestore"], list)
    assert len(data["filestore"]) == 2
    assert all("id" in fs and "name" in fs and "status" in fs for fs in data["filestore"])

def test_get_storage():
    response = client.get("/resources/storage")
    assert response.status_code == 200
    data = response.json()
    assert "storage" in data
    assert isinstance(data["storage"], list)
    assert len(data["storage"]) == 2
    assert all("id" in bucket and "name" in bucket and "location" in bucket for bucket in data["storage"])
