"""
Định nghĩa các ngoại lệ nghiệp vụ miền (Domain Exceptions)
Bảo đảm tính tường minh và kiểm soát các kịch bản ngoại lệ theo chuẩn ISAD.
"""

class DomainException(Exception):
    """Ngoại lệ cơ sở của Tầng Miền."""
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class OutOfStockException(DomainException):
    """Ngoại lệ ném ra khi ấn bản sách không đủ tồn kho khả dụng (BR02)."""
    def __init__(self, sku: str, requested: int, available: int):
        super().__init__(
            f"Ấn bản SKU '{sku}' không đủ tồn kho khả dụng "
            f"(Yêu cầu: {requested}, Khả dụng trong kho: {available})."
        )
        self.sku = sku
        self.requested = requested
        self.available = available


class EntityNotFoundException(DomainException):
    """Ngoại lệ không tìm thấy thực thể trong hệ thống."""
    def __init__(self, entity_name: str, entity_id: str):
        super().__init__(f"Không tìm thấy {entity_name} với mã '{entity_id}'.")
        self.entity_name = entity_name
        self.entity_id = entity_id


class InvalidOrderStateException(DomainException):
    """Ngoại lệ chuyển trạng thái đơn hàng bất hợp lệ theo máy trạng thái."""
    pass


class ReservationExpiredException(DomainException):
    """Ngoại lệ phiên giữ chỗ tồn kho 15 phút đã hết hạn."""
    pass


class DroneOverweightException(DomainException):
    """Ngoại lệ bưu kiện vượt quá tải trọng bay tối đa của Drone (2kg)."""
    def __init__(self, total_weight_grams: int, max_allowed: int = 2000):
        super().__init__(
            f"Tổng trọng lượng đơn hàng ({total_weight_grams}g) vượt quá tải trọng tối đa "
            f"của Drone ({max_allowed}g). Vui lòng chọn phương thức vận chuyển đường bộ GHN."
        )
        self.total_weight_grams = total_weight_grams
        self.max_allowed = max_allowed
