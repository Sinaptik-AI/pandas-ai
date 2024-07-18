from fastapi import APIRouter, Depends

from app.controllers import AuthController
from app.controllers.user import UserController
from app.schemas.extras.token import Token
from app.schemas.requests.users import LoginUserRequest
from app.schemas.responses.users import UserInfo
from core.factory import Factory
from core.fastapi.dependencies.current_user import get_current_user
from typing import Any, Dict
user_router = APIRouter()


@user_router.post("/login")
async def login_user(
    login_user_request: LoginUserRequest,
    auth_controller: AuthController = Depends(Factory().get_auth_controller),
) -> Token:
    return await auth_controller.login(
        email=login_user_request.email, password=login_user_request.password
    )


@user_router.get("/me")
async def get_user(
    user_controller: UserController = Depends(Factory().get_user_controller),
) -> UserInfo:
    return await user_controller.me()


@user_router.patch("/update_features")
async def update_user_routes(
    routes: Dict[str, Any],
    user_controller: UserController = Depends(Factory().get_user_controller),
    user: UserInfo = Depends(get_current_user),
):
    return await user_controller.update_features(user.id, routes)
