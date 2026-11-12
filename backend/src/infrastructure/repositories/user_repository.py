"""
Infrastructure Repository: UserRepository
Quản lý lưu trữ người dùng, khách hàng và nhân viên (Single Table Inheritance).
"""
from typing import Optional
from ..database import DatabaseSession
from ...domain.entities.user import User, UserRole

class UserRepository:
    def __init__(self, session: DatabaseSession):
        self.session = session

    def get_by_username(self, username: str) -> Optional[User]:
        conn = self.session.get_connection()
        row = conn.execute("SELECT * FROM users WHERE username = ?;", (username,)).fetchone()
        return self._to_entity(row) if row else None

    def get_by_email(self, email: str) -> Optional[User]:
        conn = self.session.get_connection()
        row = conn.execute("SELECT * FROM users WHERE email = ?;", (email,)).fetchone()
        return self._to_entity(row) if row else None

    def get_by_id(self, user_id: str) -> Optional[User]:
        conn = self.session.get_connection()
        row = conn.execute("SELECT * FROM users WHERE user_id = ?;", (user_id,)).fetchone()
        return self._to_entity(row) if row else None

    def create_user(self, user: User) -> User:
        conn = self.session.get_connection()
        query = """
        INSERT INTO users (
            user_id, username, password_hash, email, full_name, phone,
            role, shipping_address, loyalty_points, staff_role, department
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """
        conn.execute(query, (
            user.user_id, user.username, user.password_hash, user.email,
            user.full_name, user.phone, user.role.value, user.shipping_address,
            user.loyalty_points, user.staff_role, user.department
        ))
        return user

    def _to_entity(self, row) -> User:
        return User(
            user_id=row["user_id"],
            username=row["username"],
            password_hash=row["password_hash"],
            email=row["email"],
            full_name=row["full_name"],
            phone=row["phone"],
            role=UserRole(row["role"]),
            shipping_address=row["shipping_address"],
            loyalty_points=row["loyalty_points"],
            staff_role=row["staff_role"],
            department=row["department"],
            created_at=row["created_at"]
        )
