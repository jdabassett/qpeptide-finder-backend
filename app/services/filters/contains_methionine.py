"""
Methionine criteria filter.
"""

from app.domain import PeptideDomain, ProteinDomain
from app.enums import AminoAcidEnum, CriteriaEnum
from app.services.filters.base import BaseCriteriaFilter


class ContainsMethionineFilter(BaseCriteriaFilter):
    """Filter peptide if contains methionine."""

    @property
    def criteria_enum(self) -> CriteriaEnum:
        return CriteriaEnum.CONTAINS_METHIONINE

    def evaluate(
        self,
        peptide: PeptideDomain,
        protein: ProteinDomain,
    ) -> bool:
        """True if peptide contains methionine."""
        return AminoAcidEnum.METHIONINE in peptide.sequence
