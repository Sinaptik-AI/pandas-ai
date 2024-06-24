from fastapi import APIRouter, Depends

from app.controllers.chat import ChatController
from app.schemas.requests.chat import ChatRequest
from app.schemas.responses import APIResponse
from app.schemas.responses.chat import ChatResponse
from app.schemas.responses.users import UserInfo
from core.factory import Factory
from core.fastapi.dependencies.current_user import get_current_user

chat_router = APIRouter()


@chat_router.post("/")
async def chat(
    chat_request: ChatRequest,
    chat_controller: ChatController = Depends(Factory().get_chat_controller),
    user: UserInfo = Depends(get_current_user),
) -> APIResponse[ChatResponse]:
    response = await chat_controller.chat(user, chat_request)
    return APIResponse(data=response, message="Chat response returned successfully!")
