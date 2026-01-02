"""
Tests for the digest endpoint.
"""

from unittest.mock import ANY, patch

import pytest
from fastapi import HTTPException, status
from fastapi.testclient import TestClient
from sqlalchemy.exc import IntegrityError

from app.enums import ProteaseEnum
from tests.factories import DigestFactory, ProteinDomainFactory, UserFactory


@pytest.mark.unit
def test_create_digest_job_success(client: TestClient) -> None:
    """Test creating a new digest job with all functions patched."""
    # setup
    user = UserFactory.build()
    digest = DigestFactory.create(user=user)
    protein_domain = ProteinDomainFactory.build()

    request_data = {
        "user_id": user.id,
        "protease": ProteaseEnum.TRYPSIN.value,
        "protein_name": "Test Protein",
        "sequence": "MKTAYIAKQR",
    }

    with (
        patch(
            "app.api.routes.digest.User.find_one_by_or_raise", return_value=user
        ) as mock_get_user,
        patch(
            "app.api.routes.digest.request_within_digest_limit_or_exception"
        ) as mock_limit_check,
        patch(
            "app.api.routes.digest.request_outside_digest_interval_or_exception"
        ) as mock_interval_check,
        patch(
            "app.api.routes.digest.Digest.create", return_value=digest
        ) as mock_create,
        patch(
            "app.api.routes.digest.ProteinDomain.from_digest",
            return_value=protein_domain,
        ) as mock_from_digest,
        patch("app.api.routes.digest.process_digest_job") as mock_process_job,
    ):
        # execute
        response = client.post(
            "/api/v1/digest/job",
            json=request_data,
        )

    # validate
    assert response.status_code == 201
    data = response.json()
    assert data["digest_id"] == digest.id

    mock_get_user.assert_called_once_with(ANY, id=user.id)
    mock_limit_check.assert_called_once()
    mock_interval_check.assert_called_once()
    mock_create.assert_called_once()
    mock_from_digest.assert_called_once_with(digest)
    mock_process_job.assert_called_once_with(protein_domain)


@pytest.mark.unit
def test_create_digest_job_user_not_found(client: TestClient) -> None:
    """Test that 404 is returned when user is not found."""
    # setup
    request_data = {
        "user_id": "fc502bbe-5a1b-4f99-b716-e1970db2aef7",
        "protease": ProteaseEnum.TRYPSIN.value,
        "protein_name": "Test Protein",
        "sequence": "MKTAYIAKQR",
    }

    with patch("app.api.routes.digest.User.find_one_by_or_raise") as mock_get_user:
        mock_get_user.side_effect = HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No User records found with id='fc502bbe-5a1b-4f99-b716-e1970db2aef7'.",
        )

        # execute
        response = client.post(
            "/api/v1/digest/job",
            json=request_data,
        )

    # validate
    assert response.status_code == 404
    data = response.json()
    assert "fc502bbe-5a1b-4f99-b716-e1970db2aef7" in data["detail"]
    mock_get_user.assert_called_once_with(
        ANY, id="fc502bbe-5a1b-4f99-b716-e1970db2aef7"
    )


@pytest.mark.unit
def test_create_digest_job_limit_exceeded(client: TestClient) -> None:
    """Test that 400 is returned when digest limit is exceeded."""
    # setup
    user = UserFactory.build()
    request_data = {
        "user_id": user.id,
        "protease": ProteaseEnum.TRYPSIN.value,
        "protein_name": "Test Protein",
        "sequence": "MKTAYIAKQR",
    }

    with (
        patch(
            "app.api.routes.digest.User.find_one_by_or_raise", return_value=user
        ) as mock_get_user,
        patch(
            "app.api.routes.digest.request_within_digest_limit_or_exception"
        ) as mock_limit_check,
    ):
        mock_limit_check.side_effect = HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User has more than 3 digest jobs. To keep this a free service we limit the number of user records.",
        )

        # execute
        response = client.post(
            "/api/v1/digest/job",
            json=request_data,
        )

    # validate
    assert response.status_code == 400
    data = response.json()
    assert "limit" in data["detail"].lower() or "more than" in data["detail"].lower()
    mock_get_user.assert_called_once_with(ANY, id=user.id)
    mock_limit_check.assert_called_once()


@pytest.mark.unit
def test_create_digest_job_too_soon(client: TestClient) -> None:
    """Test that 429 is returned when digest job is submitted too soon."""
    # setup
    user = UserFactory.build()
    request_data = {
        "user_id": user.id,
        "protease": ProteaseEnum.TRYPSIN.value,
        "protein_name": "Test Protein",
        "sequence": "MKTAYIAKQR",
    }

    with (
        patch(
            "app.api.routes.digest.User.find_one_by_or_raise", return_value=user
        ) as mock_get_user,
        patch(
            "app.api.routes.digest.request_within_digest_limit_or_exception"
        ) as mock_limit_check,
        patch(
            "app.api.routes.digest.request_outside_digest_interval_or_exception"
        ) as mock_interval_check,
    ):
        mock_interval_check.side_effect = HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="A digest job was submitted less than 2 minutes ago.",
        )

        # execute
        response = client.post(
            "/api/v1/digest/job",
            json=request_data,
        )

    # validate
    assert response.status_code == 429
    data = response.json()
    assert "wait" in data["detail"].lower() or "minutes ago" in data["detail"].lower()
    mock_get_user.assert_called_once_with(ANY, id=user.id)
    mock_limit_check.assert_called_once()
    mock_interval_check.assert_called_once()


@pytest.mark.unit
def test_create_digest_job_integrity_error(client: TestClient) -> None:
    """Test that 400 is returned when IntegrityError occurs during creation."""
    # setup
    user = UserFactory.build()
    request_data = {
        "user_id": user.id,
        "protease": ProteaseEnum.TRYPSIN.value,
        "protein_name": "Test Protein",
        "sequence": "MKTAYIAKQR",
    }

    with (
        patch(
            "app.api.routes.digest.User.find_one_by_or_raise", return_value=user
        ) as mock_get_user,
        patch(
            "app.api.routes.digest.request_within_digest_limit_or_exception"
        ) as mock_limit_check,
        patch(
            "app.api.routes.digest.request_outside_digest_interval_or_exception"
        ) as mock_interval_check,
        patch("app.api.routes.digest.Digest.create") as mock_create,
    ):
        mock_create.side_effect = IntegrityError(
            "statement", "params", Exception("Database constraint violation")
        )

        # execute
        response = client.post(
            "/api/v1/digest/job",
            json=request_data,
        )

    # validate
    assert response.status_code == 400
    data = response.json()
    assert (
        "database constraint violation" in data["detail"].lower()
        or "constraint" in data["detail"].lower()
    )
    mock_get_user.assert_called_once_with(ANY, id=user.id)
    mock_limit_check.assert_called_once()
    mock_interval_check.assert_called_once()
    mock_create.assert_called_once()


@pytest.mark.unit
def test_create_digest_job_value_error(client: TestClient) -> None:
    """Test that 400 is returned when ValueError occurs during creation."""
    # setup
    user = UserFactory.build()
    request_data = {
        "user_id": user.id,
        "protease": ProteaseEnum.TRYPSIN.value,
        "protein_name": "Test Protein",
        "sequence": "MKTAYIAKQR",
    }

    with (
        patch(
            "app.api.routes.digest.User.find_one_by_or_raise", return_value=user
        ) as mock_get_user,
        patch(
            "app.api.routes.digest.request_within_digest_limit_or_exception"
        ) as mock_limit_check,
        patch(
            "app.api.routes.digest.request_outside_digest_interval_or_exception"
        ) as mock_interval_check,
        patch("app.api.routes.digest.Digest.create") as mock_create,
    ):
        mock_create.side_effect = ValueError("Invalid digest job data")

        # execute
        response = client.post(
            "/api/v1/digest/job",
            json=request_data,
        )

    # validate
    assert response.status_code == 400
    data = response.json()
    assert "invalid digest job data" in data["detail"].lower()
    mock_get_user.assert_called_once_with(ANY, id=user.id)
    mock_limit_check.assert_called_once()
    mock_interval_check.assert_called_once()
    mock_create.assert_called_once()
