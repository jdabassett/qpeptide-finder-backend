from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import Select, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse

users_router = APIRouter(prefix="/users", tags=["users"])


@users_router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_or_retrieve_user(
    user_request: UserCreate, session: Session = Depends(get_db)
):
    """
    Create or retrieve user record base on email address.

    - username: User's name (3-50 characters)
    - email: Valid email address
    """
    query: Select = select(User).where(User.email == user_request.email)
    existing_user: User | None = session.scalar(query)

    if existing_user:
        existing_user.username = user_request.username
        existing_user.updated_at = datetime.now(UTC)
        session.commit()
        session.refresh(existing_user)
        return existing_user

    try:
        new_user: User = User(username=user_request.username, email=user_request.email)
        session.add(new_user)
        session.commit()
        session.refresh(new_user)
        return new_user
    except IntegrityError as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create or retrieve user due to database constraint violation. Error:{str(e)}",
        ) from e
    except ValueError as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid user data: {str(e)}",
        ) from e
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}",
        ) from e
