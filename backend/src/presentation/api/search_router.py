"""
Presentation Layer: SearchController & FastAPI Router
Cung cấp các API tìm kiếm đa phương thức: Từ khóa SQL, Ngữ nghĩa AI (Vector) và Bìa sách (dHash).
"""
import os
from typing import Optional
from fastapi import APIRouter, Depends, Query, UploadFile, File, HTTPException, status

from ...application.dtos.models import SearchResponse, SemanticSearchRequest
from ...application.services.search_service import SearchService
from ..dependencies import get_search_service

router = APIRouter(prefix="/search", tags=["Search Multi-Modal"])

# Đường dẫn thư mục assets chứa ảnh bìa so khớp dHash
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


@router.get("/keyword", response_model=SearchResponse)
def search_keyword(
    q: str = Query("", description="Từ khóa tìm kiếm (tên sách, tác giả, ISBN, SKU)"),
    category_id: Optional[str] = Query(None, description="Lọc theo thể loại"),
    binding_type: Optional[str] = Query(None, description="Lọc theo quy cách bìa (PAPERBACK/HARDCOVER)"),
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
async def search_by_image(
    file: UploadFile = File(..., description="Tệp ảnh chụp bìa sách (JPEG, PNG, WEBP)"),
    search_service: SearchService = Depends(get_search_service),
):
    image_bytes = await file.read()
    return SearchController(search_service).search_by_image(image_bytes, ASSETS_DIR)
