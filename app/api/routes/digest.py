# TODO revisit when other endpoints are working again.
# from fastapi import APIRouter, Depends, HTTPException, status
# from sqlalchemy import Select, select
# from sqlalchemy.exc import IntegrityError
# from sqlalchemy.orm import Session

# from app.db.session import get_db
# from app.enums import DigestStatusEnum
# from app.models import Digest, User
# from app.schemas.digest import DigestJobRequest, DigestJobResponse

# digest_router = APIRouter(prefix="/digests", tags=["digests"])


# @digest_router.post(
#     "/jobs",
#     response_model=DigestJobResponse,
#     status_code=status.HTTP_201_CREATED,
# )
# def create_digest_job(
#     job_request: DigestJobRequest, session: Session = Depends(get_db)
# ):
#     """
#     Create a new digest job.

#     - user_email: Email address of the user
#     - protein: Protein information (name, sequence, optional accession numbers)
#     - digest: Digest configuration (proteases and ordering strategy)

#     Returns the digest job ID and status.
#     """
#     try:
#         query: Select = select(User).where(User.email == job_request.user_email)
#         user: User | None = session.scalar(query)

#         if not user:
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail=f"User with email {job_request.user_email} not found. Please create a user first.",
#             )

#         protein = Protein(
#             uni_prot_accession_number=job_request.protein.uni_prot_accession_number,
#             ncbi_protein_accession=job_request.protein.ncbi_protein_accession,
#             protein_name=job_request.protein.protein_name,
#             sequence=job_request.protein.sequence_to_str(),
#             user_id=user.id,
#         )
#         session.add(protein)
#         session.flush()

#         digest = Digest(
#             status=DigestStatusEnum.PROCESSING,
#             user_id=user.id,
#             protein_id=protein.id,
#         )
#         session.add(digest)
#         session.flush()

#         for protease_action in job_request.digest.proteases:
#             digest_protease = DigestProtease(
#                 digest_id=digest.id,
#                 protease=protease_action.protease,
#                 order=protease_action.order,
#             )
#             session.add(digest_protease)

#         session.commit()
#         session.refresh(digest)

#         # TODO: generate backgroud task here

#         return DigestJobResponse(
#             digest_id=digest.id,
#         )

#     except IntegrityError as e:
#         session.rollback()
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail=f"Failed to create digest job due to database constraint violation. Error: {str(e)}",
#         ) from e
#     except ValueError as e:
#         session.rollback()
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail=f"Invalid digest job data: {str(e)}",
#         ) from e
#     except Exception as e:
#         session.rollback()
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"An unexpected error occurred while creating digest job: {str(e)}",
#         ) from e
