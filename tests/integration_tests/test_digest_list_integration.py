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
def test_get_digests_by_id_success(
    client: TestClient,
    db_session: Session,
) -> None:
    """Test successfully getting digests by user id with real database operations."""
    # setup
    user = UserFactory.create()

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
        user=other_user,
        status=DigestStatusEnum.COMPLETED,
    )

    db_session.expire_all()

    # execute
    response = client.get(f"/api/v1/digest/list/{user.id}")

    # validate
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
def test_get_digests_by_id_empty_list(
    client: TestClient,
    db_session: Session,
) -> None:
    """Test getting digests when user has no digests."""
    # setup
    user = UserFactory.create()

    # execute
    response = client.get(f"/api/v1/digest/list/{user.id}")

    # validate
    assert response.status_code == 200
    data = response.json()
    assert "digests" in data
    assert data["digests"] == []

    db_digests = db_session.query(Digest).filter(Digest.user_id == user.id).all()
    assert len(db_digests) == 0
