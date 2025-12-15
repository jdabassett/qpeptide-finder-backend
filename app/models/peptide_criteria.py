# app/models/peptide_criteria.py
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModelNoTimestamps

if TYPE_CHECKING:
    from app.models import Criteria, Peptide


class PeptideCriteria(BaseModelNoTimestamps):
    """Join table linking peptides to criteria. Read-only."""

    __tablename__ = "peptide_criteria"

    peptide_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("peptides.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    criteria_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("criteria.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    peptide: Mapped["Peptide"] = relationship(back_populates="criteria")
    criteria: Mapped["Criteria"] = relationship(back_populates="peptides")
