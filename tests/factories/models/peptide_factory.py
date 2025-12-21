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
    digest = SubFactory(DigestFactory)
