"""
Application Service: CheckoutService
Điều phối quy trình Đặt hàng và Checkout 10 bước bọc trong Transaction CSDL.
Khớp 100% với Mục 4.4.3 và Slide 12 trong bài giảng của PGS. TS. Trần Đình Quế.
"""
import uuid
from datetime import datetime, timedelta
from typing import Optional

from ...domain.entities.order import Order, OrderItem, OrderStatus, PaymentMethod, Carrier
from ...domain.entities.stock_reservation import StockReservation, ReservationStatus
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

    def checkout(self, customer_id: str, request: CheckoutRequest) -> OrderResponse:
        """
        Thực thi Quy trình Đặt hàng và Checkout 10 bước bọc trong ranh giới Giao dịch:
        """
        self.session.begin_transaction()
        try:
            # Bước 1: Nạp giỏ hàng của khách
            cart = self.cart_repo.get_cart_by_id(request.cart_id)
            if not cart.items:
                raise ValueError("Giỏ hàng đang rỗng, không thể tiến hành đặt hàng.")

            # Bước 2 & 3: Kiểm tra tồn kho khả dụng cho từng dòng ấn bản (BR02)
            editions_map = {}
            for edition_id, cart_item in cart.items.items():
                edition = self.book_repo.get_edition_by_id(edition_id)
                if not edition:
                    raise ValueError(f"Ấn bản sách {edition_id} không tồn tại trong kho.")
                # Kiểm tra Invariant miền: available_stock >= quantity
                if not edition.is_available(cart_item.quantity):
                    raise OutOfStockException(
                        sku=edition.sku,
                        requested=cart_item.quantity,
                        available=edition.available_stock()
                    )
                editions_map[edition_id] = edition

            # Bước 4: Tính tổng trọng lượng gram & Kiểm tra tải trọng Drone
            books_weight_grams = sum(
                editions_map[eid].weight_gram * item.quantity
                for eid, item in cart.items.items()
            )
            total_package_weight_grams = books_weight_grams + 150  # 150g màng xốp + hộp

            carrier_enum = Carrier(request.carrier) if request.carrier in Carrier.__members__ else Carrier.GHN_STANDARD
            
            # Ràng buộc Drone tải trọng tối đa 2000g
            if carrier_enum == Carrier.HANOI_DRONE and total_package_weight_grams > 2000:
                raise DroneOverweightException(total_weight_grams=total_package_weight_grams, max_allowed=2000)

            # Ràng buộc Drone không hỗ trợ thanh toán tiền mặt COD
            if carrier_enum == Carrier.HANOI_DRONE and request.payment_method == "COD":
                raise ValueError("Giao hàng bằng Drone không hỗ trợ thanh toán tiền mặt (COD). Vui lòng thanh toán trực tuyến qua VietQR.")

            # Tính cước phí giao vận
            if carrier_enum == Carrier.HANOI_DRONE:
                shipping_fee = 60000
            elif carrier_enum == Carrier.GHN_EXPRESS:
                shipping_fee = 45000
            else:
                shipping_fee = 25000

            subtotal_amount = sum(
                editions_map[eid].unit_price * item.quantity
                for eid, item in cart.items.items()
            )

            # Giảm giá nếu có voucher
            discount_amount = 0
            if request.voucher_code and request.voucher_code.upper() in ("BOOKHAVEN10", "VOUCHER10"):
                discount_amount = min(50000, int(subtotal_amount * 0.1))
            elif request.voucher_code and request.voucher_code.upper() == "FREESHIP":
                discount_amount = shipping_fee

            final_amount = max(0, subtotal_amount + shipping_fee - discount_amount)
            order_id = f"DH_{int(datetime.now().timestamp())}_{uuid.uuid4().hex[:4].upper()}"

            # Bước 5: Khởi tạo Order & OrderItem (Snapshot bất biến - BR04)
            order_items = []
            order_items_dtos = []
            for edition_id, cart_item in cart.items.items():
                edition = editions_map[edition_id]
                oi = OrderItem(
                    order_item_id=f"ITEM_{order_id}_{edition.edition_id}",
                    order_id=order_id,
                    edition_id=edition.edition_id,
                    title_snapshot=edition.title or "Sách",
                    sku_snapshot=edition.sku,
                    binding_type_snapshot=edition.binding_type,
                    isbn13_snapshot=edition.isbn13,
                    unit_price_at_purchase=edition.unit_price,
                    quantity=cart_item.quantity,
                    weight_gram_snapshot=edition.weight_gram
                )
                order_items.append(oi)
                order_items_dtos.append(OrderItemDTO(
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
                ))

            initial_status = (
                OrderStatus.PENDING_CASH
                if request.payment_method == "COD"
                else OrderStatus.AWAITING_PAYMENT
            )

            order = Order(
                order_id=order_id,
                customer_id=customer_id,
                receiver_name=request.receiver_name,
                receiver_phone=request.receiver_phone,
                shipping_address=request.shipping_address,
                payment_method=PaymentMethod(request.payment_method),
                carrier=carrier_enum,
                total_amount=subtotal_amount,
                shipping_fee=shipping_fee,
                discount_amount=discount_amount,
                final_amount=final_amount,
                status=initial_status,
                items=order_items
            )
            # Lưu Order trước để thỏa mãn ràng buộc khóa ngoại (Foreign Key constraint)
            self.order_repo.save_order(order)

            # Bước 6: Khóa giữ chỗ tồn kho 15 phút (Stock Reservation - BR03)
            expires_at = (datetime.now() + timedelta(minutes=self.reservation_ttl_minutes)).isoformat()
            reservations = []
            for edition_id, cart_item in cart.items.items():
                edition = editions_map[edition_id]
                # Gọi domain method khóa giữ chỗ
                edition.reserve_stock(cart_item.quantity)
                self.book_repo.update_edition_stock(edition)

                res = StockReservation(
                    reservation_id=f"RES_{order_id}_{edition.edition_id}",
                    order_id=order_id,
                    edition_id=edition.edition_id,
                    reserved_quantity=cart_item.quantity,
                    expires_at=expires_at,
                    status=ReservationStatus.PENDING
                )
                reservations.append(res)
                self.order_repo.save_stock_reservation(res)

            # Bước 7: Sinh mã VietQR động
            vietqr_data = None
            if order.payment_method == PaymentMethod.VIETQR:
                vietqr_data = self.vietqr_service.generate_payment_qr(order.order_id, order.final_amount)

            # Bước 8: Làm rỗng giỏ hàng (Cart.clear())
            self.cart_repo.clear_cart(request.cart_id)

            # Bước 9: Commit giao dịch CSDL an toàn
            self.session.commit()

            # Bước 10: Trả về kết quả
            return OrderResponse(
                order_id=order.order_id,
                customer_id=order.customer_id,
                receiver_name=order.receiver_name,
                receiver_phone=order.receiver_phone,
                shipping_address=order.shipping_address,
                payment_method=order.payment_method.value,
                carrier=order.carrier.value,
                total_amount=order.total_amount,
                shipping_fee=order.shipping_fee,
                discount_amount=order.discount_amount,
                final_amount=order.final_amount,
                status=order.status.value,
                tracking_code=order.tracking_code,
                created_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                items=order_items_dtos,
                vietqr_data=vietqr_data,
                reservation_expires_at=expires_at
            )

        except Exception as e:
            # Tự động Rollback nếu có bất kỳ ngoại lệ nào
            self.session.rollback()
            raise e

    def get_shipping_options(self, cart_id: Optional[str] = None) -> ShippingOptionsResponse:
        """Tính tổng trọng lượng bưu phẩm (+150g bao bì) và kiểm tra điều kiện giao Drone (<= 2.000g)."""
        total_package_weight = 150
        if cart_id:
            cart = self.cart_repo.get_cart_by_id(cart_id)
            if cart:
                total_package_weight += cart.calculate_total_weight_grams()

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
