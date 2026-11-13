"""
Domain Entity: StockReservation
Bản ghi khóa giữ chỗ kho tạm thời 15 phút trong phiên Checkout (BR03).
Khớp 100% với Hình 4.3. KHÔNG dùng Enum - status là chuỗi ('PENDING', 'COMMITTED', 'RELEASED').
"""
from typing import Optional
from datetime import datetime


class StockReservation:
    def __init__(
        self,
        reservation_id: Optional[int] = None,
        order_id: int = 0,
        product_id: int = 0,
        reserved_quantity: int = 1,
        expires_at: Optional[datetime] = None,
        status: str = "PENDING",
        created_at: Optional[datetime] = None,
    ):
        self._reservation_id = reservation_id
        self._order_id = order_id
        self._product_id = product_id
        self._reserved_quantity = reserved_quantity
        self._expires_at = expires_at or datetime.utcnow()
        self._status = status
        self._created_at = created_at or datetime.utcnow()

    @property
    def reservation_id(self) -> Optional[int]:
        return self._reservation_id

    @property
    def order_id(self) -> int:
        return self._order_id

    @property
    def product_id(self) -> int:
        return self._product_id

    @property
    def reserved_quantity(self) -> int:
        return self._reserved_quantity

    @property
    def expires_at(self) -> datetime:
        return self._expires_at

    @property
    def status(self) -> str:
        return self._status

    @property
    def created_at(self) -> datetime:
        return self._created_at

    # Business Operations from UML
    def is_expired(self) -> bool:
        """Kiểm tra thời điểm hiện tại đã vượt quá mốc 15 phút chưa."""
        if self._status != "PENDING":
            return False
        return datetime.utcnow() > self._expires_at

    def commit(self) -> None:
        """Chuyển trạng thái giữ chỗ sang COMMITTED khi đơn hàng thanh toán thành công."""
        if self._status != "PENDING":
            raise ValueError(f"Không thể commit bản ghi giữ chỗ ở trạng thái {self._status}")
        self._status = "COMMITTED"

    def release(self) -> None:
        """Giải phóng giữ chỗ kho khi đơn hàng bị hủy hoặc hết hạn thanh toán."""
        if self._status == "COMMITTED":
            raise ValueError("Không thể release bản ghi giữ chỗ đã chốt thành công (COMMITTED)")
        self._status = "RELEASED"
