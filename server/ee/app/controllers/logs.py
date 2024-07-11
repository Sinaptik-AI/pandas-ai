from fastapi import status, HTTPException
from app.models import Logs
from ee.app.repositories import LogsRepository
from core.controller import BaseController
from ee.app.schemas.responses.logs import LogsResponseModel, LogResponseModel

class LogsController(BaseController[Logs]):
    def __init__(
        self, 
        logs_repository: LogsRepository,
    ):
        super().__init__(model=Logs, repository=logs_repository)
        self.logs_repository = logs_repository

    async def get_logs(self, user_id: str, skip: int = 0, limit: int = 10):
        logs = await self.logs_repository.get_user_logs(user_id=user_id, skip=skip, limit=limit)
        logs_count = await self.logs_repository.get_logs_count(user_id=user_id)

        if not logs:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No logs found for this user.")

        return LogsResponseModel(message="Logs returned successfully", logs_count=logs_count, logs=logs)
    

    async def get_log(self, log_id: str):
        log = await self.logs_repository.get_by_id(id=log_id)

        if not log:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No log found")

        return LogResponseModel(message="Log returned successfully", log=log)