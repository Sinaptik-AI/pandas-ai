from fastapi import APIRouter, Depends

from app.schemas.extras.health import Health
from core.config import config
from core.fastapi.dependencies.authentication import AuthenticationRequired

health_router = APIRouter()


@health_router.get("/", dependencies=[Depends(AuthenticationRequired)])
async def health() -> Health:
    return Health(version=config.RELEASE_VERSION, status="Healthy")
