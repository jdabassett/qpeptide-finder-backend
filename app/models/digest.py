from typing import TYPE_CHECKING

from sqlalchemy import Enum as SQLEnum
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.enums import DigestStatusEnum, ProteaseEnum
from app.models.base import BaseModel

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

    def sort_peptides(self) -> list["Peptide"]:
        """
        Sort peptides by rank (ascending).

        Returns:
            List of peptides sorted by rank
        """
        return sorted(self.peptides, key=lambda x: x.rank)
