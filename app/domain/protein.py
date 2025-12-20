# classes for protein digest job processing
from pydantic import BaseModel, Field

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

    def get_sequence_length(self) -> int:
        return len(self.sequence)
