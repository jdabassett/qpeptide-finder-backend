"""
Tests for the users endpoint with database integration.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.user import User
from tests.factories.dto.user_factory import UserCreateFactory
from tests.factories.models.user_factory import UserFactory


@pytest.mark.unit
def test_create_user(client: TestClient, db_session: Session):
    """Test creating a new user."""
    # setup
    user_request: UserCreateFactory = UserCreateFactory.build()
    user_request_dict: dict[str, str] = user_request.model_dump()

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
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data

    # new record is created
    user = db_session.query(User).filter(User.email == user_request.email).first()
    assert user is not None
    assert user.email == user_request.email


@pytest.mark.unit
def test_update_user(client: TestClient, db_session: Session):
    """Test update user."""
    # setup
    user_request: UserCreateFactory = UserCreateFactory.build()
    user_request_dict: dict[str, str] = user_request.model_dump()
    user_record: UserFactory = UserFactory.create(
        username="foobar", email=user_request.email
    )

    # execute
    response = client.post(
        "/api/v1/users",
        json=user_request_dict,
    )

    # validate
    # response is accurate
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == user_request.username
    assert data["email"] == user_request.email
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data

    user = db_session.query(User).filter(User.email == user_request.email).first()
    assert user is not None
    assert user.id == user_record.id
    assert user.email == user_record.email
    assert user.username == user_record.username
    assert user.username != "foobar"


@pytest.mark.parametrize(
    "request_body",
    [
        {"username": "", "email": "test@example.com"},
        {"username": "username", "email": ""},
        {"email": ""},
        {"username": "username"},
    ],
)
@pytest.mark.unit
def test_failed_create_user(client: TestClient, request_body):
    """Test that endpoint won't create new user when missing required data."""
    response = client.post(
        "/api/v1/users",
        json=request_body,
    )

    assert response.status_code == 422


@pytest.mark.unit
def test_delete_user_by_email_success(client: TestClient, db_session: Session):
    """Test successfully deleting a user by email."""
    # setup
    user: User = UserFactory.create()
    user_email: str = user.email

    # execute
    response = client.delete(f"/api/v1/users/email/{user_email}")

    # validate
    assert response.status_code == 204
    assert response.content == b""

    deleted_user = db_session.query(User).filter(User.email == user_email).first()
    assert deleted_user is None


@pytest.mark.unit
def test_delete_user_by_email_no_user_found(client: TestClient, db_session: Session):
    """Test if no user is found associated with given email."""
    # setup
    user: User = UserFactory.create()

    # execute
    response = client.delete("/api/v1/users/email/email_wont_be_found@email.com")

    # validate
    assert response.status_code == 404
    response_data = response.json()
    assert "detail" in response_data
    assert "User" in response_data["detail"]
    assert "email_wont_be_found@email.com" in response_data["detail"]
    assert "not found" in response_data["detail"].lower()

    user_retrieved = db_session.query(User).first()
    assert user_retrieved is not None
    assert user_retrieved.id == user.id
