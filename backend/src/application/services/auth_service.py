"""
Application Service: AuthService
Quản lý xác thực người dùng, băm mật khẩu Bcrypt, phát hành & kiểm tra JSON Web Token (JWT).
Phân quyền RBAC khớp theo Báo cáo Phân tích Thiết kế Hệ thống Thông tin.
"""
import os
import uuid
import bcrypt
import jwt
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any

from ...domain.entities.user import User, UserRole
from ...domain.exceptions import DomainException, EntityNotFoundException
from ...infrastructure.repositories.user_repository import UserRepository
from ..dtos.models import LoginRequest, RegisterRequest, TokenResponse, UserProfileResponse

DEFAULT_SECRET = "bookhaven-ecommerce-secret-key-pttkhttt-2026-ptit-security"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24

class AuthService:
    def __init__(self, user_repo: UserRepository, secret_key: Optional[str] = None):
        self.user_repo = user_repo
        self.secret_key = secret_key or os.getenv("JWT_SECRET_KEY", DEFAULT_SECRET)

    def hash_password(self, password: str) -> str:
        salt = bcrypt.gensalt(rounds=12)
        return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        try:
            return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
        except Exception:
            return False

    def create_access_token(self, user_id: str, username: str, role: str) -> str:
        expire = datetime.now(timezone.utc) + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
        payload = {
            "sub": user_id,
            "username": username,
            "role": role,
            "exp": expire,
            "iat": datetime.now(timezone.utc)
        }
        return jwt.encode(payload, self.secret_key, algorithm=ALGORITHM)

    def decode_token(self, token: str) -> Dict[str, Any]:
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            raise DomainException("Phiên đăng nhập đã hết hạn, vui lòng đăng nhập lại.")
        except jwt.InvalidTokenError:
            raise DomainException("Token xác thực không hợp lệ.")

    def login(self, request: LoginRequest) -> TokenResponse:
        user = self.user_repo.get_by_username(request.username)
        if not user:
            user = self.user_repo.get_by_email(request.username)
        if not user or not self.verify_password(request.password, user.password_hash):
            raise DomainException("Tài khoản hoặc mật khẩu không chính xác.")

        token = self.create_access_token(user.user_id, user.username, user.role.value)
        return TokenResponse(
            access_token=token,
            token_type="bearer",
            user_id=user.user_id,
            username=user.username,
            full_name=user.full_name,
            role=user.role.value
        )

    def register(self, request: RegisterRequest) -> TokenResponse:
        # Kiểm tra trùng username
        existing_username = self.user_repo.get_by_username(request.username)
        if existing_username:
            raise DomainException(f"Tên tài khoản '{request.username}' đã được đăng ký.")

        # Kiểm tra trùng email
        existing_email = self.user_repo.get_by_email(request.email)
        if existing_email:
            raise DomainException(f"Địa chỉ email '{request.email}' đã được sử dụng.")

        user_id = f"USER_{uuid.uuid4().hex[:8].upper()}"
        password_hash = self.hash_password(request.password)

        new_user = User(
            user_id=user_id,
            username=request.username,
            password_hash=password_hash,
            email=request.email,
            full_name=request.full_name,
            phone=request.phone,
            role=UserRole.CUSTOMER,
            shipping_address=request.shipping_address,
            loyalty_points=0
        )
        self.user_repo.create_user(new_user)

        token = self.create_access_token(new_user.user_id, new_user.username, new_user.role.value)
        return TokenResponse(
            access_token=token,
            token_type="bearer",
            user_id=new_user.user_id,
            username=new_user.username,
            full_name=new_user.full_name,
            role=new_user.role.value
        )

    def get_profile(self, user_id: str) -> UserProfileResponse:
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise EntityNotFoundException("User", user_id)
        return UserProfileResponse(
            user_id=user.user_id,
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            phone=user.phone,
            role=user.role.value,
            shipping_address=user.shipping_address,
            loyalty_points=user.loyalty_points
        )
