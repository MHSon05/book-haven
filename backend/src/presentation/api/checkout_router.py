"""
Presentation Layer: CheckoutController & FastAPI Router
Xử lý Quy trình Đặt hàng 10 bước (Checkout) và Tra cứu Tùy chọn Giao vận (Drone & GHN).
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status

from ...application.dtos.models import CheckoutRequest, OrderResponse, ShippingOptionsResponse
from ...application.services.checkout_service import CheckoutService
from ...domain.exceptions import OutOfStockException, DroneOverweightException, DomainException
from ..dependencies import get_checkout_service
from .cart_router import resolve_customer_id

router = APIRouter(tags=["Checkout & Shipping"])


class CheckoutController:
    """Bộ điều khiển quy trình đặt hàng và giao vận (Presentation Layer)."""

    def __init__(self, checkout_service: CheckoutService):
        self.checkout_service = checkout_service

    def execute_checkout(self, customer_id: str, request: CheckoutRequest) -> OrderResponse:
        try:
            return self.checkout_service.checkout(customer_id=customer_id, request=request)
        except (OutOfStockException, DroneOverweightException, ValueError, DomainException) as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    def get_shipping_options(self, cart_id: Optional[str] = None) -> ShippingOptionsResponse:
        return self.checkout_service.get_shipping_options(cart_id)


@router.post("/checkout", response_model=OrderResponse)
def execute_checkout(
    request: CheckoutRequest,
    customer_id: str = Depends(resolve_customer_id),
    checkout_service: CheckoutService = Depends(get_checkout_service),
):
    return CheckoutController(checkout_service).execute_checkout(customer_id, request)


@router.get("/shipping/options", response_model=ShippingOptionsResponse)
def get_shipping_options(
    cart_id: Optional[str] = Query(None, description="Mã giỏ hàng để tính trọng lượng thực"),
    checkout_service: CheckoutService = Depends(get_checkout_service),
):
    return CheckoutController(checkout_service).get_shipping_options(cart_id)
