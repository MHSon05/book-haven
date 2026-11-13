"""
Application Service: CheckoutService
Điều phối quy trình Đặt hàng và Checkout bọc trong Transaction CSDL.
Tuân thủ UML Hình 4.3: Không dùng Enum, sử dụng chuỗi nguyên thủy (str).
"""
import uuid
from datetime import datetime, timedelta
from typing import Optional

from ...domain.entities.order import Order
from ...domain.entities.order_item import OrderItem
from ...domain.entities.stock_reservation import StockReservation
from ...domain.exceptions import OutOfStockException, DroneOverweightException
from ...infrastructure.database import DatabaseSession
from ...infrastructure.repositories.book_repository import BookRepository
from ...infrastructure.repositories.cart_repository import CartRepository
from ...infrastructure.repositories.order_repository import OrderRepository
from ...infrastructure.adapters.vietqr_service import VietQRService
from ..dtos.models import CheckoutRequest, OrderResponse, OrderItemDTO, ShippingOptionsResponse, ShippingOption


class CheckoutService:
    def __init__(
        self,
        session: DatabaseSession,
        book_repo: BookRepository,
        cart_repo: CartRepository,
        order_repo: OrderRepository,
        vietqr_service: VietQRService,
        reservation_ttl_minutes: int = 15
    ):
        self.session = session
        self.book_repo = book_repo
        self.cart_repo = cart_repo
        self.order_repo = order_repo
        self.vietqr_service = vietqr_service
        self.reservation_ttl_minutes = reservation_ttl_minutes

    def checkout(self, customer_id: int, request: CheckoutRequest) -> OrderResponse:
        """
        Thực thi Quy trình Đặt hàng và Checkout 10 bước bọc trong ranh giới Giao dịch:
        """
        self.session.begin_transaction()
        try:
            # Bước 1: Nạp giỏ hàng của khách
            cart = self.cart_repo.get_cart_by_id(int(request.cart_id))
            if not cart or not cart.items:
                raise ValueError("Giỏ hàng đang rỗng, không thể tiến hành đặt hàng.")

            # Bước 2 & 3: Kiểm tra tồn kho khả dụng cho từng sản phẩm (BR02)
            products_map = {}
            for item in cart.items:
                pid = item.product_id
                prod = self.book_repo.get_product_by_id(pid)
                if not prod:
                    raise ValueError(f"Sản phẩm {pid} không tồn tại trong kho.")
                # Kiểm tra tồn kho khả dụng
                if not prod.check_availability(item.quantity):
                    raise OutOfStockException(
                        sku=prod.sku,
                        requested=item.quantity,
                        available=prod.get_available_stock()
                    )
                products_map[pid] = prod

            # Bước 4: Tính tổng trọng lượng gram & Kiểm tra tải trọng Drone
            total_pkg_weight_grams = cart.calculate_total_weight() + 150  # 150g màng xốp + hộp

            carrier = str(request.carrier or "GHN").upper()

            # Ràng buộc Drone tải trọng tối đa 2000g
            if "DRONE" in carrier and total_pkg_weight_grams > 2000:
                raise DroneOverweightException(total_weight_grams=total_pkg_weight_grams, max_allowed=2000)

            # Ràng buộc Drone không hỗ trợ thanh toán tiền mặt COD
            if "DRONE" in carrier and str(request.payment_method).upper() == "COD":
                raise ValueError("Giao hàng bằng Drone không hỗ trợ thanh toán tiền mặt (COD). Vui lòng thanh toán trực tuyến qua VietQR.")

            # Tính cước phí giao vận
            if "DRONE" in carrier:
                shipping_fee = 60000
            elif "EXP" in carrier:
                shipping_fee = 45000
            else:
                shipping_fee = 25000

            subtotal_amount = cart.calculate_subtotal()

            # Giảm giá nếu có voucher
            discount_amount = 0
            if request.voucher_code and request.voucher_code.upper() in ("BOOKHAVEN10", "VOUCHER10"):
                discount_amount = min(50000, int(subtotal_amount * 0.1))
            elif request.voucher_code and request.voucher_code.upper() == "FREESHIP":
                discount_amount = shipping_fee

            final_amount = max(0, subtotal_amount + shipping_fee - discount_amount)

            initial_status = (
                "PENDING_CASH"
                if str(request.payment_method).upper() == "COD"
                else "AWAITING_PAYMENT"
            )

            # Bước 5: Khởi tạo Order & OrderItem
            order = Order(
                customer_id=int(customer_id),
                receiver_name=request.receiver_name,
                receiver_phone=request.receiver_phone,
                shipping_address=request.shipping_address,
                payment_method=str(request.payment_method).upper(),
                carrier=carrier,
                total_amount=subtotal_amount,
                shipping_fee=shipping_fee,
                discount_amount=discount_amount,
                final_amount=final_amount,
                status=initial_status,
                items=[]
            )
            # Lưu Order trước để nhận auto-increment order_id
            assigned_order_id = self.order_repo.save_order(order)
            order._order_id = assigned_order_id

            order_items = []
            order_items_dtos = []
            for item in cart.items:
                prod = products_map[item.product_id]
                oi = OrderItem(
                    order_id=assigned_order_id,
                    product_id=prod.product_id,
                    product_name_snapshot=prod.name,
                    sku_snapshot=prod.sku,
                    product_kind_snapshot=getattr(prod, "binding_type", "Product"),
                    unit_price_at_purchase=prod.unit_price,
                    quantity=item.quantity,
                    weight_gram_snapshot=prod.weight_gram
                )
                order_items.append(oi)
                order_items_dtos.append(OrderItemDTO(
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
                ))

            order._items = order_items
            self.order_repo.save_order(order)

            # Bước 6: Khóa giữ chỗ tồn kho 15 phút (Stock Reservation - BR03)
            expires_at = datetime.utcnow() + timedelta(minutes=self.reservation_ttl_minutes)
            for item in cart.items:
                prod = products_map[item.product_id]
                prod.reserve_stock(item.quantity)
                self.book_repo.update_product_stock(prod)

                res = StockReservation(
                    order_id=assigned_order_id,
                    product_id=prod.product_id,
                    reserved_quantity=item.quantity,
                    expires_at=expires_at,
                    status="PENDING"
                )
                self.order_repo.save_stock_reservation(res)

            # Bước 7: Sinh mã VietQR động nếu chọn chuyển khoản
            vietqr_data = None
            if order.payment_method == "VIETQR":
                vietqr_data = self.vietqr_service.generate_payment_qr(str(assigned_order_id), order.final_amount)

            # Bước 8: Làm rỗng giỏ hàng
            self.cart_repo.clear_cart(int(request.cart_id))

            # Bước 9: Commit transaction
            self.session.commit()

            # Bước 10: Trả về kết quả
            return OrderResponse(
                order_id=str(assigned_order_id),
                customer_id=str(order.customer_id),
                receiver_name=order.receiver_name,
                receiver_phone=order.receiver_phone,
                shipping_address=order.shipping_address,
                payment_method=order.payment_method,
                carrier=order.carrier,
                total_amount=order.total_amount,
                shipping_fee=order.shipping_fee,
                discount_amount=order.discount_amount,
                final_amount=order.final_amount,
                status=order.status,
                tracking_code=order.tracking_code,
                created_at=order.created_at.strftime("%Y-%m-%d %H:%M:%S") if isinstance(order.created_at, datetime) else str(order.created_at),
                items=order_items_dtos,
                vietqr_data=vietqr_data,
                reservation_expires_at=expires_at.strftime("%Y-%m-%d %H:%M:%S")
            )

        except Exception as e:
            self.session.rollback()
            raise e

    def get_shipping_options(self, cart_id: Optional[str] = None) -> ShippingOptionsResponse:
        """Tính tổng trọng lượng bưu phẩm (+150g bao bì) và kiểm tra điều kiện giao Drone (<= 2.000g)."""
        total_package_weight = 150
        if cart_id:
            try:
                cart = self.cart_repo.get_cart_by_id(int(cart_id))
                if cart:
                    total_package_weight += cart.calculate_total_weight()
            except Exception:
                pass

        is_drone_eligible = total_package_weight <= 2000
        drone_disabled_msg = None
        if not is_drone_eligible:
            drone_disabled_msg = (
                f"Tổng khối lượng kiện hàng ({total_package_weight}g) vượt quá "
                f"tải trọng bay tối đa của Drone (2.000g). Vui lòng chọn GHN."
            )

        options = [
            ShippingOption(
                carrier_code="GHN_STANDARD",
                carrier_name="Giao Hàng Nhanh - Tiêu chuẩn (GHN)",
                fee=25000,
                estimated_time="2 - 3 ngày",
                is_available=True,
                disabled_reason=None
            ),
            ShippingOption(
                carrier_code="GHN_EXPRESS",
                carrier_name="Giao Hàng Nhanh - Hỏa tốc đường bộ",
                fee=45000,
                estimated_time="Trong 24 giờ",
                is_available=True,
                disabled_reason=None
            ),
            ShippingOption(
                carrier_code="HANOI_DRONE",
                carrier_name="Hanoi Drone Express (Giao hàng không người lái hỏa tốc)",
                fee=60000,
                estimated_time="30 - 45 phút",
                is_available=is_drone_eligible,
                disabled_reason=drone_disabled_msg
            )
        ]

        return ShippingOptionsResponse(
            total_weight_grams=total_package_weight,
            options=options
        )
