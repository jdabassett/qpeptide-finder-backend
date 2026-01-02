from typing import TYPE_CHECKING

from fastapi import HTTPException, status
from sqlalchemy import Float, ForeignKey, Integer, String, UniqueConstraint, asc, select
from sqlalchemy.orm import Mapped, Session, mapped_column, relationship

from app.models.base import BaseModelNoTimestamps

if TYPE_CHECKING:
    from app.models import Digest, PeptideCriteria


class Peptide(BaseModelNoTimestamps):
    __tablename__ = "peptides"
    __table_args__ = (
        UniqueConstraint("digest_id", "rank", name="uq_peptide_digest_rank"),
    )

    digest_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("digests.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    sequence: Mapped[str] = mapped_column(String(500), nullable=False)
    position: Mapped[int] = mapped_column(Integer, nullable=False)

    pi: Mapped[float | None] = mapped_column(Float, nullable=True)
    charge_state: Mapped[int | None] = mapped_column(Integer, nullable=True)
    max_kd_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    rank: Mapped[int] = mapped_column(Integer, nullable=False)

    digest: Mapped["Digest"] = relationship(back_populates="peptides")

    criteria: Mapped[list["PeptideCriteria"]] = relationship(
        back_populates="peptide",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    @classmethod
    def find_by_digest_id_ordered_by_rank_or_raise(
        cls,
        session: Session,
        digest_id: str,
    ) -> list["Peptide"]:
        """
        Find all peptides for a digest, ordered by rank (ascending), or raise exception if none found.

        Args:
            session: Database session
            digest_id: Digest ID to filter by

        Returns:
            List of peptides ordered by rank (guaranteed to be non-empty)

        Raises:
            HTTPException: 404 if no peptides found
        """
        query = select(cls).where(cls.digest_id == digest_id).order_by(asc(cls.rank))
        peptides = list(session.scalars(query).all())

        if not peptides:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No Peptide records found with digest_id={digest_id!r}.",
            )

        return peptides
