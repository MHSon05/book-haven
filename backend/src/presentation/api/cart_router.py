"""
Presentation Layer: CartController & FastAPI Router
Quản lý giỏ hàng: xem, thêm ấn bản, thay đổi số lượng, xóa và làm rỗng.
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Header, status

from ...application.dtos.models import AddToCartRequest, UpdateCartItemRequest, CartResponse
from ...application.services.cart_service import CartService
from ...domain.entities.user import User
from ...domain.exceptions import OutOfStockException, EntityNotFoundException
from ..dependencies import get_cart_service, get_current_user_optional

router = APIRouter(prefix="/cart", tags=["Shopping Cart"])


def resolve_customer_id(
    current_user: Optional[User] = Depends(get_current_user_optional),
    x_customer_id: Optional[str] = Header(None),
) -> str:
    if current_user:
        return current_user.user_id
    if x_customer_id and x_customer_id.strip():
        return x_customer_id.strip()
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Vui lòng cung cấp mã phiên khách (X-Customer-Id) hoặc đăng nhập để thao tác giỏ hàng.",
    )


class CartController:
    """Bộ điều khiển nghiệp vụ giỏ hàng (Presentation Layer)."""

    def __init__(self, cart_service: CartService):
        self.cart_service = cart_service

    def get_cart(self, customer_id: str) -> CartResponse:
        return self.cart_service.get_cart(customer_id)

    def add_to_cart(self, customer_id: str, request: AddToCartRequest) -> CartResponse:
        try:
            return self.cart_service.add_to_cart(customer_id, request.edition_id, request.quantity)
        except (OutOfStockException, ValueError) as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        except EntityNotFoundException as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    def update_item_quantity(
        self, customer_id: str, edition_id: str, request: UpdateCartItemRequest
    ) -> CartResponse:
        try:
            return self.cart_service.update_quantity(customer_id, edition_id, request.quantity)
        except OutOfStockException as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        except EntityNotFoundException as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    def remove_item(self, customer_id: str, edition_id: str) -> CartResponse:
        return self.cart_service.remove_item(customer_id, edition_id)

    def clear_cart(self, customer_id: str) -> CartResponse:
        return self.cart_service.clear_cart(customer_id)


@router.get("", response_model=CartResponse)
def get_cart(
    customer_id: str = Depends(resolve_customer_id),
    cart_service: CartService = Depends(get_cart_service),
):
    return CartController(cart_service).get_cart(customer_id)


@router.post("/items", response_model=CartResponse)
def add_to_cart(
    request: AddToCartRequest,
    customer_id: str = Depends(resolve_customer_id),
    cart_service: CartService = Depends(get_cart_service),
):
    return CartController(cart_service).add_to_cart(customer_id, request)


@router.put("/items/{edition_id}", response_model=CartResponse)
def update_item_quantity(
    edition_id: str,
    request: UpdateCartItemRequest,
    customer_id: str = Depends(resolve_customer_id),
    cart_service: CartService = Depends(get_cart_service),
):
    return CartController(cart_service).update_item_quantity(customer_id, edition_id, request)


@router.delete("/items/{edition_id}", response_model=CartResponse)
def remove_item(
    edition_id: str,
    customer_id: str = Depends(resolve_customer_id),
    cart_service: CartService = Depends(get_cart_service),
):
    return CartController(cart_service).remove_item(customer_id, edition_id)


@router.delete("", response_model=CartResponse)
def clear_cart(
    customer_id: str = Depends(resolve_customer_id),
    cart_service: CartService = Depends(get_cart_service),
):
    return CartController(cart_service).clear_cart(customer_id)
