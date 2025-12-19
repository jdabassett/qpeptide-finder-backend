"""
Unit tests for database helper functions.
"""

import random
import uuid
from typing import Any

import pytest
from fastapi import HTTPException
from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from app.enums import DigestStatusEnum, ProteaseEnum
from app.helpers.database import (
    create_record,
    delete_record,
    get_record,
    get_record_or_exception,
    update_record,
)
from app.models import Criteria, Digest, Peptide, PeptideCriteria, User
from tests.factories.models import (
    DigestFactory,
    PeptideCriteriaFactory,
    PeptideFactory,
    UserFactory,
)


@pytest.fixture
def user() -> dict[str, str]:
    """Fixture provides dictionary for successful user record creation."""
    return {"username": "testuser", "email": "test@example.com"}


@pytest.fixture
def digest() -> dict[str, Any]:
    """Fixture provides dictionary for successful digest record creation."""
    return {
        "user_id": str(uuid.uuid4()),
        "status": DigestStatusEnum.PROCESSING,
        "protease": ProteaseEnum.TRYPSIN,
        "protein_name": "protein_name",
        "sequence": "MKTAYIAKQRQISFVKSHFSRQLEERLGLIEVQAPILSRVGDGTQDNLSGAEKAVQVKVKALPDAQFEVVHSLAKWKRQTLGQHDFSAGEGLYTHMKALRPDEDRLSPLHSVYVDQWDWERVMGDGERQFSTLKSTVEAIWAGIKATEAAVSEEFGLAPFLPDQIHFVHSQELLSRYPDLDAKGRERAIAKDLGAVFLVGIGGKLSDGHRHDVRAPDYDDWSTPSELGHAGLNGDILVWNPVLEDAFELSSMGIRVDADTLKHQLALTGDEDRLELEWHQALLRGEMPQTIGGGIGQSRLTMLLLQLPHIGQVQAGVWPAAVRESVPSLL",
    }


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


@pytest.mark.unit
def test_create_record_user_successfully(db_session: Session, user: dict[str, str]):
    """Test successfully create a user record with `create_record` helper function."""
    # execute
    result: User = create_record(db_session, User, **user)  # type: ignore[arg-type]

    # validate
    assert isinstance(result, User)
    assert result.username == user["username"]
    assert result.email == user["email"]


@pytest.mark.unit
def test_create_record_digest_successfully(db_session: Session, digest: dict[str, Any]):
    """Test successfully create a digest record with `create_record` helper function."""
    # setup
    user_record = UserFactory.create()
    digest["user_id"] = user_record.id

    # execute
    result: Digest = create_record(db_session, Digest, **digest)  # type: ignore[arg-type]

    # validate
    assert isinstance(result, Digest)
    assert result.status == DigestStatusEnum.PROCESSING
    assert result.protease == ProteaseEnum.TRYPSIN
    assert result.user_id == user_record.id
    assert result.sequence == digest["sequence"]
    assert result.user == user_record


@pytest.mark.unit
def test_create_record_peptide_successfully(db_session: Session):
    """Test successfully create a peptide record with `create_record` helper function."""
    # setup
    digest_record = DigestFactory.create()
    peptide: dict[str, Any] = {
        "digest_id": digest_record.id,
        "sequence": "smallpeptide",
        "position": random.randint(1, 200),
    }

    # execute
    result: Peptide = create_record(db_session, Peptide, **peptide)  # type: ignore[arg-type]

    # validate
    assert isinstance(result, Peptide)
    assert result.digest_id == digest_record.id
    assert result.digest == digest_record
    assert result.sequence == peptide["sequence"]
    assert result.position == peptide["position"]


@pytest.mark.unit
def test_create_record_peptide_criteria_successfully(db_session: Session):
    """Test successfully create a peptide criteria record with `create_record` helper function."""
    # setup
    peptide = PeptideFactory.create()
    criteria = db_session.query(Criteria).first()
    assert criteria is not None, "No criteria found in database"
    peptide_criteria: dict[str, str] = {
        "peptide_id": peptide.id,
        "criteria_id": criteria.id,
    }

    # execute
    result: PeptideCriteria = create_record(
        db_session,
        PeptideCriteria,
        **peptide_criteria,  # type: ignore[arg-type]
    )

    # validate
    assert isinstance(result, PeptideCriteria)
    assert result.peptide_id == peptide_criteria["peptide_id"]
    assert result.criteria_id == peptide_criteria["criteria_id"]


@pytest.mark.unit
def test_get_record_or_exception_successfully_returns_record(db_session: Session):
    """Test get_record_or_exception returns record when found."""
    # setup
    user = UserFactory.create()
    # execute
    found_user = get_record_or_exception(db_session, User, id=user.id)
    # validate
    assert found_user is not None
    assert found_user.id == user.id
    assert found_user.username == user.username


@pytest.mark.unit
def test_get_record_or_exception_raises_exception(db_session: Session):
    """Test get_record_or_exception raises HTTPException when not found."""
    # setup
    non_existent_id = str(uuid.uuid4())
    # execute and validate
    with pytest.raises(HTTPException) as exc_info:
        get_record_or_exception(db_session, User, id=non_existent_id)
    assert exc_info.value.status_code == 404
    assert "User" in exc_info.value.detail
    assert non_existent_id in exc_info.value.detail


@pytest.mark.unit
def test_update_record_user_successfully(db_session: Session):
    """Test successfully updating a user record with `update_record` helper function."""
    # setup
    user = UserFactory.create()
    original_username = user.username
    original_email = user.email

    # execute
    updated_user = update_record(
        db_session,
        user,
        username="updated_username",
        email="updated@example.com",
    )

    # validate - returned record is updated
    assert updated_user.username == "updated_username"
    assert updated_user.email == "updated@example.com"
    assert updated_user.id == user.id
    assert updated_user.username != original_username
    assert updated_user.email != original_email
