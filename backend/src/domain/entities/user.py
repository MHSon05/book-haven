"""
Domain Entity: User, Customer, Staff (Single Table Inheritance)
Định danh người dùng, kiểm soát phân quyền RBAC và sổ địa chỉ.
"""
from dataclasses import dataclass
from enum import Enum
from typing import Optional

class UserRole(str, Enum):
    CUSTOMER = "CUSTOMER"
    STAFF = "STAFF"
    ADMIN = "ADMIN"
    MANAGER = "MANAGER"

@dataclass
class User:
    user_id: str
    username: str
    password_hash: str
    email: str
    full_name: str
    phone: Optional[str] = None
    role: UserRole = UserRole.CUSTOMER
    shipping_address: Optional[str] = None
    loyalty_points: int = 0
    staff_role: Optional[str] = None
    department: Optional[str] = None
    created_at: Optional[str] = None

    def is_admin(self) -> bool:
        return self.role in (UserRole.ADMIN, UserRole.MANAGER)

    def is_staff(self) -> bool:
        return self.role in (UserRole.STAFF, UserRole.ADMIN, UserRole.MANAGER)

    def is_customer(self) -> bool:
        return self.role == UserRole.CUSTOMER
