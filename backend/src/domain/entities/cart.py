"""
Domain Entity: Cart
Giỏ hàng khách hàng lưu giữ các mặt hàng chọn mua tạm thời.
Khớp 100% với Hình 4.3. KHÔNG dùng Enum.
"""
from typing import Optional, List
from datetime import datetime
from src.domain.entities.cart_item import CartItem
from src.domain.entities.product import Product


class Cart:
    def __init__(
        self,
        cart_id: Optional[int] = None,
        customer_id: Optional[int] = None,
        items: Optional[List[CartItem]] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self._cart_id = cart_id
        self._customer_id = customer_id
        self._items = items or []
        self._created_at = created_at or datetime.utcnow()
        self._updated_at = updated_at or datetime.utcnow()

    @property
    def cart_id(self) -> Optional[int]:
        return self._cart_id

    @property
    def customer_id(self) -> Optional[int]:
        return self._customer_id

    @property
    def items(self) -> List[CartItem]:
        return self._items

    @property
    def created_at(self) -> datetime:
        return self._created_at

    @property
    def updated_at(self) -> datetime:
        return self._updated_at

    # Business Operations from UML
    def add_item(self, product: Product, quantity: int = 1) -> CartItem:
        """Thêm mặt hàng mới hoặc cộng dồn số lượng nếu đã có trong giỏ."""
        for item in self._items:
            if item.product_id == product.product_id:
                item.increment_quantity(quantity)
                self._updated_at = datetime.utcnow()
                return item

        new_item = CartItem(
            cart_id=self._cart_id,
            product=product,
            product_id=product.product_id,
            quantity=quantity,
        )
        self._items.append(new_item)
        self._updated_at = datetime.utcnow()
        return new_item

    def update_item_quantity(self, cart_item_id: int, quantity: int) -> None:
        """Cập nhật trực tiếp số lượng một dòng sản phẩm."""
        for item in self._items:
            if item.cart_item_id == cart_item_id:
                if quantity <= 0:
                    self.remove_item(cart_item_id)
                else:
                    item._quantity = quantity
                    self._updated_at = datetime.utcnow()
                return
        raise ValueError(f"Không tìm thấy dòng sản phẩm {cart_item_id} trong giỏ hàng")

    def remove_item(self, cart_item_id: int) -> None:
        """Xóa một sản phẩm ra khỏi giỏ."""
        self._items = [item for item in self._items if item.cart_item_id != cart_item_id]
        self._updated_at = datetime.utcnow()

    def calculate_total_weight(self) -> int:
        """Tổng khối lượng thuần của các mặt hàng trong giỏ (gram)."""
        return sum(item.calculate_line_weight() for item in self._items)

    def calculate_subtotal(self) -> int:
        """Tổng tiền hàng tạm tính trước khi áp dụng voucher và phí vận chuyển."""
        return sum(item.calculate_line_total() for item in self._items)

    def validate_drone_payload(self) -> bool:
        """Kiểm tra điều kiện tải trọng Drone (BR05: Tổng khối lượng + 150g hộp chống sốc <= 2.000g)."""
        total_package_weight = self.calculate_total_weight() + 150
        return total_package_weight <= 2000

    def clear(self) -> None:
        """Làm rỗng toàn bộ giỏ hàng sau khi đã chuyển thành đơn hàng chính thức."""
        self._items = []
        self._updated_at = datetime.utcnow()
