# """
# Unit tests for the get digest peptides endpoint.
# """

# from unittest.mock import ANY, MagicMock, patch

# import pytest
# from fastapi import HTTPException, status
# from fastapi.testclient import TestClient
# from pydantic import ValidationError
# from sqlalchemy.exc import DatabaseError, OperationalError

# from app.schemas.digest import CriteriaResponse, DigestPeptidesResponse, PeptideResponse
# from tests.factories import CriteriaFactory, DigestFactory, PeptideFactory, UserFactory


# @pytest.mark.unit
# def test_get_digest_peptides_by_id_success(client: TestClient) -> None:
#     """Test successfully getting peptides for a digest with all functions patched."""
#     # setup
#     user = UserFactory.build()
#     digest = DigestFactory.build(user=user)
#     peptide1 = PeptideFactory.build(digest=digest, rank=1)
#     peptide2 = PeptideFactory.build(digest=digest, rank=2)
#     peptides = [peptide1, peptide2]
#     criteria = [CriteriaFactory.build(rank=i) for i in range(1, 15)]

#     response_data = DigestPeptidesResponse(
#         digest_id=digest.id,
#         peptides=[
#             PeptideResponse(
#                 id=peptide1.id,
#                 sequence=peptide1.sequence,
#                 position=peptide1.position,
#                 pi=peptide1.pi,
#                 charge_state=peptide1.charge_state,
#                 max_kd_score=peptide1.max_kd_score,
#                 rank=peptide1.rank,
#                 criteria_ranks=[],
#             ),
#             PeptideResponse(
#                 id=peptide2.id,
#                 sequence=peptide2.sequence,
#                 position=peptide2.position,
#                 pi=peptide2.pi,
#                 charge_state=peptide2.charge_state,
#                 max_kd_score=peptide2.max_kd_score,
#                 rank=peptide2.rank,
#                 criteria_ranks=[],
#             ),
#         ],
#         criteria=[CriteriaResponse.model_validate(c) for c in criteria],
#     )

#     with (
#         patch(
#             "app.api.routes.digest.User.find_one_by_or_raise", return_value=user
#         ) as mock_get_user,
#         patch(
#             "app.api.routes.digest.Digest.find_one_by_or_raise", return_value=digest
#         ) as mock_get_digest,
#         patch(
#             "app.api.routes.digest.Peptide.find_by_digest_id_ordered_by_rank_or_raise",
#             return_value=peptides,
#         ) as mock_get_peptides,
#         patch(
#             "app.api.routes.digest.Criteria.get_all_ordered_by_rank",
#             return_value=criteria,
#         ) as mock_get_criteria,
#         patch(
#             "app.api.routes.digest.DigestPeptidesResponse.from_peptides",
#             return_value=response_data,
#         ) as mock_from_peptides,
#     ):
#         # execute
#         response = client.get(f"/api/v1/digest/{user.id}/{digest.id}/peptides")

#     # validate
#     assert response.status_code == 200
#     data = response.json()
#     assert data["digest_id"] == digest.id
#     assert "peptides" in data
#     assert "criteria" in data

#     mock_get_user.assert_called_once_with(ANY, id=user.id)
#     mock_get_digest.assert_called_once_with(ANY, user_id=user.id, id=digest.id)
#     mock_get_peptides.assert_called_once_with(ANY, digest_id=digest.id)
#     mock_get_criteria.assert_called_once_with(ANY)
#     mock_from_peptides.assert_called_once_with(digest.id, peptides, criteria)


# @pytest.mark.unit
# def test_get_digest_peptides_user_not_found(client: TestClient) -> None:
#     """Test that 404 is returned when user is not found."""
#     # setup
#     user_id = "non-existent-user-id"
#     digest_id = "non-existent-digest-id"

#     with patch("app.api.routes.digest.User.find_one_by_or_raise") as mock_get_user:
#         mock_get_user.side_effect = HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=f"No User records found with id={user_id!r}.",
#         )

#         # execute
#         response = client.get(f"/api/v1/digest/{user_id}/{digest_id}/peptides")

#     # validate
#     assert response.status_code == 404
#     data = response.json()
#     assert user_id in data["detail"]
#     mock_get_user.assert_called_once_with(ANY, id=user_id)


# @pytest.mark.unit
# def test_get_digest_peptides_digest_not_found(client: TestClient) -> None:
#     """Test that 404 is returned when digest is not found."""
#     # setup
#     user = UserFactory.build()
#     digest_id = "non-existent-digest-id"

#     with (
#         patch(
#             "app.api.routes.digest.User.find_one_by_or_raise", return_value=user
#         ) as mock_get_user,
#         patch("app.api.routes.digest.Digest.find_one_by_or_raise") as mock_get_digest,
#     ):
#         mock_get_digest.side_effect = HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=f"No Digest records found with user_id={user.id!r}, id={digest_id!r}.",
#         )

#         # execute
#         response = client.get(f"/api/v1/digest/{user.id}/{digest_id}/peptides")

#     # validate
#     assert response.status_code == 404
#     data = response.json()
#     assert digest_id in data["detail"] or user.id in data["detail"]
#     mock_get_user.assert_called_once_with(ANY, id=user.id)
#     mock_get_digest.assert_called_once_with(ANY, user_id=user.id, id=digest_id)


# @pytest.mark.unit
# def test_get_digest_peptides_digest_belongs_to_different_user(client: TestClient) -> None:
#     """Test that 404 is returned when digest doesn't belong to user."""
#     # setup
#     user = UserFactory.build()
#     other_user = UserFactory.build()
#     digest = DigestFactory.build(user=other_user)

#     with (
#         patch(
#             "app.api.routes.digest.User.find_one_by_or_raise", return_value=user
#         ) as mock_get_user,
#         patch("app.api.routes.digest.Digest.find_one_by_or_raise") as mock_get_digest,
#     ):
#         mock_get_digest.side_effect = HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=f"No Digest records found with user_id={user.id!r}, id={digest.id!r}.",
#         )

#         # execute
#         response = client.get(f"/api/v1/digest/{user.id}/{digest.id}/peptides")

#     # validate
#     assert response.status_code == 404
#     data = response.json()
#     assert user.id in data["detail"] or digest.id in data["detail"]
#     mock_get_user.assert_called_once_with(ANY, id=user.id)
#     mock_get_digest.assert_called_once_with(ANY, user_id=user.id, id=digest.id)


# @pytest.mark.unit
# def test_get_digest_peptides_no_peptides_found(client: TestClient) -> None:
#     """Test that 404 is returned when no peptides are found."""
#     # setup
#     user = UserFactory.build()
#     digest = DigestFactory.build(user=user)

#     with (
#         patch(
#             "app.api.routes.digest.User.find_one_by_or_raise", return_value=user
#         ) as mock_get_user,
#         patch(
#             "app.api.routes.digest.Digest.find_one_by_or_raise", return_value=digest
#         ) as mock_get_digest,
#         patch(
#             "app.api.routes.digest.Peptide.find_by_digest_id_ordered_by_rank_or_raise"
#         ) as mock_get_peptides,
#     ):
#         mock_get_peptides.side_effect = HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=f"No Peptide records found with digest_id={digest.id!r}.",
#         )

#         # execute
#         response = client.get(f"/api/v1/digest/{user.id}/{digest.id}/peptides")

#     # validate
#     assert response.status_code == 404
#     data = response.json()
#     assert digest.id in data["detail"]
#     mock_get_user.assert_called_once_with(ANY, id=user.id)
#     mock_get_digest.assert_called_once_with(ANY, user_id=user.id, id=digest.id)
#     mock_get_peptides.assert_called_once_with(ANY, digest_id=digest.id)


# @pytest.mark.unit
# def test_get_digest_peptides_database_error(client: TestClient) -> None:
#     """Test that 500 is returned when database error occurs."""
#     # setup
#     user = UserFactory.build()
#     digest = DigestFactory.build(user=user)
#     peptides = [PeptideFactory.build(digest=digest)]

#     with (
#         patch(
#             "app.api.routes.digest.User.find_one_by_or_raise", return_value=user
#         ) as mock_get_user,
#         patch(
#             "app.api.routes.digest.Digest.find_one_by_or_raise", return_value=digest
#         ) as mock_get_digest,
#         patch(
#             "app.api.routes.digest.Peptide.find_by_digest_id_ordered_by_rank_or_raise",
#             return_value=peptides,
#         ) as mock_get_peptides,
#         patch("app.api.routes.digest.Criteria.get_all_ordered_by_rank") as mock_get_criteria,
#     ):
#         mock_get_criteria.side_effect = DatabaseError(
#             "Database connection failed", None, None
#         )

#         # execute
#         response = client.get(f"/api/v1/digest/{user.id}/{digest.id}/peptides")

#     # validate
#     assert response.status_code == 500
#     data = response.json()
#     assert "database error" in data["detail"].lower()
#     mock_get_user.assert_called_once_with(ANY, id=user.id)
#     mock_get_digest.assert_called_once_with(ANY, user_id=user.id, id=digest.id)
#     mock_get_peptides.assert_called_once_with(ANY, digest_id=digest.id)
#     mock_get_criteria.assert_called_once_with(ANY)


# @pytest.mark.unit
# def test_get_digest_peptides_operational_error(client: TestClient) -> None:
#     """Test that 500 is returned when operational error occurs."""
#     # setup
#     user = UserFactory.build()
#     digest = DigestFactory.build(user=user)
#     peptides = [PeptideFactory.build(digest=digest)]

#     with (
#         patch(
#             "app.api.routes.digest.User.find_one_by_or_raise", return_value=user
#         ) as mock_get_user,
#         patch(
#             "app.api.routes.digest.Digest.find_one_by_or_raise", return_value=digest
#         ) as mock_get_digest,
#         patch(
#             "app.api.routes.digest.Peptide.find_by_digest_id_ordered_by_rank_or_raise",
#             return_value=peptides,
#         ) as mock_get_peptides,
#         patch("app.api.routes.digest.Criteria.get_all_ordered_by_rank") as mock_get_criteria,
#     ):
#         mock_get_criteria.side_effect = OperationalError(
#             "Connection lost", None, None
#         )

#         # execute
#         response = client.get(f"/api/v1/digest/{user.id}/{digest.id}/peptides")

#     # validate
#     assert response.status_code == 500
#     data = response.json()
#     assert "database error" in data["detail"].lower()
#     mock_get_user.assert_called_once_with(ANY, id=user.id)
#     mock_get_digest.assert_called_once_with(ANY, user_id=user.id, id=digest.id)
#     mock_get_peptides.assert_called_once_with(ANY, digest_id=digest.id)
#     mock_get_criteria.assert_called_once_with(ANY)


# @pytest.mark.unit
# def test_get_digest_peptides_validation_error(client: TestClient) -> None:
#     """Test that 500 is returned when validation error occurs."""
#     # setup
#     user = UserFactory.build()
#     digest = DigestFactory.build(user=user)
#     peptides = [PeptideFactory.build(digest=digest)]
#     criteria = [CriteriaFactory.build()]

#     with (
#         patch(
#             "app.api.routes.digest.User.find_one_by_or_raise", return_value=user
#         ) as mock_get_user,
#         patch(
#             "app.api.routes.digest.Digest.find_one_by_or_raise", return_value=digest
#         ) as mock_get_digest,
#         patch(
#             "app.api.routes.digest.Peptide.find_by_digest_id_ordered_by_rank_or_raise",
#             return_value=peptides,
#         ) as mock_get_peptides,
#         patch(
#             "app.api.routes.digest.Criteria.get_all_ordered_by_rank", return_value=criteria
#         ) as mock_get_criteria,
#         patch("app.api.routes.digest.DigestPeptidesResponse.from_peptides") as mock_from_peptides,
#     ):
#         mock_from_peptides.side_effect = ValidationError.from_exception_data(
#             "DigestPeptidesResponse", [{"type": "missing", "loc": ("digest_id",), "msg": "Field required"}]
#         )

#         # execute
#         response = client.get(f"/api/v1/digest/{user.id}/{digest.id}/peptides")

#     # validate
#     assert response.status_code == 500
#     data = response.json()
#     assert "formatting the response" in data["detail"].lower() or "error occurred" in data["detail"].lower()
#     mock_get_user.assert_called_once_with(ANY, id=user.id)
#     mock_get_digest.assert_called_once_with(ANY, user_id=user.id, id=digest.id)
#     mock_get_peptides.assert_called_once_with(ANY, digest_id=digest.id)
#     mock_get_criteria.assert_called_once_with(ANY)
#     mock_from_peptides.assert_called_once_with(digest.id, peptides, criteria)


# @pytest.mark.unit
# def test_get_digest_peptides_attribute_error(client: TestClient) -> None:
#     """Test that 500 is returned when attribute error occurs (missing relationship data)."""
#     # setup
#     user = UserFactory.build()
#     digest = DigestFactory.build(user=user)
#     peptide = PeptideFactory.build(digest=digest)
#     # Create a mock peptide without criteria relationship
#     peptide_mock = MagicMock()
#     peptide_mock.criteria = None  # Missing relationship
#     peptides = [peptide_mock]
#     criteria = [CriteriaFactory.build()]

#     with (
#         patch(
#             "app.api.routes.digest.User.find_one_by_or_raise", return_value=user
#         ) as mock_get_user,
#         patch(
#             "app.api.routes.digest.Digest.find_one_by_or_raise", return_value=digest
#         ) as mock_get_digest,
#         patch(
#             "app.api.routes.digest.Peptide.find_by_digest_id_ordered_by_rank_or_raise",
#             return_value=peptides,
#         ) as mock_get_peptides,
#         patch(
#             "app.api.routes.digest.Criteria.get_all_ordered_by_rank", return_value=criteria
#         ) as mock_get_criteria,
#         patch("app.api.routes.digest.DigestPeptidesResponse.from_peptides") as mock_from_peptides,
#     ):
#         mock_from_peptides.side_effect = AttributeError("'NoneType' object has no attribute 'rank'")

#         # execute
#         response = client.get(f"/api/v1/digest/{user.id}/{digest.id}/peptides")

#     # validate
#     assert response.status_code == 500
#     data = response.json()
#     assert "processing peptide data" in data["detail"].lower() or "error occurred" in data["detail"].lower()
#     mock_get_user.assert_called_once_with(ANY, id=user.id)
#     mock_get_digest.assert_called_once_with(ANY, user_id=user.id, id=digest.id)
#     mock_get_peptides.assert_called_once_with(ANY, digest_id=digest.id)
#     mock_get_criteria.assert_called_once_with(ANY)
#     mock_from_peptides.assert_called_once_with(digest.id, peptides, criteria)


# @pytest.mark.unit
# def test_get_digest_peptides_unexpected_error(client: TestClient) -> None:
#     """Test that 500 is returned when unexpected error occurs."""
#     # setup
#     user = UserFactory.build()
#     digest = DigestFactory.build(user=user)

#     with (
#         patch("app.api.routes.digest.User.find_one_by_or_raise") as mock_get_user,
#     ):
#         mock_get_user.side_effect = RuntimeError("Unexpected runtime error")

#         # execute
#         response = client.get(f"/api/v1/digest/{user.id}/{digest.id}/peptides")

#     # validate
#     assert response.status_code == 500
#     data = response.json()
#     assert "unexpected error" in data["detail"].lower()
#     mock_get_user.assert_called_once_with(ANY, id=user.id)
