import logging
from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import User
from app.schemas.user import UserCreate, UserResponse

logger = logging.getLogger(__name__)

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
    logger.info(f"Received user create/retrieve request: email={user_request.email}")

    existing_user: User | None = User.find_one_by(session, email=user_request.email)

    try:
        if existing_user:
            updated_user: User = User.update(
                session,
                existing_user,
                values={
                    "username": user_request.username,
                    "updated_at": datetime.now(UTC),
                },
            )
            logger.info(f"User successfully updated: email={updated_user.email}")
            return updated_user

        new_user: User = User.create(
            session,
            flush=True,
            username=user_request.username,
            email=user_request.email,
        )
        logger.info(f"User successfully created: email={new_user.email}")
        return new_user

    except IntegrityError as e:
        logger.error(
            f"Database constraint violation while creating/updating user: "
            f"email={user_request.email}, error={str(e)}"
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create or update user due to database constraint violation. Error: {str(e)}",
        ) from e
    except ValueError as e:
        logger.error(f"Invalid user data: email={user_request.email}, error={str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid user data: {str(e)}",
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
    logger.info(f"Received user delete request: email={email}")
    user: User = User.find_one_by_or_raise(session, email=email)

    try:
        User.delete(session, user)
        logger.info(f"User deleted successfully: email={email}")
        return
    except IntegrityError as e:
        logger.error(
            f"Database constraint violation while deleting user: email={email}, "
            f"error={str(e)}"
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to delete user due to database constraint violation. Error: {str(e)}",
        ) from e
    except Exception as e:
        logger.exception(
            f"Unexpected error while deleting user: email={email}, error={str(e)}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred while deleting user: {str(e)}",
        ) from e
