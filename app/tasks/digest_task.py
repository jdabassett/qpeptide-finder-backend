"""
Background task for processing digest jobs.
"""

import logging
import time

from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.domain import ProteinDomain
from app.enums import DigestStatusEnum
from app.helpers import save_peptides_with_criteria
from app.models import Digest
from app.services import (
    ContainsAsparagineGlycineMotifFilter,
    ContainsAsparticProlineMotifFilter,
    ContainsCysteineFilter,
    ContainsLongHomopolymericStretchFilter,
    ContainsMethionineFilter,
    ContainsMissedCleavagesFilter,
    ContainsNTerminalGlutamineMotifFilter,
    CriteriaEvaluator,
    HasFlankingCutSitesFilter,
    LackingFlankingAminoAcidsFilter,
    NotUniqueFilter,
    OutlierChargeStateFilter,
    OutlierHydrophobicityFilter,
    OutlierLengthFilter,
    OutlierPIFilter,
)

logger = logging.getLogger(__name__)


def create_default_criteria_evaluator() -> CriteriaEvaluator:
    """Create a default criteria evaluator with standard filters."""
    filters = [
        ContainsAsparagineGlycineMotifFilter(),
        ContainsAsparticProlineMotifFilter(),
        ContainsCysteineFilter(),
        ContainsLongHomopolymericStretchFilter(),
        ContainsMethionineFilter(),
        ContainsMissedCleavagesFilter(),
        ContainsNTerminalGlutamineMotifFilter(),
        HasFlankingCutSitesFilter(),
        LackingFlankingAminoAcidsFilter(),
        NotUniqueFilter(),
        OutlierChargeStateFilter(),
        OutlierHydrophobicityFilter(),
        OutlierLengthFilter(),
        OutlierPIFilter(),
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
        digest: Digest | None = Digest.find_one_by(session, id=protein_domain.digest_id)

        if not digest:
            logger.error(
                f"Digest with id {protein_domain.digest_id} not found. "
                "Cannot process digest job."
            )
            return

        protein_domain.digest_sequence()

        logger.info(f"Digested protein for digest_id: {protein_domain.digest_id}")

        evaluator = create_default_criteria_evaluator()

        num_peptides_before = len(protein_domain.peptides)
        filter_start_time = time.perf_counter()
        evaluator.evaluate_peptides(protein_domain)
        filter_duration = time.perf_counter() - filter_start_time

        logger.info(
            f"Filtered all peptides for digest_id: {protein_domain.digest_id} - "
            f"processed {num_peptides_before} peptides through {len(evaluator.filters)} filters "
            f"in {filter_duration:.4f} seconds"
        )

        save_peptides_with_criteria(
            session=session,
            digest_id=protein_domain.digest_id,
            peptides=protein_domain.peptides,
        )

        logger.info(f"Saved all peptides for digest_id: {protein_domain.digest_id}")

        Digest.update(
            session,
            digest,
            values={"status": DigestStatusEnum.COMPLETED},
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
            if digest is not None:
                Digest.update(
                    session,
                    digest,
                    values={"status": DigestStatusEnum.FAILED},
                )
        except Exception as update_error:
            logger.error(
                f"Failed to update digest status to FAILED for "
                f"digest_id: {protein_domain.digest_id}. Error: {str(update_error)}",
                exc_info=True,
            )

    finally:
        session.close()
