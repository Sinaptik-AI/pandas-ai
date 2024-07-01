from app.models import Logs
from core.repository import BaseRepository
from core.database.transactional import Propagation, Transactional
from sqlalchemy.future import select
from ee.app.schemas.responses.logs import LogResponse
from typing import List
from sqlalchemy import func


class LogsRepository(BaseRepository[Logs]):
    """
    Logs repository provides all the Logs operations for the Logs model.
    """
    @Transactional(propagation=Propagation.REQUIRED)
    async def add_log(
        self, user_id: str, api_key: str, json_log: str, query: str, 
        success: bool = True, execution_time: float = 0.0
    ):  
        new_log = Logs(
            user_id=user_id,
            api_key=api_key,
            json_log=json_log,
            query=query,
            success=success,
            execution_time=execution_time
        )
        self.session.add(new_log)
        return new_log
    
    async def get_user_logs(self, user_id: str, skip: int = 0, limit: int = 10) -> List[LogResponse]:
        query = select(Logs).where(Logs.user_id == user_id).offset(skip).limit(limit)
        
        result = await self.session.execute(query)
        return result.unique().scalars().all()



    async def get_logs_count(self, user_id: str) -> int:
        query = select(func.count(Logs.id)).where(Logs.user_id == user_id)

        result = await self.session.execute(query)
        return result.scalar_one()