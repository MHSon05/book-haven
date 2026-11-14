"""
Application DTOs: Payment & Webhooks
"""
from typing import Optional
from pydantic import BaseModel


class ConfirmPaymentRequest(BaseModel):
    order_id: str
    transaction_code: Optional[str] = None
