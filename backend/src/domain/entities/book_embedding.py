"""
Domain Entity: BookEmbedding
Vector nhúng ngữ nghĩa d=384 của sách in (Chương 3).
Khớp 100% với Hình 4.3. KHÔNG dùng Enum.
"""
import json
import math
from typing import Optional, List
from datetime import datetime


class BookEmbedding:
    def __init__(
        self,
        product_id: int,
        vector_json: str = "[]",
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
        created_at: Optional[datetime] = None,
    ):
        self._product_id = product_id
        self._vector_json = vector_json
        self._model_name = model_name
        self._created_at = created_at or datetime.utcnow()
        self._cached_vector: Optional[List[float]] = None

    @property
    def product_id(self) -> int:
        return self._product_id

    @property
    def vector_json(self) -> str:
        return self._vector_json

    @property
    def model_name(self) -> str:
        return self._model_name

    @property
    def created_at(self) -> datetime:
        return self._created_at

    def get_vector_array(self) -> List[float]:
        """Giải mã JSON string thành danh sách 384 số thực float."""
        if self._cached_vector is None:
            self._cached_vector = json.loads(self._vector_json)
        return self._cached_vector

    def compute_cosine_similarity(self, query_vector: List[float]) -> float:
        """Tính khoảng cách Cosine giữa vector sách và vector truy vấn của độc giả."""
        v = self.get_vector_array()
        if len(v) != len(query_vector):
            return 0.0
        dot_product = sum(a * b for a, b in zip(v, query_vector))
        norm_v = math.sqrt(sum(a * a for a in v))
        norm_q = math.sqrt(sum(b * b for b in query_vector))
        if norm_v == 0.0 or norm_q == 0.0:
            return 0.0
        return dot_product / (norm_v * norm_q)
