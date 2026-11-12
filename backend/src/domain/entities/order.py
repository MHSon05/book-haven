"""
Domain Entity: Order & OrderItem
Quản lý trạng thái đơn hàng, snapshot tài chính bất biến và các quy tắc chuyển đổi trạng thái.
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional
from ..exceptions import InvalidOrderStateException

class OrderStatus(str, Enum):
    AWAITING_PAYMENT = "AWAITING_PAYMENT"
    PAID = "PAID"
    PENDING_CASH = "PENDING_CASH"  # Đối với đơn COD
    PACKED = "PACKED"
    SHIPPING = "SHIPPING"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"

class PaymentMethod(str, Enum):
    VIETQR = "VIETQR"
    COD = "COD"

class Carrier(str, Enum):
    GHN_STANDARD = "GHN_STANDARD"
    GHN_EXPRESS = "GHN_EXPRESS"
    HANOI_DRONE = "HANOI_DRONE"

@dataclass
class OrderItem:
    """OrderItem là bản chụp (Snapshot) tài chính bất biến tại thời điểm đặt hàng (BR04)."""
    order_item_id: str
    order_id: str
    edition_id: str
    title_snapshot: str
    sku_snapshot: str
    binding_type_snapshot: str
    isbn13_snapshot: str
    unit_price_at_purchase: int
    quantity: int
    weight_gram_snapshot: int

    def subtotal(self) -> int:
        return self.unit_price_at_purchase * self.quantity

    def total_weight(self) -> int:
        return self.weight_gram_snapshot * self.quantity


@dataclass
class Order:
    order_id: str
    customer_id: str
    receiver_name: str
    receiver_phone: str
    shipping_address: str
    payment_method: PaymentMethod
    carrier: Carrier
    total_amount: int
    shipping_fee: int
    discount_amount: int
    final_amount: int
    status: OrderStatus = OrderStatus.AWAITING_PAYMENT
    items: List[OrderItem] = field(default_factory=list)
    tracking_code: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    def mark_paid(self):
        """Chuyển trạng thái sang PAID sau khi xác thực chuyển khoản thành công."""
        if self.status != OrderStatus.AWAITING_PAYMENT:
            raise InvalidOrderStateException(
                f"Không thể chuyển sang PAID từ trạng thái '{self.status}'."
            )
        self.status = OrderStatus.PAID

    def mark_packed(self):
        """Thủ kho đóng gói sách, bọc màng xốp hoàn thành."""
        if self.status not in (OrderStatus.PAID, OrderStatus.PENDING_CASH):
            raise InvalidOrderStateException(
                f"Đơn hàng phải ở trạng thái PAID hoặc PENDING_CASH mới có thể đóng gói."
            )
        self.status = OrderStatus.PACKED

    def mark_dispatched(self, carrier: Carrier, tracking_code: str):
        """Bàn giao bưu kiện cho đơn vị vận chuyển (GHN hoặc Hanoi Drone)."""
        if self.status != OrderStatus.PACKED:
            raise InvalidOrderStateException("Đơn hàng phải được đóng gói trước khi bàn giao giao vận.")
        self.carrier = carrier
        self.tracking_code = tracking_code
        self.status = OrderStatus.SHIPPING

    def mark_delivered(self):
        """Giao hàng thành công đến tay độc giả."""
        if self.status != OrderStatus.SHIPPING:
            raise InvalidOrderStateException("Đơn hàng phải đang trong trạng thái SHIPPING mới có thể giao thành công.")
        self.status = OrderStatus.DELIVERED

    def cancel(self):
        """Hủy đơn hàng và giải phóng giữ chỗ kho."""
        if self.status in (OrderStatus.SHIPPING, OrderStatus.DELIVERED):
            raise InvalidOrderStateException("Không thể hủy đơn hàng đang giao hoặc đã giao thành công.")
        self.status = OrderStatus.CANCELLED

    def calculate_total_weight_grams(self) -> int:
        """Tổng trọng lượng sách + 150g màng xốp và hộp carton đóng gói."""
        books_weight = sum(item.total_weight() for item in self.items)
        return books_weight + 150
