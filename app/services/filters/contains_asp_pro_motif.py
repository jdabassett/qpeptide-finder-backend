"""
Aspartic-Proline motif criteria filter.
"""

from app.domain import PeptideDomain, ProteinDomain
from app.enums import AminoAcidEnum, CriteriaEnum
from app.services.filters.base import BaseCriteriaFilter


class ContainsAsparticProlineMotifFilter(BaseCriteriaFilter):
    """Filter peptide for Aspartic-Prolime motifs."""

    @property
    def criteria_enum(self) -> CriteriaEnum:
        return CriteriaEnum.CONTAINS_ASPARTIC_PROLINE_MOTIF

    def evaluate(
        self,
        peptide: PeptideDomain,
        protein: ProteinDomain,
    ) -> bool:
        """True if peptide contains a Aspartic-Proline motif."""
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
