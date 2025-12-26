"""
No Asparagine-Glycine motif criteria filter.
"""

from app.domain import PeptideDomain, ProteinDomain
from app.enums import CriteriaEnum
from app.services.filters.base import BaseCriteriaFilter


class NoAsparagineGlycineMotifFilter(BaseCriteriaFilter):
    """Filter peptide for no Asparagine-Glycine motifs."""

    @property
    def criteria_enum(self) -> CriteriaEnum:
        return CriteriaEnum.NO_ASN_GLY_MOTIF

    def evaluate(
        self,
        peptide: PeptideDomain,
        protein: ProteinDomain,
    ) -> bool:
        """Check if peptide contains an Asparagine-Glycine motif."""
        return "NG" in peptide.sequence
