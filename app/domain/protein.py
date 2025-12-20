# classes for protein digest job processing
from pydantic import BaseModel, Field, field_validator

from app.domain import PeptideDomain
from app.enums import ProteaseEnum
from app.models import Digest


class ProteinDomain(BaseModel):
    """Data transfer object for protein during digest processing."""

    digest_id: str
    sequence: str
    protease: ProteaseEnum

    peptides: list["PeptideDomain"] = Field(default_factory=list)

    @classmethod
    def from_digest(cls, digest: "Digest") -> "ProteinDomain":
        """Create ProteinDomain from a Digest database record."""
        return cls(
            digest_id=digest.id,
            sequence=digest.sequence,
            protease=digest.protease,
        )

    @field_validator("sequence")
    @classmethod
    def validate_sequence(cls, v: str) -> str:
        if not v:
            raise ValueError("Protein sequence cannot be empty")
        return v

    def get_sequence_length(self) -> int:
        return len(self.sequence)
