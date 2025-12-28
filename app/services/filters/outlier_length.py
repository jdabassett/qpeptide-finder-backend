"""
Outlier length criteria filter.
"""

from app.core import settings
from app.domain import PeptideDomain, ProteinDomain
from app.enums import CriteriaEnum
from app.services.filters.base import BaseCriteriaFilter


class OutlierLengthFilter(BaseCriteriaFilter):
    """Check that peptide's length is an outlier for LC-MS."""

    @property
    def criteria_enum(self) -> CriteriaEnum:
        return CriteriaEnum.OUTLIER_LENGTH

    def evaluate(
        self,
        peptide: PeptideDomain,
        protein: ProteinDomain,
    ) -> bool:
        """True if peptide length is an outlier for LC-MS."""
        return (
            peptide.length < settings.MIN_PEPTIDE_LENGTH
            or settings.MAX_PEPTIDE_LENGTH < peptide.length
        )
