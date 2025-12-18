"""
Factory for creating PeptideCriteria test data.
"""

import random

from factory import SubFactory
from factory.alchemy import SQLAlchemyModelFactory
from factory.declarations import LazyAttribute

from app.models.criteria import Criteria
from app.models.peptide_criteria import PeptideCriteria
from tests.factories.models.peptide_factory import PeptideFactory


class PeptideCriteriaFactory(SQLAlchemyModelFactory):
    """Factory for creating PeptideCriteria instances."""

    class Meta:
        model = PeptideCriteria
        sqlalchemy_session_persistence = "commit"

    peptide = SubFactory(PeptideFactory)
    criteria = LazyAttribute(
        lambda obj: _get_random_criteria(
            PeptideCriteriaFactory._meta.sqlalchemy_session
        )
    )


def _get_random_criteria(session):
    """Get a random existing Criteria from the database."""
    all_criteria = session.query(Criteria).all()
    if not all_criteria:
        raise ValueError(
            "No Criteria records found in database. "
            "Ensure migrations have been run to populate the criteria table."
        )
    return random.choice(all_criteria)
