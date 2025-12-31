"""
Integration tests for the digest list endpoint.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.enums import DigestStatusEnum
from app.models import Digest
from tests.factories import DigestFactory, UserFactory


@pytest.mark.integration
def test_get_digests_by_email_success(
    client: TestClient,
    db_session: Session,
) -> None:
    """Test successfully getting digests by email with real database operations."""
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
    digest3 = DigestFactory.create(
        user=user,
        status=DigestStatusEnum.COMPLETED,
        protein_name=None,
        sequence="MKTAYIAKQRQISFVKSHFSRQLEERLGLIEVQAPILSRVGDGTQDNLSGAEKAVQVKVKALPDAQFEVVHSLAKWKRQTLGQHDFSAGEGLYTHMKALRPDEDRLSPLHSVYVDQWDWYVYSQIAEEYEVHSSFLK",
    )

    other_user = UserFactory.create()
    other_digest = DigestFactory.create(
        user_id=other_user.id,
        status=DigestStatusEnum.COMPLETED,
    )

    db_session.expire_all()

    # execute
    response = client.get(f"/api/v1/digest/list/{user_email}")

    # validate
    # breakpoint()
    assert response.status_code == 200
    data = response.json()
    assert "digests" in data
    assert len(data["digests"]) == 3

    digest_ids = {d["id"] for d in data["digests"]}
    assert digest1.id in digest_ids
    assert digest2.id in digest_ids
    assert digest3.id in digest_ids
    assert other_digest.id not in digest_ids

    db_digests = (
        db_session.query(Digest)
        .filter(Digest.user_id == user.id)
        .order_by(Digest.created_at)
        .all()
    )
    assert len(db_digests) == 3
    assert {d.id for d in db_digests} == {digest1.id, digest2.id, digest3.id}


@pytest.mark.integration
def test_get_digests_by_email_empty_list(
    client: TestClient,
    db_session: Session,
) -> None:
    """Test getting digests when user has no digests."""
    # setup
    user = UserFactory.create()
    user_email = user.email

    # execute
    response = client.get(f"/api/v1/digest/list/{user_email}")

    # validate
    assert response.status_code == 200
    data = response.json()
    assert "digests" in data
    assert data["digests"] == []

    db_digests = db_session.query(Digest).filter(Digest.user_id == user.id).all()
    assert len(db_digests) == 0


@pytest.mark.integration
def test_get_digests_by_email_user_not_found(
    client: TestClient,
    db_session: Session,
) -> None:
    """Test that 404 is returned when user is not found."""
    # setup
    nonexistent_email = "nonexistent@example.com"

    # execute
    response = client.get(f"/api/v1/digest/list/{nonexistent_email}")

    # validate
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "User" in data["detail"]
    assert nonexistent_email in data["detail"]
    assert (
        "records found" in data["detail"].lower()
        or "not found" in data["detail"].lower()
    )
