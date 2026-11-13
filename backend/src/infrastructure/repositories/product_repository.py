"""
Infrastructure Repository: ProductRepository
Bao bọc truy vấn danh mục sản phẩm đa hình (Products, Books, Stationeries, Collectibles).
Khớp 100% với Hình 4.4.
"""
from src.infrastructure.repositories.book_repository import BookRepository

ProductRepository = BookRepository
