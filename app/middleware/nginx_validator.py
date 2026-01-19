import logging

from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class NginxValidatorMiddleware(BaseHTTPMiddleware):
    """
    Middleware to ensure requests come through nginx proxy.
    Rejects direct access to backend endpoints.

    Health endpoint is exempted to allow Docker healthchecks.
    """

    async def dispatch(self, request: Request, call_next):
        client_host = request.client.host if request.client else "unknown"
        if request.url.path == "/health":
            forwarded_by = request.headers.get("X-Forwarded-By")
            if forwarded_by == "nginx" or client_host in (
                "127.0.0.1",
                "localhost",
                "::1",
            ):
                response = await call_next(request)
                return response
            else:
                logger.warning(f"Direct access attempt to /health from {client_host}")
                return JSONResponse(
                    status_code=status.HTTP_403_FORBIDDEN,
                    content={"detail": "Direct access not allowed. Use nginx proxy."},
                )

        if request.url.path.startswith("/api"):
            forwarded_by = request.headers.get("X-Forwarded-By")
            if forwarded_by != "nginx":
                logger.warning(
                    f"Direct access attempt to {request.url.path} from {client_host}"
                )
                return JSONResponse(
                    status_code=status.HTTP_403_FORBIDDEN,
                    content={"detail": "Direct access not allowed. Use nginx proxy."},
                )

        response = await call_next(request)
        return response
