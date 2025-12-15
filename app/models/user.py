from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models import Digest


class User(BaseModel):
    __tablename__ = "users"

    username: Mapped[str] = mapped_column(
        String(50), unique=False, index=True, nullable=False
    )
    email: Mapped[str] = mapped_column(String(255), nullable=False)

    digests: Mapped[list["Digest"]] = relationship(
        back_populates="user", cascade="all, delete-orphan", passive_deletes=True
    )
