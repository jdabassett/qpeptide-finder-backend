"""
Check that peptide's predominant charge state is within ideal range.
"""

from app.core import settings
from app.domain import PeptideDomain, ProteinDomain
from app.enums import CriteriaEnum
from app.services.filters.base import BaseCriteriaFilter


class OutlierChargeStateFilter(BaseCriteriaFilter):
    """Check that peptide's predominant charge state is within ideal range."""

    @property
    def criteria_enum(self) -> CriteriaEnum:
        return CriteriaEnum.OUTLIER_CHARGE_STATE

    def evaluate(
        self,
        peptide: PeptideDomain,
        protein: ProteinDomain,
    ) -> bool:
        """Check that peptide's predominant charge state is within ideal range."""
        charge_state: int = peptide.charge_state_in_formic_acid()
        return (
            charge_state <= settings.LOW_CHARGE_STATE
            or settings.HIGH_CHARGE_STATE <= charge_state
        )
