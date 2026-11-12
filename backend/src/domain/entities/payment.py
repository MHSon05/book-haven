"""
Domain Entity: Payment
Quản lý chứng từ thanh toán dòng tiền (VietQR / COD) phục vụ đối soát doanh thu thực thu (BR06).
"""
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional


class PaymentStatus(str, Enum):
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"


@dataclass
class Payment:
    payment_id: str
    order_id: str
    payment_method: str
    amount: int
    transaction_code: Optional[str] = None
    status: PaymentStatus = PaymentStatus.PENDING
    paid_at: Optional[str] = None

    def mark_success(self, transaction_code: str) -> None:
        """Ghi nhận giao dịch thanh toán thành công kèm mã đối soát ngân hàng."""
        self.transaction_code = transaction_code
        self.status = PaymentStatus.SUCCESS
        self.paid_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def mark_failed(self) -> None:
        """Đánh dấu giao dịch thanh toán thất bại."""
        self.status = PaymentStatus.FAILED
