"""
Check that peptide pI is within ideal range.
"""

from app.core import settings
from app.domain import PeptideDomain, ProteinDomain
from app.enums import CriteriaEnum
from app.services.filters.base import BaseCriteriaFilter


class PeptidePIFilter(BaseCriteriaFilter):
    """Check that peptide pI is within ideal range."""

    @property
    def criteria_enum(self) -> CriteriaEnum:
        return CriteriaEnum.PEPTIDE_PI

    def evaluate(
        self,
        peptide: PeptideDomain,
        protein: ProteinDomain,
    ) -> bool:
        """Check that peptide pI is within ideal range."""
        peptide_pI: float = peptide.get_pI()
        return settings.LOW_PI_RANGE <= peptide_pI <= settings.HIGH_PI_RANGE
