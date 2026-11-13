"""
Infrastructure Repository: CartRepository
Quản lý lưu trữ trạng thái giỏ hàng và danh mục sản phẩm chọn mua tạm thời.
Khớp 100% với Hình 4.3, 4.4 và CSDL 17 bảng.
KHÔNG dùng Enum.
"""
from typing import Optional, List
from datetime import datetime
from src.infrastructure.database import DatabaseSession
from src.domain.entities.cart import Cart
from src.domain.entities.cart_item import CartItem
from src.domain.entities.product import Product
from src.domain.entities.book import Book
from src.domain.entities.stationery import Stationery
from src.domain.entities.collectible import Collectible


class CartRepository:
    def __init__(self, session: DatabaseSession):
        self.session = session

    def get_or_create_cart(self, customer_id: int) -> Cart:
        conn = self.session.get_connection()
        row = conn.execute("SELECT cart_id FROM carts WHERE customer_id = ?;", (customer_id,)).fetchone()
        if row:
            cart_id = row["cart_id"]
        else:
            # Tạo mới giỏ hàng
            cur = conn.execute(
                "INSERT INTO carts (customer_id) VALUES (?);",
                (customer_id,)
            )
            cart_id = cur.lastrowid
        return self.get_cart_by_id(cart_id)

    def get_cart_by_id(self, cart_id: int) -> Cart:
        conn = self.session.get_connection()
        cart_row = conn.execute("SELECT customer_id FROM carts WHERE cart_id = ?;", (cart_id,)).fetchone()
        customer_id = cart_row["customer_id"] if cart_row else 0
        cart = Cart(cart_id=cart_id, customer_id=customer_id)

        query = """
        SELECT ci.cart_item_id, ci.cart_id, ci.product_id, ci.quantity,
               p.sku, p.name, p.unit_price, p.weight_gram, p.stock_on_hand, p.stock_reserved,
               p.category_id, p.description, p.cover_image, p.is_active,
               b.isbn13, b.publish_year, b.binding_type,
               s.brand, s.material as stat_material, s.color,
               c.origin, c.material as coll_material, c.dimensions
        FROM cart_items ci
        JOIN products p ON ci.product_id = p.product_id
        LEFT JOIN books b ON p.product_id = b.product_id
        LEFT JOIN stationeries s ON p.product_id = s.product_id
        LEFT JOIN collectibles c ON p.product_id = c.product_id
        WHERE ci.cart_id = ?;
        """
        rows = conn.execute(query, (cart_id,)).fetchall()
        for r in rows:
            # Reconstruct domain Product subclass
            if r["isbn13"]:
                prod = Book(
                    product_id=r["product_id"],
                    sku=r["sku"],
                    name=r["name"],
                    unit_price=r["unit_price"],
                    weight_gram=r["weight_gram"],
                    stock_on_hand=r["stock_on_hand"],
                    stock_reserved=r["stock_reserved"],
                    category_id=r["category_id"],
                    description=r["description"],
                    cover_image=r["cover_image"],
                    is_active=bool(r["is_active"]),
                    isbn13=r["isbn13"],
                    publish_year=r["publish_year"] or 2024,
                    binding_type=r["binding_type"] or "Paperback",
                )
            elif r["brand"]:
                prod = Stationery(
                    product_id=r["product_id"],
                    sku=r["sku"],
                    name=r["name"],
                    unit_price=r["unit_price"],
                    weight_gram=r["weight_gram"],
                    stock_on_hand=r["stock_on_hand"],
                    stock_reserved=r["stock_reserved"],
                    category_id=r["category_id"],
                    description=r["description"],
                    cover_image=r["cover_image"],
                    is_active=bool(r["is_active"]),
                    brand=r["brand"],
                    material=r["stat_material"] or "",
                    color=r["color"] or "",
                )
            elif r["origin"] or r["dimensions"]:
                prod = Collectible(
                    product_id=r["product_id"],
                    sku=r["sku"],
                    name=r["name"],
                    unit_price=r["unit_price"],
                    weight_gram=r["weight_gram"],
                    stock_on_hand=r["stock_on_hand"],
                    stock_reserved=r["stock_reserved"],
                    category_id=r["category_id"],
                    description=r["description"],
                    cover_image=r["cover_image"],
                    is_active=bool(r["is_active"]),
                    origin=r["origin"] or "",
                    material=r["coll_material"] or "",
                    dimensions=r["dimensions"] or "",
                )
            else:
                prod = Book(
                    product_id=r["product_id"],
                    sku=r["sku"],
                    name=r["name"],
                    unit_price=r["unit_price"],
                    weight_gram=r["weight_gram"],
                    stock_on_hand=r["stock_on_hand"],
                    stock_reserved=r["stock_reserved"],
                    category_id=r["category_id"],
                    description=r["description"],
                    cover_image=r["cover_image"],
                    is_active=bool(r["is_active"]),
                    isbn13="",
                )

            item = CartItem(
                cart_item_id=r["cart_item_id"],
                cart_id=cart_id,
                product=prod,
                product_id=r["product_id"],
                quantity=r["quantity"],
            )
            cart.items.append(item)
        return cart

    def save_item(self, cart_id: int, product_id: int, quantity: int) -> None:
        conn = self.session.get_connection()
        query = """
        INSERT INTO cart_items (cart_id, product_id, quantity, updated_at)
        VALUES (?, ?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(cart_id, product_id) DO UPDATE SET
            quantity = excluded.quantity,
            updated_at = CURRENT_TIMESTAMP;
        """
        conn.execute(query, (cart_id, product_id, quantity))

    def remove_item(self, cart_id: int, product_id: int) -> None:
        conn = self.session.get_connection()
        conn.execute(
            "DELETE FROM cart_items WHERE cart_id = ? AND product_id = ?;",
            (cart_id, product_id)
        )

    def clear_cart(self, cart_id: int) -> None:
        conn = self.session.get_connection()
        conn.execute("DELETE FROM cart_items WHERE cart_id = ?;", (cart_id,))
