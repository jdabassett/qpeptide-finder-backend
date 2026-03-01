import logging

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.dependencies import verify_internal_api_key
from app.db.session import get_db
from app.models import Criteria
from app.schemas.digest import CriteriaResponse

logger = logging.getLogger(__name__)

criteria_router = APIRouter(prefix="/criteria", tags=["criteria"])


@criteria_router.get(
    "",
    response_model=list[CriteriaResponse],
    status_code=status.HTTP_200_OK,
)
def list_criteria(
    api_key: str = Depends(verify_internal_api_key),
    session: Session = Depends(get_db),
) -> list[CriteriaResponse]:
    """
    Return all QPeptide criteria (code, goal, rationale, is_optional, id, rank).
    """
    criteria_records = Criteria.get_all_ordered_by_rank(session)
    return [CriteriaResponse.model_validate(c) for c in criteria_records]
