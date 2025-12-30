"""
Peptide contains missed cleavage sites.
"""

from app.domain import PeptideDomain, ProteinDomain
from app.enums import CriteriaEnum
from app.services.filters.base import BaseCriteriaFilter


class ContainsMissedCleavagesFilter(BaseCriteriaFilter):
    """Fitler whether peptide contains any missed cleavages."""

    @property
    def criteria_enum(self) -> CriteriaEnum:
        return CriteriaEnum.CONTAINS_MISSED_CLEAVAGES

    def evaluate(
        self,
        peptide: PeptideDomain,
        protein: ProteinDomain,
    ) -> bool:
        """True if missed cleavage sites in peptide."""
        peptide_positions = set(
            range(peptide.position, peptide.position + peptide.length)
        )

        return bool(protein.missed_cut_sites & peptide_positions)
