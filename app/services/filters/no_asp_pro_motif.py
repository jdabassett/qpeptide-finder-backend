"""
No Aspartic-Proline motif criteria filter.
"""

from app.domain import PeptideDomain, ProteinDomain
from app.enums import CriteriaEnum
from app.services.filters.base import BaseCriteriaFilter


class NoAsparticProlineMotifFilter(BaseCriteriaFilter):
    """Filter peptide for no Aspartic-Prolime motifs."""

    @property
    def criteria_enum(self) -> CriteriaEnum:
        return CriteriaEnum.NO_ASP_PRO_MOTIF

    def evaluate(
        self,
        peptide: PeptideDomain,
        protein: ProteinDomain,
    ) -> bool:
        """Check if peptide contains an Aspartic-Proline motif."""
        return "DP" in peptide.sequence
