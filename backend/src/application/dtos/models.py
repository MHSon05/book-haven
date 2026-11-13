"""
Application DTOs (Data Transfer Objects)
Định nghĩa cấu trúc dữ liệu giao tiếp vào/ra chuẩn hóa bằng Pydantic.
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

# ==================== AUTH DTOs ====================
class LoginRequest(BaseModel):
    username: str
    password: str

class RegisterRequest(BaseModel):
    username: str
    password: str
    email: str
    full_name: str
    phone: Optional[str] = None
    shipping_address: Optional[str] = None

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    username: str
    full_name: str
    role: str

class UserProfileResponse(BaseModel):
    user_id: str
    username: str
    email: str
    full_name: str
    phone: Optional[str] = None
    role: str
    shipping_address: Optional[str] = None
    loyalty_points: int = 0


# ==================== CART DTOs ====================
class AddToCartRequest(BaseModel):
    edition_id: str
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


# ==================== CHECKOUT DTOs ====================
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


# ==================== SEARCH DTOs ====================
class SemanticSearchRequest(BaseModel):
    query: str
    limit: int = 5

class SearchResultItem(BaseModel):
    book_id: Any
    title: str
    author_name: str
    publisher_name: str
    category_id: Optional[Any] = None
    category_name: str
    description: str
    cover_image: Optional[str] = None
    min_price: int
    max_price: int
    available_stock: int
    similarity_score: Optional[float] = None
    explanation_snippet: Optional[str] = None

class SearchResponse(BaseModel):
    total_found: int
    search_mode: str
    results: List[SearchResultItem]


# ==================== CHATBOT DTOs ====================
class ChatMessageRequest(BaseModel):
    message: str

class BookCardDTO(BaseModel):
    book_id: Any
    title: str
    author_name: str
    unit_price: int
    binding_type: str
    edition_id: Any
    cover_image: Optional[str] = None
    available_stock: int

class ChatMessageResponse(BaseModel):
    reply: str
    suggested_books: List[BookCardDTO] = []


# ==================== ADMIN DTOs ====================
class RestockRequest(BaseModel):
    edition_id: str
    quantity: int = Field(gt=0)

class DispatchOrderRequest(BaseModel):
    carrier: str = "HANOI_DRONE"  # HANOI_DRONE hoặc GHN_EXPRESS


# ==================== PAYMENT DTOs ====================
class ConfirmPaymentRequest(BaseModel):
    order_id: str
    transaction_code: Optional[str] = None
