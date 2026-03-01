# app/models/digest_criteria.py
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models import Criteria, Digest


class DigestCriteria(Base):
    """Join table linking digests to criteria (by code) for digest-specific criterion selection."""

    __tablename__ = "digest_criteria"

    digest_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("digests.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
        index=True,
    )
    criteria_code: Mapped[str] = mapped_column(
        String(50),
        ForeignKey("criteria.code", ondelete="RESTRICT"),
        primary_key=True,
        nullable=False,
        index=True,
    )

    digest: Mapped["Digest"] = relationship(back_populates="digest_criteria")
    criteria: Mapped["Criteria"] = relationship(back_populates="digest_criteria")
