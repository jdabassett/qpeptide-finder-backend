"""
Peptide length criteria filter.
"""

from app.core.config import settings
from app.domain import PeptideDomain, ProteinDomain
from app.enums import CriteriaEnum
from app.services.filters.base import BaseCriteriaFilter


class PeptideLengthFilter(BaseCriteriaFilter):
    """Filter peptides by length."""

    @property
    def criteria_enum(self) -> CriteriaEnum:
        return CriteriaEnum.PEPTIDE_LENGTH

    def evaluate(
        self,
        peptide: PeptideDomain,
        protein: ProteinDomain,
    ) -> bool:
        """Check if peptide length is within acceptable range."""
        return (
            settings.MIN_PEPTIDE_LENGTH <= peptide.length <= settings.MAX_PEPTIDE_LENGTH
        )
