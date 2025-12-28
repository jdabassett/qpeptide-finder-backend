import random
from typing import Any

from faker import Faker
from polyfactory.factories.pydantic_factory import ModelFactory

from app.domain import PeptideDomain
from app.enums import AminoAcidEnum

faker = Faker()


class PeptideDomainFactory(ModelFactory[PeptideDomain]):
    """Factory for creating PeptideDomain instances."""

    __model__ = PeptideDomain

    @classmethod
    def sequence(cls) -> Any:
        """Generate a random peptide sequence as list of AminoAcidEnum."""
        amino_acids = list(AminoAcidEnum)
        length = random.randint(7, 30)
        return [random.choice(amino_acids) for _ in range(length)]

    @classmethod
    def position(cls) -> Any:
        """Generate a random position (1-indexed)."""
        return random.randint(1, 200)

    @classmethod
    def criteria(cls) -> Any:
        """Generate empty criteria list by default."""
        return []
