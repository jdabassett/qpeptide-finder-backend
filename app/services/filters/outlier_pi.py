"""
Check that peptide pI is within ideal range.
"""

from app.core import settings
from app.domain import PeptideDomain, ProteinDomain
from app.enums import CriteriaEnum
from app.services.filters.base import BaseCriteriaFilter


class OutlierPIFilter(BaseCriteriaFilter):
    """Check if peptide pI is an outlier for LC-MS."""

    @property
    def criteria_enum(self) -> CriteriaEnum:
        return CriteriaEnum.OUTLIER_PI

    def evaluate(
        self,
        peptide: PeptideDomain,
        protein: ProteinDomain,
    ) -> bool:
        """True if peptide pI is an outlier for LC-MS."""
        peptide_pI: float = peptide.get_pI()
        return peptide_pI < settings.LOW_PI_RANGE or settings.HIGH_PI_RANGE < peptide_pI
