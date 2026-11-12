"""
Presentation Layer: ChatbotController & FastAPI Router
Trợ lý ảo AI Bookie tư vấn mua sách theo ngữ cảnh RAG (Retrieval-Augmented Generation).
"""
from fastapi import APIRouter, Depends, HTTPException, status
from ...application.dtos.models import ChatMessageRequest, ChatMessageResponse
from ...application.services.chatbot_service import ChatbotService
from ..dependencies import get_chatbot_service

router = APIRouter(prefix="/chatbot", tags=["AI Chatbot Bookie"])


class ChatbotController:
    """Bộ điều khiển hội thoại trợ lý ảo AI Bookie (Presentation Layer)."""

    def __init__(self, chatbot_service: ChatbotService):
        self.chatbot_service = chatbot_service

    def chat_with_bookie(self, request: ChatMessageRequest) -> ChatMessageResponse:
        try:
            return self.chatbot_service.process_message(request.message)
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Dịch vụ AI Chatbot hiện không khả dụng: {exc}",
            )


@router.post("/message", response_model=ChatMessageResponse)
def chat_with_bookie(
    request: ChatMessageRequest,
    chatbot_service: ChatbotService = Depends(get_chatbot_service),
):
    return ChatbotController(chatbot_service).chat_with_bookie(request)
