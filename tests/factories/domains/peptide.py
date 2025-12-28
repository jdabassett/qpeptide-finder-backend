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

    @classmethod
    def pi(cls) -> Any:
        """Generate a random pI value."""
        return random.uniform(1.0, 11.0)

    @classmethod
    def charge_state(cls) -> Any:
        """Generate a random charge state."""
        return random.randint(-3, 4)

    @classmethod
    def max_kd_score(cls) -> Any:
        """Generate a random KD score."""
        return random.uniform(-2.0, 4.0)
