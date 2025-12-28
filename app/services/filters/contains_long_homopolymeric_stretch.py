"""
Long homopolymeric stretch criteria filter.
"""

from app.core import settings
from app.domain import PeptideDomain, ProteinDomain
from app.enums import CriteriaEnum
from app.services.filters.base import BaseCriteriaFilter


class ContainsLongHomopolymericStretchFilter(BaseCriteriaFilter):
    """Filter if peptide contains long homopolymeric stretches."""

    @property
    def criteria_enum(self) -> CriteriaEnum:
        return CriteriaEnum.CONTAINS_LONG_HOMOPOLYMERIC_STRETCH

    def evaluate(
        self,
        peptide: PeptideDomain,
        protein: ProteinDomain,
    ) -> bool:
        """True if peptide contains at least one long homopolymeric stretch."""
        current_aa = peptide.sequence[0]
        current_stretch = 1

        for i in range(1, peptide.length):
            if peptide.sequence[i] == current_aa:
                current_stretch += 1
                if current_stretch > settings.MAX_HOMOPOLYMERIC_LENGTH:
                    return True
            else:
                current_aa = peptide.sequence[i]
                current_stretch = 1

        return False
