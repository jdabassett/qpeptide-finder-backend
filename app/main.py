from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.health import health_router
from app.api.routes.users import users_router
from app.core.config import settings

app = FastAPI(title="QPeptide Cutter Backend", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(users_router, prefix=settings.API_V1_PREFIX)
