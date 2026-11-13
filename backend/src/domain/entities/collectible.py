"""
Domain Entity: Collectible
Lớp con kế thừa từ Product đại diện cho đồ sưu tầm / Manga Anime Merchandise (20 mặt hàng).
Khớp 100% với Hình 4.3. KHÔNG dùng Enum - origin, material, dimensions là chuỗi (string).
"""
from typing import Dict, Any, Optional
from datetime import datetime
from src.domain.entities.product import Product


class Collectible(Product):
    def __init__(
        self,
        product_id: Optional[int] = None,
        sku: str = "",
        name: str = "",
        unit_price: int = 0,
        weight_gram: int = 0,
        stock_on_hand: int = 0,
        stock_reserved: int = 0,
        category_id: Optional[int] = None,
        description: str = "",
        cover_image: str = "",
        is_active: bool = True,
        origin: str = "",
        material: str = "",
        dimensions: str = "",
        created_at: Optional[datetime] = None,
    ):
        super().__init__(
            product_id=product_id,
            sku=sku,
            name=name,
            unit_price=unit_price,
            weight_gram=weight_gram,
            stock_on_hand=stock_on_hand,
            stock_reserved=stock_reserved,
            category_id=category_id,
            description=description,
            cover_image=cover_image,
            is_active=is_active,
            created_at=created_at,
        )
        self._origin = origin
        self._material = material
        self._dimensions = dimensions

    @property
    def origin(self) -> str:
        return self._origin

    @property
    def material(self) -> str:
        return self._material

    @property
    def dimensions(self) -> str:
        return self._dimensions

    # Overridden Polymorphic Operations
    def is_searchable(self) -> bool:
        return self._is_active and self.get_available_stock() > 0

    def get_specifications(self) -> Dict[str, Any]:
        return {
            "kind": "COLLECTIBLE",
            "origin": self._origin,
            "material": self._material,
            "dimensions": self._dimensions,
        }

    def build_search_document(self) -> str:
        return f"{self._name} Xuất xứ: {self._origin} Chất liệu: {self._material} Kích thước: {self._dimensions} {self._description}"
