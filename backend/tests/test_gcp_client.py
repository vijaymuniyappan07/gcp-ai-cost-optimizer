import sys
import os
import pytest
import importlib.util

# Add backend/app to sys.path for direct import
app_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'app'))
sys.path.insert(0, app_path)

# Patch sys.modules to allow "app.utils.auth" import in gcp_client.py
import types
auth_mod = importlib.util.spec_from_file_location("auth", os.path.join(app_path, "utils", "auth.py"))
auth = importlib.util.module_from_spec(auth_mod)
auth_mod.loader.exec_module(auth)
sys.modules["app.utils.auth"] = auth

import services.gcp_client as gcp_client

def test_gcp_client_initialization(monkeypatch):
    monkeypatch.setenv("GCP_PROJECT_ID", "dummy-project")
    monkeypatch.setattr(gcp_client, "load_gcp_credentials", lambda: "dummy-creds")
    client = gcp_client.GCPClient()
    assert isinstance(client, gcp_client.GCPClient)
    assert client.credentials == "dummy-creds"

def test_gcp_client_max_workers_env(monkeypatch):
    monkeypatch.setenv("GCP_PROJECT_ID", "dummy-project")
    monkeypatch.setenv("GCP_VM_FETCH_MAX_WORKERS", "3")
    monkeypatch.setattr(gcp_client, "load_gcp_credentials", lambda: "dummy-creds")
    client = gcp_client.GCPClient()
    assert client.max_workers == 3
    monkeypatch.delenv("GCP_VM_FETCH_MAX_WORKERS")
