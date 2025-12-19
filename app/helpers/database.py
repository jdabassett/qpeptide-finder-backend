"""
Database helper functions for common database operations.
"""

from typing import TypeVar

from fastapi import HTTPException, status
from sqlalchemy import Select, select
from sqlalchemy.orm import Session

# Type variable for SQLAlchemy models
T = TypeVar("T")


def get_record(  # noqa: UP047
    session: Session,
    model_class: type[T],
    **kwargs,
) -> T | None:
    """
    Get a single record from a table matching the given criteria.

    Args:
        session: Database session
        model_class: The SQLAlchemy model class to query
        **kwargs: Keyword arguments representing field=value pairs to match.

    Returns:
        The found record if exists, None otherwise
    """
    if not kwargs:
        raise ValueError(
            f"Cannot query {model_class.__name__}: no search criteria provided"
        )

    query: Select = select(model_class)

    for key, value in kwargs.items():
        if not hasattr(model_class, key):
            raise AttributeError(f"{model_class.__name__} has no attribute '{key}'")
        column = getattr(model_class, key)
        query = query.where(column == value)

    result = session.scalar(query)
    return result if isinstance(result, model_class) else None


def get_record_or_exception(  # noqa: UP047
    session: Session,
    model_class: type[T],
    **kwargs,
) -> T:
    """
    Get a single record from a table matching the given criteria, or raise exception.

    Args:
        session: Database session
        model_class: The SQLAlchemy model class to query
        **kwargs: Keyword arguments representing field=value pairs to match.

    Returns:
        The found record

    Raises:
        HTTPException: 404 if record not found
        ValueError: If no search criteria provided
        AttributeError: If invalid field names provided
    """
    record = get_record(session, model_class, **kwargs)

    if not record:
        criteria = ", ".join(f"{k}={v!r}" for k, v in kwargs.items())
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{model_class.__name__} with {criteria} not found.",
        )

    return record


def create_record(  # noqa: UP047
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

    try:
        session.commit()
    except Exception:
        session.rollback()
        raise

    if refresh:
        session.refresh(instance)

    return instance


def update_record(  # noqa: UP047
    session: Session,
    record: T,
    *,
    refresh: bool = True,
    **kwargs,
) -> T:
    """
    Update an existing database record with keyword arguments.

    Args:
        session: Database session to use for the operation
        record: The existing model instance to update
        refresh: If True, refresh the instance from DB after commit to
            ensure all database-generated fields are up-to-date.
        **kwargs: Keyword arguments representing fields to update.
            Must match the model's field names.

    Returns:
        The updated model instance.

    Raises:
        IntegrityError: If a database constraint violation occurs
        AttributeError: If invalid field names are provided in kwargs
        ValueError: If model validation fails
    """
    if not kwargs:
        raise ValueError(
            f"Cannot update {type(record).__name__} record: no keyword arguments provided"
        )

    for key, value in kwargs.items():
        if not hasattr(record, key):
            raise AttributeError(f"{type(record).__name__} has no attribute '{key}'")
        setattr(record, key, value)

    try:
        session.commit()
    except Exception:
        session.rollback()
        raise

    if refresh:
        session.refresh(record)

    return record


def delete_record(  # noqa: UP047
    session: Session,
    record: T,
) -> None:
    """
    Delete a database record.

    Args:
        session: Database session to use for the operation
        record: The model instance to delete (must be attached to session)

    Returns:
        None

    Raises:
        IntegrityError: If a database constraint violation occurs
    """
    session.delete(record)

    try:
        session.commit()
    except Exception:
        session.rollback()
        raise
