import random

from factory import LazyAttribute, SubFactory
from factory.alchemy import SQLAlchemyModelFactory
from factory.faker import Faker

from app.models.peptide import Peptide
from tests.factories.models.digest_factory import DigestFactory


class PeptideFactory(SQLAlchemyModelFactory):
    """Factory for creating Peptide instances."""

    class Meta:
        model = Peptide
        sqlalchemy_session_persistence = "commit"

    sequence = Faker(
        "text",
        max_nb_chars=300,
        ext_word_list="ACDEFGHIKLMNPQRSTVWY",
    )
    position = LazyAttribute(lambda obj: random.randint(1, 299))
    digest = SubFactory(DigestFactory)
