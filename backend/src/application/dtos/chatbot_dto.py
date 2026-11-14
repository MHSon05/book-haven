"""
Application DTOs: AI Chatbot Assistant Bookie
"""
from typing import Any, List, Optional
from pydantic import BaseModel


class ChatMessageRequest(BaseModel):
    message: str


class BookCardDTO(BaseModel):
    book_id: Any
    title: str
    author_name: str
    unit_price: int
    binding_type: str
    edition_id: Any
    cover_image: Optional[str] = None
    available_stock: int


class ChatMessageResponse(BaseModel):
    reply: str
    suggested_books: List[BookCardDTO] = []
