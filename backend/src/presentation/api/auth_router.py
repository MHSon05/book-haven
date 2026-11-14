"""
Presentation Layer: AuthController & FastAPI Router (presentation.api)
Xử lý Đăng nhập, Đăng ký, Lấy thông tin cá nhân và Lịch sử đơn hàng của tài khoản.
Khớp 100% Listing 4.2 và Figure 4.5.
"""
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status

from ...application.dtos.auth_dto import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    UserProfileResponse,
)
from ...application.services.auth_service import AuthService
from ...infrastructure.repositories.order_repository import OrderRepository
from ...domain.entities.user import User
from ...domain.exceptions import DomainException
from ..dependencies import get_auth_service, get_order_repo, get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])


class AuthController:
    """Bộ điều khiển xác thực và hồ sơ người dùng (Presentation Layer)."""

    def __init__(
        self,
        auth_service: AuthService,
        order_repo: OrderRepository,
    ):
        self.auth_service = auth_service
        self.order_repo = order_repo

    def login(self, request: LoginRequest) -> TokenResponse:
        try:
            return self.auth_service.login(request)
        except DomainException as e:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

    def register(self, request: RegisterRequest) -> TokenResponse:
        try:
            return self.auth_service.register(request)
        except DomainException as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    def get_profile(self, user_id: str) -> UserProfileResponse:
        return self.auth_service.get_profile(user_id)

    def get_user_orders(self, user_id: str) -> List[Dict[str, Any]]:
        orders = self.order_repo.get_orders_by_customer(user_id)
        return [
            {
                "order_id": o.order_id,
                "created_at": o.created_at,
                "status": o.status.value,
                "final_amount": o.final_amount,
                "carrier": o.carrier.value if o.carrier else None,
                "tracking_code": o.tracking_code,
                "receiver_name": o.receiver_name,
                "shipping_address": o.shipping_address,
                "items_count": len(o.items),
                "items": [
                    {
                        "title": it.title_snapshot,
                        "binding_type": it.binding_type_snapshot,
                        "quantity": it.quantity,
                        "unit_price": it.unit_price_at_purchase,
                        "subtotal": it.subtotal(),
                    }
                    for it in o.items
                ],
            }
            for o in orders
        ]


@router.post("/login", response_model=TokenResponse)
def login(
    request: LoginRequest,
    auth_service: AuthService = Depends(get_auth_service),
    order_repo: OrderRepository = Depends(get_order_repo),
):
    return AuthController(auth_service, order_repo).login(request)


@router.post("/register", response_model=TokenResponse)
def register(
    request: RegisterRequest,
    auth_service: AuthService = Depends(get_auth_service),
    order_repo: OrderRepository = Depends(get_order_repo),
):
    return AuthController(auth_service, order_repo).register(request)


@router.get("/me", response_model=UserProfileResponse)
def get_current_user_profile(
    current_user: User = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service),
    order_repo: OrderRepository = Depends(get_order_repo),
):
    return AuthController(auth_service, order_repo).get_profile(current_user.user_id)


@router.get("/orders")
def get_user_orders(
    current_user: User = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service),
    order_repo: OrderRepository = Depends(get_order_repo),
):
    return AuthController(auth_service, order_repo).get_user_orders(current_user.user_id)


__all__ = ["router", "AuthController"]
