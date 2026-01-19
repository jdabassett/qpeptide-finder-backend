"""
Integration tests for API security (API key and middleware validation).
"""

import pytest
from fastapi.testclient import TestClient

from tests.factories import UserCreateFactory


@pytest.mark.integration
def test_api_endpoint_without_api_key_fails(secure_client: TestClient):
    """
    Test that API endpoints fail with 403 when API key is not provided.
    """
    # setup
    user_request = UserCreateFactory.build()
    user_request_dict = user_request.model_dump()

    # execute
    response = secure_client.post(
        "/api/v1/users",
        json=user_request_dict,
    )

    # validate
    assert response.status_code == 403
    response_data = response.json()
    assert "detail" in response_data
    assert (
        "API key" in response_data["detail"].lower()
        or "Missing" in response_data["detail"]
    )


@pytest.mark.integration
def test_api_endpoint_with_invalid_api_key_fails(secure_client: TestClient):
    """
    Test that API endpoints fail with 403 when invalid API key is provided.
    """
    # setup
    user_request = UserCreateFactory.build()
    user_request_dict = user_request.model_dump()

    # execute
    response = secure_client.post(
        "/api/v1/users",
        json=user_request_dict,
        headers={"X-API-Key": "wrong-api-key"},
    )

    # validate
    assert response.status_code == 403
    response_data = response.json()
    assert "detail" in response_data
    assert (
        "Invalid" in response_data["detail"]
        or "API key" in response_data["detail"].lower()
    )


@pytest.mark.integration
def test_health_endpoint_without_api_key_succeeds(secure_client: TestClient):
    """
    Test that health endpoint works without API key (but requires nginx header).
    """
    # execute
    response = secure_client.get(
        "/health",
        headers={"X-Forwarded-By": "nginx"},
    )
    # validate
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "service" in data
