"""
Domain Entity: Book
Đại diện cho Tác phẩm chung (thông tin văn học, ngữ nghĩa và trạng thái mở bán BR01),
tách biệt với các Ấn bản vật lý cụ thể (BookEdition).
"""
from dataclasses import dataclass, field
from typing import List, Optional
from .book_edition import BookEdition


@dataclass
class Book:
    book_id: str
    title: str
    author_id: str
    publisher_id: str
    category_id: str
    publish_year: Optional[int] = None
    description: Optional[str] = None
    cover_image: Optional[str] = None
    is_active: bool = True
    author_name: Optional[str] = None
    publisher_name: Optional[str] = None
    category_name: Optional[str] = None
    created_at: Optional[str] = None
    editions: List[BookEdition] = field(default_factory=list)

    def is_searchable(self) -> bool:
        """Chỉ những tác phẩm đang trạng thái mở bán (is_active = True) mới hiển thị trong tìm kiếm (BR01)."""
        return bool(self.is_active)

    def has_available_stock(self) -> bool:
        """Kiểm tra tác phẩm có ít nhất một ấn bản còn tồn kho khả dụng > 0."""
        return any(ed.available_stock() > 0 for ed in self.editions)

    def min_price(self) -> int:
        return min((ed.unit_price for ed in self.editions), default=0)

    def max_price(self) -> int:
        return max((ed.unit_price for ed in self.editions), default=0)

    def total_available_stock(self) -> int:
        return sum(ed.available_stock() for ed in self.editions)
