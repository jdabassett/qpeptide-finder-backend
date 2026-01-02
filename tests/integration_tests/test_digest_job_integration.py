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
from app.models import Digest, Peptide, PeptideCriteria
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
    with (
        patch("app.api.routes.digest.request_outside_digest_interval_or_exception"),
        patch("app.tasks.digest_task.SessionLocal") as mock_session_local,
    ):
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
