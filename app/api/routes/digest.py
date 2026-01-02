import logging

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from pydantic import ValidationError
from sqlalchemy.exc import DatabaseError, IntegrityError, OperationalError
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.domain import ProteinDomain
from app.enums import DigestStatusEnum
from app.helpers import (
    request_outside_digest_interval_or_exception,
    request_within_digest_limit_or_exception,
)
from app.models import Criteria, Digest, Peptide, User
from app.schemas.digest import (
    DigestJobRequest,
    DigestJobResponse,
    DigestListResponse,
    DigestPeptidesResponse,
    DigestResponse,
)
from app.tasks import process_digest_job

logger = logging.getLogger(__name__)

digest_router = APIRouter(prefix="/digest", tags=["digest"])


@digest_router.post(
    "/job",
    response_model=DigestJobResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_digest_job(
    job_request: DigestJobRequest,
    background_tasks: BackgroundTasks,
    session: Session = Depends(get_db),
):
    """
    Create a new digest job.

    Returns the digest job ID.
    """
    logger.info(f"Received digest job request: user_id={job_request.user_id}")

    user: User = User.find_one_by_or_raise(session, id=job_request.user_id)
    request_within_digest_limit_or_exception(user.id, session)
    request_outside_digest_interval_or_exception(user.id, session)

    logger.debug(f"Digest checks passed for user_id={job_request.user_id}")

    try:
        digest: Digest = Digest.create(
            session,
            flush=True,
            status=DigestStatusEnum.PROCESSING,
            user_id=user.id,
            protease=job_request.protease,
            protein_name=job_request.protein_name,
            sequence=job_request.sequence,
        )

        protein_domain: ProteinDomain = ProteinDomain.from_digest(digest)
        background_tasks.add_task(process_digest_job, protein_domain)

        logger.info(
            f"Background task queued for digest_id={digest.id} and user_id={job_request.user_id}"
        )

        return DigestJobResponse(
            digest_id=digest.id,
        )
    except IntegrityError as e:
        logger.error(
            f"Database constraint violation while creating digest job: "
            f"user_id={job_request.user_id}, error={str(e)}"
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create digest job due to database constraint violation. Error: {str(e)}",
        ) from e
    except ValueError as e:
        logger.error(
            f"Invalid digest job data: user_id={job_request.user_id}, error={str(e)}"
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid digest job data: {str(e)}",
        ) from e


@digest_router.get(
    "/list/{user_id}",
    response_model=DigestListResponse,
    status_code=status.HTTP_200_OK,
)
def get_digests_by_id(
    user_id: str,
    session: Session = Depends(get_db),
):
    """
    Get all digests for a user by id.

    - user_id: User's id
    - Returns list of digests (without peptides or peptide_criteria)
    """
    logger.info(f"Received digest list request: user_id={user_id}")

    digests: list[Digest] = Digest.find_by(session, user_id=user_id)

    logger.info(f"Found {len(digests)} digests for user_id={user_id}")

    return DigestListResponse(
        digests=[DigestResponse.model_validate(digest) for digest in digests]
    )


@digest_router.delete(
    "/delete/{user_id}/{digest_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_digest_by_id(
    user_id: str,
    digest_id: str,
    session: Session = Depends(get_db),
):
    """
    Delete a digest by ID for a specific user.

    - user_id: User's id
    - digest_id: Digest ID to delete
    - Returns 204 No Content on success
    - Returns 404 if user or digest not found, or if digest doesn't belong to user
    """
    logger.info(
        f"Received digest delete request: user_id={user_id}, digest_id={digest_id}"
    )

    digest: Digest = Digest.find_one_by_or_raise(
        session,
        user_id=user_id,
        id=digest_id,
    )

    try:
        Digest.delete(session, digest)
        logger.info(
            f"Successfully deleted digest: user_id={user_id}, digest_id={digest_id}"
        )
        return
    except IntegrityError as e:
        logger.error(
            f"Database constraint violation while deleting digest: "
            f"user_id={user_id}, digest_id={digest_id}, error={str(e)}"
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to delete digest due to database constraint violation. Error: {str(e)}",
        ) from e


@digest_router.get(
    "/{user_id}/{digest_id}/peptides",
    status_code=status.HTTP_200_OK,
)
def get_digest_peptides_by_id(
    user_id: str,
    digest_id: str,
    session: Session = Depends(get_db),
):
    """
    Get digest peptides by ID for a specific user.

    - user_id: User's id
    - digest_id: Digest ID
    """
    logger.info(f"Received peptides request: user_id={user_id}, digest_id={digest_id}")

    try:
        User.find_one_by_or_raise(
            session,
            id=user_id,
        )

        digest: Digest = Digest.find_one_by_or_raise(
            session,
            user_id=user_id,
            id=digest_id,
        )

        peptides: list[Peptide] = Peptide.find_by_digest_id_ordered_by_rank_or_raise(
            session,
            digest_id=digest_id,
        )

        all_criteria = Criteria.get_all_ordered_by_rank(session)

        response = DigestPeptidesResponse.from_peptides(
            digest.id, peptides, all_criteria
        )

        logger.info(
            f"Successfully returned peptides request: user_id={user_id}, digest_id={digest_id} number={len(peptides)}"
        )

        return response

    except HTTPException:
        # Re-raise HTTPExceptions (404s from find_one_by_or_raise methods)
        # These should pass through unchanged
        raise
    except (DatabaseError, OperationalError) as e:
        logger.error(
            f"Database error getting peptides: user_id={user_id}, "
            f"digest_id={digest_id}, error={str(e)}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="A database error occurred while retrieving peptides. Please try again later.",
        ) from e

    except ValidationError as e:
        logger.error(
            f"Data validation error building response: user_id={user_id}, "
            f"digest_id={digest_id}, error={str(e)}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while formatting the response. Please contact support.",
        ) from e
    except AttributeError as e:
        logger.error(
            f"Missing relationship data: user_id={user_id}, "
            f"digest_id={digest_id}, error={str(e)}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing peptide data. Please contact support.",
        ) from e
    except Exception as e:
        logger.error(
            f"Unexpected error getting peptides: user_id={user_id}, "
            f"digest_id={digest_id}, error={str(e)}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while retrieving peptides. Please try again later.",
        ) from e
