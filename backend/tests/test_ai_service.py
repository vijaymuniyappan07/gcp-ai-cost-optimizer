import sys
import os
import pytest

# Ensure the services module is importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'app', 'services')))

from ai_service import AIService

def test_get_recommendations_stub():
    service = AIService()
    mock_analysis_data = {"analysis": "This is a stub for cost analysis results."}
    result = service.get_recommendations(mock_analysis_data)
    assert isinstance(result, dict)
    assert "recommendations" in result
    assert isinstance(result["recommendations"], list)
    assert result["recommendations"] == ["This is a stub for AI-generated recommendations."]
