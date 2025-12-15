"""
Factory for creating Criteria test data.
"""

import random

from factory import LazyFunction
from factory.alchemy import SQLAlchemyModelFactory
from factory.faker import Faker

from app.enums import CriteriaEnum
from app.models.criteria import Criteria


class CriteriaFactory(SQLAlchemyModelFactory):
    """Factory for creating Criteria instances."""

    class Meta:
        model = Criteria
        sqlalchemy_session_persistence = "commit"

    code = LazyFunction(lambda _: random.choice(list(CriteriaEnum)))
    goal = Faker("sentence", nb_words=8)
    rationale = Faker("paragraph", nb_sentences=3)
    rank = LazyFunction(lambda _: random.randint(1, 15))
