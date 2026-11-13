"""
Infrastructure Repository: OrderRepository
Quản lý lưu trữ Đơn hàng, OrderItem snapshot, StockReservation và Payment.
Khớp 100% với Hình 4.3, Hình 4.4 và CSDL 17 bảng.
KHÔNG dùng Enum - toàn bộ trạng thái, phương thức thanh toán, đơn vị vận chuyển là chuỗi (string).
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from src.infrastructure.database import DatabaseSession
from src.domain.entities.order import Order
from src.domain.entities.order_item import OrderItem
from src.domain.entities.payment import Payment
from src.domain.entities.stock_reservation import StockReservation


class OrderRepository:
    def __init__(self, session: DatabaseSession):
        self.session = session

    def save_order(self, order: Order) -> int:
        conn = self.session.get_connection()
        query_order = """
        INSERT INTO orders (
            order_id, customer_id, receiver_name, receiver_phone, shipping_address,
            payment_method, total_amount, shipping_fee, discount_amount, final_amount,
            status, carrier, tracking_code, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(order_id) DO UPDATE SET
            status = excluded.status,
            carrier = excluded.carrier,
            tracking_code = excluded.tracking_code,
            updated_at = CURRENT_TIMESTAMP;
        """
        cur = conn.execute(query_order, (
            order.order_id,
            order.customer_id,
            order.receiver_name,
            order.receiver_phone,
            order.shipping_address,
            str(order.payment_method),
            order.total_amount,
            order.shipping_fee,
            order.discount_amount,
            order.final_amount,
            str(order.status),
            str(order.carrier) if order.carrier else "GHN",
            order.tracking_code,
            order.created_at.strftime("%Y-%m-%d %H:%M:%S") if isinstance(order.created_at, datetime) else str(order.created_at),
            datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
        ))
        assigned_id = order.order_id or cur.lastrowid

        # Lưu OrderItems (Snapshot bất biến)
        for item in order.items:
            query_item = """
            INSERT OR REPLACE INTO order_items (
                order_item_id, order_id, product_id, product_name_snapshot, sku_snapshot,
                product_kind_snapshot, unit_price_at_purchase, quantity, weight_gram_snapshot, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """
            conn.execute(query_item, (
                item.order_item_id,
                assigned_id,
                item.product_id,
                item.product_name_snapshot,
                item.sku_snapshot,
                str(item.product_kind_snapshot),
                item.unit_price_at_purchase,
                item.quantity,
                item.weight_gram_snapshot,
                item.created_at.strftime("%Y-%m-%d %H:%M:%S") if isinstance(item.created_at, datetime) else str(item.created_at),
            ))
        return assigned_id

    def get_order_by_id(self, order_id: int) -> Optional[Order]:
        conn = self.session.get_connection()
        row = conn.execute("SELECT * FROM orders WHERE order_id = ?;", (order_id,)).fetchone()
        if not row:
            return None

        # Nạp items
        items_rows = conn.execute("SELECT * FROM order_items WHERE order_id = ?;", (order_id,)).fetchall()
        items = [
            OrderItem(
                order_item_id=ir["order_item_id"],
                order_id=ir["order_id"],
                product_id=ir["product_id"],
                product_name_snapshot=ir["product_name_snapshot"],
                sku_snapshot=ir["sku_snapshot"],
                product_kind_snapshot=ir["product_kind_snapshot"],
                unit_price_at_purchase=ir["unit_price_at_purchase"],
                quantity=ir["quantity"],
                weight_gram_snapshot=ir["weight_gram_snapshot"],
                created_at=datetime.strptime(ir["created_at"], "%Y-%m-%d %H:%M:%S") if ir["created_at"] and len(str(ir["created_at"])) == 19 else None,
            )
            for ir in items_rows
        ]

        return Order(
            order_id=row["order_id"],
            customer_id=row["customer_id"],
            receiver_name=row["receiver_name"],
            receiver_phone=row["receiver_phone"],
            shipping_address=row["shipping_address"],
            payment_method=row["payment_method"],
            carrier=row["carrier"] or "GHN",
            total_amount=row["total_amount"],
            shipping_fee=row["shipping_fee"],
            discount_amount=row["discount_amount"],
            final_amount=row["final_amount"],
            status=row["status"],
            items=items,
            tracking_code=row["tracking_code"],
        )

    def get_orders_by_customer(self, customer_id: int) -> List[Order]:
        conn = self.session.get_connection()
        rows = conn.execute(
            "SELECT order_id FROM orders WHERE customer_id = ? ORDER BY created_at DESC;",
            (customer_id,)
        ).fetchall()
        orders = []
        for r in rows:
            o = self.get_order_by_id(r["order_id"])
            if o:
                orders.append(o)
        return orders

    def get_all_orders(self, status: Optional[str] = None, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        conn = self.session.get_connection()
        conditions = []
        params = []
        if status:
            conditions.append("o.status = ?")
            params.append(status)

        where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""
        query = f"""
        SELECT o.*, u.full_name as customer_name, u.email as customer_email,
               COUNT(oi.order_item_id) as total_items
        FROM orders o
        JOIN users u ON o.customer_id = u.user_id
        LEFT JOIN order_items oi ON o.order_id = oi.order_id
        {where_clause}
        GROUP BY o.order_id
        ORDER BY o.created_at DESC
        LIMIT ? OFFSET ?;
        """
        params.extend([limit, offset])
        rows = conn.execute(query, params).fetchall()
        return [dict(r) for r in rows]

    def save_stock_reservation(self, reservation: StockReservation) -> int:
        conn = self.session.get_connection()
        query = """
        INSERT INTO stock_reservations (order_id, product_id, reserved_quantity, expires_at, status)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(reservation_id) DO UPDATE SET status = excluded.status;
        """
        cur = conn.execute(query, (
            reservation.order_id,
            reservation.product_id,
            reservation.reserved_quantity,
            reservation.expires_at.strftime("%Y-%m-%d %H:%M:%S") if isinstance(reservation.expires_at, datetime) else str(reservation.expires_at),
            str(reservation.status)
        ))
        return reservation.reservation_id or cur.lastrowid

    def get_pending_expired_reservations(self) -> List[Dict[str, Any]]:
        conn = self.session.get_connection()
        now_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        query = """
        SELECT r.*, p.sku, p.name as product_name
        FROM stock_reservations r
        JOIN products p ON r.product_id = p.product_id
        WHERE r.status = 'PENDING' AND r.expires_at < ?;
        """
        rows = conn.execute(query, (now_str,)).fetchall()
        return [dict(r) for r in rows]

    def update_reservation_status(self, reservation_id: int, status: str) -> None:
        conn = self.session.get_connection()
        conn.execute(
            "UPDATE stock_reservations SET status = ? WHERE reservation_id = ?;",
            (status, reservation_id)
        )

    def update_reservations_status_by_order(self, order_id: int, status: str) -> None:
        conn = self.session.get_connection()
        conn.execute(
            "UPDATE stock_reservations SET status = ? WHERE order_id = ?;",
            (status, order_id)
        )

    def save_payment_record(self, payment: Payment) -> int:
        conn = self.session.get_connection()
        query = """
        INSERT INTO payments (order_id, payment_method, amount, transaction_code, status, paid_at)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(order_id) DO UPDATE SET
            status = excluded.status,
            transaction_code = excluded.transaction_code,
            paid_at = excluded.paid_at;
        """
        cur = conn.execute(query, (
            payment.order_id,
            str(payment.payment_method),
            payment.amount,
            payment.transaction_code,
            str(payment.status),
            payment.paid_at.strftime("%Y-%m-%d %H:%M:%S") if payment.paid_at else None
        ))
        return payment.payment_id or cur.lastrowid

    def get_payment_by_order_id(self, order_id: int) -> Optional[Payment]:
        conn = self.session.get_connection()
        row = conn.execute("SELECT * FROM payments WHERE order_id = ?;", (order_id,)).fetchone()
        if not row:
            return None
        return Payment(
            payment_id=row["payment_id"],
            order_id=row["order_id"],
            payment_method=row["payment_method"],
            amount=row["amount"],
            transaction_code=row["transaction_code"],
            status=row["status"],
        )

    def get_revenue_summary(self) -> Dict[str, Any]:
        """Thống kê tổng doanh thu thực thu và top 5 sách bán chạy nhất."""
        conn = self.session.get_connection()
        rev_row = conn.execute("""
            SELECT COALESCE(SUM(final_amount), 0) as total_revenue,
                   COUNT(order_id) as total_orders
            FROM orders
            WHERE status IN ('PAID', 'SHIPPING', 'DELIVERED');
        """).fetchone()

        items_row = conn.execute("""
            SELECT COALESCE(SUM(oi.quantity), 0) as total_items_sold
            FROM order_items oi
            JOIN orders o ON oi.order_id = o.order_id
            WHERE o.status IN ('PAID', 'SHIPPING', 'DELIVERED');
        """).fetchone()

        top_books_rows = conn.execute("""
            SELECT oi.product_id, oi.product_name_snapshot as title,
                   SUM(oi.quantity) as sold_quantity,
                   SUM(oi.unit_price_at_purchase * oi.quantity) as revenue
            FROM order_items oi
            JOIN orders o ON oi.order_id = o.order_id
            WHERE o.status IN ('PAID', 'SHIPPING', 'DELIVERED')
            GROUP BY oi.product_id
            ORDER BY sold_quantity DESC
            LIMIT 5;
        """).fetchall()

        return {
            "total_revenue": rev_row["total_revenue"],
            "total_orders": rev_row["total_orders"],
            "paid_orders_count": rev_row["total_orders"],
            "total_items_sold": items_row["total_items_sold"],
            "top_books": [dict(r) for r in top_books_rows]
        }
