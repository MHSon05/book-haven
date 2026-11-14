"""
Presentation Layer: AdminController & FastAPI Router (presentation.api)
Dành cho Quản trị viên (ADMIN) & Thủ kho: Nhập kho, Quản lý tồn kho, Bàn giao giao vận Drone/GHN, Báo cáo doanh thu.
Khớp 100% Listing 4.2 và Figure 4.5.
"""
from typing import Dict, Any
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, status

from ...application.dtos.admin_dto import RestockRequest, DispatchOrderRequest
from ...application.dtos.checkout_dto import OrderResponse
from ...application.services.inventory_service import InventoryService
from ...infrastructure.repositories.order_repository import OrderRepository
from ...domain.exceptions import (
    EntityNotFoundException,
    InvalidOrderStateException,
    DroneOverweightException,
)
from ..dependencies import get_inventory_service, get_order_repo, require_admin

router = APIRouter(
    prefix="/admin",
    tags=["Admin & Back-office"],
    dependencies=[Depends(require_admin)],
)


class AdminController:
    """Bộ điều khiển nghiệp vụ quản trị kho và đơn hàng (Presentation Layer)."""

    def __init__(
        self,
        inventory_service: InventoryService,
        order_repo: OrderRepository,
    ):
        self.inventory_service = inventory_service
        self.order_repo = order_repo

    def get_inventory(self) -> Dict[str, Any]:
        return {"inventory": self.inventory_service.get_inventory_status()}

    def restock(self, request: RestockRequest) -> Dict[str, Any]:
        try:
            updated_edition = self.inventory_service.restock(request.edition_id, request.quantity)
            return {
                "message": f"Nhập kho thành công +{request.quantity} cuốn cho SKU '{updated_edition.sku}'.",
                "edition_id": updated_edition.edition_id,
                "sku": updated_edition.sku,
                "stock_on_hand": updated_edition.stock_on_hand,
                "available_stock": updated_edition.available_stock(),
            }
        except EntityNotFoundException as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    def get_orders(self, limit: int = 50, offset: int = 0) -> Dict[str, Any]:
        orders = self.order_repo.get_all_orders(limit=limit, offset=offset)
        for ord_dict in orders:
            if (
                ord_dict.get("status") == "SHIPPING"
                and ord_dict.get("carrier") == "HANOI_DRONE"
                and ord_dict.get("updated_at")
            ):
                try:
                    raw_time = str(ord_dict["updated_at"]).split(".")[0]
                    updated_dt = datetime.strptime(raw_time, "%Y-%m-%d %H:%M:%S")
                    if (datetime.now() - updated_dt).total_seconds() >= 25:
                        self.inventory_service.mark_delivered(ord_dict["order_id"])
                        ord_dict["status"] = "DELIVERED"
                except Exception:
                    pass
        return {"total": len(orders), "orders": orders}

    def dispatch_order(self, order_id: str, request: DispatchOrderRequest) -> OrderResponse:
        try:
            return self.inventory_service.dispatch_order(
                order_id=order_id, carrier_name=request.carrier
            )
        except EntityNotFoundException as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        except (InvalidOrderStateException, DroneOverweightException) as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    def mark_delivered(self, order_id: str) -> OrderResponse:
        try:
            return self.inventory_service.mark_delivered(order_id)
        except EntityNotFoundException as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        except InvalidOrderStateException as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    def get_revenue_report(self) -> Dict[str, Any]:
        return self.inventory_service.get_revenue_report()


@router.get("/inventory")
def get_inventory(
    inventory_service: InventoryService = Depends(get_inventory_service),
    order_repo: OrderRepository = Depends(get_order_repo),
):
    return AdminController(inventory_service, order_repo).get_inventory()


@router.post("/inventory/restock")
def restock_books(
    request: RestockRequest,
    inventory_service: InventoryService = Depends(get_inventory_service),
    order_repo: OrderRepository = Depends(get_order_repo),
):
    return AdminController(inventory_service, order_repo).restock(request)


@router.get("/orders")
def get_all_orders(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    order_repo: OrderRepository = Depends(get_order_repo),
    inventory_service: InventoryService = Depends(get_inventory_service),
):
    return AdminController(inventory_service, order_repo).get_orders(limit=limit, offset=offset)


@router.post("/orders/{order_id}/dispatch", response_model=OrderResponse)
def dispatch_order(
    order_id: str,
    request: DispatchOrderRequest,
    inventory_service: InventoryService = Depends(get_inventory_service),
    order_repo: OrderRepository = Depends(get_order_repo),
):
    return AdminController(inventory_service, order_repo).dispatch_order(order_id, request)


@router.post("/orders/{order_id}/delivered", response_model=OrderResponse)
def mark_delivered(
    order_id: str,
    inventory_service: InventoryService = Depends(get_inventory_service),
    order_repo: OrderRepository = Depends(get_order_repo),
):
    return AdminController(inventory_service, order_repo).mark_delivered(order_id)


@router.get("/reports/revenue")
def get_revenue_report(
    inventory_service: InventoryService = Depends(get_inventory_service),
    order_repo: OrderRepository = Depends(get_order_repo),
):
    return AdminController(inventory_service, order_repo).get_revenue_report()


__all__ = ["router", "AdminController"]
