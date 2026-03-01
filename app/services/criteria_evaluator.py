"""
Service for evaluating peptides against criteria filters.
"""

from abc import abstractmethod
from collections.abc import Sequence
from typing import Protocol

from app.domain import PeptideDomain, ProteinDomain
from app.enums import CriteriaEnum
from app.services.filters import (
    ContainsAsparagineGlycineMotifFilter,
    ContainsAsparticProlineMotifFilter,
    ContainsCysteineFilter,
    ContainsLongHomopolymericStretchFilter,
    ContainsMethionineFilter,
    ContainsMissedCleavagesFilter,
    ContainsNTerminalGlutamineMotifFilter,
    HasFlankingCutSitesFilter,
    LackingFlankingAminoAcidsFilter,
    NotUniqueFilter,
    OutlierChargeStateFilter,
    OutlierHydrophobicityFilter,
    OutlierLengthFilter,
    OutlierPIFilter,
)


class CriteriaFilter(Protocol):
    """Protocol for criteria filter implementations."""

    def evaluate(self, peptide: PeptideDomain, protein: ProteinDomain) -> bool:
        """
        Evaluate if a peptide meets this criteria.
        """
        ...

    @property
    @abstractmethod
    def criteria_enum(self) -> CriteriaEnum:
        """Return the CriteriaEnum this filter represents."""
        ...


class CriteriaEvaluator:
    """
    Service for applying criteria filters to peptides.

    This service evaluates each peptide against a collection of criteria filters
    and records which criteria each peptide meets.
    """

    _default_filters: list[CriteriaFilter] | None = None

    def __init__(
        self,
        filters: Sequence[CriteriaFilter],
    ):
        """
        Initialize the evaluator with a list of filters.
        """
        self.filters = list(filters)

    @classmethod
    def _get_default_filters(cls) -> list[CriteriaFilter]:
        if cls._default_filters is None:
            cls._default_filters = [
                ContainsAsparagineGlycineMotifFilter(),
                ContainsAsparticProlineMotifFilter(),
                ContainsCysteineFilter(),
                ContainsLongHomopolymericStretchFilter(),
                ContainsMethionineFilter(),
                ContainsMissedCleavagesFilter(),
                ContainsNTerminalGlutamineMotifFilter(),
                HasFlankingCutSitesFilter(),
                LackingFlankingAminoAcidsFilter(),
                NotUniqueFilter(),
                OutlierChargeStateFilter(),
                OutlierHydrophobicityFilter(),
                OutlierLengthFilter(),
                OutlierPIFilter(),
            ]
        return cls._default_filters

    @classmethod
    def from_criteria(cls, protein_domain: "ProteinDomain") -> "CriteriaEvaluator":
        """Build an evaluator that only runs filters for the given criteria (by rank)."""
        filter_map = {f.criteria_enum: f for f in cls._get_default_filters()}
        filters = [filter_map[e] for e in protein_domain.criteria if e in filter_map]
        return cls(filters)

    def evaluate_peptides(
        self,
        protein: ProteinDomain,
    ) -> None:
        """
        Evaluate all peptides in the protein against all criteria filters.

        This method modifies the peptides in-place, adding criteria to each
        peptide that passes the corresponding filter.
        """
        for peptide in protein.peptides:
            for filter_instance in self.filters:
                if filter_instance.evaluate(peptide, protein):
                    peptide.add_criteria(filter_instance.criteria_enum)

        ordered_enums: list[CriteriaEnum] = [f.criteria_enum for f in self.filters]
        n = len(ordered_enums)
        weights: dict[CriteriaEnum, float] = {}
        for idx, enum in enumerate(ordered_enums):
            weights[enum] = 2 ** (n - 1 - idx)

        peptide_weights: list[tuple[PeptideDomain, float]] = []
        for peptide in protein.peptides:
            total_weight = 0.0
            for criteria_enum in peptide.criteria:
                total_weight += weights.get(criteria_enum, 0.0)
            peptide_weights.append((peptide, total_weight))

        peptide_weights.sort(key=lambda x: x[1])
        for rank, (peptide, _) in enumerate(peptide_weights, start=1):
            peptide.rank = rank
