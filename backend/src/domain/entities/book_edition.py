"""
Domain Entity: BookEdition
Chịu trách nhiệm kiểm soát quy tắc nghiệp vụ bất biến về Tồn kho (BR01, BR02, BR03).
"""
from dataclasses import dataclass
from typing import Optional
from ..exceptions import OutOfStockException

@dataclass
class BookEdition:
    edition_id: str
    book_id: str
    sku: str
    isbn13: str
    binding_type: str  # PAPERBACK, HARDCOVER
    unit_price: int
    weight_gram: int
    stock_on_hand: int
    stock_reserved: int = 0
    title: Optional[str] = None
    cover_image: Optional[str] = None

    def available_stock(self) -> int:
        """Tồn kho khả dụng = tồn thực tế - tồn đang giữ chỗ (BR02)."""
        return max(0, self.stock_on_hand - self.stock_reserved)

    def is_available(self, requested_qty: int) -> bool:
        """Kiểm tra số lượng yêu cầu có hợp lệ với tồn khả dụng không."""
        if requested_qty <= 0:
            return False
        return self.available_stock() >= requested_qty

    def reserve_stock(self, quantity: int):
        """Khóa giữ chỗ tồn kho 15 phút (BR03). Ném ngoại lệ OutOfStockException nếu không đủ."""
        if not self.is_available(quantity):
            raise OutOfStockException(
                sku=self.sku,
                requested=quantity,
                available=self.available_stock()
            )
        self.stock_reserved += quantity

    def release_reservation(self, quantity: int):
        """Giải phóng lượng giữ chỗ khi đơn bị hủy hoặc hết hạn 15 phút."""
        self.stock_reserved = max(0, self.stock_reserved - quantity)

    def confirm_deduction(self, quantity: int):
        """Khấu trừ chính thức cả tồn kho thực tế và lượng giữ chỗ khi thanh toán thành công."""
        self.stock_on_hand = max(0, self.stock_on_hand - quantity)
        self.stock_reserved = max(0, self.stock_reserved - quantity)

    def add_stock(self, quantity: int):
        """Thủ kho nhập thêm sách từ NXB (UC12)."""
        if quantity <= 0:
            raise ValueError("Số lượng nhập kho phải là số nguyên dương lớn hơn 0.")
        self.stock_on_hand += quantity
