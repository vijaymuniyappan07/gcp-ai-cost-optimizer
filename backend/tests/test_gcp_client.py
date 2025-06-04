import sys
import os
import pytest

# Ensure the services module is importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'app', 'services')))

from gcp_client import GCPClient

class DummyCreds:
    pass

def test_gcp_client_initialization():
    creds = DummyCreds()
    client = GCPClient(credentials=creds)
    assert isinstance(client, GCPClient)
    assert client.credentials is creds
