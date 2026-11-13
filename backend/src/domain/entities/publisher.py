"""
Domain Entity: Publisher
Nhà xuất bản đối tác của BookHaven.
Khớp 100% với Hình 4.3. KHÔNG dùng Enum.
"""
from typing import Optional, List
from datetime import datetime


class Publisher:
    def __init__(
        self,
        publisher_id: Optional[int] = None,
        publisher_name: str = "",
        address: str = "",
        contact_email: str = "",
        phone: str = "",
        created_at: Optional[datetime] = None,
    ):
        self._publisher_id = publisher_id
        self._publisher_name = publisher_name
        self._address = address
        self._contact_email = contact_email
        self._phone = phone
        self._created_at = created_at or datetime.utcnow()
        self._books: List[Any] = []

    @property
    def publisher_id(self) -> Optional[int]:
        return self._publisher_id

    @property
    def publisher_name(self) -> str:
        return self._publisher_name

    @property
    def address(self) -> str:
        return self._address

    @property
    def contact_email(self) -> str:
        return self._contact_email

    @property
    def phone(self) -> str:
        return self._phone

    @property
    def created_at(self) -> datetime:
        return self._created_at

    def get_published_books(self) -> List[Any]:
        return self._books

    def update_contact_info(self, email: str, phone: str) -> None:
        if email:
            self._contact_email = email
        if phone:
            self._phone = phone
