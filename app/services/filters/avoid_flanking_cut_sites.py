# """
# Check if sequence flanking peptide have cut motif.
# """

# from app.core.config import settings
# from app.domain import PeptideDomain, ProteinDomain
# from app.enums import CriteriaEnum
# from app.services.filters.base import BaseCriteriaFilter


# class AvoidFlankingCutSitesFilter(BaseCriteriaFilter):
#     """Check if equence flanking peptide have cut motif."""

#     @property
#     def criteria_enum(self) -> CriteriaEnum:
#         return CriteriaEnum.AVOID_FLANKING_CUT_SITES

#     def evaluate(
#         self,
#         peptide: PeptideDomain,
#         protein: ProteinDomain,
#     ) -> bool:
#       """Check if sequence flanking peptide have cut motif."""
#       protein_length = len(protein.sequence)

#       left_start: int = 1
#       left_end: int = peptide.position - 1
#       if new_start := (left_end - settings.NUMBER_FLANKING_AMINO_ACIDS) > 1:
#         left_start = new_start

#       # the x left flanking aas before cut amino acid
#       left_flanking = protein.sequence[left_start-1:peptide.position-1]

#       left_flanking_sites: int = 0
#       for aa in protein.protease.cleavage_aas:
#         left_flanking_sites += left_flanking.count(aa)

#       if left_flanking_sites > 0:
#         return True

#       right_start: int = peptide.position + peptide.length
#       right_end: int = len(protein.sequence)

#       if new_end := (right_start + settings.NUMBER_FLANKING_AMINO_ACIDS) > protein_length:
#         right_end = new_end

#       right_flanking = protein.sequence[]
