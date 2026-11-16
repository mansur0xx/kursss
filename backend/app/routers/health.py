from fastapi import APIRouter

from app.core.config import settings
from app.schemas.health import HealthRead

router = APIRouter(prefix="/api")


@router.get("/health", response_model=HealthRead)
async def get_health():
    return HealthRead(
        status="ok",
        environment=settings.environment
    )
