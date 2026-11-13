"""
Infrastructure Repository: UserRepository
Quản lý lưu trữ Người dùng (users), Khách hàng (customers) và Nhân viên (staffs).
Khớp 100% với Hình 4.3, 4.4 và CSDL 17 bảng (Table-per-subclass).
KHÔNG dùng Enum - role là chuỗi ('CUSTOMER', 'STAFF', 'ADMIN', 'MANAGER').
"""
from typing import Optional, Union
from src.infrastructure.database import DatabaseSession
from src.domain.entities.user import User
from src.domain.entities.customer import Customer
from src.domain.entities.staff import Staff


class UserRepository:
    def __init__(self, session: DatabaseSession):
        self.session = session

    def get_by_username(self, username: str) -> Optional[Union[Customer, Staff, User]]:
        conn = self.session.get_connection()
        query = """
        SELECT u.*, c.shipping_address, c.loyalty_points, s.staff_role, s.department
        FROM users u
        LEFT JOIN customers c ON u.user_id = c.user_id
        LEFT JOIN staffs s ON u.user_id = s.user_id
        WHERE u.username = ?;
        """
        row = conn.execute(query, (username,)).fetchone()
        return self._to_entity(row) if row else None

    def get_by_email(self, email: str) -> Optional[Union[Customer, Staff, User]]:
        conn = self.session.get_connection()
        query = """
        SELECT u.*, c.shipping_address, c.loyalty_points, s.staff_role, s.department
        FROM users u
        LEFT JOIN customers c ON u.user_id = c.user_id
        LEFT JOIN staffs s ON u.user_id = s.user_id
        WHERE u.email = ?;
        """
        row = conn.execute(query, (email,)).fetchone()
        return self._to_entity(row) if row else None

    def get_by_id(self, user_id: int) -> Optional[Union[Customer, Staff, User]]:
        conn = self.session.get_connection()
        query = """
        SELECT u.*, c.shipping_address, c.loyalty_points, s.staff_role, s.department
        FROM users u
        LEFT JOIN customers c ON u.user_id = c.user_id
        LEFT JOIN staffs s ON u.user_id = s.user_id
        WHERE u.user_id = ?;
        """
        row = conn.execute(query, (user_id,)).fetchone()
        return self._to_entity(row) if row else None

    def create_customer(self, customer: Customer) -> Customer:
        conn = self.session.get_connection()
        cur = conn.execute("""
            INSERT INTO users (username, password_hash, email, full_name, phone, role)
            VALUES (?, ?, ?, ?, ?, 'CUSTOMER');
        """, (customer.username, customer.password_hash, customer.email, customer.full_name, customer.phone))
        assigned_id = cur.lastrowid
        customer._user_id = assigned_id

        conn.execute("""
            INSERT INTO customers (user_id, shipping_address, loyalty_points)
            VALUES (?, ?, ?);
        """, (assigned_id, customer.shipping_address, customer.loyalty_points))
        return customer

    def _to_entity(self, row) -> Union[Customer, Staff, User]:
        role = row["role"]
        if role == "CUSTOMER":
            return Customer(
                user_id=row["user_id"],
                username=row["username"],
                password_hash=row["password_hash"],
                email=row["email"],
                full_name=row["full_name"],
                phone=row["phone"],
                role=role,
                shipping_address=row["shipping_address"] or "",
                loyalty_points=row["loyalty_points"] or 0,
            )
        elif role in ("STAFF", "ADMIN", "MANAGER"):
            return Staff(
                user_id=row["user_id"],
                username=row["username"],
                password_hash=row["password_hash"],
                email=row["email"],
                full_name=row["full_name"],
                phone=row["phone"],
                role=role,
                staff_role=row["staff_role"] or f"{role} Lead",
                department=row["department"] or "Operations",
            )
        return User(
            user_id=row["user_id"],
            username=row["username"],
            password_hash=row["password_hash"],
            email=row["email"],
            full_name=row["full_name"],
            phone=row["phone"],
            role=role,
        )
