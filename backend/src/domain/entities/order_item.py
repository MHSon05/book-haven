"""
Domain Entity: OrderItem
Dòng sản phẩm chốt mua chính thức - Lưu trữ bản chụp bất biến (Financial Snapshot - BR04).
Khớp 100% với Hình 4.3. KHÔNG dùng Enum - product_kind_snapshot là string ('BOOK', 'STATIONERY', 'COLLECTIBLE').
"""
from typing import Optional, Dict, Any
from datetime import datetime


class OrderItem:
    def __init__(
        self,
        order_item_id: Optional[int] = None,
        order_id: Optional[int] = None,
        product_id: int = 0,
        product_name_snapshot: str = "",
        sku_snapshot: str = "",
        product_kind_snapshot: str = "BOOK",
        unit_price_at_purchase: int = 0,
        quantity: int = 1,
        weight_gram_snapshot: int = 0,
        created_at: Optional[datetime] = None,
    ):
        self._order_item_id = order_item_id
        self._order_id = order_id
        self._product_id = product_id
        self._product_name_snapshot = product_name_snapshot
        self._sku_snapshot = sku_snapshot
        self._product_kind_snapshot = product_kind_snapshot
        self._unit_price_at_purchase = unit_price_at_purchase
        self._quantity = quantity
        self._weight_gram_snapshot = weight_gram_snapshot
        self._created_at = created_at or datetime.utcnow()

    @property
    def order_item_id(self) -> Optional[int]:
        return self._order_item_id

    @property
    def order_id(self) -> Optional[int]:
        return self._order_id

    @property
    def product_id(self) -> int:
        return self._product_id

    @property
    def product_name_snapshot(self) -> str:
        return self._product_name_snapshot

    @property
    def sku_snapshot(self) -> str:
        return self._sku_snapshot

    @property
    def product_kind_snapshot(self) -> str:
        return self._product_kind_snapshot

    @property
    def unit_price_at_purchase(self) -> int:
        return self._unit_price_at_purchase

    @property
    def quantity(self) -> int:
        return self._quantity

    @property
    def weight_gram_snapshot(self) -> int:
        return self._weight_gram_snapshot

    @property
    def created_at(self) -> datetime:
        return self._created_at

    # Business Operations from UML
    def calculate_subtotal(self) -> int:
        """Thành tiền của dòng đơn hàng theo giá chốt mua = đơn giá lịch sử * số lượng."""
        return self._unit_price_at_purchase * self._quantity

    def get_immutable_snapshot(self) -> Dict[str, Any]:
        """Xuất thông tin bản chụp bất biến phục vụ kế toán và in hóa đơn VAT."""
        return {
            "product_id": self._product_id,
            "name": self._product_name_snapshot,
            "sku": self._sku_snapshot,
            "kind": self._product_kind_snapshot,
            "unit_price": self._unit_price_at_purchase,
            "quantity": self._quantity,
            "weight_gram": self._weight_gram_snapshot,
            "line_subtotal": self.calculate_subtotal(),
        }
