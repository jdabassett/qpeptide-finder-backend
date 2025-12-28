"""
Base classes for criteria filters.
"""

from abc import ABC, abstractmethod

from app.domain import PeptideDomain, ProteinDomain
from app.enums import CriteriaEnum


class BaseCriteriaFilter(ABC):
    """Base class for criteria filter implementations."""

    @property
    @abstractmethod
    def criteria_enum(self) -> CriteriaEnum:
        """Return the CriteriaEnum this filter represents."""
        ...

    @abstractmethod
    def evaluate(self, peptide: PeptideDomain, protein: ProteinDomain) -> bool:
        """
        Evaluate if a peptide meets this criteria.

        Returns:
            True if peptide meets criteria, False otherwise
        """
        ...
