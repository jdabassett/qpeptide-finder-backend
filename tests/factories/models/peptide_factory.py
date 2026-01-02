import random
from collections import defaultdict

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

    _rank_counters: dict[str, int] = defaultdict(int)

    sequence = LazyAttribute(
        lambda obj: "".join(
            random.choice([aa.value for aa in AminoAcidEnum])
            for _ in range(random.randint(5, 50))
        )
    )
    position = LazyAttribute(lambda obj: random.randint(1, 299))
    pi = LazyAttribute(lambda obj: round(random.uniform(2.0, 11.0), 2))
    charge_state = LazyAttribute(lambda obj: random.randint(-3, 6))
    max_kd_score = LazyAttribute(lambda obj: round(random.uniform(-2.0, 4.0), 2))
    digest = SubFactory(DigestFactory)

    @classmethod
    def _get_next_rank(cls, digest_id: str) -> int:
        """Get the next unique rank for a given digest_id."""
        cls._rank_counters[digest_id] += 1
        return cls._rank_counters[digest_id]

    rank = LazyAttribute(lambda obj: PeptideFactory._get_next_rank(obj.digest.id))
