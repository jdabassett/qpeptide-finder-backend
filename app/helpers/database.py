"""
Database helper functions for common database operations.
"""

from typing import TypeVar

from fastapi import HTTPException, status
from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from app.models import User

# Type variable for SQLAlchemy models
T = TypeVar("T")


def get_user_by_email(email: str, session: Session) -> User | None:
    """
    Get a user by email address, returning None if not found.

    Use this when you need to check if a user exists without raising an exception.
    Use find_user() when the user must exist (e.g., for validation).

    Args:
        email: Email address of the user
        session: Database session

    Returns:
        User if found, None otherwise
    """
    user_query: Select = select(User).where(User.email == email)
    result = session.scalar(user_query)
    return result if isinstance(result, User) else None


def get_user_by_email_or_exception(email: str, session: Session) -> User:
    """
    Find a user by email address or raise exception.

    Args:
        email: Email address of the user
        session: Database session

    Returns:
        User: The found user

    Raises:
        HTTPException: 404 if user not found
    """

    user: User | None = get_user_by_email(email, session)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with email {email} not found.",
        )

    return user


def create_new_record(  # noqa: UP047
    session: Session,
    model_class: type[T],
    *,
    flush: bool = False,
    refresh: bool = True,
    **kwargs,
) -> T:
    """
    Create a new database record from a model class and keyword arguments.

    Args:
        session: Database session to use for the operation
        model_class: The SQLAlchemy model class to instantiate
        flush: If True, flush to DB before commit.
        refresh: If True, refresh the instance from DB after commit to
            ensure all database-generated fields
        **kwargs: Keyword arguments to pass to the model constructor.
            Must match the model's field names.

    Returns:
        The created model instance. If refresh=True, the instance will have all database-generated fields populated (e.g., id, created_at).

    Raises:
        IntegrityError: If a database constraint violation occurs
        TypeError: If invalid kwargs are provided to the model constructor
        ValueError: If model validation fails

    """
    if not kwargs:
        raise ValueError(
            f"Cannot create {model_class.__name__} record: no keyword arguments provided"
        )

    instance = model_class(**kwargs)
    session.add(instance)

    if flush:
        session.flush()

    session.commit()

    if refresh:
        session.refresh(instance)

    return instance
