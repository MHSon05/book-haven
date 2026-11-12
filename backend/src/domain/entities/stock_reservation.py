"""
Domain Entity: StockReservation
Mô hình hóa bản ghi giữ chỗ tồn kho 15 phút (BR03).
"""
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

class ReservationStatus(str, Enum):
    PENDING = "PENDING"
    COMMITTED = "COMMITTED"
    RELEASED = "RELEASED"

@dataclass
class StockReservation:
    reservation_id: str
    order_id: str
    edition_id: str
    reserved_quantity: int
    expires_at: str  # ISO timestamp
    status: ReservationStatus = ReservationStatus.PENDING
    created_at: str = None

    def is_expired(self, current_time: datetime = None) -> bool:
        """Kiểm tra xem bản ghi giữ chỗ đã quá hạn 15 phút chưa."""
        if self.status != ReservationStatus.PENDING:
            return False
        now = current_time or datetime.now()
        try:
            exp_time = datetime.fromisoformat(self.expires_at)
            return now >= exp_time
        except Exception:
            return False

    def commit(self):
        """Khóa giữ chỗ chuyển thành trừ kho chính thức khi đơn đã thanh toán."""
        self.status = ReservationStatus.COMMITTED

    def release(self):
        """Hủy giữ chỗ và hoàn trả tồn khả dụng khi đơn bị hủy hoặc hết hạn."""
        self.status = ReservationStatus.RELEASED
