from fastapi import status, HTTPException
from app.models import Logs
from app.repositories import LogsRepository
from core.controller import BaseController
from core.exceptions.base import NotFoundException

class LogsController(BaseController[Logs]):
    def __init__(
        self, 
        logs_repository: LogsRepository,
    ):
        super().__init__(model=Logs, repository=logs_repository)
        self.logs_repository = logs_repository

    async def get_logs(self):
        # logs = await self.get_all()

        # if not logs:
        #     raise NotFoundException(
        #         "No logs found. Please restart the server and try again"
        #     )

        return {"Logs", {"logs"}}
