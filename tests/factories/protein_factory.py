"""
Factory for creating Protein test data.
"""

from factory import SubFactory
from factory.alchemy import SQLAlchemyModelFactory
from factory.faker import Faker

from app.models.protein import Protein
from tests.factories.user_factory import UserFactory


class ProteinFactory(SQLAlchemyModelFactory):
    """Factory for creating Protein instances."""

    class Meta:
        model = Protein
        sqlalchemy_session_persistence = "commit"

    uni_prot_accession_number = Faker("bothify", text="P#####")
    ncbi_protein_accession = Faker("bothify", text="NP_######")
    protein_name = Faker("word")
    sequence = Faker(
        "text",
        max_nb_chars=200,
        ext_word_list="ACDEFGHIKLMNPQRSTVWY",
    )
    user = SubFactory(UserFactory)
