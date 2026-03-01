"""
Integration tests for the digest endpoint.
Tests the full flow without patching.
"""

from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import asc
from sqlalchemy.orm import Session

from app.domain import ProteinDomain
from app.enums import CriteriaEnum, DigestStatusEnum, ProteaseEnum
from app.models import Digest, DigestCriteria, Peptide, PeptideCriteria
from tests.factories import UserFactory


@pytest.mark.integration
def test_create_digest_job_integration(
    universal_protein: ProteinDomain,
    client: TestClient,
    db_session: Session,
) -> None:
    """Test creating a digest job with real database operations."""
    # setup
    user = UserFactory.create()
    user_id = user.id

    request_data = {
        "user_id": user_id,
        "protease": ProteaseEnum.TRYPSIN.value,
        "protein_name": "Test Protein",
        "sequence": universal_protein.sequence_as_str,
    }

    def get_test_session():
        return db_session

    # execute
    with (patch("app.tasks.digest_task.SessionLocal") as mock_session_local,):
        mock_session_local.return_value = db_session

        response = client.post(
            "/api/v1/digest/job",
            json=request_data,
        )

    # validate
    assert response.status_code == 201
    data = response.json()
    assert "digest_id" in data
    digest_id = data["digest_id"]

    db_session.expire_all()

    digest = db_session.query(Digest).filter(Digest.id == digest_id).first()
    assert digest is not None

    db_session.refresh(digest)

    assert digest.status == DigestStatusEnum.COMPLETED
    assert digest.user_id == user_id
    assert digest.protein_name == "Test Protein"
    assert digest.sequence == universal_protein.sequence_as_str
    assert digest.protease == ProteaseEnum.TRYPSIN

    peptides = (
        db_session.query(Peptide)
        .filter(Peptide.digest_id == digest_id)
        .order_by(asc(Peptide.rank))
        .all()
    )

    assert len(peptides) == 3

    expected_bad_peptide_criteria = {
        CriteriaEnum.CONTAINS_MISSED_CLEAVAGES,
        CriteriaEnum.CONTAINS_ASPARAGINE_GLYCINE_MOTIF,
        CriteriaEnum.LACKING_FLANKING_AMINO_ACIDS,
        CriteriaEnum.OUTLIER_LENGTH,
        CriteriaEnum.CONTAINS_CYSTEINE,
        CriteriaEnum.CONTAINS_LONG_HOMOPOLYMERIC_STRETCH,
        CriteriaEnum.CONTAINS_METHIONINE,
        CriteriaEnum.OUTLIER_CHARGE_STATE,
        CriteriaEnum.NOT_UNIQUE,
        CriteriaEnum.OUTLIER_HYDROPHOBICITY,
        CriteriaEnum.CONTAINS_N_TERMINAL_GLUTAMINE_MOTIF,
        CriteriaEnum.CONTAINS_ASPARTIC_PROLINE_MOTIF,
    }

    for i, peptide in enumerate(peptides):
        assert peptide.rank is not None and peptide.rank == (i + 1)
        assert peptide.pi is not None and isinstance(peptide.pi, float)
        assert peptide.charge_state is not None and isinstance(
            peptide.charge_state, int
        )
        assert peptide.max_kd_score is not None and isinstance(
            peptide.max_kd_score, float
        )

        criteria = (
            db_session.query(PeptideCriteria)
            .filter(PeptideCriteria.peptide_id == peptide.id)
            .all()
        )

        criteria_codes = {c.criteria.code for c in criteria}

        if i in {1, 2}:
            assert criteria_codes == expected_bad_peptide_criteria
        elif i == 0:
            assert criteria_codes == {CriteriaEnum.OUTLIER_HYDROPHOBICITY}


@pytest.mark.integration
def test_create_digest_job_invalid_criteria_ids_returns_400(
    universal_protein: ProteinDomain,
    client: TestClient,
    db_session: Session,
) -> None:
    """When criteria_ids contains an id not in the criteria table, request fails with 400."""
    # setup
    user = UserFactory.create()
    invalid_criteria_id = "00000000-0000-0000-0000-000000000000"

    request_data = {
        "user_id": user.id,
        "protease": ProteaseEnum.TRYPSIN.value,
        "protein_name": "Test Protein",
        "sequence": universal_protein.sequence_as_str,
        "criteria_ids": [invalid_criteria_id],
    }

    # execute
    response = client.post(
        "/api/v1/digest/job",
        json=request_data,
    )

    # validate:
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "Invalid criteria_id" in data["detail"]
    assert invalid_criteria_id in data["detail"]

    digest_count = db_session.query(Digest).filter(Digest.user_id == user.id).count()
    assert digest_count == 0


@pytest.mark.skip
@pytest.mark.integration
def test_create_digest_job_no_criteria_ids_uses_all_criteria(
    universal_protein: ProteinDomain,
    client: TestClient,
    db_session: Session,
    seeded_criteria: list,
) -> None:
    """When criteria_ids is empty, digest gets all criteria and peptides are evaluated with all."""
    user = UserFactory.create()
    request_data = {
        "user_id": user.id,
        "protease": ProteaseEnum.TRYPSIN.value,
        "protein_name": "Test Protein",
        "sequence": universal_protein.sequence_as_str,
        "criteria_ids": [],
    }

    with patch("app.tasks.digest_task.SessionLocal", return_value=db_session):
        response = client.post("/api/v1/digest/job", json=request_data)

    assert response.status_code == 201
    digest_id = response.json()["digest_id"]
    db_session.expire_all()

    digest = db_session.query(Digest).filter(Digest.id == digest_id).first()
    assert digest is not None
    db_session.refresh(digest)

    digest_criteria_rows = (
        db_session.query(DigestCriteria)
        .filter(DigestCriteria.digest_id == digest_id)
        .all()
    )
    assert len(digest_criteria_rows) == len(seeded_criteria)
    digest_codes = {dc.criteria_code for dc in digest_criteria_rows}
    assert digest_codes == {c.code.value for c in seeded_criteria}

    peptides = (
        db_session.query(Peptide)
        .filter(Peptide.digest_id == digest_id)
        .order_by(asc(Peptide.rank))
        .all()
    )
    assert len(peptides) == 3
    for peptide in peptides:
        peptide_criteria = (
            db_session.query(PeptideCriteria)
            .filter(PeptideCriteria.peptide_id == peptide.id)
            .all()
        )
        assert len(peptide_criteria) > 0


@pytest.mark.integration
def test_create_digest_job_all_criteria_ids_uses_all_criteria(
    universal_protein: ProteinDomain,
    client: TestClient,
    db_session: Session,
    seeded_criteria: list,
) -> None:
    """When criteria_ids contains all criterion IDs, digest gets all criteria and peptides evaluated with all."""
    user = UserFactory.create()
    all_ids = [c.id for c in seeded_criteria]
    request_data = {
        "user_id": user.id,
        "protease": ProteaseEnum.TRYPSIN.value,
        "protein_name": "Test Protein",
        "sequence": universal_protein.sequence_as_str,
        "criteria_ids": all_ids,
    }
    expected_all_codes = {c.code.value for c in seeded_criteria}

    with patch("app.tasks.digest_task.SessionLocal", return_value=db_session):
        response = client.post("/api/v1/digest/job", json=request_data)

    assert response.status_code == 201
    digest_id = response.json()["digest_id"]
    db_session.expire_all()

    digest = db_session.query(Digest).filter(Digest.id == digest_id).first()
    assert digest is not None
    db_session.refresh(digest)

    digest_criteria_rows = (
        db_session.query(DigestCriteria)
        .filter(DigestCriteria.digest_id == digest_id)
        .all()
    )
    assert len(digest_criteria_rows) == len(seeded_criteria)
    digest_codes = {dc.criteria_code for dc in digest_criteria_rows}
    assert digest_codes == expected_all_codes

    peptides = (
        db_session.query(Peptide)
        .filter(Peptide.digest_id == digest_id)
        .order_by(asc(Peptide.rank))
        .all()
    )
    assert len(peptides) == 3
    for peptide in peptides:
        peptide_criteria = (
            db_session.query(PeptideCriteria)
            .filter(PeptideCriteria.peptide_id == peptide.id)
            .all()
        )
        assert len(peptide_criteria) > 0


@pytest.mark.skip
@pytest.mark.integration
def test_create_digest_job_subset_criteria_ids_uses_only_those_criteria(
    universal_protein: ProteinDomain,
    client: TestClient,
    db_session: Session,
    seeded_criteria: list,
) -> None:
    """When criteria_ids contains a subset, digest gets only those criteria and peptides evaluated only against them."""
    user = UserFactory.create()
    subset_size = 3
    subset = seeded_criteria[:subset_size]
    subset_ids = [c.id for c in subset]
    allowed_codes = {c.code.value for c in subset}

    request_data = {
        "user_id": user.id,
        "protease": ProteaseEnum.TRYPSIN.value,
        "protein_name": "Test Protein",
        "sequence": universal_protein.sequence_as_str,
        "criteria_ids": subset_ids,
    }

    with patch("app.tasks.digest_task.SessionLocal", return_value=db_session):
        response = client.post("/api/v1/digest/job", json=request_data)

    assert response.status_code == 201
    digest_id = response.json()["digest_id"]
    db_session.expire_all()

    digest = db_session.query(Digest).filter(Digest.id == digest_id).first()
    assert digest is not None
    db_session.refresh(digest)

    digest_criteria_rows = (
        db_session.query(DigestCriteria)
        .filter(DigestCriteria.digest_id == digest_id)
        .all()
    )
    assert len(digest_criteria_rows) == subset_size
    digest_codes = {dc.criteria_code for dc in digest_criteria_rows}
    assert digest_codes == allowed_codes

    peptides = (
        db_session.query(Peptide)
        .filter(Peptide.digest_id == digest_id)
        .order_by(asc(Peptide.rank))
        .all()
    )
    assert len(peptides) == 3
    for peptide in peptides:
        peptide_criteria = (
            db_session.query(PeptideCriteria)
            .filter(PeptideCriteria.peptide_id == peptide.id)
            .all()
        )
        for pc in peptide_criteria:
            assert pc.criteria.code.value in allowed_codes
