from fastapi import APIRouter

from .v1 import v1_router

ee_router = APIRouter()
ee_router.include_router(v1_router, prefix="/v1")


__all__ = ["router"]
