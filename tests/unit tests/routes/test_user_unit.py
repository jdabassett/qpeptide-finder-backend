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
        patch(
            "app.api.routes.users.User.find_one_by", return_value=None
        ) as mock_find_one_by,
        patch("app.api.routes.users.User.create", return_value=new_user) as mock_create,
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

    mock_find_one_by.assert_called_once_with(ANY, email=user_request.email)
    mock_create.assert_called_once()


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
        patch(
            "app.api.routes.users.User.find_one_by", return_value=existing_user
        ) as mock_find_one_by,
        patch(
            "app.api.routes.users.User.update", return_value=updated_user
        ) as mock_update,
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

    mock_find_one_by.assert_called_once_with(ANY, email=user_request.email)
    mock_update.assert_called_once_with(
        ANY,
        existing_user,
        values={
            "username": user_request.username,
            "updated_at": ANY,
        },
    )


@pytest.mark.unit
def test_delete_user_by_id_success(client: TestClient) -> None:
    """Test successfully deleting a user by user id with all functions patched."""
    # setup
    user = UserFactory.build()

    with (
        patch(
            "app.api.routes.users.User.find_one_by_or_raise", return_value=user
        ) as mock_find_one,
        patch("app.api.routes.users.User.delete") as mock_delete,
    ):
        # execute
        response = client.delete(f"/api/v1/users/id/{user.id}")

    # validate
    assert response.status_code == 204
    assert response.content == b""

    mock_find_one.assert_called_once_with(ANY, id=user.id)
    mock_delete.assert_called_once_with(ANY, user)


@pytest.mark.unit
def test_delete_user_by_id_no_user_found(client: TestClient) -> None:
    """Test delete user when user is not found with all functions patched."""
    # setup
    with patch("app.api.routes.users.User.find_one_by_or_raise") as mock_find_one:
        mock_find_one.side_effect = HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No User records found with id='id_wont_be_found'.",
        )

        # execute
        response = client.delete("/api/v1/users/id/id_wont_be_found")

    # validate
    assert response.status_code == 404
    response_data = response.json()
    assert "detail" in response_data
    assert "User" in response_data["detail"]
    assert "id_wont_be_found" in response_data["detail"]

    mock_find_one.assert_called_once_with(ANY, id="id_wont_be_found")
