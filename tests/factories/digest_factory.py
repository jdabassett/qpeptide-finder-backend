"""
Factory for creating Digest test data.
"""

import random

from factory import LazyFunction, SubFactory
from factory.alchemy import SQLAlchemyModelFactory

from app.enums.digest_statuses import DigestStatusEnum
from app.enums.proteases import ProteaseEnum
from app.models.digest import Digest
from tests.factories.protein_factory import ProteinFactory
from tests.factories.user_factory import UserFactory


class DigestFactory(SQLAlchemyModelFactory):
    """Factory for creating Digest instances."""

    class Meta:
        model = Digest
        sqlalchemy_session_persistence = "commit"

    protease_1 = LazyFunction(lambda _: random.choice(list(ProteaseEnum)))
    protease_2 = None
    protease_3 = None
    status = DigestStatusEnum.PENDING
    user = SubFactory(UserFactory)
    protein = SubFactory(ProteinFactory)
