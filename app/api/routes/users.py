from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.helpers import (
    create_record,
    delete_record,
    get_record,
    get_record_or_exception,
    update_record,
)
from app.models import User
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
    existing_user: User | None = get_record(session, User, email=user_request.email)

    try:
        if existing_user:
            return update_record(
                session,
                existing_user,
                username=user_request.username,
                updated_at=datetime.now(UTC),
            )

        return create_record(
            session,
            User,
            username=user_request.username,
            email=user_request.email,
            flush=True,
        )

    except AttributeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid field name: {str(e)}",
        ) from e
    except IntegrityError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create or retrieve user due to database constraint violation. Error:{str(e)}",
        ) from e
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid user data: {str(e)}",
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}",
        ) from e


@users_router.delete("/email/{email}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user_by_email(email: str, session: Session = Depends(get_db)):
    """
    Delete a user by email address.

    - email: Email address of the user to delete
    - Returns 204 No Content on success
    - Returns 404 if user not found
    - Returns 400/500 for other errors
    """
    user: User = get_record_or_exception(session, User, email=email)

    try:
        delete_record(session, user)
        return
    except IntegrityError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to delete user due to database constraint violation. Error: {str(e)}",
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred while deleting user: {str(e)}",
        ) from e
