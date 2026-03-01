"""
Unit tests for the list criteria endpoint.
"""

from unittest.mock import ANY, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.enums import CriteriaEnum


@pytest.mark.unit
def test_list_criteria_success(client: TestClient) -> None:
    """Test successfully getting all criteria with get_all_ordered_by_rank patched."""
    # setup
    mock_criterion = MagicMock()
    mock_criterion.id = "test-criteria-id-1"
    mock_criterion.code = CriteriaEnum.NOT_UNIQUE
    mock_criterion.goal = "Filter duplicate sequences"
    mock_criterion.rationale = "Rationale text"
    mock_criterion.rank = 1
    mock_criterion.is_optional = False
    criteria_records = [mock_criterion]

    with patch(
        "app.api.routes.criteria.Criteria.get_all_ordered_by_rank",
        return_value=criteria_records,
    ) as mock_get_criteria:
        # execute
        response = client.get("/api/v1/criteria")

    # validate
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["id"] == "test-criteria-id-1"
    assert data[0]["code"] == CriteriaEnum.NOT_UNIQUE.value
    assert data[0]["goal"] == "Filter duplicate sequences"
    assert data[0]["rationale"] == "Rationale text"
    assert data[0]["rank"] == 1
    assert data[0]["is_optional"] is False

    mock_get_criteria.assert_called_once_with(ANY)
