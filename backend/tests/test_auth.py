import sys
import os
import tempfile
import json
import pytest

# Ensure the app module is importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'app', 'utils')))

from auth import load_gcp_credentials

@pytest.fixture
def fake_service_account_file():
    # Minimal valid service account JSON for Google Auth
    data = {
        "type": "service_account",
        "project_id": "test-project",
        "private_key_id": "fake-key-id",
        "private_key": "-----BEGIN PRIVATE KEY-----\\nfake\\n-----END PRIVATE KEY-----\\n",
        "client_email": "test@test-project.iam.gserviceaccount.com",
        "client_id": "fake-client-id",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/test@test-project.iam.gserviceaccount.com"
    }
    with tempfile.NamedTemporaryFile("w+", delete=False) as f:
        json.dump(data, f)
        f.flush()
        yield f.name
    os.remove(f.name)

def test_load_gcp_credentials(monkeypatch, fake_service_account_file):
    # Patch the load_credentials_from_file function to avoid parsing the key
    import auth
    class DummyCreds:
        token = "dummy"
    monkeypatch.setenv("GOOGLE_APPLICATION_CREDENTIALS", fake_service_account_file)
    monkeypatch.setattr(auth, "load_credentials_from_file", lambda path: (DummyCreds(), "test-project"))
    creds = load_gcp_credentials()
    assert creds is not None
    assert hasattr(creds, "token")
