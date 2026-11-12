"""
Infrastructure Repository: OrderRepository
Quản lý lưu trữ Đơn hàng, OrderItem snapshot, StockReservation và Payment.
"""
from typing import List, Optional, Dict, Any
from ..database import DatabaseSession
from ...domain.entities.order import Order, OrderItem, OrderStatus, PaymentMethod, Carrier
from ...domain.entities.payment import Payment, PaymentStatus
from ...domain.entities.stock_reservation import StockReservation, ReservationStatus

class OrderRepository:
    def __init__(self, session: DatabaseSession):
        self.session = session

    def save_order(self, order: Order):
        conn = self.session.get_connection()
        query_order = """
        INSERT INTO orders (
            order_id, customer_id, receiver_name, receiver_phone, shipping_address,
            payment_method, total_amount, shipping_fee, discount_amount, final_amount,
            status, carrier, tracking_code
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(order_id) DO UPDATE SET
            status = excluded.status,
            carrier = excluded.carrier,
            tracking_code = excluded.tracking_code,
            updated_at = datetime('now', 'localtime');
        """
        conn.execute(query_order, (
            order.order_id, order.customer_id, order.receiver_name, order.receiver_phone,
            order.shipping_address, order.payment_method.value, order.total_amount,
            order.shipping_fee, order.discount_amount, order.final_amount,
            order.status.value, order.carrier.value if order.carrier else None,
            order.tracking_code
        ))

        # Lưu các dòng OrderItem (Snapshot bất biến)
        for item in order.items:
            query_item = """
            INSERT OR REPLACE INTO order_items (
                order_item_id, order_id, edition_id, title_snapshot, sku_snapshot,
                binding_type_snapshot, isbn13_snapshot, unit_price_at_purchase,
                quantity, weight_gram_snapshot
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """
            conn.execute(query_item, (
                item.order_item_id, item.order_id, item.edition_id,
                item.title_snapshot, item.sku_snapshot, item.binding_type_snapshot,
                item.isbn13_snapshot, item.unit_price_at_purchase, item.quantity,
                item.weight_gram_snapshot
            ))

    def get_order_by_id(self, order_id: str) -> Optional[Order]:
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
                edition_id=ir["edition_id"],
                title_snapshot=ir["title_snapshot"],
                sku_snapshot=ir["sku_snapshot"],
                binding_type_snapshot=ir["binding_type_snapshot"],
                isbn13_snapshot=ir["isbn13_snapshot"],
                unit_price_at_purchase=ir["unit_price_at_purchase"],
                quantity=ir["quantity"],
                weight_gram_snapshot=ir["weight_gram_snapshot"]
            )
            for ir in items_rows
        ]

        return Order(
            order_id=row["order_id"],
            customer_id=row["customer_id"],
            receiver_name=row["receiver_name"],
            receiver_phone=row["receiver_phone"],
            shipping_address=row["shipping_address"],
            payment_method=PaymentMethod(row["payment_method"]),
            carrier=Carrier(row["carrier"]) if row["carrier"] else Carrier.GHN_STANDARD,
            total_amount=row["total_amount"],
            shipping_fee=row["shipping_fee"],
            discount_amount=row["discount_amount"],
            final_amount=row["final_amount"],
            status=OrderStatus(row["status"]),
            items=items,
            tracking_code=row["tracking_code"],
            created_at=row["created_at"],
            updated_at=row["updated_at"]
        )

    def get_orders_by_customer(self, customer_id: str) -> List[Order]:
        conn = self.session.get_connection()
        rows = conn.execute(
            "SELECT order_id FROM orders WHERE customer_id = ? ORDER BY created_at DESC;",
            (customer_id,)
        ).fetchall()
        return [self.get_order_by_id(r["order_id"]) for r in rows if r]

    def get_all_orders(self, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        conn = self.session.get_connection()
        query = """
        SELECT o.*, u.full_name as customer_name, u.email as customer_email,
               COUNT(oi.order_item_id) as total_items
        FROM orders o
        JOIN users u ON o.customer_id = u.user_id
        LEFT JOIN order_items oi ON o.order_id = oi.order_id
        GROUP BY o.order_id
        ORDER BY o.created_at DESC
        LIMIT ? OFFSET ?;
        """
        rows = conn.execute(query, (limit, offset)).fetchall()
        return [dict(r) for r in rows]

    def save_stock_reservation(self, res: StockReservation):
        conn = self.session.get_connection()
        query = """
        INSERT OR REPLACE INTO stock_reservations (
            reservation_id, order_id, edition_id, reserved_quantity, expires_at, status
        ) VALUES (?, ?, ?, ?, ?, ?);
        """
        conn.execute(query, (
            res.reservation_id, res.order_id, res.edition_id,
            res.reserved_quantity, res.expires_at, res.status.value
        ))

    def get_pending_expired_reservations(self, current_time_iso: str) -> List[StockReservation]:
        conn = self.session.get_connection()
        query = """
        SELECT sr.* FROM stock_reservations sr
        JOIN orders o ON sr.order_id = o.order_id
        WHERE sr.status = 'PENDING'
          AND sr.expires_at <= ?
          AND o.status = 'AWAITING_PAYMENT';
        """
        rows = conn.execute(query, (current_time_iso,)).fetchall()
        return [
            StockReservation(
                reservation_id=r["reservation_id"],
                order_id=r["order_id"],
                edition_id=r["edition_id"],
                reserved_quantity=r["reserved_quantity"],
                expires_at=r["expires_at"],
                status=ReservationStatus(r["status"]),
                created_at=r["created_at"]
            )
            for r in rows
        ]

    def update_reservation_status(self, reservation_id: str, status: ReservationStatus):
        conn = self.session.get_connection()
        conn.execute(
            "UPDATE stock_reservations SET status = ? WHERE reservation_id = ?;",
            (status.value, reservation_id)
        )

    def update_reservations_status_by_order(self, order_id: str, status: ReservationStatus) -> None:
        """Cập nhật trạng thái toàn bộ bản ghi giữ chỗ thuộc một đơn hàng."""
        conn = self.session.get_connection()
        conn.execute(
            "UPDATE stock_reservations SET status = ? WHERE order_id = ?;",
            (status.value, order_id)
        )

    def save_payment_record(self, payment: Payment) -> None:
        """Lưu trữ thực thể Payment vào bảng payments."""
        conn = self.session.get_connection()
        query = """
        INSERT OR REPLACE INTO payments (
            payment_id, order_id, payment_method, amount, transaction_code, status, paid_at
        ) VALUES (?, ?, ?, ?, ?, ?, COALESCE(?, datetime('now', 'localtime')));
        """
        conn.execute(
            query,
            (
                payment.payment_id,
                payment.order_id,
                payment.payment_method,
                payment.amount,
                payment.transaction_code,
                payment.status.value,
                payment.paid_at,
            ),
        )

    def get_payment_by_order_id(self, order_id: str) -> Optional[Payment]:
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
            status=PaymentStatus(row["status"]),
            paid_at=row["paid_at"],
        )

    def save_payment(
        self,
        payment_id: str,
        order_id: str,
        payment_method: str,
        amount: int,
        transaction_code: Optional[str] = None,
        status: str = "PENDING"
    ):
        payment = Payment(
            payment_id=payment_id,
            order_id=order_id,
            payment_method=payment_method,
            amount=amount,
            transaction_code=transaction_code,
            status=PaymentStatus(status),
        )
        if status == PaymentStatus.SUCCESS.value and transaction_code:
            payment.mark_success(transaction_code)
        self.save_payment_record(payment)

    def get_revenue_summary(self) -> Dict[str, Any]:
        """Báo cáo doanh thu thực thu và thống kê (BR06 - loại trừ đơn hủy và đơn COD chưa thu tiền)."""
        conn = self.session.get_connection()
        rev_row = conn.execute("""
        SELECT COALESCE(SUM(
                   CASE
                       WHEN (payment_method = 'VIETQR' AND status IN ('PAID', 'PACKED', 'SHIPPING', 'DELIVERED'))
                         OR (payment_method = 'COD' AND status = 'DELIVERED')
                       THEN final_amount
                       ELSE 0
                   END
               ), 0) as total_revenue,
               COUNT(CASE
                   WHEN (payment_method = 'VIETQR' AND status IN ('PAID', 'PACKED', 'SHIPPING', 'DELIVERED'))
                     OR (payment_method = 'COD' AND status = 'DELIVERED')
                   THEN 1
               END) as paid_orders_count,
               COUNT(CASE WHEN status = 'DELIVERED' THEN 1 END) as completed_orders_count
        FROM orders;
        """).fetchone()

        # Tổng số lượng cuốn sách bán ra thực tế từ các đơn thành công
        items_sold_row = conn.execute("""
        SELECT COALESCE(SUM(oi.quantity), 0) as total_items_sold
        FROM order_items oi
        JOIN orders o ON oi.order_id = o.order_id
        WHERE o.status IN ('PAID', 'DELIVERED', 'SHIPPING', 'PACKED');
        """).fetchone()

        # Top sách bán chạy
        top_books = conn.execute("""
        SELECT oi.title_snapshot as title,
               oi.binding_type_snapshot as binding_type,
               SUM(oi.quantity) as total_sold,
               SUM(oi.unit_price_at_purchase * oi.quantity) as revenue
        FROM order_items oi
        JOIN orders o ON oi.order_id = o.order_id
        WHERE o.status IN ('PAID', 'DELIVERED', 'SHIPPING', 'PACKED')
        GROUP BY oi.edition_id
        ORDER BY total_sold DESC
        LIMIT 5;
        """).fetchall()

        top_books_list = [dict(tb) for tb in top_books]
        return {
            "total_revenue": rev_row["total_revenue"],
            "paid_orders_count": rev_row["paid_orders_count"],
            "completed_orders_count": rev_row["completed_orders_count"],
            "total_items_sold": items_sold_row["total_items_sold"],
            "top_books": top_books_list,
            "top_selling_books": top_books_list,
        }
