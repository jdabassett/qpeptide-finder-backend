"""
Avoid cysteine criteria filter.
"""

from app.domain import PeptideDomain, ProteinDomain
from app.enums import CriteriaEnum
from app.services.filters.base import BaseCriteriaFilter


class AvoidCysteineFilter(BaseCriteriaFilter):
    """Filter peptide to avoid cysteine."""

    @property
    def criteria_enum(self) -> CriteriaEnum:
        return CriteriaEnum.AVOID_CYSTEINE

    def evaluate(
        self,
        peptide: PeptideDomain,
        protein: ProteinDomain,
    ) -> bool:
        """Check if peptide contains cysteine."""
        return "C" in peptide.sequence
