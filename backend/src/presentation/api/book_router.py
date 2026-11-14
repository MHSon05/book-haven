"""
Presentation Layer: ProductCatalogController (BookController) & FastAPI Router (presentation.api)
Cung cấp API duyệt danh mục sách, xem chi tiết sách và các quy cách ấn bản.
Khớp 100% Listing 4.2 và Figure 4.5.
"""
from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status

from ...infrastructure.repositories.book_repository import BookRepository
from ..dependencies import get_book_repo

router = APIRouter(tags=["Books & Categories"])


class ProductCatalogController:
    """Bộ điều khiển danh mục và chi tiết sản phẩm / sách (Presentation Layer)."""

    def __init__(self, book_repo: BookRepository):
        self.book_repo = book_repo

    def list_books(
        self,
        category_id: Optional[str] = None,
        min_price: Optional[int] = None,
        max_price: Optional[int] = None,
        limit: int = 500,
        offset: int = 0,
    ) -> Dict[str, Any]:
        books = self.book_repo.get_all_books(
            category_id=category_id,
            min_price=min_price,
            max_price=max_price,
            limit=limit,
            offset=offset,
        )
        return {"total": len(books), "books": books}

    def get_book_detail(self, book_id: str) -> Dict[str, Any]:
        book = self.book_repo.get_book_by_id(book_id)
        if not book:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Không tìm thấy đầu sách với ID '{book_id}'.",
            )

        editions = self.book_repo.get_editions_by_book_id(int(book_id))
        editions_data = [
            {
                "edition_id": ed.product_id,
                "sku": ed.sku,
                "isbn13": getattr(ed, "isbn13", ""),
                "binding_type": getattr(ed, "binding_type", "Standard"),
                "unit_price": ed.unit_price,
                "weight_gram": ed.weight_gram,
                "stock_on_hand": ed.stock_on_hand,
                "stock_reserved": ed.stock_reserved,
                "available_stock": ed.get_available_stock(),
                "is_in_stock": ed.get_available_stock() > 0,
            }
            for ed in editions
        ]
        return {**book, "editions": editions_data}

    def list_categories(self) -> Dict[str, Any]:
        categories = self.book_repo.get_all_categories()
        return {"total": len(categories), "categories": categories}


# Alias tương thích ngược với Figure 4.5 và mã nguồn cũ
BookController = ProductCatalogController


@router.get("/books")
def list_books(
    category_id: Optional[str] = Query(None, description="Lọc theo mã thể loại"),
    min_price: Optional[int] = Query(None, description="Giá thấp nhất"),
    max_price: Optional[int] = Query(None, description="Giá cao nhất"),
    limit: int = Query(500, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    book_repo: BookRepository = Depends(get_book_repo),
):
    return ProductCatalogController(book_repo).list_books(
        category_id=category_id,
        min_price=min_price,
        max_price=max_price,
        limit=limit,
        offset=offset,
    )


@router.get("/books/{book_id}")
def get_book_detail(book_id: str, book_repo: BookRepository = Depends(get_book_repo)):
    return ProductCatalogController(book_repo).get_book_detail(book_id)


@router.get("/categories")
def list_categories(book_repo: BookRepository = Depends(get_book_repo)):
    return ProductCatalogController(book_repo).list_categories()


__all__ = ["router", "ProductCatalogController", "BookController"]
