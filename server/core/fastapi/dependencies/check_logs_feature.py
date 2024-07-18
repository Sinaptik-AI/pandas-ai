from fastapi import Depends
from app.schemas.responses.users import UserInfo
from core.fastapi.dependencies.current_user import get_current_user
from app.controllers.user import UserController
from core.factory import Factory

async def check_logs_feature(
    user: UserInfo = Depends(get_current_user),
    user_controller: UserController = Depends(Factory().get_user_controller),
):
    return await user_controller.check_log_feature(user.id)

