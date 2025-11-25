from typing import TYPE_CHECKING

from sqlalchemy import Enum as SQLEnum
from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.enums.proteases import OrderEnum, ProteaseEnum
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
        SQLEnum(ProteaseEnum, native_enum=False, length=50), nullable=False
    )
    order: Mapped[OrderEnum] = mapped_column(
        SQLEnum(OrderEnum, native_enum=False, length=10),
        default=OrderEnum.FIRST,
        nullable=False,
    )

    digest: Mapped["Digest"] = relationship(back_populates="proteases")

    __table_args__ = (
        UniqueConstraint("digest_id", "order", name="uq_digest_order"),
        UniqueConstraint("digest_id", "protease", name="uq_digest_protease"),
    )
