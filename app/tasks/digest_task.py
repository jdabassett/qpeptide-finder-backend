"""
Background task for processing digest jobs.
"""

import logging

from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.domain import ProteinDomain
from app.enums import DigestStatusEnum
from app.helpers import save_peptides_with_criteria
from app.helpers.database import get_record, update_record
from app.models import Digest
from app.services import (
    AvoidCysteineFilter,
    AvoidFlankingCutSitesFilter,
    AvoidMethionineFilter,
    CriteriaEvaluator,
    NoAsparagineGlycineMotifFilter,
    NoAsparticProlineMotifFilter,
    PeptideLengthFilter,
    UniqueSequenceFilter,
)

logger = logging.getLogger(__name__)


def create_default_criteria_evaluator() -> CriteriaEvaluator:
    """Create a default criteria evaluator with standard filters."""
    filters = [
        PeptideLengthFilter(),
        AvoidMethionineFilter(),
        AvoidCysteineFilter(),
        NoAsparagineGlycineMotifFilter(),
        NoAsparticProlineMotifFilter(),
        UniqueSequenceFilter(),
        AvoidFlankingCutSitesFilter(),
    ]
    return CriteriaEvaluator(filters)


def process_digest_job(protein_domain: ProteinDomain) -> None:
    """
    Background task to process a digest job.

    Args:
        protein_domain: ProteinDomain object containing digest information

    Raises:
        Exception: If digest processing fails, the digest status will be
            updated to FAILED and the exception will be logged.
    """
    session: Session = SessionLocal()
    try:
        logger.info(
            f"Starting digest job processing for digest_id: {protein_domain.digest_id}"
        )

        digest = get_record(session, Digest, id=protein_domain.digest_id)

        if not digest:
            logger.error(
                f"Digest with id {protein_domain.digest_id} not found. "
                "Cannot process digest job."
            )
            return

        protein_domain.digest_sequence()

        logger.info(f"Digested protein for digest_id: {protein_domain.digest_id}")

        evaluator = create_default_criteria_evaluator()
        evaluator.evaluate_peptides(protein_domain)

        logger.info(f"Filtered all peptides for digest_id: {protein_domain.digest_id}")

        save_peptides_with_criteria(
            session=session,
            digest_id=protein_domain.digest_id,
            peptides=protein_domain.peptides,
        )

        logger.info(f"Saved all peptides for digest_id: {protein_domain.digest_id}")

        update_record(
            session,
            digest,
            status=DigestStatusEnum.COMPLETED,
            refresh=True,
        )

        logger.info(
            f"Successfully completed digest job for digest_id: {protein_domain.digest_id}"
        )

    except Exception as e:
        logger.error(
            f"Error processing digest job for digest_id: {protein_domain.digest_id}. "
            f"Error: {str(e)}",
            exc_info=True,
        )

        try:
            digest = get_record(session, Digest, id=protein_domain.digest_id)
            if digest:
                update_record(
                    session,
                    digest,
                    status=DigestStatusEnum.FAILED,
                    refresh=True,
                )
        except Exception as update_error:
            logger.error(
                f"Failed to update digest status to FAILED for "
                f"digest_id: {protein_domain.digest_id}. Error: {str(update_error)}",
                exc_info=True,
            )

    finally:
        session.close()
