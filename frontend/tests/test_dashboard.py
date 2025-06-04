import sys
import os
import pytest

# Ensure the components module is importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'app', 'components')))

from dashboard import Dashboard

def test_dashboard_render():
    dashboard = Dashboard()
    html = dashboard.render()
    assert isinstance(html, str)
    assert "Dashboard Component (Stub)" in html
