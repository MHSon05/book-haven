"""
Domain Entity: Author
Tác giả tác phẩm sách.
Khớp 100% với Hình 4.3. KHÔNG dùng Enum.
"""
from typing import Optional, List
from datetime import datetime


class Author:
    def __init__(
        self,
        author_id: Optional[int] = None,
        author_name: str = "",
        biography: str = "",
        nationality: str = "",
        created_at: Optional[datetime] = None,
    ):
        self._author_id = author_id
        self._author_name = author_name
        self._biography = biography
        self._nationality = nationality
        self._created_at = created_at or datetime.utcnow()
        self._books: List[Any] = []

    @property
    def author_id(self) -> Optional[int]:
        return self._author_id

    @property
    def author_name(self) -> str:
        return self._author_name

    @property
    def biography(self) -> str:
        return self._biography

    @property
    def nationality(self) -> str:
        return self._nationality

    @property
    def created_at(self) -> datetime:
        return self._created_at

    def get_authored_books(self) -> List[Any]:
        return self._books

    def update_biography(self, bio: str) -> None:
        self._biography = bio
