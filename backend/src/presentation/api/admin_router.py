"""
Presentation Router: AdminRouter
Dành cho Quản trị viên (ADMIN) & Thủ kho: Nhập kho, Quản lý tồn kho, Bàn giao giao vận Drone/GHN, Báo cáo doanh thu.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, status

from ...application.dtos.models import RestockRequest, DispatchOrderRequest, OrderResponse
from ...application.services.inventory_service import InventoryService
from ...infrastructure.repositories.order_repository import OrderRepository
from ...domain.exceptions import EntityNotFoundException, InvalidOrderStateException, DroneOverweightException
from ..dependencies import get_inventory_service, get_order_repo, require_admin

router = APIRouter(
    prefix="/admin",
    tags=["Admin & Back-office"],
    dependencies=[Depends(require_admin)]
)

@router.get("/inventory")
def get_inventory(
    inventory_service: InventoryService = Depends(get_inventory_service)
):
    return {"inventory": inventory_service.get_inventory_status()}

@router.post("/inventory/restock")
def restock_books(
    request: RestockRequest,
    inventory_service: InventoryService = Depends(get_inventory_service)
):
    try:
        updated_edition = inventory_service.restock(request.edition_id, request.quantity)
        return {
            "message": f"Nhập kho thành công +{request.quantity} cuốn cho SKU '{updated_edition.sku}'.",
            "edition_id": updated_edition.edition_id,
            "sku": updated_edition.sku,
            "stock_on_hand": updated_edition.stock_on_hand,
            "available_stock": updated_edition.available_stock()
        }
    except EntityNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/orders")
def get_all_orders(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    order_repo: OrderRepository = Depends(get_order_repo),
    inventory_service: InventoryService = Depends(get_inventory_service)
):
    orders = order_repo.get_all_orders(limit=limit, offset=offset)
    for ord_dict in orders:
        if ord_dict.get("status") == "SHIPPING" and ord_dict.get("carrier") == "HANOI_DRONE" and ord_dict.get("updated_at"):
            try:
                raw_time = str(ord_dict["updated_at"]).split(".")[0]
                updated_dt = datetime.strptime(raw_time, "%Y-%m-%d %H:%M:%S")
                if (datetime.now() - updated_dt).total_seconds() >= 25:
                    inventory_service.mark_delivered(ord_dict["order_id"])
                    ord_dict["status"] = "DELIVERED"
            except Exception:
                pass
    return {"total": len(orders), "orders": orders}

@router.post("/orders/{order_id}/dispatch", response_model=OrderResponse)
def dispatch_order(
    order_id: str,
    request: DispatchOrderRequest,
    inventory_service: InventoryService = Depends(get_inventory_service)
):
    try:
        return inventory_service.dispatch_order(order_id=order_id, carrier_name=request.carrier)
    except EntityNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except InvalidOrderStateException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except DroneOverweightException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/orders/{order_id}/delivered", response_model=OrderResponse)
def mark_delivered(
    order_id: str,
    inventory_service: InventoryService = Depends(get_inventory_service)
):
    try:
        return inventory_service.mark_delivered(order_id)
    except EntityNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except InvalidOrderStateException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/reports/revenue")
def get_revenue_report(
    inventory_service: InventoryService = Depends(get_inventory_service)
):
    return inventory_service.get_revenue_report()
