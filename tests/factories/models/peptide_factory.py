import random

from factory import LazyAttribute, SubFactory
from factory.alchemy import SQLAlchemyModelFactory

from app.enums import AminoAcidEnum
from app.models.peptide import Peptide
from tests.factories.models.digest_factory import DigestFactory


class PeptideFactory(SQLAlchemyModelFactory):
    """Factory for creating Peptide instances."""

    class Meta:
        model = Peptide
        sqlalchemy_session_persistence = "commit"

    sequence = LazyAttribute(
        lambda obj: "".join(
            random.choice([aa.value for aa in AminoAcidEnum])
            for _ in range(random.randint(5, 50))
        )
    )
    position = LazyAttribute(lambda obj: random.randint(1, 299))
    pi = LazyAttribute(lambda obj: random.uniform(2.0, 11.0))
    charge_state = LazyAttribute(lambda obj: random.randint(-3, 6))
    max_kd_score = LazyAttribute(lambda obj: random.uniform(-2.0, 4.0))
    digest = SubFactory(DigestFactory)
