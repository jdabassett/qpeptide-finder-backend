# classes for protein digest job processing
from pydantic import BaseModel, Field

from app.domain import PeptideDomain
from app.enums import AminoAcidEnum, ProteaseEnum
from app.enums.enums import CleavageStatusEnum
from app.models import Digest


class ProteinDomain(BaseModel):
    """Data transfer object for protein during digest processing."""

    digest_id: str
    protease: ProteaseEnum
    sequence: list[AminoAcidEnum] = Field(default_factory=list)
    peptides: list["PeptideDomain"] = Field(default_factory=list)
    cut_sites: set[int] = Field(default_factory=set)
    missed_cut_sites: set[int] = Field(default_factory=set)
    all_cut_sites: set[int] = Field(default_factory=set)

    @property
    def length(self) -> int:
        return len(self.sequence)

    @property
    def sequence_as_str(self) -> str:
        """Convert protein sequence into a string."""
        return "".join([aa.value for aa in self.sequence])

    @classmethod
    def from_digest(cls, digest: "Digest") -> "ProteinDomain":
        """Create ProteinDomain from a Digest database record."""
        return cls(
            digest_id=digest.id,
            sequence=AminoAcidEnum.to_amino_acids(digest.sequence),
            protease=digest.protease,
        )

    def digest_sequence(self) -> None:
        """
        Digest the protein sequence using the configured protease.
        """
        self.peptides = []
        self.cut_sites = set()
        self.missed_cut_sites = set()
        for i in range(self.length):
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
            peptide = self.sequence[start:cut_site]
            if peptide:
                self.peptides.append(
                    PeptideDomain(
                        sequence=peptide,
                        position=start + 1,
                    )
                )
            start = cut_site

        if start < self.length:
            peptide = self.sequence[start:]
            if peptide:
                self.peptides.append(
                    PeptideDomain(
                        sequence=peptide,
                        position=start + 1,
                    )
                )

        self.all_cut_sites = self.cut_sites | self.missed_cut_sites
