"""
Factory for creating Digest test data.
"""

import random
import uuid
from datetime import UTC, datetime

from factory import SubFactory, post_generation
from factory.alchemy import SQLAlchemyModelFactory
from factory.declarations import LazyAttribute
from factory.faker import Faker

from app.enums import AminoAcidEnum, DigestStatusEnum, ProteaseEnum
from app.models.digest import Digest
from tests.factories.models.user_factory import UserFactory


class DigestFactory(SQLAlchemyModelFactory):
    """Factory for creating Digest instances."""

    class Meta:
        model = Digest
        sqlalchemy_session_persistence = "commit"

    id = LazyAttribute(lambda obj: str(uuid.uuid4()))
    status = DigestStatusEnum.PROCESSING
    protease = ProteaseEnum.TRYPSIN
    protein_name = Faker("sentence", nb_words=3)
    sequence = LazyAttribute(
        lambda obj: "".join(
            random.choice(list(AminoAcidEnum)).value
            for _ in range(random.randint(20, 200))
        )
    )
    created_at = LazyAttribute(lambda obj: datetime.now(UTC))
    updated_at = LazyAttribute(lambda obj: datetime.now(UTC))
    user = SubFactory(UserFactory)

    @post_generation
    def set_user(self, create, extracted, **kwargs) -> None:
        """Handle user/user_id assignment after instance creation."""
        if not create:
            return

        if extracted is not None:
            self.user = extracted
            self.user_id = extracted.id
            return
