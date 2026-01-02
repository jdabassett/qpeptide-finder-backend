"""
Unit tests for the digest peptides endpoint.
"""

import uuid

import pytest
from fastapi.testclient import TestClient

from app.enums import DigestStatusEnum, ProteaseEnum
from tests.factories import DigestFactory, UserFactory


@pytest.mark.integration
def test_get_digest_peptides_by_id_success(
    client: TestClient,
    setup_digest_with_peptides: tuple[str, str],
) -> None:
    """Test successfully getting peptides for a digest with all functions patched."""
    # setup
    user_id, digest_id = setup_digest_with_peptides

    # execute
    response = client.get(f"/api/v1/digest/{user_id}/{digest_id}/peptides")

    # validate
    assert response.status_code == 200
    data = response.json()
    assert "digest_id" in data
    assert data["digest_id"] == digest_id

    assert "peptides" in data
    peptides = data["peptides"]
    assert isinstance(peptides, list)
    assert len(peptides) == 3
    ranks = [p["rank"] for p in peptides]
    assert ranks == [1, 2, 3]

    for peptide in peptides:
        assert "id" in peptide
        assert "sequence" in peptide
        assert "position" in peptide
        assert "pi" in peptide
        assert "charge_state" in peptide
        assert "max_kd_score" in peptide
        assert "rank" in peptide
        assert "criteria_ranks" in peptide
        assert isinstance(peptide["criteria_ranks"], list)
        assert all(isinstance(r, int) for r in peptide["criteria_ranks"])

    assert "criteria" in data
    criteria = data["criteria"]
    assert isinstance(criteria, list)
    assert len(criteria) == 14

    for criterion in criteria:
        assert "code" in criterion
        assert "goal" in criterion
        assert "rationale" in criterion
        assert "rank" in criterion


@pytest.mark.integration
def test_get_digest_peptides_by_id_user_not_found(
    client: TestClient,
    setup_digest_with_peptides: tuple[str, str],
) -> None:
    """Test that 404 is returned when user is not found."""
    # setup
    _, digest_id = setup_digest_with_peptides
    nonexistent_user_id = str(uuid.uuid4())

    # execute
    response = client.get(f"/api/v1/digest/{nonexistent_user_id}/{digest_id}/peptides")

    # validate
    assert response.status_code == 404


@pytest.mark.integration
def test_get_digest_peptides_by_id_digest_not_found(
    client: TestClient,
    setup_digest_with_peptides: tuple[str, str],
) -> None:
    """Test that 404 is returned when digest is not found."""
    # setup
    user_id, _ = setup_digest_with_peptides
    nonexistent_digest_id = str(uuid.uuid4())

    # execute
    response = client.get(f"/api/v1/digest/{user_id}/{nonexistent_digest_id}/peptides")

    # validate
    assert response.status_code == 404


@pytest.mark.integration
def test_get_digest_peptides_by_id_no_peptides_found(
    client: TestClient,
    db_session: pytest.Session,
) -> None:
    """Test that 404 is returned when digest exists but has no peptides."""
    # setup
    user = UserFactory.create()
    digest = DigestFactory.create(
        user=user,
        status=DigestStatusEnum.PROCESSING,
        sequence="MKTAYIAKQR",
        protease=ProteaseEnum.TRYPSIN,
    )
    db_session.commit()

    # execute
    response = client.get(f"/api/v1/digest/{user.id}/{digest.id}/peptides")

    # validate
    assert response.status_code == 404
