from fastapi import APIRouter

from .datasets import dataset_router

datasets_router = APIRouter()
datasets_router.include_router(dataset_router, tags=["Dataset"])

__all__ = ["datasets_router"]
