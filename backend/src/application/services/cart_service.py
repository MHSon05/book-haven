"""
Application Service: CartService
Điều phối các nghiệp vụ giỏ hàng của độc giả: xem, thêm, sửa số lượng, xóa và làm rỗng.
"""
from ...domain.entities.cart import Cart
from ...domain.exceptions import EntityNotFoundException, OutOfStockException
from ...infrastructure.repositories.cart_repository import CartRepository
from ...infrastructure.repositories.book_repository import BookRepository
from ..dtos.models import CartResponse, CartItemDTO

class CartService:
    def __init__(self, cart_repo: CartRepository, book_repo: BookRepository):
        self.cart_repo = cart_repo
        self.book_repo = book_repo

    def get_cart(self, customer_id: str) -> CartResponse:
        cart = self.cart_repo.get_or_create_cart(customer_id)
        return self._to_cart_response(cart)

    def add_to_cart(self, customer_id: str, edition_id: str, quantity: int = 1) -> CartResponse:
        if quantity <= 0:
            raise ValueError("Số lượng thêm vào giỏ phải lớn hơn 0.")

        edition = self.book_repo.get_edition_by_id(edition_id)
        if not edition:
            raise EntityNotFoundException("BookEdition", edition_id)

        cart = self.cart_repo.get_or_create_cart(customer_id)
        current_in_cart = cart.items[edition_id].quantity if edition_id in cart.items else 0
        new_total_quantity = current_in_cart + quantity

        # Kiểm tra tồn kho khả dụng (BR02)
        if new_total_quantity > edition.available_stock():
            raise OutOfStockException(
                sku=edition.sku,
                requested=new_total_quantity,
                available=edition.available_stock()
            )

        cart.add_item(edition, quantity)
        self.cart_repo.save_item(cart.cart_id, edition_id, cart.items[edition_id].quantity)
        # Nạp lại giỏ hàng đầy đủ
        refreshed_cart = self.cart_repo.get_cart_by_id(cart.cart_id)
        return self._to_cart_response(refreshed_cart)

    def update_quantity(self, customer_id: str, edition_id: str, quantity: int) -> CartResponse:
        cart = self.cart_repo.get_or_create_cart(customer_id)
        if edition_id not in cart.items:
            raise EntityNotFoundException("CartItem", edition_id)

        if quantity <= 0:
            return self.remove_item(customer_id, edition_id)

        edition = self.book_repo.get_edition_by_id(edition_id)
        if not edition:
            raise EntityNotFoundException("BookEdition", edition_id)

        if quantity > edition.available_stock():
            raise OutOfStockException(
                sku=edition.sku,
                requested=quantity,
                available=edition.available_stock()
            )

        cart.update_quantity(edition_id, quantity)
        self.cart_repo.save_item(cart.cart_id, edition_id, quantity)
        refreshed_cart = self.cart_repo.get_cart_by_id(cart.cart_id)
        return self._to_cart_response(refreshed_cart)

    def remove_item(self, customer_id: str, edition_id: str) -> CartResponse:
        cart = self.cart_repo.get_or_create_cart(customer_id)
        self.cart_repo.remove_item(cart.cart_id, edition_id)
        refreshed_cart = self.cart_repo.get_cart_by_id(cart.cart_id)
        return self._to_cart_response(refreshed_cart)

    def clear_cart(self, customer_id: str) -> CartResponse:
        cart = self.cart_repo.get_or_create_cart(customer_id)
        self.cart_repo.clear_cart(cart.cart_id)
        refreshed_cart = self.cart_repo.get_cart_by_id(cart.cart_id)
        return self._to_cart_response(refreshed_cart)

    def _to_cart_response(self, cart: Cart) -> CartResponse:
        items_dtos = []
        for eid, item in cart.items.items():
            edition = item.edition
            if not edition:
                continue
            items_dtos.append(CartItemDTO(
                cart_item_id=item.cart_item_id,
                edition_id=edition.edition_id,
                book_id=edition.book_id,
                title=edition.title or "Sách",
                sku=edition.sku,
                binding_type=edition.binding_type,
                isbn13=edition.isbn13,
                unit_price=edition.unit_price,
                weight_gram=edition.weight_gram,
                quantity=item.quantity,
                subtotal=item.subtotal(),
                cover_image=edition.cover_image,
                available_stock=edition.available_stock()
            ))

        return CartResponse(
            cart_id=cart.cart_id,
            customer_id=cart.customer_id,
            subtotal=cart.calculate_subtotal(),
            total_weight_grams=cart.calculate_total_weight_grams(),
            items=items_dtos
        )
