from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import BaseModel


class Protein(BaseModel):
    __tablename__ = "proteins"

    uni_prot_accession_number: Mapped[str | None] = mapped_column(String(20), nullable=True)
    ncbi_protein_accession: Mapped[str | None] = mapped_column(String(50), nullable=True)
    protein_name: Mapped[str] = mapped_column(String(255), nullable=False)
    sequence: Mapped[str] = mapped_column(String(2000), nullable=False)
    user_id: Mapped[str] = mapped_column(
        String(36), 
        ForeignKey("users.id", ondelete="CASCADE"), 
        nullable=False,
        index=True 
    )
    
    user: Mapped["User"] = relationship(back_populates="proteins")
    digests: Mapped[list["Digest"]] = relationship(
        back_populates="protein", 
        cascade="all, delete-orphan",
        passive_deletes=True
    )