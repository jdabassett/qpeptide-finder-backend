"""
N-Terminal Glutamine criteria filter.
"""

from app.domain import PeptideDomain, ProteinDomain
from app.enums import AminoAcidEnum, CriteriaEnum
from app.services.filters.base import BaseCriteriaFilter


class ContainsNTerminalGlutamineMotifFilter(BaseCriteriaFilter):
    """Filter if peptide contains N-Terminal Glutamine."""

    @property
    def criteria_enum(self) -> CriteriaEnum:
        return CriteriaEnum.CONTAINS_N_TERMINAL_GLUTAMINE_MOTIF

    def evaluate(
        self,
        peptide: PeptideDomain,
        protein: ProteinDomain,
    ) -> bool:
        """True if peptide contains N-Terminal Glutamine."""
        return AminoAcidEnum.GLUTAMINE == peptide.sequence[0]
