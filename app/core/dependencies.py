import logging

from fastapi import Header, HTTPException, status

from app.core import settings

logger = logging.getLogger(__name__)


async def verify_internal_api_key(
    x_api_key: str | None = Header(None, alias="X-API-Key")
) -> str:
    """
    Verify that the request includes a valid internal API key.
    Used for nginx-to-backend authentication.

    Args:
        x_api_key: API key from X-API-Key header

    Returns:
        The validated API key

    Raises:
        HTTPException: If API key is invalid or missing
    """
    if not settings.API_KEY:
        logger.debug("API_KEY not set, skipping API key validation")
        return "no-key-set"

    if not x_api_key:
        logger.warning("API key missing from request")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Missing API key. X-API-Key header required.",
        )

    if x_api_key != settings.API_KEY:
        logger.warning("Invalid API key attempt from request")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid API key"
        )

    logger.debug("API key validated successfully")
    return x_api_key
