from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.enums import DigestStatusEnum
from app.helpers import (
    create_new_record,
    get_user_by_email_or_exception,
    request_outside_digest_interval_or_exception,
    request_within_digest_limit_or_exception,
)
from app.models import Digest
from app.schemas.digest import DigestJobRequest, DigestJobResponse

digest_router = APIRouter(prefix="/digests", tags=["digests"])


@digest_router.post(
    "/jobs",
    response_model=DigestJobResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_digest_job(
    job_request: DigestJobRequest, session: Session = Depends(get_db)
):
    """
    Create a new digest job.

    - user_email: Email address of the user
    - protein: Protein information (name, sequence)
    - digest: Digest configuration (proteases)

    Returns the digest job ID and status.
    """
    user = get_user_by_email_or_exception(job_request.user_email, session)

    request_within_digest_limit_or_exception(user.id, session)

    request_outside_digest_interval_or_exception(user.id, session)

    try:
        digest = create_new_record(
            session,
            Digest,
            status=DigestStatusEnum.PROCESSING,
            user_id=user.id,
            protease=job_request.protease,
            protein_name=job_request.protein_name,
            sequence=job_request.sequence_to_str(),
            flush=True,
        )

        # TODO: generate backgroud task here

        return DigestJobResponse(
            digest_id=digest.id,
        )
    except IntegrityError as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create digest job due to database constraint violation. Error: {str(e)}",
        ) from e
    except ValueError as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid digest job data: {str(e)}",
        ) from e
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred while creating digest job: {str(e)}",
        ) from e
