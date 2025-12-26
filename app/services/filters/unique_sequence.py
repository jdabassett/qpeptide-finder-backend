"""
Peptide unique criteria filter.
"""

from app.domain import PeptideDomain, ProteinDomain
from app.enums import CriteriaEnum
from app.services.filters.base import BaseCriteriaFilter


class UniqueSequenceFilter(BaseCriteriaFilter):
    """Filter peptides if unique."""

    @property
    def criteria_enum(self) -> CriteriaEnum:
        return CriteriaEnum.UNIQUE_SEQUENCE

    def evaluate(
        self,
        peptide: PeptideDomain,
        protein: ProteinDomain,
    ) -> bool:
        """Check if peptide is unique."""
        return protein.sequence.count(peptide.sequence) == 1
