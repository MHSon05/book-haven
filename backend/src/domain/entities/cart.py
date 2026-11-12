"""
Domain Entity: Cart & CartItem
Mô hình hóa giỏ hàng và danh mục sản phẩm chọn mua tạm thời của độc giả.
Tuân thủ nguyên tắc: CartItem is NOT OrderItem (Slide 04 & Slide 19).
"""
from dataclasses import dataclass, field
from typing import Dict, Optional
from .book_edition import BookEdition

@dataclass
class CartItem:
    cart_item_id: str
    cart_id: str
    edition_id: str
    quantity: int
    edition: Optional[BookEdition] = None

    def subtotal(self) -> int:
        if not self.edition:
            return 0
        return self.edition.unit_price * self.quantity


@dataclass
class Cart:
    cart_id: str
    customer_id: str
    items: Dict[str, CartItem] = field(default_factory=dict)  # Key: edition_id

    def add_item(self, edition: BookEdition, quantity: int = 1):
        """Thêm hoặc cộng dồn số lượng ấn bản sách trong giỏ."""
        if quantity <= 0:
            raise ValueError("Số lượng thêm vào giỏ phải lớn hơn 0.")
        
        if edition.edition_id in self.items:
            self.items[edition.edition_id].quantity += quantity
        else:
            self.items[edition.edition_id] = CartItem(
                cart_item_id=f"ITEM_{self.cart_id}_{edition.edition_id}",
                cart_id=self.cart_id,
                edition_id=edition.edition_id,
                quantity=quantity,
                edition=edition
            )

    def update_quantity(self, edition_id: str, quantity: int):
        """Cập nhật số lượng ấn bản trong giỏ hoặc xóa nếu quantity <= 0."""
        if edition_id not in self.items:
            raise KeyError(f"Ấn bản {edition_id} không có trong giỏ hàng.")
        
        if quantity <= 0:
            del self.items[edition_id]
        else:
            self.items[edition_id].quantity = quantity

    def remove_item(self, edition_id: str):
        """Xóa hẳn một dòng ấn bản khỏi giỏ."""
        if edition_id in self.items:
            del self.items[edition_id]

    def clear(self):
        """Dọn sạch giỏ hàng sau khi checkout thành công."""
        self.items.clear()

    def calculate_subtotal(self) -> int:
        """Tính tổng tiền tạm tính của các dòng giỏ hàng."""
        return sum(item.subtotal() for item in self.items.values())

    def calculate_total_weight_grams(self) -> int:
        """Tính tổng trọng lượng gram sách trong giỏ."""
        total = 0
        for item in self.items.values():
            if item.edition:
                total += item.edition.weight_gram * item.quantity
        return total
