# tests/factories/dto/digest_factory.py
import random
from datetime import UTC, datetime
from uuid import uuid4

from faker import Faker
from polyfactory.factories.pydantic_factory import ModelFactory

from app.enums import AminoAcidEnum, DigestStatusEnum, ProteaseEnum
from app.schemas.digest import DigestListResponse, DigestResponse

faker = Faker()


class DigestResponseFactory(ModelFactory[DigestResponse]):
    """Factory for creating DigestResponse instances for testing."""

    __model__ = DigestResponse

    @classmethod
    def id(cls) -> str:
        """Generate a UUID string for digest ID."""
        return str(uuid4())

    @classmethod
    def status(cls) -> str:
        """Generate a random digest status."""
        return random.choice([e.value for e in DigestStatusEnum])

    @classmethod
    def user_id(cls) -> str:
        """Generate a UUID string for user ID."""
        return str(uuid4())

    @classmethod
    def protease(cls) -> str:
        """Generate a random protease value."""
        return random.choice([e.value for e in ProteaseEnum])

    @classmethod
    def protein_name(cls) -> str | None:
        """Generate a protein name or None."""
        if faker.boolean(chance_of_getting_true=80):
            return str(faker.sentence(nb_words=3).rstrip("."))
        else:
            return None

    @classmethod
    def sequence(cls) -> str:
        """Generate a random protein sequence."""
        amino_acids = [aa.value for aa in AminoAcidEnum]
        length = faker.random_int(min=20, max=200)
        return "".join(random.choice(amino_acids) for _ in range(length))

    @classmethod
    def created_at(cls) -> datetime:
        """Generate a creation timestamp."""
        return datetime.now(UTC)

    @classmethod
    def updated_at(cls) -> datetime:
        """Generate an update timestamp."""
        return datetime.now(UTC)


class DigestListResponseFactory(ModelFactory[DigestListResponse]):
    """Factory for creating DigestListResponse instances for testing."""

    __model__ = DigestListResponse

    @classmethod
    def digests(cls) -> list[DigestResponse]:
        """Generate a list of DigestResponse instances."""
        count = random.randint(0, 10)
        return [DigestResponseFactory.build() for _ in range(count)]
