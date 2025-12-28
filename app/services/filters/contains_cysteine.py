"""
Cysteine criteria filter.
"""

from app.domain import PeptideDomain, ProteinDomain
from app.enums import AminoAcidEnum, CriteriaEnum
from app.services.filters.base import BaseCriteriaFilter


class ContainsCysteineFilter(BaseCriteriaFilter):
    """Filter peptide to avoid cysteine."""

    @property
    def criteria_enum(self) -> CriteriaEnum:
        return CriteriaEnum.CONTAINS_CYSTEINE

    def evaluate(
        self,
        peptide: PeptideDomain,
        protein: ProteinDomain,
    ) -> bool:
        """True if peptide contains cysteine."""
        return AminoAcidEnum.CYSTEINE in peptide.sequence
