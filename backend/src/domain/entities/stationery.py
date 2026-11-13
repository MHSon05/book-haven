"""
Domain Entity: Stationery
Lớp con kế thừa từ Product đại diện cho văn phòng phẩm (30 mặt hàng Fahasa).
Khớp 100% với Hình 4.3. KHÔNG dùng Enum - brand, material, color là chuỗi (string).
"""
from typing import Dict, Any, Optional
from datetime import datetime
from src.domain.entities.product import Product


class Stationery(Product):
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
        brand: str = "",
        material: str = "",
        color: str = "",
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
        self._brand = brand
        self._material = material
        self._color = color

    @property
    def brand(self) -> str:
        return self._brand

    @property
    def material(self) -> str:
        return self._material

    @property
    def color(self) -> str:
        return self._color

    # Overridden Polymorphic Operations
    def is_searchable(self) -> bool:
        return self._is_active and self.get_available_stock() > 0 and len(self._brand) > 0

    def get_specifications(self) -> Dict[str, Any]:
        return {
            "kind": "STATIONERY",
            "brand": self._brand,
            "material": self._material,
            "color": self._color,
        }

    def build_search_document(self) -> str:
        return f"{self._name} Thương hiệu: {self._brand} Chất liệu: {self._material} Màu sắc: {self._color} {self._description}"
