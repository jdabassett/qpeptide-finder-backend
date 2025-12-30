# helper functions for the digest route

from fastapi import HTTPException, status
from sqlalchemy import desc, func, select, text
from sqlalchemy.orm import Session

from app.core import settings
from app.models import Digest


def request_within_digest_limit_or_exception(user_id: str, session: Session) -> None:
    """
    Check if user has exceeded the digest job limit.

    Args:
        user_id: User id to search with
        session: Database session

    Raises:
        HTTPException: 400 if user has exceeded the digest job limit
    """
    digest_count: int | None = session.scalar(
        select(func.count(Digest.id)).where(Digest.user_id == user_id)
    )

    if digest_count is None or digest_count >= settings.DIGEST_JOB_LIMIT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"User has more than {settings.DIGEST_JOB_LIMIT} digest jobs. "
                "To keep this a free service we limit the number of user records."
                "Please delete old records before submitting a new digest job."
            ),
        )

    return


def request_outside_digest_interval_or_exception(
    user_id: str, session: Session
) -> None:
    """
    Check if user has submitted a digest job too recently.

    Args:
        user: User to check
        session: Database session

    Raises:
        HTTPException: 429 if user submitted a digest job within the interval
    """
    time_threshold = func.date_sub(
        func.now(), text(f"INTERVAL {settings.DIGEST_JOB_INTERVAL} MINUTE")
    )

    latest_digest = session.scalar(
        select(Digest)
        .where(Digest.user_id == user_id)
        .where(Digest.created_at >= time_threshold)
        .order_by(desc(Digest.created_at))
        .limit(1)
    )

    if latest_digest:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=(
                f"A digest job was submitted less than {settings.DIGEST_JOB_INTERVAL} minutes ago. "
                "To keep this service free we meter the number of jobs per user."
                "Please wait before submitting a new digest job."
            ),
        )

    return
