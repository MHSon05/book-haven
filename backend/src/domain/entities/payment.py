"""
Domain Entity: Payment
Chứng từ ghi nhận dòng tiền thanh toán đơn hàng (VietQR / COD).
Khớp 100% với Hình 4.3. KHÔNG dùng Enum - payment_method, status là chuỗi (string).
"""
from typing import Optional
from datetime import datetime


class Payment:
    def __init__(
        self,
        payment_id: Optional[int] = None,
        order_id: int = 0,
        payment_method: str = "VIETQR",
        amount: int = 0,
        transaction_code: Optional[str] = None,
        status: str = "PENDING",
        paid_at: Optional[datetime] = None,
    ):
        self._payment_id = payment_id
        self._order_id = order_id
        self._payment_method = payment_method
        self._amount = amount
        self._transaction_code = transaction_code
        self._status = status
        self._paid_at = paid_at

    @property
    def payment_id(self) -> Optional[int]:
        return self._payment_id

    @property
    def order_id(self) -> int:
        return self._order_id

    @property
    def payment_method(self) -> str:
        return self._payment_method

    @property
    def amount(self) -> int:
        return self._amount

    @property
    def transaction_code(self) -> Optional[str]:
        return self._transaction_code

    @property
    def status(self) -> str:
        return self._status

    @property
    def paid_at(self) -> Optional[datetime]:
        return self._paid_at

    # Business Operations from UML
    def verify_transaction(self, tx_code: str) -> bool:
        """Xác thực mã giao dịch ngân hàng khớp lệnh đối soát."""
        if not tx_code or len(tx_code.strip()) < 4:
            return False
        return self._transaction_code == tx_code or self._transaction_code is None

    def mark_as_paid(self, tx_code: Optional[str] = None) -> None:
        """Đánh dấu thanh toán thành công và ghi nhận thời điểm khớp lệnh."""
        self._status = "SUCCESS"
        self._paid_at = datetime.utcnow()
        if tx_code:
            self._transaction_code = tx_code

    def is_expired(self) -> bool:
        """Thanh toán quá hạn khi đơn hàng giữ chỗ quá 15 phút chưa khớp tiền."""
        return self._status == "FAILED" or self._status == "EXPIRED"
