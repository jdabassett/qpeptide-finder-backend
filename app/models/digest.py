from typing import TYPE_CHECKING, Self

from sqlalchemy import Enum as SQLEnum
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, Session, mapped_column, relationship

from app.enums import CriteriaEnum, DigestStatusEnum, ProteaseEnum
from app.models.base import BaseModel
from app.models.criteria import Criteria
from app.models.digest_criteria import DigestCriteria

if TYPE_CHECKING:
    from app.models import Peptide, User


class Digest(BaseModel):
    __tablename__ = "digests"

    status: Mapped[DigestStatusEnum] = mapped_column(
        SQLEnum(DigestStatusEnum, native_enum=False, length=20),
        default=DigestStatusEnum.PROCESSING,
        nullable=False,
    )
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    protease: Mapped[ProteaseEnum] = mapped_column(
        SQLEnum(ProteaseEnum, native_enum=False, length=50),
        default=ProteaseEnum.TRYPSIN,
        nullable=False,
    )
    protein_name: Mapped[str] = mapped_column(String(200), nullable=True)
    sequence: Mapped[str] = mapped_column(String(3000), default="", nullable=False)

    user: Mapped["User"] = relationship(back_populates="digests")
    peptides: Mapped[list["Peptide"]] = relationship(
        back_populates="digest", cascade="all, delete-orphan", passive_deletes=True
    )

    digest_criteria: Mapped[list["DigestCriteria"]] = relationship(
        back_populates="digest",
        cascade="all, delete-orphan",
    )

    @classmethod
    def create(
        cls,
        session: Session,
        *,
        flush: bool = False,
        refresh: bool = True,
        commit: bool = True,
        criteria_ids: list[str] | None = None,
        **kwargs,
    ) -> Self:
        criteria_ids = criteria_ids or []

        instance = super().create(
            session,
            flush=True,
            commit=False,
            refresh=False,
            **kwargs,
        )
        instance.add_criteria_from_ids(session, criteria_ids)
        if commit:
            try:
                session.commit()
            except Exception:
                session.rollback()
                raise
        if refresh:
            session.refresh(instance)
        return instance

    def sort_peptides(self) -> list["Peptide"]:
        """
        Sort peptides by rank (ascending).

        Returns:
            List of peptides sorted by rank
        """
        return sorted(self.peptides, key=lambda x: x.rank)

    def add_criteria_from_ids(self, session: Session, criteria_ids: list[str]) -> None:
        """
        Populate digest_criteria for this digest from the given criteria IDs.
        Resolves IDs to criteria codes and inserts rows.
        If criteria_ids is empty, adds all criteria (digest uses full set).
        """
        criteria_list = Criteria.get_all_ordered_by_rank(session)
        if criteria_ids:
            criteria_ids_set = set(criteria_ids)
            criteria_list = [c for c in criteria_list if c.id in criteria_ids_set]
        for c in criteria_list:
            session.add(DigestCriteria(digest_id=self.id, criteria_code=c.code.value))
        session.flush()

    def retrieve_criteria_enums(self) -> list[CriteriaEnum]:
        """Return criteria enums for this digest, ordered by criteria rank."""
        return [
            dc.criteria.code
            for dc in sorted(
                self.digest_criteria,
                key=lambda dc: dc.criteria.rank,
            )
        ]

    def get_criteria_ordered_by_rank(self) -> list[Criteria]:
        """
        Return the Criteria records used for this digest, in rank order.

        Returns:
            List of Criteria for this digest (from digest_criteria), sorted by rank.
        """
        criteria_for_digest = [
            dc.criteria
            for dc in sorted(
                self.digest_criteria,
                key=lambda dc: dc.criteria.rank,
            )
        ]
        if not criteria_for_digest:
            raise ValueError(
                f"Digest {self.id} has no criteria; cannot determine criteria for this analysis."
            )
        return criteria_for_digest
