"""
Unit tests for the users endpoint with all functions patched.
"""

import datetime
from unittest.mock import ANY, patch

import pytest
from fastapi import HTTPException, status
from fastapi.testclient import TestClient

from tests.factories import UserCreateFactory, UserFactory


@pytest.mark.unit
def test_create_user(client: TestClient) -> None:
    """Test creating a new user with all functions patched."""
    # setup
    user_request = UserCreateFactory.build()
    user_request_dict = user_request.model_dump()
    now = datetime.datetime.now(datetime.UTC)
    new_user = UserFactory.build(
        username=user_request.username,
        email=user_request.email,
        created_at=now,
        updated_at=now,
    )

    with (
        patch("app.api.routes.users.get_record", return_value=None) as mock_get_record,
        patch(
            "app.api.routes.users.create_record", return_value=new_user
        ) as mock_create_record,
    ):
        # execute
        response = client.post(
            "/api/v1/users",
            json=user_request_dict,
        )

    # validate
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == user_request.username
    assert data["email"] == user_request.email
    assert data["id"] == new_user.id

    mock_get_record.assert_called_once()
    mock_create_record.assert_called_once()


@pytest.mark.unit
def test_update_user(client: TestClient) -> None:
    """Test updating an existing user with all functions patched."""
    # setup
    user_request = UserCreateFactory.build()
    user_request_dict = user_request.model_dump()
    now = datetime.datetime.now(datetime.UTC)
    existing_user = UserFactory.build(
        username="foobar",
        email=user_request.email,
        created_at=now,
        updated_at=now,
    )
    updated_user = UserFactory.build(
        id=existing_user.id,
        username=user_request.username,
        email=user_request.email,
        created_at=now,
        updated_at=now,
    )

    with (
        patch("app.api.routes.users.get_record", return_value=None) as mock_get_record,
        patch(
            "app.api.routes.users.create_record", return_value=updated_user
        ) as mock_update_record,
    ):
        # execute
        response = client.post(
            "/api/v1/users",
            json=user_request_dict,
        )

    # validate
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == user_request.username
    assert data["email"] == user_request.email
    assert data["id"] == existing_user.id
    assert data["username"] != "foobar"

    mock_get_record.assert_called_once()
    mock_update_record.assert_called_once()


@pytest.mark.unit
def test_delete_user_by_email_success(client: TestClient) -> None:
    """Test successfully deleting a user by email with all functions patched."""
    # setup
    user = UserFactory.build()
    user_email = user.email

    with (
        patch(
            "app.api.routes.users.get_record_or_exception", return_value=user
        ) as mock_get_record,
        patch("app.api.routes.users.delete_record") as mock_delete_record,
    ):
        # execute
        response = client.delete(f"/api/v1/users/email/{user_email}")

    # validate
    assert response.status_code == 204
    assert response.content == b""

    mock_get_record.assert_called_once()
    mock_delete_record.assert_called_once_with(ANY, user)


@pytest.mark.unit
def test_delete_user_by_email_no_user_found(client: TestClient) -> None:
    """Test delete user when user is not found with all functions patched."""
    # setup
    with patch("app.api.routes.users.get_record_or_exception") as mock_get_record:
        mock_get_record.side_effect = HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User with email='email_wont_be_found@email.com' not found.",
        )

        # execute
        response = client.delete("/api/v1/users/email/email_wont_be_found@email.com")

    # validate
    assert response.status_code == 404
    response_data = response.json()
    assert "detail" in response_data
    assert "User" in response_data["detail"]
    assert "email_wont_be_found@email.com" in response_data["detail"]
    assert "not found" in response_data["detail"].lower()

    mock_get_record.assert_called_once()
