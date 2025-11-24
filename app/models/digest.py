from typing import TYPE_CHECKING

from sqlalchemy import Enum as SQLEnum
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.enums.digest_statuses import DigestStatusEnum
from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.digest_proteases import DigestProtease
    from app.models.peptides import Peptide
    from app.models.protein import Protein
    from app.models.user import User


class Digest(BaseModel):
    __tablename__ = "digests"

    status: Mapped[DigestStatusEnum] = mapped_column(
        SQLEnum(DigestStatusEnum), default=DigestStatusEnum.PROCESSING, nullable=False
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
    proteases: Mapped[list["DigestProtease"]] = relationship(
        back_populates="digest",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="DigestProtease.order",
    )
