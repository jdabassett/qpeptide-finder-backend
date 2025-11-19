from fastapi import APIRouter
from sqlalchemy import text

health_router = APIRouter()


@health_router.get("/health")
async def health():
    """Health check endpoint for container orchestration."""
    try:
        from app.db.session import engine

        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception:
        db_status = "disconnected"

    return {
        "status": "healthy",
        "service": "qpeptide-cutter-backend",
        "database": db_status,
    }
