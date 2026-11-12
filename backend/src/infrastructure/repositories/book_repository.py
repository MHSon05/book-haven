"""
Infrastructure Repository: BookRepository
Thực thi các câu lệnh truy vấn CSDL cho Book, BookEdition và BookEmbedding.
"""
from typing import List, Optional, Dict, Any
from ..database import DatabaseSession
from ...domain.entities.book import Book
from ...domain.entities.book_edition import BookEdition

class BookRepository:
    def __init__(self, session: DatabaseSession):
        self.session = session

    def get_book_by_id(self, book_id: str) -> Optional[Dict[str, Any]]:
        conn = self.session.get_connection()
        query = """
        SELECT b.*, a.author_name, a.nationality, p.publisher_name, c.category_name
        FROM books b
        JOIN authors a ON b.author_id = a.author_id
        JOIN publishers p ON b.publisher_id = p.publisher_id
        JOIN categories c ON b.category_id = c.category_id
        WHERE b.book_id = ? AND b.is_active = 1;
        """
        row = conn.execute(query, (book_id,)).fetchone()
        return dict(row) if row else None

    def get_all_books(
        self,
        category_id: Optional[str] = None,
        min_price: Optional[int] = None,
        max_price: Optional[int] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        conn = self.session.get_connection()
        conditions = ["b.is_active = 1"]
        params = []

        if category_id:
            conditions.append("b.category_id = ?")
            params.append(category_id)

        where_clause = " AND ".join(conditions)
        query = f"""
        SELECT b.*, a.author_name, p.publisher_name, c.category_name,
               MIN(e.unit_price) as min_price,
               MAX(e.unit_price) as max_price,
               SUM(e.stock_on_hand - e.stock_reserved) as total_available_stock
        FROM books b
        JOIN authors a ON b.author_id = a.author_id
        JOIN publishers p ON b.publisher_id = p.publisher_id
        JOIN categories c ON b.category_id = c.category_id
        JOIN book_editions e ON b.book_id = e.book_id
        WHERE {where_clause}
        GROUP BY b.book_id
        ORDER BY b.publish_year DESC, b.created_at DESC
        LIMIT ? OFFSET ?;
        """
        params.extend([limit, offset])
        rows = conn.execute(query, params).fetchall()
        results = [dict(r) for r in rows]

        # Lọc thêm theo khoảng giá nếu có yêu cầu
        if min_price is not None:
            results = [r for r in results if r.get("min_price", 0) >= min_price]
        if max_price is not None:
            results = [r for r in results if r.get("min_price", 0) <= max_price]

        return results

    def get_editions_by_book_id(self, book_id: str) -> List[BookEdition]:
        conn = self.session.get_connection()
        query = """
        SELECT e.*, b.title, b.cover_image
        FROM book_editions e
        JOIN books b ON e.book_id = b.book_id
        WHERE e.book_id = ?;
        """
        rows = conn.execute(query, (book_id,)).fetchall()
        return [
            BookEdition(
                edition_id=r["edition_id"],
                book_id=r["book_id"],
                sku=r["sku"],
                isbn13=r["isbn13"],
                binding_type=r["binding_type"],
                unit_price=r["unit_price"],
                weight_gram=r["weight_gram"],
                stock_on_hand=r["stock_on_hand"],
                stock_reserved=r["stock_reserved"],
                title=r["title"],
                cover_image=r["cover_image"]
            )
            for r in rows
        ]

    def get_edition_by_id(self, edition_id: str) -> Optional[BookEdition]:
        conn = self.session.get_connection()
        query = """
        SELECT e.*, b.title, b.cover_image
        FROM book_editions e
        JOIN books b ON e.book_id = b.book_id
        WHERE e.edition_id = ?;
        """
        r = conn.execute(query, (edition_id,)).fetchone()
        if not r:
            return None
        return BookEdition(
            edition_id=r["edition_id"],
            book_id=r["book_id"],
            sku=r["sku"],
            isbn13=r["isbn13"],
            binding_type=r["binding_type"],
            unit_price=r["unit_price"],
            weight_gram=r["weight_gram"],
            stock_on_hand=r["stock_on_hand"],
            stock_reserved=r["stock_reserved"],
            title=r["title"],
            cover_image=r["cover_image"]
        )

    def update_edition_stock(self, edition: BookEdition):
        conn = self.session.get_connection()
        query = """
        UPDATE book_editions
        SET stock_on_hand = ?, stock_reserved = ?
        WHERE edition_id = ?;
        """
        conn.execute(query, (edition.stock_on_hand, edition.stock_reserved, edition.edition_id))

    def search_books_sql(
        self,
        keyword: str,
        category_id: Optional[str] = None,
        binding_type: Optional[str] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        conn = self.session.get_connection()
        like_pattern = f"%{keyword.strip()}%"
        conditions = ["b.is_active = 1"]
        params = []

        if keyword:
            conditions.append("(b.title LIKE ? OR b.description LIKE ? OR a.author_name LIKE ? OR e.isbn13 LIKE ? OR e.sku LIKE ?)")
            params.extend([like_pattern, like_pattern, like_pattern, like_pattern, like_pattern])

        if category_id:
            conditions.append("b.category_id = ?")
            params.append(category_id)

        if binding_type:
            conditions.append("e.binding_type = ?")
            params.append(binding_type)

        where_clause = " AND ".join(conditions)
        query = f"""
        SELECT DISTINCT b.book_id, b.title, b.cover_image, b.description, b.category_id,
               a.author_name, p.publisher_name, c.category_name,
               e.edition_id, e.sku, e.binding_type, e.unit_price, e.weight_gram,
               (e.stock_on_hand - e.stock_reserved) as available_stock
        FROM books b
        JOIN authors a ON b.author_id = a.author_id
        JOIN publishers p ON b.publisher_id = p.publisher_id
        JOIN categories c ON b.category_id = c.category_id
        JOIN book_editions e ON b.book_id = e.book_id
        WHERE {where_clause}
        ORDER BY b.title ASC
        LIMIT ?;
        """
        params.append(limit)
        rows = conn.execute(query, params).fetchall()
        return [dict(r) for r in rows]

    def get_all_embeddings(self) -> List[Dict[str, Any]]:
        conn = self.session.get_connection()
        query = """
        SELECT be.book_id, be.vector_json, b.title, b.description, b.cover_image
        FROM book_embeddings be
        JOIN books b ON be.book_id = b.book_id
        WHERE b.is_active = 1;
        """
        rows = conn.execute(query).fetchall()
        return [dict(r) for r in rows]

    def get_all_categories(self) -> List[Dict[str, Any]]:
        conn = self.session.get_connection()
        rows = conn.execute("SELECT * FROM categories ORDER BY category_name ASC;").fetchall()
        return [dict(r) for r in rows]

    def get_book_entity_by_id(self, book_id: str) -> Optional[Book]:
        """Nạp thực thể Book đầy đủ thông tin văn học và danh sách ấn bản BookEdition."""
        conn = self.session.get_connection()
        query = """
        SELECT b.*, a.author_name, p.publisher_name, c.category_name
        FROM books b
        JOIN authors a ON b.author_id = a.author_id
        JOIN publishers p ON b.publisher_id = p.publisher_id
        JOIN categories c ON b.category_id = c.category_id
        WHERE b.book_id = ?;
        """
        row = conn.execute(query, (book_id,)).fetchone()
        if not row:
            return None
        editions = self.get_editions_by_book_id(book_id)
        return Book(
            book_id=row["book_id"],
            title=row["title"],
            author_id=row["author_id"],
            publisher_id=row["publisher_id"],
            category_id=row["category_id"],
            publish_year=row["publish_year"],
            description=row["description"],
            cover_image=row["cover_image"],
            is_active=bool(row["is_active"]),
            author_name=row["author_name"],
            publisher_name=row["publisher_name"],
            category_name=row["category_name"],
            created_at=row["created_at"],
            editions=editions,
        )

    def get_inventory_status(self) -> List[Dict[str, Any]]:
        """Truy vấn trạng thái tồn kho thực tế / giữ chỗ / khả dụng của toàn bộ ấn bản."""
        conn = self.session.get_connection()
        query = """
        SELECT e.edition_id, e.sku, e.binding_type, e.unit_price, e.weight_gram,
               e.stock_on_hand, e.stock_reserved,
               (e.stock_on_hand - e.stock_reserved) as available_stock,
               b.book_id, b.title, b.cover_image, c.category_name
        FROM book_editions e
        JOIN books b ON e.book_id = b.book_id
        JOIN categories c ON b.category_id = c.category_id
        ORDER BY b.title ASC, e.binding_type ASC;
        """
        rows = conn.execute(query).fetchall()
        return [dict(r) for r in rows]
