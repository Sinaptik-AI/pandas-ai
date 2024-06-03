from fastapi import APIRouter, Depends
from typing import List

from app.controllers.datasets import DatasetController
from core.factory import Factory

dataset_router = APIRouter()


@dataset_router.get("/")
async def get_datasets(datasets_controller: DatasetController = Depends(Factory().get_datasets_controller)):
    return await datasets_controller.get_all_datasets()
