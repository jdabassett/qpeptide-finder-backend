"""
Not unique criteria filter.
"""

from app.domain import PeptideDomain, ProteinDomain
from app.enums import CriteriaEnum
from app.services.filters.base import BaseCriteriaFilter


class NotUniqueFilter(BaseCriteriaFilter):
    """Filter if peptide is not unique."""

    @property
    def criteria_enum(self) -> CriteriaEnum:
        return CriteriaEnum.NOT_UNIQUE

    def evaluate(
        self,
        peptide: PeptideDomain,
        protein: ProteinDomain,
    ) -> bool:
        """Check if peptide is unique."""
        count = 0
        peptide_len = peptide.length

        for i in range(0, protein.length - peptide_len + 1):
            if count > 1:
                break
            if protein.sequence[i : i + peptide_len] == peptide.sequence:
                count += 1

        return count > 1
