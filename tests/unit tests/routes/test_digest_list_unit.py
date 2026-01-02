"""
Unit tests for the digest list endpoint.
"""

from unittest.mock import ANY, patch

import pytest
from fastapi.testclient import TestClient

from tests.factories import DigestFactory, UserFactory


@pytest.mark.unit
def test_get_digests_by_id_success(client: TestClient) -> None:
    """Test successfully getting digests by user id with all functions patched."""
    # setup
    user = UserFactory.build()
    user_id = user.id
    digest1 = DigestFactory.create(user=user)
    digest2 = DigestFactory.create(user=user)
    digests = [digest1, digest2]

    with (
        patch(
            "app.api.routes.digest.Digest.find_by", return_value=digests
        ) as mock_find_digests,
    ):
        # execute
        response = client.get(f"/api/v1/digest/list/{user.id}")

    # validate
    assert response.status_code == 200
    data = response.json()
    assert "digests" in data
    assert len(data["digests"]) == 2
    assert data["digests"][0]["id"] == digest1.id
    assert data["digests"][1]["id"] == digest2.id
    assert data["digests"][0]["user_id"] == user_id
    assert data["digests"][1]["user_id"] == user_id

    mock_find_digests.assert_called_once_with(ANY, user_id=user_id)
