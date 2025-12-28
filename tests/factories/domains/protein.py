"""
Factory for ProteinDomain.
"""

import random
import uuid
from typing import Any, cast

from faker import Faker
from polyfactory.factories.pydantic_factory import ModelFactory

from app.domain import ProteinDomain
from app.enums import AminoAcidEnum, ProteaseEnum

faker = Faker()


class ProteinDomainFactory(ModelFactory[ProteinDomain]):
    """Factory for creating ProteinDomain instances."""

    __model__ = ProteinDomain

    @classmethod
    def digest_id(cls) -> Any:
        """Generate a random digest ID."""
        return str(uuid.uuid4())

    @classmethod
    def sequence(cls) -> Any:
        """Generate a random peptide sequence as list of AminoAcidEnum."""
        amino_acids = list(AminoAcidEnum)
        length = random.randint(30, 200)
        return [random.choice(amino_acids) for _ in range(length)]

    @classmethod
    def protease(cls) -> Any:
        """Generate a random protease, defaulting to TRYPSIN."""
        return random.choice(list(ProteaseEnum))

    @classmethod
    def peptides(cls) -> Any:
        """Generate empty peptides list by default."""
        return []

    @classmethod
    def cut_sites(cls) -> Any:
        """Generate empty cut_sites set by default."""
        return set()

    @classmethod
    def missed_cut_sites(cls) -> Any:
        """Generate empty missed_cut_sites set by default."""
        return set()

    @classmethod
    def all_cut_sites(cls) -> Any:
        """Generate empty missed_cut_sites set by default."""
        return set()

    @classmethod
    def build(cls, with_peptides: bool = False, **kwargs: Any) -> ProteinDomain:
        """
        Build a ProteinDomain instance with optional peptide population.
        """
        instance = cast(ProteinDomain, super().build(**kwargs))

        if with_peptides:
            instance.digest_sequence()

        return instance

    @classmethod
    def create(
        cls,
        with_peptides: bool = False,
        sequence: str | None = None,
        protease: ProteaseEnum | None = None,
        **kwargs: Any,
    ) -> ProteinDomain:
        """
        Create a ProteinDomain instance (same as build for Pydantic models).
        """
        if sequence is not None:
            kwargs["sequence"] = AminoAcidEnum.to_amino_acids(sequence)
        if protease is not None:
            kwargs["protease"] = protease
        return cls.build(with_peptides=with_peptides, **kwargs)
