"""
Asparagine-Glycine motif criteria filter.
"""

from app.domain import PeptideDomain, ProteinDomain
from app.enums import AminoAcidEnum, CriteriaEnum
from app.services.filters.base import BaseCriteriaFilter


class ContainsAsparagineGlycineMotifFilter(BaseCriteriaFilter):
    """Filter peptide for Asparagine-Glycine motifs."""

    @property
    def criteria_enum(self) -> CriteriaEnum:
        return CriteriaEnum.CONTAINS_ASPARAGINE_GLYCINE_MOTIF

    def evaluate(
        self,
        peptide: PeptideDomain,
        protein: ProteinDomain,
    ) -> bool:
        """True if peptide contains an Asparagine-Glycine motif."""
        target: list[AminoAcidEnum] = [AminoAcidEnum.ASPARAGINE, AminoAcidEnum.GLYCINE]
        index: int = 0

        for aa in peptide.sequence:
            if aa == target[index]:
                index += 1
                if index == len(target):
                    return True
            else:
                if aa == target[0]:
                    index = 1
                else:
                    index = 0

        return False
