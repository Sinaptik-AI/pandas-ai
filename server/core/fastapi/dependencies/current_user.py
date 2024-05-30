from fastapi import Depends, Request

from app.controllers.user import UserController
from core.factory import Factory


async def get_current_user(
    request: Request,
    user_controller: UserController = Depends(Factory().get_user_controller),
):
    return await user_controller.get_by_id(request.user.id)
