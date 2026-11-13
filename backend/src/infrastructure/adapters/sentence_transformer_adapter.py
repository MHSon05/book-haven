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
        try:
            from sentence_transformers import SentenceTransformer
            model_name = os.getenv("EMBEDDING_MODEL_NAME", "all-MiniLM-L6-v2")
            self._model = SentenceTransformer(model_name)
            print(f"[AI Model] Loaded sentence-transformers '{model_name}' successfully.")
        except Exception as e:
            print(f"[AI Model] sentence-transformers fallback active ({e}). Using deterministic 384-dim dense vector encoder.")
            self._model = None

    def encode(self, text: str, dim: int = 384) -> List[float]:
        """
        Sinh vector dense chuẩn hóa L2-norm = 1.0 trực tiếp từ mô hình Transformer (FR_AI02).
        Hỗ trợ fallback deterministic cho môi trường không có PyTorch.
        """
        if self._model is not None:
            emb = self._model.encode(text, normalize_embeddings=True)
            return [round(float(x), 5) for x in emb]

        # Deterministic dense embedding fallback (L2-normalized 384-dim)
        import math, hashlib
        vec = [0.0] * dim
        tokens = text.lower().split()
        for token in tokens:
            h = int(hashlib.md5(token.encode('utf-8')).hexdigest(), 16)
            for i in range(16):
                idx = (h >> (i * 8)) % dim
                vec[idx] += 1.0
        norm = math.sqrt(sum(x * x for x in vec)) or 1.0
        return [round(x / norm, 5) for x in vec]
