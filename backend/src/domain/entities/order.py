"""
Domain Entity: Order
Đơn hàng chính thức trong hệ thống BookHaven.
Khớp 100% với Hình 4.3. KHÔNG dùng Enum - status, payment_method, carrier là chuỗi (string).
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from src.domain.entities.order_item import OrderItem


class Order:
    # Các trạng thái đơn hàng hợp lệ theo chuẩn chuỗi
    VALID_STATUSES = {
        "AWAITING_PAYMENT",
        "PENDING_PAYMENT",
        "PAID",
        "PENDING_CASH",
        "PACKED",
        "SHIPPING",
        "DELIVERED",
        "CANCELLED",
    }

    # Bảng chuyển trạng thái hợp lệ (Finite State Machine - Chương 2)
    TRANSITIONS = {
        "AWAITING_PAYMENT": {"PAID", "CANCELLED"},
        "PENDING_PAYMENT": {"PAID", "CANCELLED"},
        "PENDING_CASH": {"PACKED", "CANCELLED"},
        "PAID": {"PACKED", "CANCELLED"},
        "PACKED": {"SHIPPING", "CANCELLED"},
        "SHIPPING": {"DELIVERED", "CANCELLED"},
        "DELIVERED": set(),
        "CANCELLED": set(),
    }

    def __init__(
        self,
        order_id: Optional[int] = None,
        customer_id: int = 0,
        receiver_name: str = "",
        receiver_phone: str = "",
        shipping_address: str = "",
        payment_method: str = "VIETQR",
        carrier: str = "GHN",
        tracking_code: Optional[str] = None,
        total_amount: int = 0,
        shipping_fee: int = 0,
        discount_amount: int = 0,
        final_amount: int = 0,
        status: str = "AWAITING_PAYMENT",
        items: Optional[List[OrderItem]] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self._order_id = order_id
        self._customer_id = customer_id
        self._receiver_name = receiver_name
        self._receiver_phone = receiver_phone
        self._shipping_address = shipping_address
        self._payment_method = payment_method
        self._carrier = carrier
        self._tracking_code = tracking_code
        self._total_amount = total_amount
        self._shipping_fee = shipping_fee
        self._discount_amount = discount_amount
        self._final_amount = final_amount
        self._status = status
        self._items = items or []
        self._payment = None
        self._created_at = created_at or datetime.utcnow()
        self._updated_at = updated_at or datetime.utcnow()

    @property
    def order_id(self) -> Optional[int]:
        return self._order_id

    @property
    def customer_id(self) -> int:
        return self._customer_id

    @property
    def receiver_name(self) -> str:
        return self._receiver_name

    @property
    def receiver_phone(self) -> str:
        return self._receiver_phone

    @property
    def shipping_address(self) -> str:
        return self._shipping_address

    @property
    def payment_method(self) -> str:
        return self._payment_method

    @property
    def carrier(self) -> str:
        return self._carrier

    @property
    def tracking_code(self) -> Optional[str]:
        return self._tracking_code

    @property
    def total_amount(self) -> int:
        return self._total_amount

    @property
    def shipping_fee(self) -> int:
        return self._shipping_fee

    @property
    def discount_amount(self) -> int:
        return self._discount_amount

    @property
    def final_amount(self) -> int:
        return self._final_amount

    @property
    def status(self) -> str:
        return self._status

    @property
    def items(self) -> List[OrderItem]:
        return self._items

    @property
    def created_at(self) -> datetime:
        return self._created_at

    @property
    def updated_at(self) -> datetime:
        return self._updated_at

    # Business Operations from UML
    def calculate_grand_total(self) -> int:
        """Tổng thanh toán cuối cùng = Tổng tiền hàng + Phí vận chuyển - Giảm giá."""
        subtotal = sum(item.calculate_subtotal() for item in self._items) if self._items else self._total_amount
        self._total_amount = subtotal
        self._final_amount = max(0, subtotal + self._shipping_fee - self._discount_amount)
        return self._final_amount

    def calculate_total_weight(self) -> int:
        """Tổng trọng lượng các kiện hàng trong đơn."""
        return sum(item.weight_gram_snapshot * item.quantity for item in self._items)

    def attach_payment(self, payment) -> None:
        """Gắn chứng từ thanh toán vào đơn."""
        self._payment = payment

    def transition_to(self, new_status: str) -> None:
        """Chuyển đổi trạng thái đơn hàng theo FSM hợp lệ."""
        if new_status not in self.VALID_STATUSES:
            raise ValueError(f"Trạng thái {new_status} không hợp lệ trong hệ thống")
        allowed = self.TRANSITIONS.get(self._status, set())
        if new_status not in allowed:
            raise ValueError(f"Không thể chuyển trạng thái đơn hàng từ {self._status} sang {new_status}")
        self._status = new_status
        self._updated_at = datetime.utcnow()

    def can_cancel(self) -> bool:
        """Đơn hàng chỉ được phép hủy khi chưa bàn giao sang khâu đóng gói hoặc vận chuyển."""
        return self._status in ("AWAITING_PAYMENT", "PENDING_PAYMENT", "PENDING_CASH", "PAID")

    def cancel(self, reason: str = "") -> bool:
        """Thực hiện hủy đơn hàng nếu thỏa mãn điều kiện."""
        if not self.can_cancel():
            return False
        self.transition_to("CANCELLED")
        return True
