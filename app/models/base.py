import logging
from datetime import UTC, datetime
from typing import Self
from uuid import uuid4

from fastapi import HTTPException, status
from sqlalchemy import DateTime, Select, String, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column

logger = logging.getLogger(__name__)


class Base(DeclarativeBase):
    pass


class QueryMixin:
    """Mixin class providing query methods for models."""

    @classmethod
    def create(
        cls,
        session: Session,
        *,
        flush: bool = False,
        refresh: bool = True,
        commit: bool = True,
        **kwargs,
    ) -> Self:
        """
        Create a new database record.

        Args:
            session: Database session to use for the operation
            flush: If True, flush to DB before commit.
            refresh: If True, refresh the instance from DB after commit to
                ensure all database-generated fields are populated.
            commit: If True, commit the transaction. If False, only add to session.
            **kwargs: Keyword arguments to pass to the model constructor.
                Must match the model's field names.

        Returns:
            The created model instance. If refresh=True, the instance will have all
            database-generated fields populated (e.g., id, created_at).

        Raises:
            IntegrityError: If a database constraint violation occurs
            TypeError: If invalid kwargs are provided to the model constructor
            ValueError: If model validation fails or no kwargs provided
        """
        if not kwargs:
            raise ValueError(
                f"Cannot create {cls.__name__} record: no keyword arguments provided"
            )

        instance = cls(**kwargs)
        session.add(instance)

        if flush:
            session.flush()

        if commit:
            try:
                session.commit()
            except Exception:
                session.rollback()
                raise

        if refresh:
            session.refresh(instance)

        return instance

    @classmethod
    def find_by(
        cls,
        session: Session,
        **kwargs,
    ) -> list[Self]:
        """
        Find all records matching the given criteria.

        Args:
            session: Database session
            **kwargs: Keyword arguments representing field=value pairs to match.

        Returns:
            List of matching records (can be empty)

        Raises:
            ValueError: If no search criteria provided
            AttributeError: If invalid field names provided
        """
        if not kwargs:
            raise ValueError(
                f"Cannot query {cls.__name__}: no search criteria provided"
            )

        query: Select = select(cls)

        for key, value in kwargs.items():
            if not hasattr(cls, key):
                raise AttributeError(f"{cls.__name__} has no attribute '{key}'")
            column = getattr(cls, key)
            query = query.where(column == value)

        results = session.scalars(query).all()
        return list(results)

    @classmethod
    def find_by_or_raise(
        cls,
        session: Session,
        **kwargs,
    ) -> list[Self]:
        """
        Find all records matching the given criteria, or raise exception if none found.

        Args:
            session: Database session
            **kwargs: Keyword arguments representing field=value pairs to match.

        Returns:
            List of matching records (guaranteed to be non-empty)

        Raises:
            HTTPException: 404 if no records found
            ValueError: If no search criteria provided
            AttributeError: If invalid field names provided
        """
        records = cls.find_by(session, **kwargs)

        if not records:
            criteria = ", ".join(f"{k}={v!r}" for k, v in kwargs.items())
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No {cls.__name__} records found with {criteria}.",
            )

        return records

    @classmethod
    def find_one_by(
        cls,
        session: Session,
        **kwargs,
    ) -> Self | None:
        """
        Find a single record matching the given criteria.

        Args:
            session: Database session
            **kwargs: Keyword arguments representing field=value pairs to match.

        Returns:
            The found record if exists, None otherwise

        Raises:
            ValueError: If no search criteria provided
            AttributeError: If invalid field names provided
        """
        records = cls.find_by(session, **kwargs)
        return records[0] if records else None

    @classmethod
    def find_one_by_or_raise(
        cls,
        session: Session,
        **kwargs,
    ) -> Self:
        """
        Find a single record matching the given criteria, or raise exception if not found.

        Args:
            session: Database session
            **kwargs: Keyword arguments representing field=value pairs to match.

        Returns:
            The found record

        Raises:
            HTTPException: 404 if record not found
            ValueError: If no search criteria provided
            AttributeError: If invalid field names provided
        """
        records = cls.find_by_or_raise(session, **kwargs)

        if len(records) > 1:
            criteria = ", ".join(f"{k}={v!r}" for k, v in kwargs.items())
            logger.warning(
                f"Multiple {cls.__name__} records found with {criteria}. "
                f"Returning first result."
            )

        return records[0]

    @classmethod
    def delete(
        cls,
        session: Session,
        record: Self,
    ) -> None:
        """
        Delete a record instance.

        Args:
            session: Database session
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

    @classmethod
    def update(
        cls,
        session: Session,
        record: Self,
        *,
        values: dict,
        refresh: bool = True,
    ) -> Self:
        """
        Update a record with new values.

        Args:
            session: Database session
            record: The model instance to update
            values: Dictionary of field=value pairs to update.
            refresh: If True, refresh the instance from DB after commit to
                ensure all database-generated fields are up-to-date.

        Returns:
            The updated model instance.

        Raises:
            ValueError: If no update values provided
            AttributeError: If invalid field names provided
            IntegrityError: If a database constraint violation occurs
        """
        if not values:
            raise ValueError(
                f"Cannot update {cls.__name__}: no update values provided in 'values'"
            )

        for key, value in values.items():
            if not hasattr(record, key):
                raise AttributeError(f"{cls.__name__} has no attribute '{key}'")
            setattr(record, key, value)

        try:
            session.commit()
        except Exception:
            session.rollback()
            raise

        if refresh:
            session.refresh(record)

        return record


class BaseModel(QueryMixin, Base):
    """Base model with common fields for all tables."""

    __abstract__ = True

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda _: datetime.now(UTC),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda _: datetime.now(UTC),
        onupdate=lambda _: datetime.now(UTC),
        nullable=False,
    )


class BaseModelNoTimestamps(QueryMixin, Base):
    """Base model with only primary key (no timestamps)."""

    __abstract__ = True

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
        index=True,
    )
