"""
Presentation Router: BookRouter
Cung cấp API duyệt danh mục sách, xem chi tiết sách và các quy cách ấn bản (Bìa mềm/Bìa cứng).
"""

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from ...infrastructure.repositories.book_repository import BookRepository
from ..dependencies import get_book_repo

router = APIRouter(tags=["Books & Categories"])


@router.get("/books")
def list_books(
    category_id: Optional[str] = Query(None, description="Lọc theo mã thể loại"),
    min_price: Optional[int] = Query(None, description="Giá thấp nhất"),
    max_price: Optional[int] = Query(None, description="Giá cao nhất"),
    limit: int = Query(500, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    book_repo: BookRepository = Depends(get_book_repo),
):
    books = book_repo.get_all_books(
        category_id=category_id,
        min_price=min_price,
        max_price=max_price,
        limit=limit,
        offset=offset,
    )
    return {"total": len(books), "books": books}


@router.get("/books/{book_id}")
def get_book_detail(book_id: str, book_repo: BookRepository = Depends(get_book_repo)):
    book = book_repo.get_book_by_id(book_id)
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy đầu sách với ID '{book_id}'.",
        )

    editions = book_repo.get_editions_by_book_id(int(book_id))
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


@router.get("/categories")
def list_categories(book_repo: BookRepository = Depends(get_book_repo)):
    categories = book_repo.get_all_categories()
    return {"total": len(categories), "categories": categories}
