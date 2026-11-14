"""
Presentation Layer: PaymentController & FastAPI Router (presentation.api)
Tiếp nhận xác nhận thanh toán VietQR, Webhook ngân hàng và Polling trạng thái đơn hàng.
Khớp 100% Listing 4.2 và Figure 4.5.
"""
from typing import Dict, Any, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status

from ...application.dtos.checkout_dto import OrderResponse
from ...application.dtos.payment_dto import ConfirmPaymentRequest
from ...application.services.payment_service import PaymentService
from ...application.services.inventory_service import InventoryService
from ...domain.exceptions import EntityNotFoundException, InvalidOrderStateException
from ..dependencies import get_payment_service, get_inventory_service

router = APIRouter(tags=["Payments & Orders"])


class PaymentController:
    """Bộ điều khiển xác nhận thanh toán, webhook ngân hàng và theo dõi trạng thái đơn."""

    def __init__(
        self,
        payment_service: PaymentService,
        inventory_service: Optional[InventoryService] = None,
    ):
        self.payment_service = payment_service
        self.inventory_service = inventory_service

    def confirm_payment(self, request: ConfirmPaymentRequest) -> OrderResponse:
        try:
            return self.payment_service.confirm_payment(
                order_id=request.order_id,
                transaction_code=request.transaction_code,
            )
        except EntityNotFoundException as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        except InvalidOrderStateException as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    def receive_bank_webhook(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        result = self.payment_service.process_webhook(payload)
        if not result.get("success"):
            return {"status": "ignored", "detail": result.get("message")}
        return {"status": "success", "data": result}

    def get_order_payment_status(self, order_id: str) -> Dict[str, Any]:
        try:
            order_status = self.payment_service.get_order_status(order_id)
            if (
                self.inventory_service is not None
                and order_status.get("status") == "SHIPPING"
                and order_status.get("carrier") == "HANOI_DRONE"
                and order_status.get("updated_at")
            ):
                try:
                    raw_time = str(order_status["updated_at"]).split(".")[0]
                    updated_dt = datetime.strptime(raw_time, "%Y-%m-%d %H:%M:%S")
                    if (datetime.now() - updated_dt).total_seconds() >= 25:
                        self.inventory_service.mark_delivered(order_id)
                        order_status = self.payment_service.get_order_status(order_id)
                except Exception:
                    pass
            return order_status
        except EntityNotFoundException as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    def mark_order_delivered(self, order_id: str) -> OrderResponse:
        if self.inventory_service is None:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Thiếu InventoryService.")
        try:
            return self.inventory_service.mark_delivered(order_id)
        except EntityNotFoundException as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        except InvalidOrderStateException as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/payments/confirm", response_model=OrderResponse)
def confirm_payment(
    request: ConfirmPaymentRequest,
    payment_service: PaymentService = Depends(get_payment_service),
):
    return PaymentController(payment_service).confirm_payment(request)


@router.post("/payments/webhook")
def receive_bank_webhook(
    payload: Dict[str, Any],
    payment_service: PaymentService = Depends(get_payment_service),
):
    return PaymentController(payment_service).receive_bank_webhook(payload)


@router.get("/orders/{order_id}/status")
def get_order_payment_status(
    order_id: str,
    payment_service: PaymentService = Depends(get_payment_service),
    inventory_service: InventoryService = Depends(get_inventory_service),
):
    return PaymentController(payment_service, inventory_service).get_order_payment_status(order_id)


@router.post("/orders/{order_id}/delivered", response_model=OrderResponse)
def mark_order_delivered(
    order_id: str,
    payment_service: PaymentService = Depends(get_payment_service),
    inventory_service: InventoryService = Depends(get_inventory_service),
):
    return PaymentController(payment_service, inventory_service).mark_order_delivered(order_id)


__all__ = ["router", "PaymentController"]
