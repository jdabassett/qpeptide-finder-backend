import logging

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.domain import ProteinDomain
from app.enums import DigestStatusEnum
from app.helpers import (
    request_outside_digest_interval_or_exception,
    request_within_digest_limit_or_exception,
)
from app.models import Digest, User
from app.schemas.digest import (
    DigestJobRequest,
    DigestJobResponse,
    DigestListResponse,
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
    logger.info(f"Received digest job request: user_email={job_request.user_email}")

    user: User = User.find_one_by_or_raise(session, email=job_request.user_email)
    request_within_digest_limit_or_exception(user.id, session)
    request_outside_digest_interval_or_exception(user.id, session)

    logger.debug(f"Digest checks passed for user_email={job_request.user_email}")

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
            f"Background task queued for digest_id={digest.id} and user_email={job_request.user_email}"
        )

        return DigestJobResponse(
            digest_id=digest.id,
        )
    except IntegrityError as e:
        logger.error(
            f"Database constraint violation while creating digest job: "
            f"user_email={job_request.user_email}, error={str(e)}"
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create digest job due to database constraint violation. Error: {str(e)}",
        ) from e
    except ValueError as e:
        logger.error(
            f"Invalid digest job data: user_email={job_request.user_email}, "
            f"error={str(e)}"
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid digest job data: {str(e)}",
        ) from e


@digest_router.get(
    "/list/{email}",
    response_model=DigestListResponse,
    status_code=status.HTTP_200_OK,
)
def get_digests_by_email(
    email: str,
    session: Session = Depends(get_db),
):
    """
    Get all digests for a user by email.

    - email: User's email address
    - Returns list of digests (without peptides or peptide_criteria)
    """
    logger.info(f"Received digest list request: email={email}")

    user: User = User.find_one_by_or_raise(session, email=email)

    digests: list[Digest] = Digest.find_by(session, user_id=user.id)

    logger.info(f"Found {len(digests)} digests for user_email={email}")

    return DigestListResponse(
        digests=[DigestResponse.model_validate(digest) for digest in digests]
    )


@digest_router.delete(
    "/delete/{email}/{digest_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_digest_by_id(
    email: str,
    digest_id: str,
    session: Session = Depends(get_db),
):
    """
    Delete a digest by ID for a specific user.

    - email: User's email address
    - digest_id: Digest ID to delete
    - Returns 204 No Content on success
    - Returns 404 if user or digest not found, or if digest doesn't belong to user
    """
    logger.info(f"Received digest delete request: email={email}, digest_id={digest_id}")

    user: User = User.find_one_by_or_raise(session, email=email)

    digest: Digest = Digest.find_one_by_or_raise(
        session,
        user_id=user.id,
        id=digest_id,
    )

    try:
        Digest.delete(session, digest)
        logger.info(
            f"Successfully deleted digest: email={email}, digest_id={digest_id}"
        )
        return
    except IntegrityError as e:
        logger.error(
            f"Database constraint violation while deleting digest: "
            f"email={email}, digest_id={digest_id}, error={str(e)}"
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to delete digest due to database constraint violation. Error: {str(e)}",
        ) from e
