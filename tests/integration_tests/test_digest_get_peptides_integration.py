"""
Unit tests for the digest peptides endpoint.
"""

import pytest
from fastapi.testclient import TestClient


@pytest.mark.unit
def test_get_digest_peptides_by_id_success(
    client: TestClient, setup_digest_with_peptides: tuple[str, str]
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
