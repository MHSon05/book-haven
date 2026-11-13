"""
Domain Entity: CartItem
Sản phẩm chọn mua tạm thời trong giỏ hàng.
Khớp 100% với Hình 4.3. KHÔNG dùng Enum.
"""
from typing import Optional
from datetime import datetime
from src.domain.entities.product import Product


class CartItem:
    def __init__(
        self,
        cart_item_id: Optional[int] = None,
        cart_id: Optional[int] = None,
        product: Optional[Product] = None,
        product_id: Optional[int] = None,
        quantity: int = 1,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self._cart_item_id = cart_item_id
        self._cart_id = cart_id
        self._product = product
        self._product_id = product_id or (product.product_id if product else None)
        self._quantity = max(1, quantity)
        self._created_at = created_at or datetime.utcnow()
        self._updated_at = updated_at or datetime.utcnow()

    @property
    def cart_item_id(self) -> Optional[int]:
        return self._cart_item_id

    @property
    def cart_id(self) -> Optional[int]:
        return self._cart_id

    @property
    def product(self) -> Optional[Product]:
        return self._product

    @property
    def product_id(self) -> Optional[int]:
        return self._product_id

    @property
    def quantity(self) -> int:
        return self._quantity

    @property
    def created_at(self) -> datetime:
        return self._created_at

    @property
    def updated_at(self) -> datetime:
        return self._updated_at

    # Business Operations from UML
    def calculate_line_total(self) -> int:
        """Thành tiền tạm tính của dòng sản phẩm = đơn giá * số lượng."""
        if self._product:
            return self._product.unit_price * self._quantity
        return 0

    def calculate_line_weight(self) -> int:
        """Tổng khối lượng vật lý của dòng = trọng lượng đơn vị * số lượng."""
        if self._product:
            return self._product.weight_gram * self._quantity
        return 0

    def increment_quantity(self, delta: int) -> None:
        """Tăng hoặc giảm số lượng chọn mua."""
        new_qty = self._quantity + delta
        if new_qty < 1:
            raise ValueError("Số lượng mặt hàng trong giỏ phải lớn hơn 0")
        self._quantity = new_qty
        self._updated_at = datetime.utcnow()
