from typing import TYPE_CHECKING

from sqlalchemy import Enum as SQLEnum
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.enums.digest_statuses import DigestStatusEnum
from app.enums.proteases import ProteaseEnum
from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.peptides import Peptide
    from app.models.protein import Protein
    from app.models.user import User


class Digest(BaseModel):
    __tablename__ = "digests"

    protease_1: Mapped[ProteaseEnum] = mapped_column(
        SQLEnum(ProteaseEnum), nullable=False
    )
    protease_2: Mapped[ProteaseEnum | None] = mapped_column(
        SQLEnum(ProteaseEnum), nullable=True
    )
    protease_3: Mapped[ProteaseEnum | None] = mapped_column(
        SQLEnum(ProteaseEnum), nullable=True
    )
    status: Mapped[DigestStatusEnum] = mapped_column(
        SQLEnum(DigestStatusEnum), default=DigestStatusEnum.PENDING, nullable=False
    )
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    protein_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("proteins.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    user: Mapped["User"] = relationship(back_populates="digests")
    protein: Mapped["Protein"] = relationship(back_populates="digests")
    peptides: Mapped[list["Peptide"]] = relationship(
        back_populates="digest", cascade="all, delete-orphan", passive_deletes=True
    )
