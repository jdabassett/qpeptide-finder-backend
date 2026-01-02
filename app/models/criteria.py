# app/models/criteria.py
from functools import lru_cache
from typing import TYPE_CHECKING

from sqlalchemy import Enum as SQLEnum
from sqlalchemy import Integer, String, Text, asc, select
from sqlalchemy.orm import Mapped, Session, mapped_column, relationship

from app.enums import CriteriaEnum
from app.models.base import BaseModelNoTimestamps

if TYPE_CHECKING:
    from app.models import PeptideCriteria


class Criteria(BaseModelNoTimestamps):
    """Reference table for Q-peptide selection criteria. Read-only."""

    __tablename__ = "criteria"

    code: Mapped[CriteriaEnum] = mapped_column(
        SQLEnum(
            CriteriaEnum,
            native_enum=False,
            length=50,
            values_callable=lambda x: [e.value for e in x],
        ),
        nullable=False,
        unique=True,
        index=True,
    )
    goal: Mapped[str] = mapped_column(
        String(250),
        nullable=False,
    )
    rationale: Mapped[str] = mapped_column(
        Text(),
        nullable=False,
    )
    rank: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        unique=True,
        index=True,
    )

    # Relationship for querying peptides that match this criteria
    peptides: Mapped[list["PeptideCriteria"]] = relationship(
        back_populates="criteria",
    )

    @classmethod
    @lru_cache(maxsize=1)
    def get_all_ordered_by_rank(cls, session: Session) -> list["Criteria"]:
        """
        Get all criteria ordered by rank (cached).

        Args:
            session: Database session

        Returns:
            List of all criteria ordered by rank (ascending)
        """
        query = select(cls).order_by(asc(cls.rank))
        return list(session.scalars(query).all())
