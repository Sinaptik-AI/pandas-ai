from app.models import Logs
from core.repository import BaseRepository
from uuid import UUID


class LogsRepository(BaseRepository[Logs]):
    """
    Logs repository provides all the Logs operations for the Logs model.
    """

    async def add_log(
        self,
        user_id: str,
    ):
        return None