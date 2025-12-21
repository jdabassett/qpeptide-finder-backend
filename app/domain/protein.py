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
    cut_sites: list[int] = Field(default_factory=list)

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

    def digest_sequence(self) -> None:
        """
        Digest the protein sequence using the configured protease.
        """
        self.peptides = []
        self.cut_sites = []
        for i in range(len(self.sequence)):
            if self.protease.would_cut_at(self.sequence, i):
                self.cut_sites.append(i + 1)

        if not self.cut_sites:
            self.peptides.append(
                PeptideDomain(
                    sequence=self.sequence,
                    position=1,
                )
            )
            return

        start = 0
        for cut_site in self.cut_sites:
            peptide_seq = self.sequence[start:cut_site]
            if peptide_seq:
                self.peptides.append(
                    PeptideDomain(
                        sequence=peptide_seq,
                        position=start + 1,
                    )
                )
            start = cut_site

        if start < len(self.sequence):
            peptide_seq = self.sequence[start:]
            if peptide_seq:
                self.peptides.append(
                    PeptideDomain(
                        sequence=peptide_seq,
                        position=start + 1,
                    )
                )
