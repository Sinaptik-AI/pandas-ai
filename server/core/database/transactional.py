from enum import Enum
from functools import wraps

from core.database import session


class Propagation(Enum):
    REQUIRED = "required"
    REQUIRED_NEW = "required_new"


class Transactional:
    def __init__(self, propagation: Propagation = Propagation.REQUIRED):
        self.propagation = propagation

    def __call__(self, function):
        @wraps(function)
        async def decorator(*args, **kwargs):
            try:
                if self.propagation == Propagation.REQUIRED:
                    result = await self._run_required(
                        function=function,
                        args=args,
                        kwargs=kwargs,
                    )
                elif self.propagation == Propagation.REQUIRED_NEW:
                    result = await self._run_required_new(
                        function=function,
                        args=args,
                        kwargs=kwargs,
                    )
                else:
                    result = await self._run_required(
                        function=function,
                        args=args,
                        kwargs=kwargs,
                    )
            except Exception as exception:
                await session.rollback()
                raise exception

            return result

        return decorator

    async def _run_required(self, function, args, kwargs) -> None:
        result = await function(*args, **kwargs)
        await session.commit()
        return result

    async def _run_required_new(self, function, args, kwargs) -> None:
        session.begin()
        result = await function(*args, **kwargs)
        await session.commit()
        return result
