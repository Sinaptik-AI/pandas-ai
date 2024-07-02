from fastapi import APIRouter
from .logs import logs_router

v1_router = APIRouter()

v1_router.include_router(
    logs_router, prefix="/logs", tags=["Logs"]
)
