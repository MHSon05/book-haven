"""
Application DTOs: Shopping Cart & Cart Items
"""
from typing import Any, List, Optional
from pydantic import BaseModel, Field


class AddToCartRequest(BaseModel):
    edition_id: Any
    quantity: int = Field(default=1, ge=1)


class UpdateCartItemRequest(BaseModel):
    quantity: int = Field(ge=0)


class CartItemDTO(BaseModel):
    cart_item_id: str
    edition_id: str
    book_id: str
    title: str
    sku: str
    binding_type: str
    isbn13: str
    unit_price: int
    weight_gram: int
    quantity: int
    subtotal: int
    cover_image: Optional[str] = None
    available_stock: int


class CartResponse(BaseModel):
    cart_id: str
    customer_id: str
    subtotal: int
    total_weight_grams: int
    items: List[CartItemDTO]
