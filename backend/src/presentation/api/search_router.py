"""
Presentation Layer: SearchController & FastAPI Router (presentation.api)
Cung cấp các API tìm kiếm đa phương thức: Từ khóa SQL, Ngữ nghĩa AI (Vector) và Bìa sách (dHash).
Khớp 100% Listing 4.2 và Figure 4.5.
"""
import os
from typing import Optional
from fastapi import APIRouter, Depends, Query, UploadFile, File, HTTPException, status

from ...application.dtos.search_dto import (
    SearchResponse,
    SemanticSearchRequest,
)
from ...application.services.search_service import SearchService
from ..dependencies import get_search_service

router = APIRouter(prefix="/search", tags=["Search Multi-Modal"])

ASSETS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "assets"))


class SearchController:
    """Bộ điều khiển tìm kiếm đa phương thức (Presentation Layer)."""

    def __init__(self, search_service: SearchService):
        self.search_service = search_service

    def search_keyword(
        self,
        keyword: str,
        category_id: Optional[str] = None,
        binding_type: Optional[str] = None,
        limit: int = 20,
    ) -> SearchResponse:
        return self.search_service.search_keyword(
            keyword=keyword,
            category_id=category_id,
            binding_type=binding_type,
            limit=limit,
        )

    def search_semantic(self, request: SemanticSearchRequest) -> SearchResponse:
        return self.search_service.search_semantic(
            query=request.query,
            limit=request.limit,
            min_threshold=0.50,
        )

    def search_by_image(
        self, image_bytes: bytes, base_static_path: Optional[str] = ASSETS_DIR
    ) -> SearchResponse:
        if not image_bytes:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Tệp ảnh trống.")
        try:
            return self.search_service.search_by_image(
                image_bytes, base_static_path=base_static_path
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Lỗi khi xử lý nhận diện ảnh bìa: {str(e)}",
            )


@router.get("", response_model=SearchResponse)
@router.get("/keyword", response_model=SearchResponse)
def search_keyword(
    q: str = Query(..., min_length=1, description="Từ khóa tìm kiếm tiêu đề, tác giả"),
    category_id: Optional[str] = Query(None, description="Mã thể loại lọc"),
    binding_type: Optional[str] = Query(None, description="Quy cách ấn bản: Paperback / Hardcover"),
    limit: int = Query(20, ge=1, le=50),
    search_service: SearchService = Depends(get_search_service),
):
    return SearchController(search_service).search_keyword(
        keyword=q,
        category_id=category_id,
        binding_type=binding_type,
        limit=limit,
    )


@router.post("/semantic", response_model=SearchResponse)
def search_semantic(
    request: SemanticSearchRequest,
    search_service: SearchService = Depends(get_search_service),
):
    return SearchController(search_service).search_semantic(request)


@router.post("/image", response_model=SearchResponse)
async def search_by_cover_image(
    file: UploadFile = File(..., description="Ảnh bìa chụp từ camera hoặc thiết bị của độc giả"),
    search_service: SearchService = Depends(get_search_service),
):
    image_bytes = await file.read()
    return SearchController(search_service).search_by_image(image_bytes)


__all__ = ["router", "SearchController"]
