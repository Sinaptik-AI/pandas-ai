from fastapi import APIRouter

from .logs import log_router

logs_router = APIRouter()
logs_router.include_router(log_router, tags=["Logs"])

__all__ = ["logs_router"]
