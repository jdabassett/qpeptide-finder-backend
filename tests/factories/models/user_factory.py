import uuid

from factory.alchemy import SQLAlchemyModelFactory
from factory.declarations import LazyAttribute
from factory.faker import Faker

from app.models.user import User


class UserFactory(SQLAlchemyModelFactory):
    """Factory for creating User instances."""

    class Meta:
        model = User
        sqlalchemy_session_persistence = "commit"

    id = LazyAttribute(lambda obj: str(uuid.uuid4()))
    username = Faker("user_name")
    email = Faker("email")
