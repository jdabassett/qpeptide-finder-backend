from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db.session import get_db

health_router = APIRouter()


@health_router.get("/health")
def health(session: Session = Depends(get_db)):
    """Health check endpoint for container orchestration."""
    try:
        session.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception:
        db_status = "disconnected"

    return {
        "status": "healthy",
        "service": "qpeptide-cutter-backend",
        "database": db_status,
    }
