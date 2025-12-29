# """
# Tests for the digest endpoint.
# """

# import uuid
# from unittest.mock import Mock, patch

# import pytest
# from fastapi.testclient import TestClient

# from app.enums import DigestStatusEnum, ProteaseEnum
# from app.models import Digest, User
# from tests.factories import DigestFactory, ProteinDomainFactory, UserFactory


# @pytest.mark.unit
# def test_create_digest_job_success(client: TestClient) -> None:
#     """Test creating a new digest job with all functions patched."""
#     # setup
#     user = UserFactory.build()
#     digest = DigestFactory.build(
#         user_id=user.id,
#         protease=ProteaseEnum.TRYPSIN,
#         protein_name="Test Protein",
#         sequence="MKTAYIAKQRP",
#     )
#     protein_domain = ProteinDomainFactory.build(sequence=digest.sequence)

#     request_data = {
#         "user_email": user.email,
#         "protease": "trypsin",
#         "protein_name": digest.protein_name,
#         "sequence": digest.sequence,
#     }

#     with patch("app.api.routes.digest.get_record_or_exception", return_value=user) as mock_get_user, \
#          patch("app.api.routes.digest.request_within_digest_limit_or_exception") as mock_limit_check, \
#          patch("app.api.routes.digest.request_outside_digest_interval_or_exception") as mock_interval_check, \
#          patch("app.api.routes.digest.create_record", return_value=digest) as mock_create, \
#          patch("app.api.routes.digest.ProteinDomain.from_digest", return_value=protein_domain) as mock_from_digest, \
#          patch("app.api.routes.digest.process_digest_job") as mock_process_job:

#         # execute
#         response = client.post(
#             "/digests/jobs",
#             json=request_data,
#         )

#     # validate
#     assert response.status_code == 201
#     data = response.json()
#     assert data["digest_id"] == digest.id

#     mock_get_user.assert_called_once()
#     mock_limit_check.assert_called_once()
#     mock_interval_check.assert_called_once()
#     mock_create.assert_called_once()
#     mock_from_digest.assert_called_once_with(digest)
#     mock_process_job.assert_not_called()
