"""
Tests for the users endpoint with database integration.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.user import User


@pytest.mark.unit
def test_create_user(client: TestClient, db_session: Session):
    """Test creating a new user."""
    # execute
    response = client.post(
        "/api/v1/users",
        json={"username": "testuser", "email": "test@example.com"},
    )

    # validate
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "testuser"
    assert data["email"] == "test@example.com"
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data

    user = db_session.query(User).filter(User.email == "test@example.com").first()
    assert user is not None
    assert user.username == "testuser"


# @pytest.mark.unit
# def test_create_user_duplicate_email_updates_username(
#     client: TestClient, db_session: Session
# ):
#     """Test that creating a user with existing email updates the username."""
#     # Setup: Create initial user
#     initial_user = User(username="oldname", email="test@example.com")
#     db_session.add(initial_user)
#     db_session.commit()

#     # execute: Create user with same email but different username
#     response = client.post(
#         "/api/v1/users",
#         json={"username": "newname", "email": "test@example.com"},
#     )

#     # validate
#     assert response.status_code == 201
#     data = response.json()
#     assert data["email"] == "test@example.com"
#     assert data["username"] == "newname"

#     # Verify only one user exists with this email
#     users = db_session.query(User).filter(User.email == "test@example.com").all()
#     assert len(users) == 1
#     assert users[0].username == "newname"


# @pytest.mark.unit
# def test_user_isolation_between_tests(client: TestClient, db_session: Session):
#     """Test that data is wiped between tests - this should pass even if run after other tests."""
#     # This test verifies that the database is clean between tests
#     # If data wasn't wiped, we'd see users from previous tests
#     users = db_session.query(User).all()
#     assert len(users) == 0

#     # Create a user
#     response = client.post(
#         "/api/v1/users",
#         json={"username": "isolated", "email": "isolated@example.com"},
#     )
#     assert response.status_code == 201

#     # Verify it exists
#     users = db_session.query(User).all()
#     assert len(users) == 1
