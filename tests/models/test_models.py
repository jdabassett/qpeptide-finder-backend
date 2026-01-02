"""
Unit tests for QueryMixin methods.
"""

import pytest
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.enums import DigestStatusEnum, ProteaseEnum
from app.models import Criteria, Digest, Peptide, PeptideCriteria, User
from tests.factories.models import (
    DigestFactory,
    PeptideFactory,
    UserFactory,
)


@pytest.mark.unit
def test_create_user_successfully(db_session: Session):
    """Test successfully creating a user record with User.create()."""
    # setup
    username = "testuser"
    email = "test@example.com"

    # execute
    result = User.create(db_session, username=username, email=email)

    # validate
    assert isinstance(result, User)
    assert result.id is not None
    assert result.username == username
    assert result.email == email
    assert result.created_at is not None
    assert result.updated_at is not None


@pytest.mark.unit
def test_create_digest_successfully(db_session: Session):
    """Test successfully creating a digest record with Digest.create()."""
    # setup
    user = UserFactory.create()
    status_enum = DigestStatusEnum.PROCESSING
    protease_enum = ProteaseEnum.TRYPSIN
    protein_name = "Test Protein"
    sequence = "MKTAYIAKQR"

    # execute
    result = Digest.create(
        db_session,
        user_id=user.id,
        status=status_enum,
        protease=protease_enum,
        protein_name=protein_name,
        sequence=sequence,
    )

    # validate
    assert isinstance(result, Digest)
    assert result.id is not None
    assert result.user_id == user.id
    assert result.status == status_enum
    assert result.protease == protease_enum
    assert result.protein_name == protein_name
    assert result.sequence == sequence
    assert result.created_at is not None
    assert result.updated_at is not None


@pytest.mark.unit
def test_create_peptide_successfully(db_session: Session):
    """Test successfully creating a peptide record with Peptide.create()."""
    # setup
    digest = DigestFactory.create()
    sequence = "MKTAYIAKQR"
    position = 1
    pi = 7.5
    charge_state = 2
    max_kd_score = 1.5
    rank = 1

    # execute
    result = Peptide.create(
        db_session,
        digest_id=digest.id,
        sequence=sequence,
        position=position,
        pi=pi,
        charge_state=charge_state,
        max_kd_score=max_kd_score,
        rank=1,
    )

    # validate
    assert isinstance(result, Peptide)
    assert result.id is not None
    assert result.digest_id == digest.id
    assert result.sequence == sequence
    assert result.position == position
    assert result.pi == pi
    assert result.charge_state == charge_state
    assert result.max_kd_score == max_kd_score
    assert result.rank == rank


@pytest.mark.unit
def test_create_peptide_criteria_successfully(db_session: Session):
    """Test successfully creating a peptide criteria record with PeptideCriteria.create()."""
    # setup
    peptide = PeptideFactory.create()
    criteria = db_session.query(Criteria).first()
    assert criteria is not None

    # execute
    result = PeptideCriteria.create(
        db_session,
        peptide_id=peptide.id,
        criteria_id=criteria.id,
    )

    # validate
    assert isinstance(result, PeptideCriteria)
    assert result.id is not None
    assert result.peptide_id == peptide.id
    assert result.criteria_id == criteria.id


@pytest.mark.unit
def test_find_one_by_user_by_email_successfully(db_session: Session):
    """Test successfully finding a user by email with User.find_one_by()."""
    # setup
    user = UserFactory.create()
    user_email = user.email

    # execute
    found_user = User.find_one_by(db_session, email=user_email)

    # validate
    assert found_user is not None
    assert isinstance(found_user, User)
    assert found_user.id == user.id
    assert found_user.email == user_email


@pytest.mark.unit
def test_find_one_by_user_by_id_successfully(db_session: Session):
    """Test successfully finding a user by id with User.find_one_by()."""
    # setup
    user = UserFactory.create()
    user_id = user.id

    # execute
    found_user = User.find_one_by(db_session, id=user_id)

    # validate
    assert found_user is not None
    assert isinstance(found_user, User)
    assert found_user.id == user.id


@pytest.mark.unit
def test_find_one_by_digest_by_id_successfully(db_session: Session):
    """Test successfully finding a digest by id with Digest.find_one_by()."""
    # setup
    digest = DigestFactory.create()
    digest_id = digest.id

    # execute
    found_digest = Digest.find_one_by(db_session, id=digest_id)

    # validate
    assert found_digest is not None
    assert isinstance(found_digest, Digest)
    assert found_digest.id == digest.id


@pytest.mark.unit
def test_find_one_by_peptide_by_id_successfully(db_session: Session):
    """Test successfully finding a peptide by id with Peptide.find_one_by()."""
    # setup
    peptide = PeptideFactory.create()
    peptide_id = peptide.id

    # execute
    found_peptide = Peptide.find_one_by(db_session, id=peptide_id)

    # validate
    assert found_peptide is not None
    assert isinstance(found_peptide, Peptide)
    assert found_peptide.id == peptide.id


@pytest.mark.unit
def test_find_one_by_user_not_found(db_session: Session):
    """Test find_one_by() returns None when user not found."""
    # execute
    found_user = User.find_one_by(db_session, email="nonexistent@example.com")

    # validate
    assert found_user is None


@pytest.mark.unit
def test_find_one_by_digest_not_found(db_session: Session):
    """Test find_one_by() returns None when digest not found."""
    # execute
    found_digest = Digest.find_one_by(
        db_session, id="00000000-0000-0000-0000-000000000000"
    )

    # validate
    assert found_digest is None


@pytest.mark.unit
def test_find_by_digest_by_status_successfully(db_session: Session):
    """Test successfully finding digests by status with Digest.find_by()."""
    # setup
    user = UserFactory.create()
    digest1 = DigestFactory.create(user=user)
    digest2 = DigestFactory.create(user=user)

    # execute
    found_digests = Digest.find_by(db_session, user_id=user.id)

    # validate
    assert len(found_digests) >= 2
    assert all(isinstance(d, Digest) for d in found_digests)
    assert all(d.user_id == user.id for d in found_digests)
    assert digest1.id in [d.id for d in found_digests]
    assert digest2.id in [d.id for d in found_digests]


@pytest.mark.unit
def test_find_by_peptide_by_digest_id_successfully(db_session: Session):
    """Test successfully finding peptides by digest_id with Peptide.find_by()."""
    # setup
    digest = DigestFactory.create()
    peptide1 = PeptideFactory.create(digest=digest)
    peptide2 = PeptideFactory.create(digest=digest)

    # execute
    found_peptides = Peptide.find_by(db_session, digest_id=digest.id)

    # validate
    assert len(found_peptides) >= 2
    assert all(isinstance(p, Peptide) for p in found_peptides)
    assert all(p.digest_id == digest.id for p in found_peptides)
    assert peptide1.id in [p.id for p in found_peptides]
    assert peptide2.id in [p.id for p in found_peptides]


@pytest.mark.unit
def test_find_by_user_not_found(db_session: Session):
    """Test find_by() returns empty list when no users found."""
    # execute
    found_users = User.find_by(db_session, email="nonexistent@example.com")

    # validate
    assert found_users == []
    assert isinstance(found_users, list)


@pytest.mark.unit
def test_find_one_by_or_raise_user_by_email_successfully(db_session: Session):
    """Test successfully finding a user by email with User.find_one_by_or_raise()."""
    # setup
    user = UserFactory.create()
    user_email = user.email

    # execute
    found_user = User.find_one_by_or_raise(db_session, email=user_email)

    # validate
    assert found_user is not None
    assert isinstance(found_user, User)
    assert found_user.id == user.id
    assert found_user.email == user_email


@pytest.mark.unit
def test_find_one_by_or_raise_digest_by_id_successfully(db_session: Session):
    """Test successfully finding a digest by id with Digest.find_one_by_or_raise()."""
    # setup
    digest = DigestFactory.create()
    digest_id = digest.id

    # execute
    found_digest = Digest.find_one_by_or_raise(db_session, id=digest_id)

    # validate
    assert found_digest is not None
    assert isinstance(found_digest, Digest)
    assert found_digest.id == digest.id


@pytest.mark.unit
def test_find_one_by_or_raise_user_not_found(db_session: Session):
    """Test find_one_by_or_raise() raises HTTPException when user not found."""
    # execute and validate
    with pytest.raises(HTTPException) as exc_info:
        User.find_one_by_or_raise(db_session, email="nonexistent@example.com")

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert "User" in exc_info.value.detail
    assert "nonexistent@example.com" in exc_info.value.detail


@pytest.mark.unit
def test_find_one_by_or_raise_digest_not_found(db_session: Session):
    """Test find_one_by_or_raise() raises HTTPException when digest not found."""
    # execute and validate
    with pytest.raises(HTTPException) as exc_info:
        Digest.find_one_by_or_raise(
            db_session, id="00000000-0000-0000-0000-000000000000"
        )

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert "Digest" in exc_info.value.detail
    assert "00000000-0000-0000-0000-000000000000" in exc_info.value.detail


@pytest.mark.unit
def test_update_user_successfully(db_session: Session):
    """Test successfully updating a user record with User.update()."""
    # setup
    user = UserFactory.create()
    original_username = user.username
    original_email = user.email
    new_username = "updated_username"
    new_email = "updated@example.com"

    # execute
    updated_user = User.update(
        db_session,
        user,
        values={"username": new_username, "email": new_email},
    )

    # validate
    assert updated_user is not None
    assert isinstance(updated_user, User)
    assert updated_user.id == user.id  # ID should not change
    assert updated_user.username == new_username
    assert updated_user.email == new_email
    assert updated_user.username != original_username
    assert updated_user.email != original_email


@pytest.mark.unit
def test_update_digest_successfully(db_session: Session):
    """Test successfully updating a digest record with Digest.update()."""
    # setup
    digest = DigestFactory.create()
    original_protein_name = digest.protein_name
    original_status = digest.status
    new_protein_name = "Updated Protein Name"
    new_status = DigestStatusEnum.COMPLETED

    # execute
    updated_digest = Digest.update(
        db_session,
        digest,
        values={"protein_name": new_protein_name, "status": new_status},
    )

    # validate
    assert updated_digest is not None
    assert isinstance(updated_digest, Digest)
    assert updated_digest.id == digest.id
    assert updated_digest.protein_name == new_protein_name
    assert updated_digest.status == new_status
    assert updated_digest.protein_name != original_protein_name
    assert updated_digest.status != original_status


@pytest.mark.unit
def test_update_peptide_successfully(db_session: Session):
    """Test successfully updating a peptide record with Peptide.update()."""
    # setup
    peptide = PeptideFactory.create()
    original_sequence = peptide.sequence
    original_pi = peptide.pi
    new_sequence = "UPDATEDSEQUENCE"
    new_pi = 8.5

    # execute
    updated_peptide = Peptide.update(
        db_session,
        peptide,
        values={"sequence": new_sequence, "pi": new_pi},
    )

    # validate
    assert updated_peptide is not None
    assert isinstance(updated_peptide, Peptide)
    assert updated_peptide.id == peptide.id  # ID should not change
    assert updated_peptide.sequence == new_sequence
    assert updated_peptide.pi == new_pi
    assert updated_peptide.sequence != original_sequence
    assert updated_peptide.pi != original_pi


@pytest.mark.unit
def test_delete_user_successfully(db_session: Session):
    """Test successfully deleting a user record with User.delete()."""
    # setup
    user = UserFactory.create()
    user_id = user.id

    # execute
    User.delete(db_session, user)

    # validate
    found_after = db_session.query(User).filter(User.id == user_id).first()
    assert found_after is None


@pytest.mark.unit
def test_delete_digest_successfully(db_session: Session):
    """Test successfully deleting a digest record with Digest.delete()."""
    # setup
    digest = DigestFactory.create()
    digest_id = digest.id

    # execute
    Digest.delete(db_session, digest)

    # validate
    found_after = db_session.query(Digest).filter(Digest.id == digest_id).first()
    assert found_after is None
