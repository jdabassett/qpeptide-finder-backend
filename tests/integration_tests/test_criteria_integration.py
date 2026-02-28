"""
Integration tests for the list criteria endpoint.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models import Criteria


@pytest.mark.integration
def test_list_criteria_success(
    client: TestClient,
    db_session: Session,
) -> None:
    """Test successfully getting all criteria with real database operations."""
    # setup: criteria are seeded by db_session when table is empty
    expected_count = db_session.query(Criteria).count()
    assert expected_count > 0, "Criteria should be seeded by db_session fixture"

    # execute
    response = client.get("/api/v1/criteria")

    # validate
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == expected_count

    for item in data:
        assert "id" in item
        assert "code" in item
        assert "goal" in item
        assert "rationale" in item
        assert "rank" in item
        assert "is_optional" in item
