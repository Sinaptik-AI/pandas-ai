from fastapi import APIRouter, Depends

from app.controllers.conversation import ConversationController
from app.schemas.responses import APIResponse

from app.schemas.responses.conversation import ConversationList
from app.schemas.responses.users import UserInfo
from core.factory import Factory
from core.fastapi.dependencies.current_user import get_current_user

conversation_router = APIRouter()


@conversation_router.get("/")
async def conversations(
    conversation_controller: ConversationController = Depends(
        Factory().get_conversation_controller
    ),
    user: UserInfo = Depends(get_current_user),
) -> APIResponse[ConversationList]:
    response = await conversation_controller.get_workspace_conversations(
        user.id, user.space.id
    )
    return APIResponse(
        data=response, message="User conversations returned successfully!"
    )
