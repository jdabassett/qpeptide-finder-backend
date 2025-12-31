"""
Database helper functions for common database operations.
"""

import logging
from collections.abc import Sequence

from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from app.domain import PeptideDomain
from app.enums import CriteriaEnum
from app.models import Criteria, Peptide, PeptideCriteria

logger = logging.getLogger(__name__)


def save_peptides_with_criteria(
    session: Session,
    digest_id: str,
    peptides: Sequence[PeptideDomain],
) -> None:
    """
    Save peptides and their criteria associations to the database.

    Args:
        session: Database session
        digest_id: ID of the digest these peptides belong to
        peptides: Sequence of PeptideDomain objects to save

    Raises:
        ValueError: If a Criteria record is not found for a CriteriaEnum
        IntegrityError: If database constraints are violated
    """
    if not peptides:
        logger.info(f"No peptides to save for digest_id: {digest_id}")
        return

    criteria_map = _get_criteria_map(session, peptides)

    try:
        for peptide_domain in peptides:
            peptide_domain.get_pI()
            peptide_domain.charge_state_in_formic_acid()
            peptide_domain.max_kyte_dolittle_score_over_sliding_window()

            peptide: Peptide = Peptide.create(
                session,
                digest_id=digest_id,
                sequence=peptide_domain.sequence_as_str,
                position=peptide_domain.position,
                pi=peptide_domain.pI,
                charge_state=peptide_domain.charge_state,
                max_kd_score=peptide_domain.max_kd_score,
                flush=True,
                refresh=True,
                commit=False,
            )

            for criteria_enum in peptide_domain.criteria:
                criteria_record = criteria_map.get(criteria_enum)
                if not criteria_record:
                    raise ValueError(
                        f"Criteria record not found for {criteria_enum.value}. "
                        "Ensure all criteria are seeded in the database."
                    )

                PeptideCriteria.create(
                    session,
                    peptide_id=peptide.id,
                    criteria_id=criteria_record.id,
                    flush=False,
                    refresh=False,
                    commit=False,
                )

        session.commit()

        logger.info(
            f"Successfully saved {len(peptides)} peptides with criteria for digest_id: {digest_id}"
        )

        return

    except Exception:
        session.rollback()
        raise


def _get_criteria_map(
    session: Session, peptides: Sequence[PeptideDomain]
) -> dict[CriteriaEnum, Criteria]:
    """
    Build a map of CriteriaEnum to Criteria records for efficient lookup.

    Args:
        session: Database session
        peptides: Sequence of peptides to extract criteria from

    Returns:
        Dictionary mapping CriteriaEnum to Criteria records
    """
    criteria_enums = set()
    for peptide in peptides:
        criteria_enums.update(peptide.criteria)

    if not criteria_enums:
        return {}

    query: Select = select(Criteria).where(Criteria.code.in_(criteria_enums))
    criteria_records = session.scalars(query).all()

    criteria_map = {record.code: record for record in criteria_records}
    missing = criteria_enums - set(criteria_map.keys())

    if missing:
        logger.warning(
            f"Some criteria not found in database: {[ce.value for ce in missing]}"
        )

    return criteria_map
