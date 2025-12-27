"""
No Asparagine-Glycine motif criteria filter.
"""

from app.domain import PeptideDomain, ProteinDomain
from app.enums import AminoAcidEnum, CriteriaEnum
from app.services.filters.base import BaseCriteriaFilter


class NoAsparagineGlycineMotifFilter(BaseCriteriaFilter):
    """Filter peptide for no Asparagine-Glycine motifs."""

    @property
    def criteria_enum(self) -> CriteriaEnum:
        return CriteriaEnum.NO_ASN_GLY_MOTIF

    def evaluate(
        self,
        peptide: PeptideDomain,
        protein: ProteinDomain,
    ) -> bool:
        """Check if peptide contains an Asparagine-Glycine motif."""
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
