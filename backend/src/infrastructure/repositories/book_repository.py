"""
Infrastructure Repository: BookRepository
Thực thi các câu lệnh truy vấn CSDL cho Products, Books, Stationeries, Collectibles và Embeddings.
Khớp 100% với cấu trúc 17 bảng (Table-per-subclass).
KHÔNG dùng Enum.
"""
from typing import List, Optional, Dict, Any
from src.infrastructure.database import DatabaseSession
from src.domain.entities.book import Book
from src.domain.entities.stationery import Stationery
from src.domain.entities.collectible import Collectible
from src.domain.entities.product import Product


class BookRepository:
    def __init__(self, session: DatabaseSession):
        self.session = session

    def get_book_by_id(self, product_id: int) -> Optional[Dict[str, Any]]:
        conn = self.session.get_connection()
        query = """
        SELECT p.product_id, p.product_id as book_id, p.category_id, p.sku, p.name as title, p.unit_price, p.weight_gram,
               p.stock_on_hand, p.stock_reserved, p.cover_image, p.description, p.is_active,
               COALESCE(b.isbn13, '') as isbn13,
               COALESCE(b.publish_year, 2026) as publish_year,
               COALESCE(b.binding_type, s.brand, c2.origin, 'Tiêu chuẩn') as binding_type,
               COALESCE(a.author_name, s.brand, 'Nhiều tác giả') as author_name,
               a.nationality,
               COALESCE(pub.publisher_name, s.brand, 'Fahasa') as publisher_name,
               c.category_name, c.slug as category_slug
        FROM products p
        LEFT JOIN books b ON p.product_id = b.product_id
        LEFT JOIN stationeries s ON p.product_id = s.product_id
        LEFT JOIN collectibles c2 ON p.product_id = c2.product_id
        LEFT JOIN authors a ON b.author_id = a.author_id
        LEFT JOIN publishers pub ON b.publisher_id = pub.publisher_id
        LEFT JOIN categories c ON p.category_id = c.category_id
        WHERE p.product_id = ? AND p.is_active = 1;
        """
        row = conn.execute(query, (product_id,)).fetchone()
        return dict(row) if row else None

    def get_all_books(
        self,
        category_id: Optional[int] = None,
        min_price: Optional[int] = None,
        max_price: Optional[int] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        conn = self.session.get_connection()
        conditions = ["p.is_active = 1"]
        params = []

        if category_id:
            conditions.append("p.category_id = ?")
            params.append(category_id)
        if min_price is not None:
            conditions.append("p.unit_price >= ?")
            params.append(min_price)
        if max_price is not None:
            conditions.append("p.unit_price <= ?")
            params.append(max_price)

        where_clause = " AND ".join(conditions)
        query = f"""
        SELECT p.product_id, p.product_id as book_id, p.category_id, p.sku, p.name as title, p.unit_price, p.weight_gram,
               p.stock_on_hand, p.stock_reserved, p.cover_image, p.description,
               (p.stock_on_hand - p.stock_reserved) as available_stock,
               p.unit_price as min_price, p.unit_price as max_price,
               (p.stock_on_hand - p.stock_reserved) as total_available_stock,
               COALESCE(b.isbn13, '') as isbn13,
               COALESCE(b.publish_year, 2026) as publish_year,
               COALESCE(b.binding_type, s.brand, c2.origin, 'Tiêu chuẩn') as binding_type,
               COALESCE(a.author_name, s.brand, 'Nhiều tác giả') as author_name,
               COALESCE(pub.publisher_name, s.brand, 'Fahasa') as publisher_name,
               c.category_name
        FROM products p
        LEFT JOIN books b ON p.product_id = b.product_id
        LEFT JOIN stationeries s ON p.product_id = s.product_id
        LEFT JOIN collectibles c2 ON p.product_id = c2.product_id
        LEFT JOIN authors a ON b.author_id = a.author_id
        LEFT JOIN publishers pub ON b.publisher_id = pub.publisher_id
        LEFT JOIN categories c ON p.category_id = c.category_id
        WHERE {where_clause}
        ORDER BY p.product_id ASC
        LIMIT ? OFFSET ?;
        """
        params.extend([limit, offset])
        rows = conn.execute(query, params).fetchall()
        return [dict(r) for r in rows]

    def get_edition_by_id(self, product_id: int) -> Optional[Book]:
        """Tương thích với các service cũ gọi get_edition_by_id."""
        return self.get_book_entity_by_id(product_id)

    def get_editions_by_book_id(self, product_id: int) -> List[Any]:
        """Tương thích với API get_book_detail: trả về Product entity tương ứng (Book, Stationery hoặc Collectible)."""
        product = self.get_product_by_id(int(product_id))
        return [product] if product else []

    def get_book_entity_by_id(self, product_id: int) -> Optional[Book]:
        conn = self.session.get_connection()
        query = """
        SELECT p.*, b.isbn13, b.author_id, b.publisher_id, b.publish_year, b.binding_type
        FROM products p
        JOIN books b ON p.product_id = b.product_id
        WHERE p.product_id = ?;
        """
        row = conn.execute(query, (product_id,)).fetchone()
        if not row:
            return None
        return Book(
            product_id=row["product_id"],
            sku=row["sku"],
            name=row["name"],
            unit_price=row["unit_price"],
            weight_gram=row["weight_gram"],
            stock_on_hand=row["stock_on_hand"],
            stock_reserved=row["stock_reserved"],
            category_id=row["category_id"],
            description=row["description"],
            cover_image=row["cover_image"],
            is_active=bool(row["is_active"]),
            isbn13=row["isbn13"],
            author_id=row["author_id"],
            publisher_id=row["publisher_id"],
            publish_year=row["publish_year"],
            binding_type=row["binding_type"],
        )

    def get_product_by_id(self, product_id: int) -> Optional[Product]:
        """Lấy thực thể Product tổng quát (Book, Stationery hoặc Collectible)."""
        book = self.get_book_entity_by_id(product_id)
        if book:
            return book

        conn = self.session.get_connection()
        # Thử Stationery
        row_stat = conn.execute("""
            SELECT p.*, s.brand, s.material, s.color
            FROM products p
            JOIN stationeries s ON p.product_id = s.product_id
            WHERE p.product_id = ?;
        """, (product_id,)).fetchone()
        if row_stat:
            return Stationery(
                product_id=row_stat["product_id"],
                sku=row_stat["sku"],
                name=row_stat["name"],
                unit_price=row_stat["unit_price"],
                weight_gram=row_stat["weight_gram"],
                stock_on_hand=row_stat["stock_on_hand"],
                stock_reserved=row_stat["stock_reserved"],
                category_id=row_stat["category_id"],
                description=row_stat["description"],
                cover_image=row_stat["cover_image"],
                is_active=bool(row_stat["is_active"]),
                brand=row_stat["brand"],
                material=row_stat["material"] or "",
                color=row_stat["color"] or "",
            )

        # Thử Collectible
        row_coll = conn.execute("""
            SELECT p.*, c.origin, c.material, c.dimensions
            FROM products p
            JOIN collectibles c ON p.product_id = c.product_id
            WHERE p.product_id = ?;
        """, (product_id,)).fetchone()
        if row_coll:
            return Collectible(
                product_id=row_coll["product_id"],
                sku=row_coll["sku"],
                name=row_coll["name"],
                unit_price=row_coll["unit_price"],
                weight_gram=row_coll["weight_gram"],
                stock_on_hand=row_coll["stock_on_hand"],
                stock_reserved=row_coll["stock_reserved"],
                category_id=row_coll["category_id"],
                description=row_coll["description"],
                cover_image=row_coll["cover_image"],
                is_active=bool(row_coll["is_active"]),
                origin=row_coll["origin"] or "",
                material=row_coll["material"] or "",
                dimensions=row_coll["dimensions"] or "",
            )
        return None

    def update_product_stock(self, product: Product) -> None:
        """Cập nhật tồn kho thực tế và tồn giữ chỗ của Product trong bảng products."""
        conn = self.session.get_connection()
        conn.execute(
            "UPDATE products SET stock_on_hand = ?, stock_reserved = ? WHERE product_id = ?;",
            (product.stock_on_hand, product.stock_reserved, product.product_id)
        )

    def update_edition_stock(self, product_or_sku: Any, stock_reserved: Optional[int] = None):
        """Tương thích ngược cho update_edition_stock."""
        if isinstance(product_or_sku, Product):
            self.update_product_stock(product_or_sku)
        elif stock_reserved is not None:
            conn = self.session.get_connection()
            conn.execute(
                "UPDATE products SET stock_reserved = ? WHERE sku = ?;",
                (stock_reserved, str(product_or_sku))
            )

    def search_books_sql(
        self,
        query: str,
        category_id: Optional[Any] = None,
        binding_type: Optional[str] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        conn = self.session.get_connection()
        param = f"%{query}%"
        conditions = ["p.is_active = 1", "(p.name LIKE ? OR a.author_name LIKE ? OR b.isbn13 LIKE ?)"]
        params: List[Any] = [param, param, param]

        if category_id:
            conditions.append("p.category_id = ?")
            params.append(category_id)
        if binding_type:
            conditions.append("b.binding_type = ?")
            params.append(binding_type)

        where_clause = " AND ".join(conditions)
        sql = f"""
        SELECT p.product_id, p.product_id as book_id, p.category_id, p.sku, p.name as title, p.unit_price, p.cover_image,
               p.description,
               (p.stock_on_hand - p.stock_reserved) as available_stock,
               COALESCE(a.author_name, s.brand, 'Nhiều tác giả') as author_name,
               COALESCE(pub.publisher_name, s.brand, 'Fahasa') as publisher_name,
               c.category_name,
               COALESCE(b.isbn13, '') as isbn13
        FROM products p
        LEFT JOIN books b ON p.product_id = b.product_id
        LEFT JOIN stationeries s ON p.product_id = s.product_id
        LEFT JOIN collectibles c2 ON p.product_id = c2.product_id
        LEFT JOIN authors a ON b.author_id = a.author_id
        LEFT JOIN publishers pub ON b.publisher_id = pub.publisher_id
        LEFT JOIN categories c ON p.category_id = c.category_id
        WHERE {where_clause}
        LIMIT ?;
        """
        params.append(limit)
        rows = conn.execute(sql, tuple(params)).fetchall()
        return [dict(r) for r in rows]

    def get_all_embeddings(self) -> List[Dict[str, Any]]:
        conn = self.session.get_connection()
        query = """
        SELECT e.product_id, e.product_id as book_id, e.vector_json, e.model_name,
               p.name as title, p.cover_image, p.unit_price, p.description,
               a.author_name, pub.publisher_name, c.category_name,
               (p.stock_on_hand - p.stock_reserved) as available_stock
        FROM book_embeddings e
        JOIN products p ON e.product_id = p.product_id
        LEFT JOIN books b ON p.product_id = b.product_id
        LEFT JOIN authors a ON b.author_id = a.author_id
        LEFT JOIN publishers pub ON b.publisher_id = pub.publisher_id
        LEFT JOIN categories c ON p.category_id = c.category_id
        WHERE p.is_active = 1;
        """
        rows = conn.execute(query).fetchall()
        return [dict(r) for r in rows]

    def get_all_categories(self) -> List[Dict[str, Any]]:
        conn = self.session.get_connection()
        rows = conn.execute("""
            SELECT c.*, COUNT(p.product_id) as product_count
            FROM categories c
            LEFT JOIN products p ON c.category_id = p.category_id AND p.is_active = 1
            GROUP BY c.category_id
            ORDER BY c.category_id ASC;
        """).fetchall()
        return [dict(r) for r in rows]

    def get_inventory_status(self) -> List[Dict[str, Any]]:
        conn = self.session.get_connection()
        query = """
        SELECT p.product_id, p.sku, p.name, p.unit_price, p.weight_gram,
               p.stock_on_hand, p.stock_reserved,
               (p.stock_on_hand - p.stock_reserved) as available_stock,
               c.category_name
        FROM products p
        LEFT JOIN categories c ON p.category_id = c.category_id
        ORDER BY p.product_id ASC;
        """
        rows = conn.execute(query).fetchall()
        return [dict(r) for r in rows]
