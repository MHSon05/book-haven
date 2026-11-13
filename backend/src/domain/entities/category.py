"""
Domain Entity: Category
Thể loại & Phân mục sản phẩm trong BookHaven.
Khớp 100% với Hình 4.3. KHÔNG dùng Enum.
"""
from typing import Optional, List
from datetime import datetime


class Category:
    def __init__(
        self,
        category_id: Optional[int] = None,
        category_name: str = "",
        description: str = "",
        slug: str = "",
        created_at: Optional[datetime] = None,
    ):
        self._category_id = category_id
        self._category_name = category_name
        self._description = description
        self._slug = slug
        self._created_at = created_at or datetime.utcnow()
        self._products: List[Any] = []

    @property
    def category_id(self) -> Optional[int]:
        return self._category_id

    @property
    def category_name(self) -> str:
        return self._category_name

    @property
    def description(self) -> str:
        return self._description

    @property
    def slug(self) -> str:
        return self._slug

    @property
    def created_at(self) -> datetime:
        return self._created_at

    def add_product(self, product) -> None:
        """Gắn sản phẩm vào thể loại."""
        self._products.append(product)

    def get_active_product_count(self) -> int:
        """Đếm số lượng sản phẩm đang mở bán trong danh mục."""
        return sum(1 for p in self._products if getattr(p, "is_active", True))
