"""
Integration tests for the digest delete endpoint.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.enums import DigestStatusEnum
from app.models import Digest
from tests.factories import DigestFactory, UserFactory


@pytest.mark.integration
def test_delete_digest_by_id_success(
    client: TestClient,
    db_session: Session,
) -> None:
    """Test successfully deleting a digest by ID with real database operations."""
    # setup
    user = UserFactory.create()
    user_email = user.email

    digest1 = DigestFactory.create(
        user=user,
        status=DigestStatusEnum.COMPLETED,
        protein_name="Test Protein 1",
        sequence="MKTAYIAKQR",
    )
    digest2 = DigestFactory.create(
        user=user,
        status=DigestStatusEnum.PROCESSING,
        protein_name="Test Protein 2",
        sequence="ACDEFGHIKLMNPQRSTVWY",
    )

    db_session.expire_all()

    # execute
    response = client.delete(f"/api/v1/digest/delete/{user_email}/{digest1.id}")

    # validate
    assert response.status_code == 204
    assert response.content == b""

    deleted_digest = db_session.query(Digest).filter(Digest.id == digest1.id).first()
    assert deleted_digest is None

    remaining_digest = db_session.query(Digest).filter(Digest.id == digest2.id).first()
    assert remaining_digest is not None
    assert remaining_digest.id == digest2.id

    remaining_digests = db_session.query(Digest).filter(Digest.user_id == user.id).all()
    assert len(remaining_digests) == 1
    assert remaining_digests[0].id == digest2.id


@pytest.mark.integration
def test_delete_digest_by_id_user_not_found(
    client: TestClient,
) -> None:
    """Test that 404 is returned when user is not found."""
    # setup
    nonexistent_email = "nonexistent@example.com"
    digest_id = "some-digest-id"

    # execute
    response = client.delete(f"/api/v1/digest/delete/{nonexistent_email}/{digest_id}")

    # validate
    assert response.status_code == 404


@pytest.mark.integration
def test_delete_digest_by_id_digest_not_found(
    client: TestClient,
) -> None:
    """Test that 404 is returned when digest is not found."""
    # setup
    user = UserFactory.create()
    user_email = user.email
    nonexistent_digest_id = "nonexistent-digest-id"

    # execute
    response = client.delete(
        f"/api/v1/digest/delete/{user_email}/{nonexistent_digest_id}"
    )

    # validate
    assert response.status_code == 404


@pytest.mark.integration
def test_delete_digest_by_id_digest_belongs_to_other_user(
    client: TestClient,
    db_session: Session,
) -> None:
    """Test that 404 is returned when digest belongs to a different user."""
    # setup
    user1 = UserFactory.create()
    user2 = UserFactory.create()

    user2_digest = DigestFactory.create(
        user=user2,
        status=DigestStatusEnum.COMPLETED,
        protein_name="User2 Protein",
        sequence="MKTAYIAKQR",
    )

    db_session.expire_all()

    # execute
    response = client.delete(f"/api/v1/digest/delete/{user1.email}/{user2_digest.id}")

    # validate
    assert response.status_code == 404

    remaining_digest = (
        db_session.query(Digest).filter(Digest.id == user2_digest.id).first()
    )
    assert remaining_digest is not None
    assert remaining_digest.user_id == user2.id
