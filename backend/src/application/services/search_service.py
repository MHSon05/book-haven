"""
Application Service: SearchService
Điều phối Tìm kiếm Từ khóa (SQL), Tìm kiếm Ngữ nghĩa AI (Dense Vector) và Tìm kiếm bằng Ảnh bìa (dHash).
Khớp 100% với Chương 3 và 4 trong Báo cáo Thiết kế BookHaven.
"""
import json
import os
import unicodedata
from typing import List, Dict, Any, Optional
from ...infrastructure.repositories.book_repository import BookRepository
from ...infrastructure.adapters.sentence_transformer_adapter import SentenceTransformerAdapter
from ...infrastructure.adapters.image_hasher import ImageHasher
from ..dtos.models import SearchResponse, SearchResultItem

VIETNAMESE_STOPWORDS = {
    "và", "của", "những", "các", "thì", "là", "mà", "cho", "với", "được", "bị", "bởi",
    "trong", "trên", "tại", "đến", "từ", "ở", "ra", "vào", "lại", "đã", "đang", "sẽ",
    "như", "để", "về", "rằng", "một", "có", "này", "kia", "đó", "gì", "nào", "sao",
    "rất", "quá", "lắm", "thế", "ấy", "hãy", "nữa", "khi", "nhưng", "hay", "hoặc",
    "nhau", "cùng", "qua", "mang", "theo", "mỗi", "từng", "lên", "xuống", "luôn"
}

# Bảng quy đổi chuẩn hóa vị trí đặt dấu thanh tiếng Việt (kiểu mới sang quy chuẩn thống nhất)
VIETNAMESE_TONE_MAP = {
    'oà': 'òa', 'oá': 'óa', 'oả': 'ỏa', 'oã': 'õa', 'oạ': 'ọa',
    'oè': 'òe', 'oé': 'óe', 'oẻ': 'ỏe', 'oẽ': 'õe', 'oẹ': 'ọe',
    'uỳ': 'ùy', 'uý': 'úy', 'uỷ': 'ủy', 'uỹ': 'ũy', 'uỵ': 'ụy',
}

def normalize_vietnamese_tones(text: str) -> str:
    """Chuẩn hóa vị trí đặt dấu thanh tiếng Việt về quy chuẩn thống nhất (NFC)."""
    if not text:
        return ""
    text = unicodedata.normalize('NFC', text.lower())
    for k, v in VIETNAMESE_TONE_MAP.items():
        text = text.replace(k, v)
    return text

class SearchService:
    def __init__(
        self,
        book_repo: BookRepository,
        transformer_adapter: Optional[SentenceTransformerAdapter] = None,
        image_hasher: Optional[ImageHasher] = None
    ):
        self.book_repo = book_repo
        self.transformer = transformer_adapter or SentenceTransformerAdapter()
        self.hasher = image_hasher or ImageHasher()
        self._cover_hashes_cache: Dict[str, str] = {}

    def search_keyword(
        self,
        keyword: str,
        category_id: Optional[str] = None,
        binding_type: Optional[str] = None,
        limit: int = 20
    ) -> SearchResponse:
        """Tìm kiếm từ khóa chuẩn xác qua SQL LIKE kết hợp lọc danh mục và quy cách bìa."""
        raw_items = self.book_repo.search_books_sql(keyword, category_id, binding_type, limit)
        
        # Nhóm theo book_id để lấy min/max price và tổng tồn kho
        books_map: Dict[str, Dict[str, Any]] = {}
        for row in raw_items:
            bid = row["book_id"]
            if bid not in books_map:
                books_map[bid] = {
                    "book_id": bid,
                    "title": row["title"],
                    "author_name": row["author_name"],
                    "publisher_name": row["publisher_name"],
                    "category_id": row.get("category_id"),
                    "category_name": row["category_name"],
                    "description": row["description"] or "",
                    "cover_image": row["cover_image"],
                    "min_price": row["unit_price"],
                    "max_price": row["unit_price"],
                    "available_stock": max(0, row["available_stock"] or 0),
                    "similarity_score": 1.0,
                    "explanation_snippet": None
                }
            else:
                b = books_map[bid]
                b["min_price"] = min(b["min_price"], row["unit_price"])
                b["max_price"] = max(b["max_price"], row["unit_price"])
                b["available_stock"] += max(0, row["available_stock"] or 0)

        results = [SearchResultItem(**item) for item in books_map.values()]
        return SearchResponse(
            total_found=len(results),
            search_mode="keyword_sql",
            results=results
        )

    def search_semantic(self, query: str, limit: int = 5, min_threshold: float = 0.35) -> SearchResponse:
        """
        Tìm kiếm ngữ nghĩa AI kết hợp Hybrid Matching & Chuẩn hóa Tiếng Việt:
        1. Biến đổi câu truy vấn thành dense vector 384 chiều và tính Cosine Similarity.
        2. Chuẩn hóa vị trí đặt dấu thanh tiếng Việt (mới/cũ) để so khớp chính xác.
        3. Khớp cụm từ nguyên câu (Exact Phrase) & cụm 2 từ (Bi-grams).
        4. Lọc nhiễu đa ngôn ngữ (chặn các sách rác không chứa cụm từ truy vấn).
        """
        if not query or not query.strip():
            return SearchResponse(total_found=0, search_mode="semantic_ai", results=[])

        query_clean = unicodedata.normalize('NFC', query.strip())
        query_norm = normalize_vietnamese_tones(query_clean)
        query_vec = self.transformer.encode(query_clean)
        all_embeddings = self.book_repo.get_all_embeddings()

        raw_words = [w for w in query_norm.replace(",", " ").replace(".", " ").replace(";", " ").replace("!", " ").replace("?", " ").split() if w]
        content_words = [w for w in raw_words if w not in VIETNAMESE_STOPWORDS]

        # Tạo danh sách cụm 2 từ liền kề (Bi-grams) loại trừ từ nối stopwords thuần túy
        bigrams = []
        for i in range(len(raw_words) - 1):
            w1, w2 = raw_words[i], raw_words[i+1]
            if (w1 not in VIETNAMESE_STOPWORDS or w2 not in VIETNAMESE_STOPWORDS) and len(w1) > 1 and len(w2) > 1:
                bigrams.append(f"{w1} {w2}")

        scored_books = []
        for item in all_embeddings:
            book_id = item["book_id"]
            vec_json = item["vector_json"]
            title = item.get("title", "")
            desc = item.get("description", "")
            try:
                doc_vec = json.loads(vec_json)
            except Exception:
                continue

            # Dot product của 2 vector đã chuẩn hóa L2 chính là Cosine Similarity
            cos_sim = sum(q * d for q, d in zip(query_vec, doc_vec))

            # Chuẩn hóa văn bản sách
            t_norm = normalize_vietnamese_tones(title)
            d_norm = normalize_vietnamese_tones(desc)
            full_text = f"{t_norm} {d_norm}"

            bonus = 0.0

            # 1. Trùng khớp toàn bộ câu truy vấn (Exact Phrase Match)
            if len(query_norm) >= 3 and query_norm in full_text:
                bonus += 0.60
                if query_norm in t_norm:
                    bonus += 0.30

            # 2. Trùng khớp cụm 2 từ liền kề có nghĩa (Bi-grams Match)
            matched_bigrams = [bg for bg in bigrams if bg in full_text]
            if matched_bigrams:
                bonus += 0.40 * min(len(matched_bigrams), 4)
                for bg in matched_bigrams:
                    if bg in t_norm:
                        bonus += 0.20

            # 3. Độ bao phủ từ khóa nội dung có nghĩa (Content Words Coverage)
            matched_content = [w for w in content_words if w in full_text]
            coverage_ratio = len(matched_content) / max(1, len(content_words))
            if coverage_ratio >= 0.5:
                bonus += 0.30 * coverage_ratio

            # 4. Lọc chuẩn xác khắt khe (Precision Filtering):
            # Với câu mô tả dài (>= 4 từ): bắt buộc phải khớp ít nhất 1 cụm từ có nghĩa (bigram)
            # HOẶC có độ bao phủ content words >= 40%. Nếu không, coi là không liên quan và loại bỏ.
            if len(raw_words) >= 4:
                if not matched_bigrams and coverage_ratio < 0.4:
                    continue
            # Với câu ngắn (2-3 từ): loại bỏ sách không khớp cụm từ nào và không có từ có nghĩa
            elif len(raw_words) >= 2:
                if not matched_bigrams and coverage_ratio == 0 and cos_sim < 0.58:
                    continue

            hybrid_score = cos_sim + bonus

            # Ngưỡng chất lượng tối thiểu nâng cao (tăng chuẩn xác)
            if hybrid_score >= 0.60 or cos_sim >= 0.60:
                scored_books.append((book_id, hybrid_score, cos_sim))

        # Sắp xếp giảm dần theo điểm tương đồng
        scored_books.sort(key=lambda x: x[1], reverse=True)

        # 5. Dynamic Gap Filter: Nếu cuốn đứng đầu đạt độ tin cậy rất cao (>= 1.2),
        # tự động gạt bỏ các sách có điểm số quá thấp (< 65% điểm của cuốn top 1)
        # để không làm loãng kết quả với những sách không liên quan.
        if scored_books:
            top_score = scored_books[0][1]
            if top_score >= 1.2:
                cutoff = top_score * 0.65
                scored_books = [x for x in scored_books if x[1] >= cutoff]

        top_candidates = scored_books[:limit]

        results = []
        for bid, h_score, c_sim in top_candidates:
            book = self.book_repo.get_book_entity_by_id(bid)
            if not book or not book.is_searchable() or not book.editions:
                continue

            min_p = book.min_price()
            max_p = book.max_price()
            total_avail = book.total_available_stock()

            # Rút trích câu tóm tắt liên quan ngữ nghĩa
            desc = book.description or ""
            explanation = f"Độ tương đồng cốt truyện: {min(99, int(h_score * 100))}%. " + (desc[:120] + "..." if len(desc) > 120 else desc)

            results.append(SearchResultItem(
                book_id=bid,
                title=book.title,
                author_name=book.author_name or "",
                publisher_name=book.publisher_name or "",
                category_id=book.category_id,
                category_name=book.category_name or "",
                description=desc,
                cover_image=book.cover_image,
                min_price=min_p,
                max_price=max_p,
                available_stock=total_avail,
                similarity_score=round(float(c_sim), 4),
                explanation_snippet=explanation
            ))

        return SearchResponse(
            total_found=len(results),
            search_mode="semantic_ai",
            results=results
        )

    def search_by_image(self, image_bytes: bytes, base_static_path: Optional[str] = None) -> SearchResponse:
        """
        Tìm kiếm bằng hình ảnh bìa (Perceptual Image Hash - dHash).
        So khớp mã băm thị giác với kho ảnh sách tĩnh trong hệ thống.
        """
        if not image_bytes:
            return SearchResponse(total_found=0, search_mode="visual_dhash", results=[])

        # Đảm bảo cache dHash của toàn bộ danh mục sách hiện có (250+ sách)
        all_books = self.book_repo.get_all_books(limit=500)
        known_hashes = {}

        for b in all_books:
            bid = b["book_id"]
            cover_path = b.get("cover_image")
            if not cover_path:
                continue

            # Nếu đã lưu cache thì lấy ra
            if bid in self._cover_hashes_cache:
                known_hashes[bid] = self._cover_hashes_cache[bid]
                continue

            # Đọc file ảnh bìa từ thư mục static
            full_path = None
            clean_cover_path = cover_path.lstrip("/")
            if clean_cover_path.startswith("static/"):
                clean_cover_path = clean_cover_path[len("static/"):]

            if base_static_path:
                candidate = os.path.join(base_static_path, clean_cover_path)
                if os.path.exists(candidate):
                    full_path = candidate

            if not full_path and os.path.exists(cover_path):
                full_path = cover_path
            elif not full_path and os.path.exists(clean_cover_path):
                full_path = clean_cover_path

            if full_path and os.path.isfile(full_path):
                try:
                    with open(full_path, "rb") as f:
                        h = self.hasher.compute_dhash(f.read())
                        self._cover_hashes_cache[bid] = h
                        known_hashes[bid] = h
                except Exception:
                    pass

        # So khớp
        best_id, confidence = self.hasher.match_cover(image_bytes, known_hashes, max_distance_threshold=24)
        if not best_id:
            return SearchResponse(total_found=0, search_mode="visual_dhash", results=[])

        book = self.book_repo.get_book_entity_by_id(best_id)
        if not book or not book.is_searchable():
            return SearchResponse(total_found=0, search_mode="visual_dhash", results=[])

        res_item = SearchResultItem(
            book_id=best_id,
            title=book.title,
            author_name=book.author_name or "",
            publisher_name=book.publisher_name or "",
            category_id=book.category_id,
            category_name=book.category_name or "",
            description=book.description or "",
            cover_image=book.cover_image,
            min_price=book.min_price(),
            max_price=book.max_price(),
            available_stock=book.total_available_stock(),
            similarity_score=round(confidence / 100.0, 3),
            explanation_snippet=f"Đã khớp ảnh bìa chính xác (Độ tin cậy: {confidence}%)"
        )

        return SearchResponse(
            total_found=1,
            search_mode="visual_dhash",
            results=[res_item]
        )
