"""
Unit tests for the get digest by ID endpoint.
"""

from unittest.mock import ANY, patch

import pytest
from fastapi import HTTPException, status
from fastapi.testclient import TestClient

from app.enums import DigestStatusEnum
from tests.factories import DigestFactory, UserFactory


@pytest.mark.unit
def test_get_digest_by_id_success(client: TestClient) -> None:
    """Test successfully getting a digest by ID with all functions patched."""
    # setup
    user = UserFactory.build()
    digest = DigestFactory.create(user=user, status=DigestStatusEnum.COMPLETED)

    with patch(
        "app.api.routes.digest.Digest.find_one_by_or_raise", return_value=digest
    ) as mock_find_digest:
        # execute
        response = client.get(f"/api/v1/digest/{user.id}/{digest.id}")

    # validate
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == digest.id
    assert data["user_id"] == user.id
    assert data["status"] == DigestStatusEnum.COMPLETED.value
    assert data["protein_name"] == digest.protein_name
    assert data["sequence"] == digest.sequence

    mock_find_digest.assert_called_once_with(
        ANY,
        user_id=user.id,
        id=digest.id,
    )


@pytest.mark.unit
def test_get_digest_by_id_processing(client: TestClient) -> None:
    """Test getting a digest that is still processing."""
    # setup
    user = UserFactory.build()
    digest = DigestFactory.create(user=user, status=DigestStatusEnum.PROCESSING)

    with patch(
        "app.api.routes.digest.Digest.find_one_by_or_raise", return_value=digest
    ) as mock_find_digest:
        # execute
        response = client.get(f"/api/v1/digest/{user.id}/{digest.id}")

    # validate
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == digest.id
    assert data["status"] == DigestStatusEnum.PROCESSING.value

    mock_find_digest.assert_called_once_with(
        ANY,
        user_id=user.id,
        id=digest.id,
    )


@pytest.mark.unit
def test_get_digest_by_id_failed(client: TestClient) -> None:
    """Test getting a digest that has failed."""
    # setup
    user = UserFactory.build()
    digest = DigestFactory.create(user=user, status=DigestStatusEnum.FAILED)

    with patch(
        "app.api.routes.digest.Digest.find_one_by_or_raise", return_value=digest
    ) as mock_find_digest:
        # execute
        response = client.get(f"/api/v1/digest/{user.id}/{digest.id}")

    # validate
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == digest.id
    assert data["status"] == DigestStatusEnum.FAILED.value

    mock_find_digest.assert_called_once_with(
        ANY,
        user_id=user.id,
        id=digest.id,
    )


@pytest.mark.unit
def test_get_digest_by_id_not_found(client: TestClient) -> None:
    """Test getting a digest that does not exist."""
    # setup
    user = UserFactory.build()
    nonexistent_digest_id = "fc502bbe-5a1b-4f99-b716-e1970db2aef7"

    with patch("app.api.routes.digest.Digest.find_one_by_or_raise") as mock_find_digest:
        mock_find_digest.side_effect = HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No Digest records found with user_id='{user.id}', id='{nonexistent_digest_id}'.",
        )

        # execute
        response = client.get(f"/api/v1/digest/{user.id}/{nonexistent_digest_id}")

    # validate
    assert response.status_code == 404
    response_data = response.json()
    assert "detail" in response_data
    assert "Digest" in response_data["detail"]
    assert nonexistent_digest_id in response_data["detail"]

    mock_find_digest.assert_called_once_with(
        ANY,
        user_id=user.id,
        id=nonexistent_digest_id,
    )


@pytest.mark.unit
def test_get_digest_by_id_user_not_found(client: TestClient) -> None:
    """Test getting a digest when user does not exist."""
    # setup
    nonexistent_user_id = "fc502bbe-5a1b-4f99-b716-e1970db2aef7"
    digest_id = "some-digest-id"

    with patch("app.api.routes.digest.Digest.find_one_by_or_raise") as mock_find_digest:
        mock_find_digest.side_effect = HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No Digest records found with user_id='{nonexistent_user_id}', id='{digest_id}'.",
        )

        # execute
        response = client.get(f"/api/v1/digest/{nonexistent_user_id}/{digest_id}")

    # validate
    assert response.status_code == 404
    response_data = response.json()
    assert "detail" in response_data

    mock_find_digest.assert_called_once_with(
        ANY,
        user_id=nonexistent_user_id,
        id=digest_id,
    )
