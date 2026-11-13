"""
Domain Entity: User (Base Identity Class)
Lớp tài khoản người dùng cơ sở.
Khớp 100% với Hình 4.3. KHÔNG dùng Enum - role là chuỗi ('CUSTOMER', 'STAFF', 'ADMIN', 'MANAGER').
"""
import bcrypt
import jwt
from typing import Optional
from datetime import datetime, timedelta

JWT_SECRET = "bookhaven-super-secret-key-ptit-2026"
JWT_ALGORITHM = "HS256"


class User:
    def __init__(
        self,
        user_id: Optional[int] = None,
        username: str = "",
        password_hash: str = "",
        email: str = "",
        full_name: str = "",
        phone: Optional[str] = None,
        role: str = "CUSTOMER",
        created_at: Optional[datetime] = None,
    ):
        self._user_id = user_id
        self._username = username
        self._password_hash = password_hash
        self._email = email
        self._full_name = full_name
        self._phone = phone
        self._role = role
        self._created_at = created_at or datetime.utcnow()

    @property
    def user_id(self) -> Optional[int]:
        return self._user_id

    @property
    def username(self) -> str:
        return self._username

    @property
    def password_hash(self) -> str:
        return self._password_hash

    @property
    def email(self) -> str:
        return self._email

    @property
    def full_name(self) -> str:
        return self._full_name

    @property
    def phone(self) -> Optional[str]:
        return self._phone

    @property
    def role(self) -> str:
        return self._role

    @property
    def created_at(self) -> datetime:
        return self._created_at

    def is_admin(self) -> bool:
        """Kiểm tra người dùng có quyền quản trị."""
        return self._role in ("ADMIN", "STAFF", "MANAGER")

    # Business Operations from UML
    def verify_password(self, plain_password: str) -> bool:
        """Xác thực mật khẩu plaintext với băm bcrypt."""
        if not self._password_hash:
            return False
        return bcrypt.checkpw(plain_password.encode("utf-8"), self._password_hash.encode("utf-8"))

    def change_password(self, new_password_hash: str) -> None:
        """Cập nhật mã băm mật khẩu mới."""
        self._password_hash = new_password_hash

    def issue_jwt_token(self, expires_delta_hours: int = 24) -> str:
        """Phát hành phiên đăng nhập Stateless JWT chứa định danh và quyền hạn."""
        payload = {
            "sub": str(self._user_id),
            "username": self._username,
            "role": self._role,
            "exp": datetime.utcnow() + timedelta(hours=expires_delta_hours),
            "iat": datetime.utcnow(),
        }
        return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
