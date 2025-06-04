import sys
import os
import pytest

# Ensure the services module is importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'app', 'services')))

from cost_analysis import CostAnalysisService

def test_analyze_costs_stub():
    service = CostAnalysisService()
    mock_resource_data = {"vms": [], "cloudsql": [], "gke": [], "filestore": [], "storage": []}
    result = service.analyze_costs(mock_resource_data)
    assert isinstance(result, dict)
    assert "analysis" in result
    assert result["analysis"] == "This is a stub for cost analysis results."
