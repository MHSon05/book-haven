"""
Domain Entity: Book
Lớp con kế thừa từ Product đại diện cho sách in (250 đầu sách Fahasa).
Khớp 100% với Hình 4.3. KHÔNG dùng Enum - binding_type là string ('Paperback', 'Hardcover').
"""
from typing import Dict, Any, Optional
from datetime import datetime
from src.domain.entities.product import Product


class Book(Product):
    def __init__(
        self,
        product_id: Optional[int] = None,
        sku: str = "",
        name: str = "",
        unit_price: int = 0,
        weight_gram: int = 0,
        stock_on_hand: int = 0,
        stock_reserved: int = 0,
        category_id: Optional[int] = None,
        description: str = "",
        cover_image: str = "",
        is_active: bool = True,
        isbn13: str = "",
        author_id: Optional[int] = None,
        publisher_id: Optional[int] = None,
        publish_year: int = 2024,
        binding_type: str = "Paperback",
        created_at: Optional[datetime] = None,
    ):
        super().__init__(
            product_id=product_id,
            sku=sku,
            name=name,
            unit_price=unit_price,
            weight_gram=weight_gram,
            stock_on_hand=stock_on_hand,
            stock_reserved=stock_reserved,
            category_id=category_id,
            description=description,
            cover_image=cover_image,
            is_active=is_active,
            created_at=created_at,
        )
        self._isbn13 = isbn13
        self._author_id = author_id
        self._publisher_id = publisher_id
        self._publish_year = publish_year
        self._binding_type = binding_type

    @property
    def isbn13(self) -> str:
        return self._isbn13

    @property
    def author_id(self) -> Optional[int]:
        return self._author_id

    @property
    def publisher_id(self) -> Optional[int]:
        return self._publisher_id

    @property
    def publish_year(self) -> int:
        return self._publish_year

    @property
    def binding_type(self) -> str:
        return self._binding_type

    # Specific Business Operations
    def is_valid_isbn13(self) -> bool:
        """Kiểm tra định dạng chuẩn ISBN-13 (13 chữ số, bắt đầu bằng 978 hoặc 979)."""
        clean = self._isbn13.replace("-", "").strip()
        return len(clean) == 13 and clean.isdigit() and clean.startswith(("978", "979"))

    def calculate_book_age(self) -> int:
        """Tính tuổi đời của sách so với năm hiện tại."""
        current_year = datetime.utcnow().year
        return max(0, current_year - self._publish_year)

    # Overridden Polymorphic Operations
    def is_searchable(self) -> bool:
        return self._is_active and self.get_available_stock() > 0 and len(self._isbn13) > 0

    def get_specifications(self) -> Dict[str, Any]:
        return {
            "kind": "BOOK",
            "isbn13": self._isbn13,
            "publish_year": self._publish_year,
            "binding_type": self._binding_type,
            "author_id": self._author_id,
            "publisher_id": self._publisher_id,
            "book_age_years": self.calculate_book_age(),
        }

    def build_search_document(self) -> str:
        return f"{self._name} ISBN: {self._isbn13} Năm xuất bản: {self._publish_year} Hình thức: {self._binding_type} {self._description}"
