from faker import Faker
from polyfactory.factories.pydantic_factory import ModelFactory

from app.schemas.user import UserCreate

faker = Faker()


class UserCreateFactory(ModelFactory[UserCreate]):
    __model__ = UserCreate

    @classmethod
    def username(cls) -> str:
        return faker.user_name().replace(".", "_").replace("@", "_")[:50]

    @classmethod
    def email(cls) -> str:
        return faker.email()
