"""
Infrastructure: DatabaseSession
Quản lý kết nối vật lý và ranh giới giao dịch CSDL SQLite (Transaction Management).
Khớp 100% với Listing 4.6 trong Báo cáo Thiết kế BookHaven.
"""
import sqlite3
import os
from typing import Optional

DEFAULT_DB_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "db", "bookhaven.db")

class DatabaseSession:
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or os.getenv("DB_PATH", DEFAULT_DB_PATH)
        # Chuẩn hóa đường dẫn tuyệt đối
        if not os.path.isabs(self.db_path):
            self.db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", self.db_path))
        self._conn: Optional[sqlite3.Connection] = None
        self._in_transaction: bool = False

    def get_connection(self) -> sqlite3.Connection:
        if self._conn is None:
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            self._conn = sqlite3.connect(self.db_path, check_same_thread=False, isolation_level=None)
            self._conn.row_factory = sqlite3.Row
            # Bắt buộc bật ràng buộc khóa ngoại (PRAGMA foreign_keys = ON)
            self._conn.execute("PRAGMA foreign_keys = ON;")
        return self._conn

    def begin_transaction(self):
        """Khởi động ranh giới giao dịch CSDL (Transaction Boundary)."""
        if not self._in_transaction:
            self.get_connection().execute("BEGIN TRANSACTION;")
            self._in_transaction = True

    def commit(self):
        """Xác nhận giao dịch CSDL thành công."""
        if self._conn and self._in_transaction:
            self._conn.execute("COMMIT;")
            self._in_transaction = False

    def rollback(self):
        """Hoàn tác an toàn khi phát sinh lỗi hoặc hết hàng."""
        if self._conn and self._in_transaction:
            self._conn.execute("ROLLBACK;")
            self._in_transaction = False

    def close(self):
        if self._conn:
            if self._in_transaction:
                self.rollback()
            self._conn.close()
            self._conn = None

    def __enter__(self):
        self.begin_transaction()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.rollback()
        else:
            self.commit()
