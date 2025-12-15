"""
Factory for creating PeptideCriteria test data.
"""

from factory import SubFactory
from factory.alchemy import SQLAlchemyModelFactory

from app.models.peptide_criteria import PeptideCriteria
from tests.factories.models.criteria_factory import CriteriaFactory
from tests.factories.models.peptide_factory import PeptideFactory


class PeptideCriteriaFactory(SQLAlchemyModelFactory):
    """Factory for creating PeptideCriteria instances."""

    class Meta:
        model = PeptideCriteria
        sqlalchemy_session_persistence = "commit"

    peptide = SubFactory(PeptideFactory)
    criteria = SubFactory(CriteriaFactory)
