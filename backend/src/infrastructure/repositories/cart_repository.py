"""
Infrastructure Repository: CartRepository
Quản lý lưu trữ trạng thái giỏ hàng và danh mục ấn bản chọn mua tạm thời.
"""
from ..database import DatabaseSession
from ...domain.entities.cart import Cart, CartItem
from ...domain.entities.book_edition import BookEdition

class CartRepository:
    def __init__(self, session: DatabaseSession):
        self.session = session

    def get_or_create_cart(self, customer_id: str) -> Cart:
        conn = self.session.get_connection()
        row = conn.execute("SELECT cart_id FROM carts WHERE customer_id = ?;", (customer_id,)).fetchone()
        if row:
            cart_id = row["cart_id"]
        else:
            cart_id = f"CART_{customer_id}"
            user_row = conn.execute("SELECT user_id FROM users WHERE user_id = ?;", (customer_id,)).fetchone()
            if not user_row:
                conn.execute(
                    """
                    INSERT OR IGNORE INTO users (user_id, username, password_hash, email, full_name, role)
                    VALUES (?, ?, ?, ?, ?, 'CUSTOMER');
                    """,
                    (customer_id, customer_id.lower(), "GUEST_NO_AUTH", f"{customer_id.lower()}@guest.bookhaven.vn", "Khách vãng lai")
                )
            conn.execute(
                "INSERT INTO carts (cart_id, customer_id) VALUES (?, ?);",
                (cart_id, customer_id)
            )
        return self.get_cart_by_id(cart_id)

    def get_cart_by_id(self, cart_id: str) -> Cart:
        conn = self.session.get_connection()
        cart_row = conn.execute("SELECT customer_id FROM carts WHERE cart_id = ?;", (cart_id,)).fetchone()
        customer_id = cart_row["customer_id"] if cart_row else ""
        cart = Cart(cart_id=cart_id, customer_id=customer_id)

        query = """
        SELECT ci.cart_item_id, ci.cart_id, ci.edition_id, ci.quantity,
               e.book_id, e.sku, e.isbn13, e.binding_type, e.unit_price, e.weight_gram,
               e.stock_on_hand, e.stock_reserved, b.title, b.cover_image
        FROM cart_items ci
        JOIN book_editions e ON ci.edition_id = e.edition_id
        JOIN books b ON e.book_id = b.book_id
        WHERE ci.cart_id = ?;
        """
        rows = conn.execute(query, (cart_id,)).fetchall()
        for r in rows:
            edition = BookEdition(
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
            cart.items[edition.edition_id] = CartItem(
                cart_item_id=r["cart_item_id"],
                cart_id=cart_id,
                edition_id=edition.edition_id,
                quantity=r["quantity"],
                edition=edition
            )
        return cart

    def save_item(self, cart_id: str, edition_id: str, quantity: int):
        conn = self.session.get_connection()
        cart_item_id = f"ITEM_{cart_id}_{edition_id}"
        query = """
        INSERT INTO cart_items (cart_item_id, cart_id, edition_id, quantity)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(cart_id, edition_id) DO UPDATE SET quantity = excluded.quantity;
        """
        conn.execute(query, (cart_item_id, cart_id, edition_id, quantity))

    def remove_item(self, cart_id: str, edition_id: str):
        conn = self.session.get_connection()
        conn.execute(
            "DELETE FROM cart_items WHERE cart_id = ? AND edition_id = ?;",
            (cart_id, edition_id)
        )

    def clear_cart(self, cart_id: str):
        conn = self.session.get_connection()
        conn.execute("DELETE FROM cart_items WHERE cart_id = ?;", (cart_id,))
