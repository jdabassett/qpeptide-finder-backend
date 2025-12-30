import logging

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.domain import ProteinDomain
from app.enums import DigestStatusEnum
from app.helpers import (
    create_record,
    get_record_or_exception,
    request_outside_digest_interval_or_exception,
    request_within_digest_limit_or_exception,
)
from app.models import Digest, User
from app.schemas.digest import DigestJobRequest, DigestJobResponse
from app.tasks import process_digest_job

logger = logging.getLogger(__name__)

digest_router = APIRouter(prefix="/digests", tags=["digests"])


@digest_router.post(
    "/jobs",
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

    user = get_record_or_exception(session, User, email=job_request.user_email)

    request_within_digest_limit_or_exception(user.id, session)

    request_outside_digest_interval_or_exception(user.id, session)

    logger.debug(f"Digest checks passed for user_email={job_request.user_email}")

    try:
        digest: Digest = create_record(
            session,
            Digest,
            status=DigestStatusEnum.PROCESSING,
            user_id=user.id,
            protease=job_request.protease,
            protein_name=job_request.protein_name,
            sequence=job_request.sequence,
            flush=True,
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
    except Exception as e:
        logger.exception(
            f"Unexpected error in create_digest_job: user_email={job_request.user_email}, "
            f"error={str(e)}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred while creating digest job: {str(e)}",
        ) from e
