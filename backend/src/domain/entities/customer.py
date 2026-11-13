"""
Domain Entity: Customer
Lớp con kế thừa từ User đại diện cho Khách hàng mua sắm.
Khớp 100% với Hình 4.3. KHÔNG dùng Enum.
"""
from typing import Optional, List, Any
from datetime import datetime
from src.domain.entities.user import User


class Customer(User):
    def __init__(
        self,
        user_id: Optional[int] = None,
        username: str = "",
        password_hash: str = "",
        email: str = "",
        full_name: str = "",
        phone: Optional[str] = None,
        role: str = "CUSTOMER",
        shipping_address: str = "",
        loyalty_points: int = 0,
        created_at: Optional[datetime] = None,
    ):
        super().__init__(
            user_id=user_id,
            username=username,
            password_hash=password_hash,
            email=email,
            full_name=full_name,
            phone=phone,
            role=role,
            created_at=created_at,
        )
        self._shipping_address = shipping_address
        self._loyalty_points = loyalty_points
        self._order_history: List[Any] = []

    @property
    def shipping_address(self) -> str:
        return self._shipping_address

    @property
    def loyalty_points(self) -> int:
        return self._loyalty_points

    # Business Operations from UML
    def add_loyalty_points(self, points: int) -> None:
        """Tích lũy điểm thưởng thành viên khi đơn hàng thanh toán thành công."""
        if points > 0:
            self._loyalty_points += points

    def can_place_order(self) -> bool:
        """Kiểm tra điều kiện khách hàng được tạo đơn hàng (đã có địa chỉ giao hàng)."""
        return len(self._shipping_address.strip()) > 0

    def get_order_history(self) -> List[Any]:
        """Xem lịch sử các đơn hàng đã đặt."""
        return self._order_history
