from fastapi import APIRouter, Depends
from app.controllers.logs import LogsController
from core.factory import Factory

log_router = APIRouter()

@log_router.get("/")
async def get_logs(logs_controller: LogsController = Depends(Factory().get_logs_controller)):
    return await logs_controller.get_logs()
