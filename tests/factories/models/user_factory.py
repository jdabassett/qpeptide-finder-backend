from factory.alchemy import SQLAlchemyModelFactory
from factory.faker import Faker

from app.models.user import User


class UserFactory(SQLAlchemyModelFactory):
    """Factory for creating User instances."""

    class Meta:
        model = User
        sqlalchemy_session_persistence = "commit"

    username = Faker("user_name")
    email = Faker("email")
