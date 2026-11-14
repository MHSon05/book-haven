"""
Application DTOs: Multi-Modal Search (Keyword, Semantic, Image)
"""
from typing import Any, List, Optional
from pydantic import BaseModel


class SemanticSearchRequest(BaseModel):
    query: str
    limit: int = 5


class SearchResultItem(BaseModel):
    book_id: Any
    title: str
    author_name: str
    publisher_name: str
    category_id: Optional[Any] = None
    category_name: str
    description: str
    cover_image: Optional[str] = None
    min_price: int
    max_price: int
    available_stock: int
    similarity_score: Optional[float] = None
    explanation_snippet: Optional[str] = None


class SearchResponse(BaseModel):
    total_found: int
    search_mode: str
    results: List[SearchResultItem]
