"""
Infrastructure Adapter: ImageHasher
So khớp thị giác ảnh bìa sách (Perceptual Image Hash - dHash) sử dụng thư viện Pillow (FR08).
Chạy offline 100%, phản hồi < 5ms.
"""
import io
from PIL import Image
from typing import Tuple, Optional, Dict

class ImageHasher:
    @staticmethod
    def compute_dhash(image_bytes: bytes, hash_size: int = 8) -> str:
        """
        Tính Difference Hash (dHash) của ảnh tải lên:
        Chuyển ảnh về grayscale kích thước (hash_size + 1, hash_size),
        so sánh các pixel liền kề để sinh chuỗi nhị phân 64-bit.
        """
        img = Image.open(io.BytesIO(image_bytes)).convert("L")
        img = img.resize((hash_size + 1, hash_size), Image.Resampling.LANCZOS)
        try:
            pixels = list(img.get_flattened_data())
        except AttributeError:
            pixels = list(img.getdata())

        difference = []
        for row in range(hash_size):
            for col in range(hash_size):
                pixel_left = pixels[row * (hash_size + 1) + col]
                pixel_right = pixels[row * (hash_size + 1) + col + 1]
                difference.append("1" if pixel_left > pixel_right else "0")

        return "".join(difference)

    @staticmethod
    def hamming_distance(hash1: str, hash2: str) -> int:
        """Đo số lượng bit khác biệt giữa 2 mã băm ảnh."""
        if len(hash1) != len(hash2):
            return 64
        return sum(c1 != c2 for c1, c2 in zip(hash1, hash2))

    @classmethod
    def match_cover(
        cls,
        uploaded_bytes: bytes,
        known_covers: Dict[str, str],  # book_id -> image_hash
        max_distance_threshold: int = 24
    ) -> Tuple[Optional[str], float]:
        """
        Tìm cuốn sách có ảnh bìa khớp nhất.
        Trả về (book_id, confidence_score_0_to_1).
        """
        if not uploaded_bytes:
            return None, 0.0

        try:
            target_hash = cls.compute_dhash(uploaded_bytes)
        except Exception:
            return None, 0.0

        best_book_id = None
        min_dist = 65

        for book_id, cover_hash in known_covers.items():
            dist = cls.hamming_distance(target_hash, cover_hash)
            if dist < min_dist:
                min_dist = dist
                best_book_id = book_id

        if min_dist <= max_distance_threshold and best_book_id is not None:
            confidence = max(0.0, min(1.0, 1.0 - (min_dist / 64.0)))
            return best_book_id, round(confidence * 100, 1)

        return None, 0.0
