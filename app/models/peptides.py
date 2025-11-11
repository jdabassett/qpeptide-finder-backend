from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.digest import Digest


class Peptide(BaseModel):
    __tablename__ = "peptides"

    digest_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("digests.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    sequence: Mapped[str] = mapped_column(String(500), nullable=False)
    rank: Mapped[int] = mapped_column(Integer, nullable=False)
    position: Mapped[int] = mapped_column(Integer, nullable=False)

    digest: Mapped["Digest"] = relationship(back_populates="peptides")
