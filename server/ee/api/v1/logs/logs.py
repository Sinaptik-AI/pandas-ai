from fastapi import APIRouter, Depends, Query, Path
from uuid import UUID
from ee.app.controllers.logs import LogsController
from core.factory import Factory
from app.schemas.responses.users import UserInfo
from core.fastapi.dependencies.current_user import get_current_user
from ee.app.schemas.responses.logs import LogsResponseModel
from core.fastapi.dependencies.check_logs_feature import check_logs_feature

log_router = APIRouter()


@log_router.get(
    "/", response_model=LogsResponseModel, dependencies=[Depends(check_logs_feature)]
)
async def get_logs(
    skip: int = Query(0, alias="skip", description="Number of logs to skip"),
    limit: int = Query(10, alias="limit", description="Max number of logs to return"),
    user: UserInfo = Depends(get_current_user),
    logs_controller: LogsController = Depends(Factory().get_logs_controller),
):
    return await logs_controller.get_logs(user.id, skip, limit)


@log_router.get("/{log_id}")
async def get_log(
    log_id: UUID = Path(..., description="ID of the log"),
    logs_controller: LogsController = Depends(Factory().get_logs_controller),
):
    return await logs_controller.get_log(log_id)
