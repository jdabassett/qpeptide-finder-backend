"""
Has flanking amino acids criteria filter
"""

from app.core import settings
from app.domain import PeptideDomain, ProteinDomain
from app.enums import CriteriaEnum
from app.services.filters.base import BaseCriteriaFilter


class LackingFlankingAminoAcidsFilter(BaseCriteriaFilter):
    """Check if peptide has minimum flanking sequence for consistant peptide digestion."""

    @property
    def criteria_enum(self) -> CriteriaEnum:
        return CriteriaEnum.LACKING_FLANKING_AMINO_ACIDS

    def evaluate(
        self,
        peptide: PeptideDomain,
        protein: ProteinDomain,
    ) -> bool:
        """True if peptide has minimum flanking sequence for consistant peptide digestion."""
        left_flank_start = peptide.position - settings.NUMBER_FLANKING_AMINO_ACIDS

        right_flank_end = (
            peptide.position + peptide.length + settings.NUMBER_FLANKING_AMINO_ACIDS - 1
        )

        return left_flank_start > 0 and right_flank_end < protein.length
