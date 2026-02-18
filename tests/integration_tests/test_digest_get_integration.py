"""
Integration tests for the get digest by ID endpoint.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.enums import DigestStatusEnum
from tests.factories import DigestFactory, UserFactory


@pytest.mark.integration
def test_get_digest_by_id_success_completed(
    client: TestClient,
    db_session: Session,
) -> None:
    """Test successfully getting a completed digest by ID with real database operations."""
    # setup
    user = UserFactory.create()
    digest = DigestFactory.create(
        user=user,
        status=DigestStatusEnum.COMPLETED,
        protein_name="Test Protein",
        sequence="MKTAYIAKQR",
    )
    db_session.expire_all()

    # execute
    response = client.get(f"/api/v1/digest/{user.id}/{digest.id}")

    # validate
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == digest.id
    assert data["user_id"] == user.id
    assert data["status"] == DigestStatusEnum.COMPLETED.value
    assert data["protein_name"] == "Test Protein"
    assert data["sequence"] == "MKTAYIAKQR"
    assert "created_at" in data
    assert "updated_at" in data


@pytest.mark.integration
def test_get_digest_by_id_success_processing(
    client: TestClient,
    db_session: Session,
) -> None:
    """Test successfully getting a processing digest by ID."""
    # setup
    user = UserFactory.create()
    digest = DigestFactory.create(
        user=user,
        status=DigestStatusEnum.PROCESSING,
        protein_name="Processing Protein",
        sequence="ACDEFGHIKLMNPQRSTVWY",
    )
    db_session.expire_all()

    # execute
    response = client.get(f"/api/v1/digest/{user.id}/{digest.id}")

    # validate
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == digest.id
    assert data["status"] == DigestStatusEnum.PROCESSING.value


@pytest.mark.integration
def test_get_digest_by_id_success_failed(
    client: TestClient,
    db_session: Session,
) -> None:
    """Test successfully getting a failed digest by ID."""
    # setup
    user = UserFactory.create()
    digest = DigestFactory.create(
        user=user,
        status=DigestStatusEnum.FAILED,
        protein_name="Failed Protein",
        sequence="MKTAYIAKQR",
    )
    db_session.expire_all()

    # execute
    response = client.get(f"/api/v1/digest/{user.id}/{digest.id}")

    # validate
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == digest.id
    assert data["status"] == DigestStatusEnum.FAILED.value


@pytest.mark.integration
def test_get_digest_by_id_not_found(
    client: TestClient,
) -> None:
    """Test that 404 is returned when digest does not exist."""
    # setup
    user = UserFactory.create()
    nonexistent_digest_id = "fc502bbe-5a1b-4f99-b716-e1970db2aef7"

    # execute
    response = client.get(f"/api/v1/digest/{user.id}/{nonexistent_digest_id}")

    # validate
    assert response.status_code == 404


@pytest.mark.integration
def test_get_digest_by_id_user_not_found(
    client: TestClient,
) -> None:
    """Test that 404 is returned when user does not exist."""
    # setup
    nonexistent_user_id = "fc502bbe-5a1b-4f99-b716-e1970db2aef7"
    digest = DigestFactory.create(
        status=DigestStatusEnum.COMPLETED,
        protein_name="Test Protein",
        sequence="MKTAYIAKQR",
    )

    # execute
    response = client.get(f"/api/v1/digest/{nonexistent_user_id}/{digest.id}")

    # validate
    assert response.status_code == 404
