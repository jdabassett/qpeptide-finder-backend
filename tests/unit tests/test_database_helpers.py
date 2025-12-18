"""
Unit tests for database helper functions.
"""

import pytest
from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from app.helpers.database import delete_record, get_record
from app.models import Digest, Peptide, PeptideCriteria, User
from tests.factories.models import (
    DigestFactory,
    PeptideCriteriaFactory,
    PeptideFactory,
    UserFactory,
)


@pytest.mark.parametrize(
    "model_class,factory,lookup_field",
    [
        (User, UserFactory, "id"),
        (Digest, DigestFactory, "id"),
        (Peptide, PeptideFactory, "id"),
        (PeptideCriteria, PeptideCriteriaFactory, "id"),
    ],
)
@pytest.mark.unit
def test_delete_record_success(
    db_session: Session,
    model_class: type,
    factory,
    lookup_field: str,
):
    """Test successfully deleting a database record for each model."""
    # setup
    record = factory.create()
    record_id = getattr(record, lookup_field)

    # execute
    delete_record(db_session, record)

    # validate
    lookup_column = getattr(model_class, lookup_field)
    query: Select = select(model_class).where(lookup_column == record_id)
    deleted_record = db_session.scalar(query)
    assert deleted_record is None


@pytest.mark.parametrize(
    "model_class,factory,lookup_attrs",
    [
        (User, UserFactory, [{"username"}]),
        (User, UserFactory, [{"email"}]),
        (Digest, DigestFactory, [{"status"}]),
        (Digest, DigestFactory, [{"user_id"}]),
        (Digest, DigestFactory, [{"protease"}]),
        (Digest, DigestFactory, [{"protein_name"}]),
        (Digest, DigestFactory, [{"sequence"}]),
        (Peptide, PeptideFactory, [{"digest_id"}]),
        (Peptide, PeptideFactory, [{"sequence"}]),
        (Peptide, PeptideFactory, [{"position"}]),
        (PeptideCriteria, PeptideCriteriaFactory, [{"peptide_id"}]),
        (PeptideCriteria, PeptideCriteriaFactory, [{"criteria_id"}]),
    ],
)
@pytest.mark.unit
def test_get_record_by_single_attribute(
    db_session: Session,
    model_class: type,
    factory,
    lookup_attrs: list[dict],
):
    """Test getting a record by a single attribute for each model."""
    # setup
    record = factory.create()

    lookup_kwargs = {}
    for attr_dict in lookup_attrs:
        for attr_name in attr_dict:
            lookup_kwargs[attr_name] = getattr(record, attr_name)

    # execute
    found_record = get_record(db_session, model_class, **lookup_kwargs)

    # validate
    assert found_record is not None
    assert found_record.id == record.id


@pytest.mark.parametrize(
    "model_class,factory,lookup_attrs",
    [
        (User, UserFactory, ["username", "email"]),
        (
            Digest,
            DigestFactory,
            ["status", "user_id", "protease", "protein_name", "sequence"],
        ),
        (Peptide, PeptideFactory, ["digest_id", "sequence", "position"]),
        (PeptideCriteria, PeptideCriteriaFactory, ["peptide_id", "criteria_id"]),
    ],
)
@pytest.mark.unit
def test_get_record_by_all_attributes(
    db_session: Session,
    model_class: type,
    factory,
    lookup_attrs: list[str],
):
    """Test getting a record by all attributes combined for each model."""
    # setup
    record = factory.create()

    lookup_kwargs = {
        attr_name: getattr(record, attr_name) for attr_name in lookup_attrs
    }

    # execute
    found_record = get_record(db_session, model_class, **lookup_kwargs)

    # validate
    assert found_record is not None
    assert found_record.id == record.id
