"""
Has flanking cut sites criteria filter.
"""

from app.core import settings
from app.domain import PeptideDomain, ProteinDomain
from app.enums import CriteriaEnum
from app.services.filters.base import BaseCriteriaFilter


class HasFlankingCutSitesFilter(BaseCriteriaFilter):
    """Check flanking sites contain cut site(s)."""

    @property
    def criteria_enum(self) -> CriteriaEnum:
        return CriteriaEnum.HAS_FLANKING_CUT_SITES

    def evaluate(
        self,
        peptide: PeptideDomain,
        protein: ProteinDomain,
    ) -> bool:
        """True if flanking sequences have cut site(s)."""
        left_flank_start = max(
            1, peptide.position - settings.NUMBER_FLANKING_AMINO_ACIDS - 1
        )
        left_flank_end = peptide.position - 2

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
