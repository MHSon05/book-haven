"""
Legacy Compatibility Module: BookEdition -> Book
Ánh xạ tương thích ngược từ BookEdition sang lớp Book mới kế thừa từ Product.
"""
from src.domain.entities.book import Book

BookEdition = Book
