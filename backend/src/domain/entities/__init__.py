"""
Domain Entities Package
Chứa đủ 17 lớp thực thể miền tương ứng 100% với Hình 4.3 (Design Class Diagram) và Hình 4.4.
Mỗi lớp tương ứng với đúng 1 file riêng biệt. KHÔNG sử dụng Enum.
"""
from src.domain.entities.product import Product
from src.domain.entities.book import Book
from src.domain.entities.stationery import Stationery
from src.domain.entities.collectible import Collectible
from src.domain.entities.category import Category
from src.domain.entities.publisher import Publisher
from src.domain.entities.author import Author
from src.domain.entities.book_embedding import BookEmbedding
from src.domain.entities.user import User
from src.domain.entities.customer import Customer
from src.domain.entities.staff import Staff
from src.domain.entities.cart import Cart
from src.domain.entities.cart_item import CartItem
from src.domain.entities.order import Order
from src.domain.entities.order_item import OrderItem
from src.domain.entities.payment import Payment
from src.domain.entities.stock_reservation import StockReservation

__all__ = [
    "Product",
    "Book",
    "Stationery",
    "Collectible",
    "Category",
    "Publisher",
    "Author",
    "BookEmbedding",
    "User",
    "Customer",
    "Staff",
    "Cart",
    "CartItem",
    "Order",
    "OrderItem",
    "Payment",
    "StockReservation",
]
