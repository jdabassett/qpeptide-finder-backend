"""
Unit tests for the digest delete endpoint.
"""

from unittest.mock import ANY, patch

import pytest
from fastapi import HTTPException, status
from fastapi.testclient import TestClient
from sqlalchemy.exc import IntegrityError

from tests.factories import DigestFactory, UserFactory


@pytest.mark.unit
def test_delete_digest_by_id_success(client: TestClient) -> None:
    """Test successfully deleting a digest by ID with all functions patched."""
    # setup
    user = UserFactory.build()
    digest = DigestFactory.create(user=user)

    with (
        patch(
            "app.api.routes.digest.Digest.find_one_by_or_raise", return_value=digest
        ) as mock_find_digest,
        patch("app.api.routes.digest.Digest.delete") as mock_delete,
    ):
        # execute
        response = client.delete(f"/api/v1/digest/delete/{user.id}/{digest.id}")

    # validate
    assert response.status_code == 204
    assert response.content == b""

    mock_find_digest.assert_called_once_with(
        ANY,
        user_id=user.id,
        id=digest.id,
    )
    mock_delete.assert_called_once_with(ANY, digest)


@pytest.mark.unit
def test_delete_digest_by_id_user_not_found(client: TestClient) -> None:
    """Test delete digest when user is not found with all functions patched."""
    # setup
    nonexistent_user_id = "fc502bbe-5a1b-4f99-b716-e1970db2aef7"
    digest_id = "some-digest-id"

    with (
        patch("app.api.routes.digest.Digest.find_one_by_or_raise") as mock_find_digest,
    ):
        mock_find_digest.side_effect = HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No User records found with id='{nonexistent_user_id}'.",
        )

        # execute
        response = client.delete(
            f"/api/v1/digest/delete/{nonexistent_user_id}/{digest_id}"
        )

    # validate
    assert response.status_code == 404
    response_data = response.json()
    assert "detail" in response_data
    assert "User" in response_data["detail"]
    assert nonexistent_user_id in response_data["detail"]

    mock_find_digest.assert_called_once_with(
        ANY, user_id=nonexistent_user_id, id=digest_id
    )


@pytest.mark.unit
def test_delete_digest_by_id_digest_not_found(client: TestClient) -> None:
    """Test delete digest when digest is not found with all functions patched."""
    # setup
    user = UserFactory.build()
    nonexistent_digest_id = "fc502bbe-5a1b-4f99-b716-e1970db2aef7"

    with (
        patch("app.api.routes.digest.Digest.find_one_by_or_raise") as mock_find_digest,
    ):
        mock_find_digest.side_effect = HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No Digest records found with user_id='{user.id}', id='{nonexistent_digest_id}'.",
        )

        # execute
        response = client.delete(
            f"/api/v1/digest/delete/{user.id}/{nonexistent_digest_id}"
        )

    # validate
    assert response.status_code == 404
    response_data = response.json()
    assert "detail" in response_data
    assert "Digest" in response_data["detail"]
    assert nonexistent_digest_id in response_data["detail"]

    mock_find_digest.assert_called_once_with(
        ANY, user_id=user.id, id=nonexistent_digest_id
    )


@pytest.mark.unit
def test_delete_digest_by_id_integrity_error(client: TestClient) -> None:
    """Test delete digest when IntegrityError occurs with all functions patched."""
    # setup
    user = UserFactory.build()
    user_id = user.id
    digest = DigestFactory.create(user=user)

    with (
        patch(
            "app.api.routes.digest.Digest.find_one_by_or_raise", return_value=digest
        ) as mock_find_digest,
        patch("app.api.routes.digest.Digest.delete") as mock_delete,
    ):
        mock_delete.side_effect = IntegrityError(
            statement="DELETE FROM digests",
            params=None,
            orig=Exception("Foreign key constraint violation"),
        )

        # execute
        response = client.delete(f"/api/v1/digest/delete/{user.id}/{digest.id}")

    # validate
    assert response.status_code == 400
    response_data = response.json()
    assert "detail" in response_data
    assert "constraint violation" in response_data["detail"].lower()

    mock_find_digest.assert_called_once_with(
        ANY,
        user_id=user_id,
        id=digest.id,
    )
    mock_delete.assert_called_once_with(ANY, digest)
