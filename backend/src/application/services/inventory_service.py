"""
Application Service: InventoryService
Điều phối nhập kho (Restock), xử lý tự động giải phóng giữ chỗ quá hạn 15 phút (Background Worker),
và nghiệp vụ xuất kho/bàn giao giao vận Drone/GHN của Quản trị viên & Thủ kho.
"""
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional

from ...domain.entities.order import OrderStatus, Carrier, PaymentMethod
from ...domain.entities.stock_reservation import ReservationStatus
from ...domain.entities.book_edition import BookEdition
from ...domain.exceptions import EntityNotFoundException, InvalidOrderStateException, DroneOverweightException
from ...infrastructure.database import DatabaseSession
from ...infrastructure.repositories.book_repository import BookRepository
from ...infrastructure.repositories.order_repository import OrderRepository
from ..dtos.models import OrderResponse, OrderItemDTO

class InventoryService:
    def __init__(
        self,
        session: DatabaseSession,
        book_repo: BookRepository,
        order_repo: OrderRepository
    ):
        self.session = session
        self.book_repo = book_repo
        self.order_repo = order_repo

    def restock(self, edition_id: str, quantity: int) -> BookEdition:
        """Thủ kho nhập thêm sách từ Nhà xuất bản (UC12)."""
        if quantity <= 0:
            raise ValueError("Số lượng nhập kho phải lớn hơn 0.")

        self.session.begin_transaction()
        try:
            edition = self.book_repo.get_edition_by_id(edition_id)
            if not edition:
                raise EntityNotFoundException("BookEdition", edition_id)

            edition.add_stock(quantity)
            self.book_repo.update_edition_stock(edition)
            self.session.commit()
            return edition
        except Exception as e:
            self.session.rollback()
            raise e

    def cleanup_expired_reservations(self, current_time: Optional[datetime] = None) -> int:
        """
        Background Worker định kỳ quét và giải phóng các bản ghi giữ chỗ quá hạn 15 phút (BR03).
        Hoàn trả lại tồn kho khả dụng cho khách hàng khác và hủy đơn hàng chưa thanh toán.
        """
        now = current_time or datetime.now()
        now_iso = now.isoformat()

        expired_list = self.order_repo.get_pending_expired_reservations(now_iso)
        if not expired_list:
            return 0

        self.session.begin_transaction()
        try:
            released_count = 0
            affected_order_ids = set()

            for res in expired_list:
                edition = self.book_repo.get_edition_by_id(res.edition_id)
                if edition:
                    # Hoàn trả số lượng giữ chỗ về tồn khả dụng
                    edition.release_reservation(res.reserved_quantity)
                    self.book_repo.update_edition_stock(edition)

                self.order_repo.update_reservation_status(res.reservation_id, ReservationStatus.RELEASED)
                affected_order_ids.add(res.order_id)
                released_count += 1

            # Hủy các đơn hàng liên quan nếu vẫn đang AWAITING_PAYMENT
            for oid in affected_order_ids:
                order = self.order_repo.get_order_by_id(oid)
                if order and order.status == OrderStatus.AWAITING_PAYMENT:
                    order.cancel()
                    self.order_repo.save_order(order)

            self.session.commit()
            return released_count

        except Exception as e:
            self.session.rollback()
            raise e

    def dispatch_order(self, order_id: str, carrier_name: Optional[str] = None) -> OrderResponse:
        """
        Thủ kho đóng gói và bàn giao bưu kiện cho Đối tác vận chuyển (Hanoi Drone hoặc GHN).
        Khởi tạo mã vận đơn (tracking_code) và chuyển trạng thái sang SHIPPING.
        """
        self.session.begin_transaction()
        try:
            order = self.order_repo.get_order_by_id(order_id)
            if not order:
                raise EntityNotFoundException("Order", order_id)

            # Đảm bảo đơn đã thanh toán hoặc COD
            if order.status == OrderStatus.PAID:
                order.mark_packed()
            elif order.status in (OrderStatus.PENDING_CASH, OrderStatus.AWAITING_PAYMENT) and order.payment_method.value == "COD":
                order.status = OrderStatus.PENDING_CASH
                order.mark_packed()
            elif order.status != OrderStatus.PACKED:
                raise InvalidOrderStateException(f"Đơn hàng đang ở trạng thái '{order.status.value}', chưa thể giao vận.")

            # Xác định đối tác giao vận
            carrier = order.carrier
            if carrier_name and carrier_name in Carrier.__members__:
                carrier = Carrier(carrier_name)

            # Ràng buộc Drone
            if carrier == Carrier.HANOI_DRONE:
                total_pkg_weight = sum(item.total_weight() for item in order.items) + 150
                if total_pkg_weight > 2000:
                    raise DroneOverweightException(total_weight_grams=total_pkg_weight, max_allowed=2000)
                tracking_code = f"DRONE-HN-{uuid.uuid4().hex[:6].upper()}"
            elif carrier == Carrier.GHN_EXPRESS:
                tracking_code = f"GHN-EXP-{uuid.uuid4().hex[:8].upper()}"
            else:
                tracking_code = f"GHN-STD-{uuid.uuid4().hex[:8].upper()}"

            order.mark_dispatched(carrier, tracking_code)
            self.order_repo.save_order(order)
            self.session.commit()

            return self._to_order_response(order)

        except Exception as e:
            self.session.rollback()
            raise e

    def mark_delivered(self, order_id: str) -> OrderResponse:
        """Cập nhật đơn hàng đã giao thành công."""
        self.session.begin_transaction()
        try:
            order = self.order_repo.get_order_by_id(order_id)
            if not order:
                raise EntityNotFoundException("Order", order_id)

            # Nếu đơn chưa xuất kho (ví dụ chạy mô phỏng trực tiếp từ Drone radar):
            if order.status in (OrderStatus.PAID, OrderStatus.PENDING_CASH):
                carrier = order.carrier or Carrier.HANOI_DRONE
                tracking = order.tracking_code or f"DRONE-HN-{uuid.uuid4().hex[:6].upper()}"
                order.mark_packed()
                order.mark_dispatched(carrier, tracking)

            order.mark_delivered()
            self.order_repo.save_order(order)

            # Nếu là đơn COD: Khấu trừ kho chính thức và commit reservation
            if order.payment_method == PaymentMethod.COD or order.payment_method.value == "COD":
                for item in order.items:
                    edition = self.book_repo.get_edition_by_id(item.edition_id)
                    if edition:
                        edition.confirm_deduction(item.quantity)
                        self.book_repo.update_edition_stock(edition)
                self.order_repo.update_reservations_status_by_order(order_id, ReservationStatus.COMMITTED)
                self.order_repo.save_payment(
                    payment_id=f"PAY_{order_id}",
                    order_id=order_id,
                    payment_method=order.payment_method.value,
                    amount=order.final_amount,
                    transaction_code=f"COD_{order_id}_{int(datetime.now().timestamp())}",
                    status="SUCCESS"
                )

            self.session.commit()
            return self._to_order_response(order)
        except Exception as e:
            self.session.rollback()
            raise e

    def get_inventory_status(self) -> List[Dict[str, Any]]:
        """Lấy danh sách tất cả các ấn bản và trạng thái tồn kho thực tế / giữ chỗ / khả dụng."""
        return self.book_repo.get_inventory_status()

    def get_revenue_report(self) -> Dict[str, Any]:
        """Báo cáo doanh thu thực thu và top sách bán chạy (BR06)."""
        return self.order_repo.get_revenue_summary()

    def _to_order_response(self, order: Order) -> OrderResponse:
        items_dtos = [
            OrderItemDTO(
                order_item_id=oi.order_item_id,
                edition_id=oi.edition_id,
                title=oi.title_snapshot,
                sku=oi.sku_snapshot,
                binding_type=oi.binding_type_snapshot,
                isbn13=oi.isbn13_snapshot,
                unit_price=oi.unit_price_at_purchase,
                quantity=oi.quantity,
                weight_gram=oi.weight_gram_snapshot,
                subtotal=oi.subtotal()
            )
            for oi in order.items
        ]
        return OrderResponse(
            order_id=order.order_id,
            customer_id=order.customer_id,
            receiver_name=order.receiver_name,
            receiver_phone=order.receiver_phone,
            shipping_address=order.shipping_address,
            payment_method=order.payment_method.value,
            carrier=order.carrier.value if order.carrier else "GHN_STANDARD",
            total_amount=order.total_amount,
            shipping_fee=order.shipping_fee,
            discount_amount=order.discount_amount,
            final_amount=order.final_amount,
            status=order.status.value,
            tracking_code=order.tracking_code,
            created_at=order.created_at,
            items=items_dtos
        )
