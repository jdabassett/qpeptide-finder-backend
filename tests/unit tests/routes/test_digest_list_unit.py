"""
Unit tests for the digest list endpoint.
"""

from unittest.mock import ANY, patch

import pytest
from fastapi.testclient import TestClient

from tests.factories import DigestFactory, UserFactory


@pytest.mark.unit
def test_get_digests_by_email_success(client: TestClient) -> None:
    """Test successfully getting digests by email with all functions patched."""
    # setup
    user = UserFactory.build()
    digest1 = DigestFactory.build(user_id=user.id)
    digest2 = DigestFactory.build(user_id=user.id)
    digests = [digest1, digest2]

    with (
        patch(
            "app.api.routes.digest_job.User.find_one_by_or_raise", return_value=user
        ) as mock_find_user,
        patch(
            "app.api.routes.digest_job.Digest.find_by", return_value=digests
        ) as mock_find_digests,
    ):
        # execute
        response = client.get(f"/api/v1/digest/list/{user.email}")

    # validate
    assert response.status_code == 200
    data = response.json()
    assert "digests" in data
    assert len(data["digests"]) == 2
    assert data["digests"][0]["id"] == digest1.id
    assert data["digests"][1]["id"] == digest2.id
    assert data["digests"][0]["user_id"] == user.id
    assert data["digests"][1]["user_id"] == user.id

    mock_find_user.assert_called_once_with(ANY, email=user.email)
    mock_find_digests.assert_called_once_with(ANY, user_id=user.id)
