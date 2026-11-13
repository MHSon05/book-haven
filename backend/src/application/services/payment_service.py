"""
Application Service: PaymentService
Xử lý giao dịch thanh toán VietQR, đối soát Webhook ngân hàng và cập nhật trạng thái đơn hàng.
Tuân thủ UML Hình 4.3: Không dùng Enum, sử dụng chuỗi nguyên thủy (str).
"""
import re
from typing import Dict, Any, Optional
from datetime import datetime

from ...domain.entities.order import Order
from ...domain.entities.payment import Payment
from ...domain.exceptions import EntityNotFoundException, InvalidOrderStateException
from ...infrastructure.database import DatabaseSession
from ...infrastructure.repositories.order_repository import OrderRepository
from ...infrastructure.repositories.book_repository import BookRepository
from ..dtos.models import OrderResponse, OrderItemDTO


class PaymentService:
    def __init__(
        self,
        session: DatabaseSession,
        order_repo: OrderRepository,
        book_repo: BookRepository
    ):
        self.session = session
        self.order_repo = order_repo
        self.book_repo = book_repo

    def confirm_payment(self, order_id: int, transaction_code: Optional[str] = None) -> OrderResponse:
        """
        Khách hàng xác nhận 'Tôi đã chuyển khoản thành công' hoặc hệ thống nhận tín hiệu thanh toán.
        Thực hiện trừ kho chính thức (commit_stock) và chuyển trạng thái đơn sang PAID.
        """
        self.session.begin_transaction()
        try:
            order = self.order_repo.get_order_by_id(int(order_id))
            if not order:
                raise EntityNotFoundException("Order", str(order_id))

            if order.status == "PAID":
                self.session.commit()
                return self._to_order_response(order)

            if order.status not in ("AWAITING_PAYMENT", "PENDING_PAYMENT"):
                raise InvalidOrderStateException(
                    f"Đơn hàng đang ở trạng thái '{order.status}', không thể xác nhận thanh toán."
                )

            # Chuyển trạng thái Order sang PAID
            order.transition_to("PAID")
            self.order_repo.save_order(order)

            # Khấu trừ kho chính thức (stock_on_hand -= qty, stock_reserved -= qty)
            for item in order.items:
                prod = self.book_repo.get_product_by_id(item.product_id)
                if prod:
                    prod.commit_stock(item.quantity)
                    self.book_repo.update_product_stock(prod)

            # Cập nhật trạng thái bản ghi giữ chỗ sang COMMITTED qua OrderRepository
            self.order_repo.update_reservations_status_by_order(int(order_id), "COMMITTED")

            # Ghi nhận thực thể Payment và lưu chứng từ thanh toán (BR06)
            txn_code = transaction_code or f"TXN_{order_id}_{int(datetime.now().timestamp())}"
            payment = Payment(
                order_id=int(order_id),
                payment_method=order.payment_method,
                amount=order.final_amount,
                transaction_code=txn_code,
                status="SUCCESS",
                paid_at=datetime.utcnow()
            )
            self.order_repo.save_payment_record(payment)

            self.session.commit()
            return self._to_order_response(order)

        except Exception as e:
            self.session.rollback()
            raise e

    def process_webhook(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Xử lý Webhook tự động nhận thông báo tiền về từ ngân hàng MBBank hoặc Cổng VietQR.
        """
        content = payload.get("content") or payload.get("description") or payload.get("transfer_content") or ""
        transfer_amount = payload.get("amount") or payload.get("transferAmount") or 0
        trans_id = payload.get("transaction_id") or payload.get("referenceCode") or "WEBHOOK_TXN"

        # Trích xuất order_id từ nội dung chuyển khoản
        match = re.search(r"(\d+)", content)
        if not match:
            return {
                "success": False,
                "message": f"Không tìm thấy mã đơn hàng hợp lệ trong nội dung: '{content}'"
            }

        order_id = int(match.group(1))
        order = self.order_repo.get_order_by_id(order_id)
        if not order:
            return {"success": False, "message": f"Đơn hàng {order_id} không tồn tại trong hệ thống."}

        # Kiểm tra khớp số tiền
        if int(transfer_amount) < order.final_amount:
            return {
                "success": False,
                "message": f"Số tiền thanh toán ({transfer_amount} đ) không đủ so với đơn ({order.final_amount} đ)."
            }

        self.confirm_payment(order_id, transaction_code=str(trans_id))
        return {
            "success": True,
            "order_id": order_id,
            "status": "PAID",
            "message": "Thanh toán tự động thành công qua Webhook ngân hàng."
        }

    def get_order_status(self, order_id: int) -> Dict[str, Any]:
        order = self.order_repo.get_order_by_id(int(order_id))
        if not order:
            raise EntityNotFoundException("Order", str(order_id))

        total_weight = order.calculate_total_weight() + 150 if order.items else 380

        return {
            "order_id": order.order_id,
            "status": order.status,
            "payment_method": order.payment_method,
            "carrier": order.carrier,
            "tracking_code": order.tracking_code,
            "final_amount": order.final_amount,
            "total_amount": order.total_amount,
            "receiver_name": order.receiver_name,
            "receiver_phone": order.receiver_phone,
            "shipping_address": order.shipping_address,
            "total_weight_grams": total_weight,
            "created_at": str(order.created_at) if order.created_at else None,
            "updated_at": str(order.updated_at) if order.updated_at else None,
            "items": [
                {
                    "product_id": it.product_id,
                    "title": it.product_name_snapshot,
                    "quantity": it.quantity,
                    "unit_price": it.unit_price_at_purchase,
                    "weight_gram": it.weight_gram_snapshot
                } for it in order.items
            ] if order.items else []
        }

    def _to_order_response(self, order: Order) -> OrderResponse:
        items_dtos = [
            OrderItemDTO(
                order_item_id=str(oi.order_item_id or ""),
                edition_id=str(oi.product_id),
                product_id=oi.product_id,
                title=oi.product_name_snapshot,
                sku=oi.sku_snapshot,
                binding_type=oi.product_kind_snapshot,
                isbn13="",
                unit_price=oi.unit_price_at_purchase,
                quantity=oi.quantity,
                weight_gram=oi.weight_gram_snapshot,
                subtotal=oi.calculate_subtotal()
            )
            for oi in order.items
        ]
        return OrderResponse(
            order_id=str(order.order_id),
            customer_id=str(order.customer_id),
            receiver_name=order.receiver_name,
            receiver_phone=order.receiver_phone,
            shipping_address=order.shipping_address,
            payment_method=order.payment_method,
            carrier=order.carrier or "GHN",
            total_amount=order.total_amount,
            shipping_fee=order.shipping_fee,
            discount_amount=order.discount_amount,
            final_amount=order.final_amount,
            status=order.status,
            tracking_code=order.tracking_code,
            created_at=order.created_at.strftime("%Y-%m-%d %H:%M:%S") if isinstance(order.created_at, datetime) else str(order.created_at),
            items=items_dtos
        )
