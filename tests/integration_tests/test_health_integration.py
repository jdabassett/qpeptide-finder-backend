"""
Tests for the health check endpoint.
"""

import pytest
from fastapi.testclient import TestClient


@pytest.mark.unit
def test_health_endpoint(client: TestClient):
    """Test that the health endpoint returns a successful response."""
    # execute
    response = client.get("/health")
    # validate
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "qpeptide-cutter-backend"
    assert "database" in data
