"""
Avoid methionine criteria filter.
"""

from app.domain import PeptideDomain, ProteinDomain
from app.enums import AminoAcidEnum, CriteriaEnum
from app.services.filters.base import BaseCriteriaFilter


class AvoidMethionineFilter(BaseCriteriaFilter):
    """Filter peptide to avoid methionine."""

    @property
    def criteria_enum(self) -> CriteriaEnum:
        return CriteriaEnum.AVOID_METHIONINE

    def evaluate(
        self,
        peptide: PeptideDomain,
        protein: ProteinDomain,
    ) -> bool:
        """Check if peptide contains methionine."""
        return AminoAcidEnum.METHIONINE in peptide.sequence
