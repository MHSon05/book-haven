"""
Application DTOs: Checkout, Orders & Shipping Options
"""
from typing import Any, Dict, List, Optional
from pydantic import BaseModel


class CheckoutRequest(BaseModel):
    cart_id: str
    receiver_name: str
    receiver_phone: str
    shipping_address: str
    payment_method: str = "VIETQR"  # VIETQR hoặc COD
    carrier: str = "GHN_STANDARD"   # GHN_STANDARD, GHN_EXPRESS, HANOI_DRONE
    voucher_code: Optional[str] = None


class OrderItemDTO(BaseModel):
    order_item_id: str
    edition_id: str
    title: str
    sku: str
    binding_type: str
    isbn13: str
    unit_price: int
    quantity: int
    weight_gram: int
    subtotal: int


class OrderResponse(BaseModel):
    order_id: str
    customer_id: str
    receiver_name: str
    receiver_phone: str
    shipping_address: str
    payment_method: str
    carrier: str
    total_amount: int
    shipping_fee: int
    discount_amount: int
    final_amount: int
    status: str
    tracking_code: Optional[str] = None
    created_at: Optional[str] = None
    items: List[OrderItemDTO]
    vietqr_data: Optional[Dict[str, Any]] = None
    reservation_expires_at: Optional[str] = None


class ShippingOption(BaseModel):
    carrier_code: str
    carrier_name: str
    fee: int
    estimated_time: str
    is_available: bool
    disabled_reason: Optional[str] = None


class ShippingOptionsResponse(BaseModel):
    total_weight_grams: int
    options: List[ShippingOption]
