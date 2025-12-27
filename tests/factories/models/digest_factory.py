"""
Factory for creating Digest test data.
"""

from factory import SubFactory
from factory.alchemy import SQLAlchemyModelFactory
from factory.faker import Faker

from app.enums import AminoAcidEnum, DigestStatusEnum, ProteaseEnum
from app.models.digest import Digest
from tests.factories.models.user_factory import UserFactory


class DigestFactory(SQLAlchemyModelFactory):
    """Factory for creating Digest instances."""

    class Meta:
        model = Digest
        sqlalchemy_session_persistence = "commit"

    status = DigestStatusEnum.PROCESSING
    protease = ProteaseEnum.TRYPSIN
    protein_name = Faker("sentence", nb_words=3)
    sequence = Faker(
        "text",
        max_nb_chars=200,
        ext_word_list="".join([aa.value for aa in AminoAcidEnum]),
    )
    user = SubFactory(UserFactory)
