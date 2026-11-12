"""
Infrastructure Adapter: SentenceTransformerAdapter
Mô hình nhúng ngữ nghĩa thực tế all-MiniLM-L6-v2 (d=384) phục vụ Semantic Search (Chương 3).
"""
import os
from typing import List


class SentenceTransformerAdapter:
    _instance = None
    _model = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_model()
        return cls._instance

    def _init_model(self):
        from sentence_transformers import SentenceTransformer

        model_name = os.getenv("EMBEDDING_MODEL_NAME", "all-MiniLM-L6-v2")
        self._model = SentenceTransformer(model_name)
        print(f"[AI Model] Loaded sentence-transformers '{model_name}' successfully.")

    def encode(self, text: str, dim: int = 384) -> List[float]:
        """
        Sinh vector dense chuẩn hóa L2-norm = 1.0 trực tiếp từ mô hình Transformer (FR_AI02).
        """
        if self._model is None:
            raise RuntimeError("Mô hình SentenceTransformer chưa được khởi tạo.")
        emb = self._model.encode(text, normalize_embeddings=True)
        return [round(float(x), 5) for x in emb]
