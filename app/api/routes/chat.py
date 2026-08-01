from fastapi import APIRouter

from app.application.chat.chat_service import (
    ChatService,
)
from app.schemas.chat_request import (
    ChatRequest,
)
from app.schemas.chat_response import (
    ChatResponse,
)

router = APIRouter(
    prefix="/chat",
    tags=["Chat"],
)

service = ChatService()


@router.post(
    "",
    response_model=ChatResponse,
)
def chat(
    request: ChatRequest,
) -> ChatResponse:

    return service.chat(
        request=request,
    )
