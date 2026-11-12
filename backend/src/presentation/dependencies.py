"""
Presentation Dependencies
Quản lý Dependency Injection (DI) cho các Router của FastAPI.
"""
import os
from typing import Optional
from fastapi import Header, HTTPException, Depends, status

from ..infrastructure.database import DatabaseSession
from ..infrastructure.repositories.book_repository import BookRepository
from ..infrastructure.repositories.cart_repository import CartRepository
from ..infrastructure.repositories.order_repository import OrderRepository
from ..infrastructure.repositories.user_repository import UserRepository
from ..infrastructure.adapters.vietqr_service import VietQRService
from ..infrastructure.adapters.sentence_transformer_adapter import SentenceTransformerAdapter
from ..infrastructure.adapters.image_hasher import ImageHasher
from ..infrastructure.adapters.cloudflare_llm import CloudflareLLMAdapter

from ..application.services.auth_service import AuthService
from ..application.services.cart_service import CartService
from ..application.services.checkout_service import CheckoutService
from ..application.services.search_service import SearchService
from ..application.services.chatbot_service import ChatbotService
from ..application.services.payment_service import PaymentService
from ..application.services.inventory_service import InventoryService
from ..domain.entities.user import User

# Khởi tạo Singleton Adapters
_vietqr_service = VietQRService()
_sentence_adapter = SentenceTransformerAdapter()
_image_hasher = ImageHasher()
_cloudflare_llm = CloudflareLLMAdapter()

def get_db_session():
    """Dependency Generator: Cung cấp kết nối CSDL riêng biệt cho từng request."""
    session = DatabaseSession()
    try:
        yield session
    finally:
        session.close()

def get_book_repo(session: DatabaseSession = Depends(get_db_session)) -> BookRepository:
    return BookRepository(session)

def get_cart_repo(session: DatabaseSession = Depends(get_db_session)) -> CartRepository:
    return CartRepository(session)

def get_order_repo(session: DatabaseSession = Depends(get_db_session)) -> OrderRepository:
    return OrderRepository(session)

def get_user_repo(session: DatabaseSession = Depends(get_db_session)) -> UserRepository:
    return UserRepository(session)

def get_auth_service(user_repo: UserRepository = Depends(get_user_repo)) -> AuthService:
    return AuthService(user_repo)

def get_cart_service(
    cart_repo: CartRepository = Depends(get_cart_repo),
    book_repo: BookRepository = Depends(get_book_repo)
) -> CartService:
    return CartService(cart_repo, book_repo)

def get_checkout_service(
    session: DatabaseSession = Depends(get_db_session),
    book_repo: BookRepository = Depends(get_book_repo),
    cart_repo: CartRepository = Depends(get_cart_repo),
    order_repo: OrderRepository = Depends(get_order_repo)
) -> CheckoutService:
    return CheckoutService(
        session=session,
        book_repo=book_repo,
        cart_repo=cart_repo,
        order_repo=order_repo,
        vietqr_service=_vietqr_service
    )

def get_search_service(book_repo: BookRepository = Depends(get_book_repo)) -> SearchService:
    return SearchService(
        book_repo=book_repo,
        transformer_adapter=_sentence_adapter,
        image_hasher=_image_hasher
    )

def get_chatbot_service(
    book_repo: BookRepository = Depends(get_book_repo),
    search_service: SearchService = Depends(get_search_service)
) -> ChatbotService:
    return ChatbotService(
        book_repo=book_repo,
        search_service=search_service,
        llm_adapter=_cloudflare_llm
    )

def get_payment_service(
    session: DatabaseSession = Depends(get_db_session),
    order_repo: OrderRepository = Depends(get_order_repo),
    book_repo: BookRepository = Depends(get_book_repo)
) -> PaymentService:
    return PaymentService(session, order_repo, book_repo)

def get_inventory_service(
    session: DatabaseSession = Depends(get_db_session),
    book_repo: BookRepository = Depends(get_book_repo),
    order_repo: OrderRepository = Depends(get_order_repo)
) -> InventoryService:
    return InventoryService(session, book_repo, order_repo)

def get_current_user_optional(
    authorization: Optional[str] = Header(None),
    auth_service: AuthService = Depends(get_auth_service),
    user_repo: UserRepository = Depends(get_user_repo)
) -> Optional[User]:
    """Trích xuất User từ header Authorization: Bearer <token>. Trả về None nếu không có."""
    if not authorization or not authorization.startswith("Bearer "):
        return None
    token = authorization.split(" ")[1]
    try:
        payload = auth_service.decode_token(token)
        user_id = payload.get("sub")
        return user_repo.get_by_id(user_id)
    except Exception:
        return None

def get_current_user(
    authorization: Optional[str] = Header(None),
    auth_service: AuthService = Depends(get_auth_service),
    user_repo: UserRepository = Depends(get_user_repo)
) -> User:
    """Bắt buộc phải có token hợp lệ."""
    user = get_current_user_optional(authorization, auth_service, user_repo)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Yêu cầu xác thực tài khoản để thực hiện thao tác này."
        )
    return user

def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """Bắt buộc quyền ADMIN hoặc MANAGER."""
    if not current_user.is_admin():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Chỉ Quản trị viên (ADMIN) mới có quyền truy cập chức năng này."
        )
    return current_user
