"""
Unit tests for digest route helpers.
"""

from contextlib import nullcontext

import pytest
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.helpers.digest_route import request_criteria_ids_valid_or_exception
from app.models import Criteria


@pytest.mark.unit
def test_request_criteria_ids_valid_or_exception_all_valid(
    db_session: Session,
    seeded_criteria: list[Criteria],
) -> None:
    """When all criteria_ids exist in the database, the function does not raise."""
    # setup
    criteria_ids = [c.id for c in seeded_criteria]
    assert len(criteria_ids) > 0

    # execute and validate
    with nullcontext():
        request_criteria_ids_valid_or_exception(criteria_ids, db_session)


@pytest.mark.unit
def test_request_criteria_ids_valid_or_exception_empty_list(
    db_session: Session,
) -> None:
    """When criteria_ids is empty, the function does not raise."""
    # execute and validate
    with nullcontext():
        request_criteria_ids_valid_or_exception([], db_session)


@pytest.mark.unit
def test_request_criteria_ids_valid_or_exception_invalid_id_raises(
    db_session: Session,
    seeded_criteria: list[Criteria],
) -> None:
    """When a criteria_id does not exist, the function raises HTTPException 400."""
    valid_ids = [c.id for c in seeded_criteria]
    invalid_id = "00000000-0000-0000-0000-000000000000"
    criteria_ids = [valid_ids[0], invalid_id] if valid_ids else [invalid_id]

    with pytest.raises(HTTPException) as exc_info:
        request_criteria_ids_valid_or_exception(criteria_ids, db_session)

    assert exc_info.value.status_code == 400
    assert "Invalid criteria_id" in exc_info.value.detail
    assert invalid_id in exc_info.value.detail
