"""
Domain Entity: Staff
Lớp con kế thừa từ User đại diện cho Nhân viên nội bộ hiệu sách.
Khớp 100% với Hình 4.3. KHÔNG dùng Enum - staff_role, department là chuỗi (string).
"""
from typing import Optional, List
from datetime import datetime
from src.domain.entities.user import User


class Staff(User):
    def __init__(
        self,
        user_id: Optional[int] = None,
        username: str = "",
        password_hash: str = "",
        email: str = "",
        full_name: str = "",
        phone: Optional[str] = None,
        role: str = "STAFF",
        staff_role: str = "Warehouse Lead",
        department: str = "Logistics",
        created_at: Optional[datetime] = None,
    ):
        super().__init__(
            user_id=user_id,
            username=username,
            password_hash=password_hash,
            email=email,
            full_name=full_name,
            phone=phone,
            role=role,
            created_at=created_at,
        )
        self._staff_role = staff_role
        self._department = department
        self._activity_logs: List[str] = []

    @property
    def staff_role(self) -> str:
        return self._staff_role

    @property
    def department(self) -> str:
        return self._department

    # Business Operations from UML
    def has_permission(self, permission_key: str) -> bool:
        """Kiểm tra quyền hạn tác nghiệp theo chức danh và phòng ban."""
        if self._role in ("ADMIN", "MANAGER"):
            return True
        if "INVENTORY" in permission_key and "Logistics" in self._department:
            return True
        if "ORDER" in permission_key and "Sales" in self._department:
            return True
        return False

    def log_activity(self, action: str) -> None:
        """Ghi nhận nhật ký thao tác nghiệp vụ nội bộ."""
        log_entry = f"[{datetime.utcnow().isoformat()}] Staff {self._username} ({self._staff_role}): {action}"
        self._activity_logs.append(log_entry)
