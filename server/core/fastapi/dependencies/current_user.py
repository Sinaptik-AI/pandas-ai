from fastapi import Depends, Request

from app.controllers.user import UserController
from app.schemas.responses.users import UserInfo
from core.factory import Factory


async def get_current_user(
    request: Request,
    user_controller: UserController = Depends(Factory().get_user_controller),
) -> UserInfo:
    return await user_controller.me()
