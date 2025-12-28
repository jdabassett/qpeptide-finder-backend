"""
Outlier hydrophobicity criteria filter
"""

from app.core import settings
from app.domain import PeptideDomain, ProteinDomain
from app.enums import CriteriaEnum
from app.services.filters.base import BaseCriteriaFilter


class OutlierHydrophobicityFilter(BaseCriteriaFilter):
    """Check that peptide's max Kyte-Doolittle hydrophobicity score over a window is outside an acceptable range."""

    @property
    def criteria_enum(self) -> CriteriaEnum:
        return CriteriaEnum.OUTLIER_HYDROPHOBICITY

    def evaluate(
        self,
        peptide: PeptideDomain,
        protein: ProteinDomain,
    ) -> bool:
        """True if peptide's max Kyte-Doolittle hydrophobicity score over a window is outside an acceptable range."""
        peptide_kd: float = peptide.max_kyte_dolittle_score_over_sliding_window()
        return (
            peptide_kd <= settings.MIN_KD_SCORE or settings.MAX_KD_SCORE <= peptide_kd
        )
