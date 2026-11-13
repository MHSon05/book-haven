"""
Domain Entity: Product (Abstract Superclass)
Lớp cha trừu tượng cho toàn bộ mặt hàng trong hệ sinh thái BookHaven.
Khớp 100% với Hình 4.3 (Design Class Diagram) và Hình 4.4 (Layered Architecture).
KHÔNG dùng Enum - sử dụng chuỗi nguyên bản (raw string).
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime


class Product(ABC):
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
        created_at: Optional[datetime] = None,
    ):
        self._product_id = product_id
        self._sku = sku
        self._name = name
        self._unit_price = unit_price
        self._weight_gram = weight_gram
        self._stock_on_hand = stock_on_hand
        self._stock_reserved = stock_reserved
        self._category_id = category_id
        self._description = description
        self._cover_image = cover_image
        self._is_active = is_active
        self._created_at = created_at or datetime.utcnow()

    # Getters / Properties
    @property
    def product_id(self) -> Optional[int]:
        return self._product_id

    @property
    def edition_id(self) -> Optional[int]:
        """Alias tương thích ngược."""
        return self._product_id

    @property
    def sku(self) -> str:
        return self._sku

    @property
    def name(self) -> str:
        return self._name

    @property
    def unit_price(self) -> int:
        return self._unit_price

    @property
    def weight_gram(self) -> int:
        return self._weight_gram

    @property
    def stock_on_hand(self) -> int:
        return self._stock_on_hand

    @property
    def stock_reserved(self) -> int:
        return self._stock_reserved

    @property
    def category_id(self) -> Optional[int]:
        return self._category_id

    @property
    def description(self) -> str:
        return self._description

    @property
    def cover_image(self) -> str:
        return self._cover_image

    @property
    def is_active(self) -> bool:
        return self._is_active

    @property
    def created_at(self) -> datetime:
        return self._created_at

    # Business Invariant Methods (UML Operations)
    def get_available_stock(self) -> int:
        """Tồn kho khả dụng = tồn thực tế - tồn đang giữ chỗ 15 phút (BR02)."""
        return max(0, self._stock_on_hand - self._stock_reserved)

    def available_stock(self) -> int:
        """Alias tương thích ngược."""
        return self.get_available_stock()

    def check_availability(self, quantity: int) -> bool:
        """Kiểm tra số lượng đặt mua có vượt tồn khả dụng không."""
        return self.get_available_stock() >= quantity

    def restock(self, quantity: int) -> None:
        """Tăng số lượng tồn kho thực tế khi thủ kho nhập hàng (UC12)."""
        if quantity <= 0:
            raise ValueError("Số lượng nhập kho phải lớn hơn 0")
        self._stock_on_hand += quantity

    def reserve_stock(self, quantity: int) -> None:
        """Tăng số lượng giữ chỗ tạm thời trong phiên checkout 15 phút (BR03)."""
        if not self.check_availability(quantity):
            raise ValueError(f"Không đủ tồn khả dụng cho sản phẩm {self._sku} (Yêu cầu: {quantity}, Khả dụng: {self.get_available_stock()})")
        self._stock_reserved += quantity

    def commit_stock(self, quantity: int) -> None:
        """Trừ kho chính thức khi đơn hàng đã thanh toán thành công."""
        if quantity > self._stock_on_hand:
            raise ValueError(f"Số lượng trừ kho {quantity} vượt quá tồn thực tế {self._stock_on_hand}")
        self._stock_on_hand -= quantity
        self._stock_reserved = max(0, self._stock_reserved - quantity)

    def release_stock(self, quantity: int) -> None:
        """Giải phóng số lượng giữ chỗ khi đơn hàng bị hủy hoặc quá hạn 15 phút."""
        self._stock_reserved = max(0, self._stock_reserved - quantity)

    # Polymorphic Operations (Đa hình bắt buộc override ở lớp con)
    @abstractmethod
    def is_searchable(self) -> bool:
        """Đánh giá điều kiện sản phẩm được xuất hiện trên thanh tìm kiếm."""
        pass

    @abstractmethod
    def get_specifications(self) -> Dict[str, Any]:
        """Trả về thông số đặc thù của từng loại sản phẩm."""
        pass

    @abstractmethod
    def build_search_document(self) -> str:
        """Xây dựng chuỗi văn bản phục vụ trích xuất vector embedding và tìm kiếm toàn văn."""
        pass
