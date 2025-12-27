"""
Check if sequence flanking peptide have cut motif.
"""

from app.core import settings
from app.domain import PeptideDomain, ProteinDomain
from app.enums import CriteriaEnum
from app.services.filters.base import BaseCriteriaFilter


class AvoidFlankingCutSitesFilter(BaseCriteriaFilter):
    """Check if equence flanking peptide have cut motif."""

    @property
    def criteria_enum(self) -> CriteriaEnum:
        return CriteriaEnum.AVOID_FLANKING_CUT_SITES

    def evaluate(
        self,
        peptide: PeptideDomain,
        protein: ProteinDomain,
    ) -> bool:
        """Check if sequence flanking peptide have cut motif."""
        left_flank_start = max(
            1, peptide.position - settings.NUMBER_FLANKING_AMINO_ACIDS
        )
        left_flank_end = peptide.position - 1

        peptide_end_position = peptide.position + peptide.length
        right_flank_start = peptide_end_position
        right_flank_end = min(
            protein.length,
            peptide_end_position + settings.NUMBER_FLANKING_AMINO_ACIDS - 1,
        )

        left_flanking_positions = set(range(left_flank_start, left_flank_end + 1))
        right_flanking_positions = set(range(right_flank_start, right_flank_end + 1))
        all_flanking_positions = left_flanking_positions | right_flanking_positions

        return bool(protein.all_cut_sites & all_flanking_positions)
