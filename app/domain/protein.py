# classes for protein digest job processing
from pydantic import BaseModel, Field

from app.domain import PeptideDomain
from app.enums import ProteaseEnum
from app.enums.enums import CleavageStatusEnum
from app.models import Digest


class ProteinDomain(BaseModel):
    """Data transfer object for protein during digest processing."""

    digest_id: str
    sequence: str
    protease: ProteaseEnum

    peptides: list["PeptideDomain"] = Field(default_factory=list)
    cut_sites: set[int] = Field(default_factory=set)
    missed_cut_sites: set[int] = Field(default_factory=set)
    all_cut_sites: set[int] = Field(default_factory=set)

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
        self.cut_sites = set()
        self.missed_cut_sites = set()
        for i in range(len(self.sequence)):
            status: CleavageStatusEnum = self.protease.site_status(self.sequence, i)
            if status == CleavageStatusEnum.CLEAVAGE:
                self.cut_sites.add(i + 1)
            elif status == CleavageStatusEnum.MISSED:
                self.missed_cut_sites.add(i + 1)

        if not self.cut_sites:
            self.peptides.append(
                PeptideDomain(
                    sequence=self.sequence,
                    position=1,
                )
            )
            return

        start = 0
        for cut_site in sorted(self.cut_sites):
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

        self.all_cut_sites = self.cut_sites | self.missed_cut_sites
