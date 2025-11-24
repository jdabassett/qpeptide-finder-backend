from typing import TYPE_CHECKING

from sqlalchemy import Enum as SQLEnum
from sqlalchemy import ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.enums.proteases import ProteaseEnum
from app.models.base import BaseModelNoTimestamps

if TYPE_CHECKING:
    from app.models.digest import Digest


class DigestProtease(BaseModelNoTimestamps):
    __tablename__ = "digest_proteases"

    digest_id: Mapped[str] = mapped_column(
        ForeignKey("digests.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    protease: Mapped[ProteaseEnum] = mapped_column(
        SQLEnum(ProteaseEnum), nullable=False
    )
    order: Mapped[int] = mapped_column(Integer, nullable=False)

    digest: Mapped["Digest"] = relationship(back_populates="proteases")

    __table_args__ = (
        UniqueConstraint("digest_id", "order", name="uq_digest_order"),
        UniqueConstraint("digest_id", "protease", name="uq_digest_protease"),
    )
