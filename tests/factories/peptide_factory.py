"""
Factory for creating Peptide test data.
"""

import random

from factory import LazyAttribute, LazyFunction, SubFactory
from factory.alchemy import SQLAlchemyModelFactory
from factory.faker import Faker

from app.models.peptides import Peptide
from tests.factories.digest_factory import DigestFactory


class PeptideFactory(SQLAlchemyModelFactory):
    """Factory for creating Peptide instances."""

    class Meta:
        model = Peptide
        sqlalchemy_session_persistence = "commit"

    sequence = Faker(
        "text",
        max_nb_chars=50,
        ext_word_list="ACDEFGHIKLMNPQRSTVWY",
    )
    rank = LazyFunction(lambda: random.randint(1, 100))
    position = LazyAttribute(lambda obj: random.randint(1, len(obj.sequence)))
    digest = SubFactory(DigestFactory)
