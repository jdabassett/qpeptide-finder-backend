"""
No Aspartic-Proline motif criteria filter.
"""

from app.domain import PeptideDomain, ProteinDomain
from app.enums import AminoAcidEnum, CriteriaEnum
from app.services.filters.base import BaseCriteriaFilter


class NoAsparticProlineMotifFilter(BaseCriteriaFilter):
    """Filter peptide for no Aspartic-Prolime motifs."""

    @property
    def criteria_enum(self) -> CriteriaEnum:
        return CriteriaEnum.NO_ASP_PRO_MOTIF

    def evaluate(
        self,
        peptide: PeptideDomain,
        protein: ProteinDomain,
    ) -> bool:
        """Check if peptide contains an Aspartic-Proline motif."""
        target: list[AminoAcidEnum] = [
            AminoAcidEnum.ASPARTIC_ACID,
            AminoAcidEnum.PROLINE,
        ]
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
