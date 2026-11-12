"""
BookHaven Comprehensive Backend Integration Test Suite
Kiểm thử tự động toàn diện: Auth, Catalog, Tìm kiếm Đa phương thức (SQL/Vector/dHash),
Giỏ hàng, Ràng buộc Drone tải trọng 2000g, Checkout 10 bước Transaction,
Nút Xác nhận Chuyển khoản thật, Webhook ngân hàng, Background Worker 15 phút, và Quản trị Admin.
"""
import os
import sys
import pytest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient

# Thêm đường dẫn project
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(ROOT_DIR)

from main import app
from src.infrastructure.database import DatabaseSession
from src.infrastructure.repositories.book_repository import BookRepository
from src.infrastructure.repositories.order_repository import OrderRepository
from src.infrastructure.repositories.cart_repository import CartRepository
from src.application.services.inventory_service import InventoryService

client = TestClient(app)

def _get_admin_headers():
    login_res = client.post("/api/auth/login", json={"username": "admin", "password": "admin123"})
    return {"Authorization": f"Bearer {login_res.json()['access_token']}"}

def _get_sample_edition_id() -> str:
    session = DatabaseSession()
    conn = session.get_connection()
    row = conn.execute("SELECT edition_id FROM book_editions WHERE weight_gram <= 600 AND stock_on_hand > 5 LIMIT 1;").fetchone()
    if not row:
        row = conn.execute("SELECT edition_id FROM book_editions LIMIT 1;").fetchone()
    return row["edition_id"]


# ==================== 1. KIỂM THỬ TRẠNG THÁI HỆ THỐNG & FRONTEND SPA ====================
def test_system_status():
    # 1. API Status JSON endpoint
    api_resp = client.get("/api/status")
    assert api_resp.status_code == 200
    data = api_resp.json()
    assert data["system"] == "BookHaven E-Commerce API"
    assert data["author"] == "Mai Hữu Sơn - B23DCAT262"
    assert data["status"] == "Operational"

    # 2. Root SPA serves React 18 index.html
    root_resp = client.get("/")
    assert root_resp.status_code == 200
    assert "BookHaven" in root_resp.text
    assert 'id="root"' in root_resp.text

    # 3. SPA Fallback (HTML5 History Mode - e.g. /admin, /orders, /checkout)
    admin_spa_resp = client.get("/admin")
    assert admin_spa_resp.status_code == 200
    assert 'id="root"' in admin_spa_resp.text

    # 4. Unknown API endpoint returns 404 JSON, NOT index.html
    bad_api_resp = client.get("/api/nonexistent_test_route")
    assert bad_api_resp.status_code == 404
    assert bad_api_resp.headers["content-type"].startswith("application/json")

def test_frontend_static_assets():
    # React SPA Assets & Entrypoint
    root_res = client.get("/")
    assert root_res.status_code == 200
    assert "/assets/" in root_res.text

    # Static Book Cover Image
    covers_dir = os.path.join(ROOT_DIR, "assets", "covers")
    if os.path.exists(covers_dir):
        files = [f for f in os.listdir(covers_dir) if f.startswith("book_")]
        if files:
            img_res = client.get(f"/static/covers/{files[0]}")
            assert img_res.status_code == 200
            assert img_res.headers["content-type"].startswith("image/")


# ==================== 2. KIỂM THỬ XÁC THỰC (REAL AUTH & RBAC) ====================
def test_auth_login_customer():
    # Đăng nhập tài khoản người dùng duy nhất
    response = client.post("/api/auth/login", json={"username": "user", "password": "user123"})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["username"] == "user"
    assert data["full_name"] == "Người Dùng BookHaven"
    assert data["role"] == "CUSTOMER"

    token = data["access_token"]
    # Kiểm tra endpoint /api/auth/me với Bearer Token
    profile_res = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert profile_res.status_code == 200
    profile_data = profile_res.json()
    assert profile_data["email"] == "user@bookhaven.vn"
    assert "Hà Đông" in profile_data["shipping_address"]

def test_auth_login_admin():
    response = client.post("/api/auth/login", json={"username": "admin", "password": "admin123"})
    assert response.status_code == 200
    data = response.json()
    assert data["role"] == "ADMIN"
    assert data["username"] == "admin"

def test_auth_invalid_password():
    response = client.post("/api/auth/login", json={"username": "user", "password": "wrong_password"})
    assert response.status_code == 401
    assert "không chính xác" in response.json()["detail"]


# ==================== 3. KIỂM THỬ DANH MỤC & ẤN BẢN (CATALOG & EDITIONS) ====================
def test_catalog_list_and_editions():
    # Lấy danh sách sách
    res = client.get("/api/books")
    assert res.status_code == 200
    data = res.json()
    assert data["total"] > 0

    first_book_id = data["books"][0]["book_id"]
    detail_res = client.get(f"/api/books/{first_book_id}")
    assert detail_res.status_code == 200
    book = detail_res.json()
    assert "title" in book
    assert len(book["editions"]) >= 1

    first_ed = book["editions"][0]
    assert first_ed["unit_price"] > 0
    assert first_ed["weight_gram"] > 0
    assert first_ed["available_stock"] >= 0

def test_categories_list():
    res = client.get("/api/categories")
    assert res.status_code == 200
    cats = res.json()["categories"]
    assert len(cats) >= 4
    cat_names = [c["category_name"] for c in cats]
    assert any("Văn học" in n or "Khoa học" in n or "Kinh tế" in n or "Manga" in n for n in cat_names)


# ==================== 4. KIỂM THỬ TÌM KIẾM ĐA PHƯƠNG THỨC ====================
def test_search_keyword_sql():
    books_res = client.get("/api/books?limit=1")
    first_book = books_res.json()["books"][0]
    sample_word = first_book["title"].split()[0]
    res = client.get(f"/api/search/keyword?q={sample_word}")
    assert res.status_code == 200
    data = res.json()
    assert data["search_mode"] == "keyword_sql"
    assert data["total_found"] >= 1
    assert any(sample_word.lower() in item["title"].lower() for item in data["results"])

def test_search_semantic_ai():
    # Tìm kiếm theo ngữ nghĩa
    res = client.post("/api/search/semantic", json={"query": "truyện tranh phiêu lưu hài hước", "limit": 3})
    assert res.status_code == 200
    data = res.json()
    assert data["search_mode"] == "semantic_ai"
    assert "results" in data

def test_search_image_visual():
    covers_dir = os.path.join(ROOT_DIR, "assets", "covers")
    if os.path.exists(covers_dir):
        files = [f for f in os.listdir(covers_dir) if f.startswith("book_")]
        if files:
            cover_path = os.path.join(covers_dir, files[0])
            with open(cover_path, "rb") as f:
                res = client.post("/api/search/image", files={"file": ("cover.jpg", f, "image/jpeg")})
            assert res.status_code == 200
            data = res.json()
            assert data["search_mode"] == "visual_dhash"
            assert data["total_found"] >= 1


# ==================== 5. KIỂM THỬ RÀNG BUỘC TẢI TRỌNG DRONE 2000G ====================
def test_drone_weight_options_and_invariant():
    customer_id = "USER_USER"
    cart_id = "CART_USER_USER"
    session = DatabaseSession()
    cart_repo = CartRepository(session)
    sample_eid = _get_sample_edition_id()

    # 1. Trường hợp hợp lệ: Giỏ chỉ có 1 cuốn sách nhẹ
    cart_repo.clear_cart(cart_id)
    cart_repo.save_item(cart_id, sample_eid, 1)

    opt_res = client.get(f"/api/shipping/options?cart_id={cart_id}")
    assert opt_res.status_code == 200
    options_data = opt_res.json()
    drone_opt = next(o for o in options_data["options"] if o["carrier_code"] == "HANOI_DRONE")
    assert drone_opt["is_available"] is True
    assert drone_opt["fee"] == 60000

    # 2. Trường hợp quá tải trọng: Thêm 15 cuốn
    cart_repo.save_item(cart_id, sample_eid, 15)
    opt_overweight_res = client.get(f"/api/shipping/options?cart_id={cart_id}")
    overweight_data = opt_overweight_res.json()
    drone_opt_overweight = next(o for o in overweight_data["options"] if o["carrier_code"] == "HANOI_DRONE")
    assert drone_opt_overweight["is_available"] is False
    assert "vượt quá tải trọng bay tối đa của Drone (2.000g)" in drone_opt_overweight["disabled_reason"]

    # 3. Cố tình gửi lệnh Checkout với Drone khi giỏ bị quá cân -> Phải trả về HTTP 400 DroneOverweightException
    checkout_payload = {
        "cart_id": cart_id,
        "receiver_name": "Mai Hữu Sơn",
        "receiver_phone": "0987654321",
        "shipping_address": "PTIT Hà Đông, Hà Nội",
        "payment_method": "VIETQR",
        "carrier": "HANOI_DRONE"
    }
    bad_res = client.post("/api/checkout", headers={"x-customer-id": customer_id}, json=checkout_payload)
    assert bad_res.status_code == 400
    assert "vượt quá tải trọng tối đa của Drone" in bad_res.json()["detail"]
    cart_repo.clear_cart(cart_id)


# ==================== 6. KIỂM THỬ CHECKOUT 10 BƯỚC TRANSACTION ====================
def _create_sample_checkout_order() -> str:
    customer_id = "USER_USER"
    cart_id = "CART_USER_USER"
    session = DatabaseSession()
    cart_repo = CartRepository(session)
    book_repo = BookRepository(session)
    sample_eid = _get_sample_edition_id()

    cart_repo.clear_cart(cart_id)
    cart_repo.save_item(cart_id, sample_eid, 1)

    ed = book_repo.get_edition_by_id(sample_eid)
    if ed and ed.available_stock() < 5:
        ed.stock_on_hand = max(ed.stock_on_hand, 50)
        ed.stock_reserved = 0
        book_repo.update_edition_stock(ed)

    checkout_payload = {
        "cart_id": cart_id,
        "receiver_name": "Mai Hữu Sơn",
        "receiver_phone": "0987654321",
        "shipping_address": "Học viện CNBCVT (PTIT), Km10 Nguyễn Trãi, Hà Đông",
        "payment_method": "VIETQR",
        "carrier": "HANOI_DRONE",
        "voucher_code": "VOUCHER10"  # Giảm 10%
    }

    res = client.post(
        "/api/checkout",
        headers={"x-customer-id": customer_id},
        json=checkout_payload
    )
    assert res.status_code == 200
    order = res.json()
    return order["order_id"]

def test_atomic_checkout_success():
    customer_id = "USER_USER"
    cart_id = "CART_USER_USER"
    session = DatabaseSession()
    cart_repo = CartRepository(session)
    book_repo = BookRepository(session)
    sample_eid = _get_sample_edition_id()

    cart_repo.clear_cart(cart_id)
    cart_repo.save_item(cart_id, sample_eid, 1)

    initial_edition = book_repo.get_edition_by_id(sample_eid)
    if initial_edition.available_stock() < 5:
        initial_edition.stock_on_hand = max(initial_edition.stock_on_hand, 50)
        initial_edition.stock_reserved = 0
        book_repo.update_edition_stock(initial_edition)

    initial_avail = initial_edition.available_stock()
    initial_reserved = initial_edition.stock_reserved

    checkout_payload = {
        "cart_id": cart_id,
        "receiver_name": "Mai Hữu Sơn",
        "receiver_phone": "0987654321",
        "shipping_address": "Học viện CNBCVT (PTIT), Km10 Nguyễn Trãi, Hà Đông",
        "payment_method": "VIETQR",
        "carrier": "HANOI_DRONE",
        "voucher_code": "VOUCHER10"
    }

    res = client.post(
        "/api/checkout",
        headers={"x-customer-id": customer_id},
        json=checkout_payload
    )
    assert res.status_code == 200
    order = res.json()

    assert order["status"] == "AWAITING_PAYMENT"
    assert order["carrier"] == "HANOI_DRONE"
    assert order["shipping_fee"] == 60000
    assert order["discount_amount"] > 0
    assert "vietqr_data" in order
    assert "qr_url" in order["vietqr_data"]
    assert "NHA SACH BOOKHAVEN" in order["vietqr_data"]["account_name"]
    assert order["reservation_expires_at"] is not None

    # Kiểm tra Invariant giữ chỗ trong CSDL:
    updated_edition = book_repo.get_edition_by_id(sample_eid)
    assert updated_edition.stock_reserved == initial_reserved + 1
    assert updated_edition.available_stock() == initial_avail - 1

    # Kiểm tra giỏ hàng đã được làm rỗng
    refreshed_cart = cart_repo.get_cart_by_id(cart_id)
    assert len(refreshed_cart.items) == 0


# ==================== 7. KIỂM THỬ XÁC NHẬN THANH TOÁN THẬT (REAL BUTTON) ====================
def test_real_payment_confirmation():
    session = DatabaseSession()
    book_repo = BookRepository(session)
    sample_eid = _get_sample_edition_id()

    edition_before = book_repo.get_edition_by_id(sample_eid)
    hand_before = edition_before.stock_on_hand
    reserved_before = edition_before.stock_reserved

    # Đặt một đơn hàng mới
    order_id = _create_sample_checkout_order()

    # Khách hàng bấm nút thật: [Tôi đã chuyển khoản thành công]
    confirm_res = client.post("/api/payments/confirm", json={"order_id": order_id, "transaction_code": "MBB_TEST_CONFIRM"})
    assert confirm_res.status_code == 200
    data = confirm_res.json()
    assert data["status"] == "PAID"

    # Kiểm tra trừ kho chính thức (confirm_deduction: cả stock_on_hand và stock_reserved đều giảm 1)
    edition_after = book_repo.get_edition_by_id(sample_eid)
    assert edition_after.stock_on_hand == hand_before - 1

    # Kiểm tra bản ghi thanh toán payments
    row = session.get_connection().execute("SELECT * FROM payments WHERE order_id = ?;", (order_id,)).fetchone()
    assert row is not None
    assert row["status"] == "SUCCESS"
    assert row["payment_method"] == "VIETQR"


# ==================== 8. KIỂM THỬ WEBHOOK NGÂN HÀNG TỰ ĐỘNG ====================
def test_bank_webhook_payment():
    order_id = _create_sample_checkout_order()
    session = DatabaseSession()
    order_repo = OrderRepository(session)
    order = order_repo.get_order_by_id(order_id)

    # Giả lập Webhook MBBank/VietQR bắn về
    webhook_payload = {
        "content": f"Chuyen tien mua sach don {order_id}",
        "amount": order.final_amount,
        "transaction_id": "AUTO_WEBHOOK_9999"
    }

    wh_res = client.post("/api/payments/webhook", json=webhook_payload)
    assert wh_res.status_code == 200
    wh_data = wh_res.json()
    assert wh_data["status"] == "success"
    assert wh_data["data"]["status"] == "PAID"

    # Kiểm tra trạng thái đơn hàng đã sang PAID
    refreshed_order = order_repo.get_order_by_id(order_id)
    assert refreshed_order.status.value == "PAID"


# ==================== 9. KIỂM THỬ BACKGROUND WORKER GIẢI PHÓNG HẾT HẠN 15 PHÚT ====================
def test_background_worker_expired_reservation():
    order_id = _create_sample_checkout_order()
    session = DatabaseSession()
    book_repo = BookRepository(session)
    order_repo = OrderRepository(session)
    sample_eid = _get_sample_edition_id()

    edition_before = book_repo.get_edition_by_id(sample_eid)
    reserved_before = edition_before.stock_reserved

    # Can thiệp thời gian hết hạn của bản ghi giữ chỗ về quá khứ (cách đây 20 phút)
    past_time = (datetime.now() - timedelta(minutes=20)).isoformat()
    session.get_connection().execute(
        "UPDATE stock_reservations SET expires_at = ? WHERE order_id = ?;",
        (past_time, order_id)
    )

    # Kích hoạt worker dọn dẹp
    inv_service = InventoryService(session, book_repo, order_repo)
    released_count = inv_service.cleanup_expired_reservations()
    assert released_count >= 1

    # Kiểm tra tồn giữ chỗ đã được hoàn trả (stock_reserved giảm ít nhất 1)
    edition_after = book_repo.get_edition_by_id(sample_eid)
    assert edition_after.stock_reserved <= reserved_before - 1

    # Đơn hàng quá hạn chưa thanh toán phải chuyển thành CANCELLED
    canceled_order = order_repo.get_order_by_id(order_id)
    assert canceled_order.status.value == "CANCELLED"


# ==================== 10. KIỂM THỬ QUẢN TRỊ ADMIN (DISPATCH, RESTOCK, REVENUE) ====================
def test_admin_dispatch_and_reports():
    admin_headers = _get_admin_headers()
    sample_eid = _get_sample_edition_id()

    # 1. Đặt và thanh toán 1 đơn hàng
    order_id = _create_sample_checkout_order()
    client.post("/api/payments/confirm", json={"order_id": order_id})

    # 2. Admin bàn giao đơn hàng cho Hanoi Drone
    dispatch_res = client.post(
        f"/api/admin/orders/{order_id}/dispatch",
        headers=admin_headers,
        json={"carrier": "HANOI_DRONE"}
    )
    assert dispatch_res.status_code == 200
    dispatched_order = dispatch_res.json()
    assert dispatched_order["status"] == "SHIPPING"
    assert dispatched_order["carrier"] == "HANOI_DRONE"
    assert dispatched_order["tracking_code"].startswith("DRONE-HN-")

    # 3. Giao hàng thành công
    delivered_res = client.post(f"/api/admin/orders/{order_id}/delivered", headers=admin_headers)
    assert delivered_res.status_code == 200
    assert delivered_res.json()["status"] == "DELIVERED"

    # 4. Thủ kho nhập thêm 20 cuốn
    restock_res = client.post(
        "/api/admin/inventory/restock",
        headers=admin_headers,
        json={"edition_id": sample_eid, "quantity": 20}
    )
    assert restock_res.status_code == 200
    assert "Nhập kho thành công +20 cuốn" in restock_res.json()["message"]

    # 5. Xem báo cáo doanh thu thực thu (BR06)
    rev_res = client.get("/api/admin/reports/revenue", headers=admin_headers)
    assert rev_res.status_code == 200
    rev_data = rev_res.json()
    assert rev_data["total_revenue"] > 0
    assert rev_data["paid_orders_count"] > 0
    assert len(rev_data["top_books"]) > 0
    assert "total_items_sold" in rev_data


def test_drone_cod_checkout_and_status_flow():
    """Kiểm thử luồng giao Drone với hình thức COD: đảm bảo không bị rơi về GHN và get_order_status hoạt động chuẩn."""
    customer_id = "USER_USER"
    cart_id = "CART_USER_USER"
    session = DatabaseSession()
    cart_repo = CartRepository(session)
    book_repo = BookRepository(session)
    sample_eid = _get_sample_edition_id()

    cart_repo.clear_cart(cart_id)
    cart_repo.save_item(cart_id, sample_eid, 1)

    ed = book_repo.get_edition_by_id(sample_eid)
    if ed and ed.available_stock() < 5:
        ed.stock_on_hand = max(ed.stock_on_hand, 50)
        ed.stock_reserved = 0
        book_repo.update_edition_stock(ed)

    # 1. Ràng buộc nghiệp vụ: Đặt hàng với Drone + COD phải bị từ chối
    bad_payload = {
        "cart_id": cart_id,
        "receiver_name": "Mai Hữu Sơn",
        "receiver_phone": "0987654321",
        "shipping_address": "PTIT Km10 Nguyễn Trãi, Hà Đông",
        "payment_method": "COD",
        "carrier": "HANOI_DRONE"
    }
    bad_res = client.post(
        "/api/checkout",
        headers={"x-customer-id": customer_id},
        json=bad_payload
    )
    assert bad_res.status_code == 400
    assert "Drone không hỗ trợ thanh toán tiền mặt (COD)" in bad_res.json()["detail"]

    # 2. Đặt hàng hợp lệ với Drone + VIETQR
    checkout_payload = {
        "cart_id": cart_id,
        "receiver_name": "Mai Hữu Sơn",
        "receiver_phone": "0987654321",
        "shipping_address": "PTIT Km10 Nguyễn Trãi, Hà Đông",
        "payment_method": "VIETQR",
        "carrier": "HANOI_DRONE"
    }
    checkout_res = client.post(
        "/api/checkout",
        headers={"x-customer-id": customer_id},
        json=checkout_payload
    )
    assert checkout_res.status_code == 200
    order_data = checkout_res.json()
    order_id = order_data["order_id"]
    assert order_data["carrier"] == "HANOI_DRONE"
    assert order_data["status"] == "AWAITING_PAYMENT"
    assert order_data["payment_method"] == "VIETQR"
    assert order_data["shipping_fee"] == 60000

    # Xác nhận thanh toán VietQR thành công
    client.post("/api/payments/confirm", json={"order_id": order_id, "transaction_code": "MBB_DRONE_TEST"})

    # 3. Kiểm tra API GET /api/orders/{order_id}/status
    status_res = client.get(f"/api/orders/{order_id}/status")
    assert status_res.status_code == 200
    status_data = status_res.json()
    assert status_data["order_id"] == order_id
    assert status_data["carrier"] == "HANOI_DRONE"
    assert status_data["payment_method"] == "VIETQR"
    assert status_data["status"] == "PAID"
    assert len(status_data["items"]) == 1
    assert status_data["items"][0]["unit_price"] > 0
    assert status_data["items"][0]["weight_gram"] > 0

    # 3. Admin điều phối bàn giao Drone
    dispatch_res = client.post(
        f"/api/admin/orders/{order_id}/dispatch",
        headers=_get_admin_headers(),
        json={"carrier": "HANOI_DRONE"}
    )
    assert dispatch_res.status_code == 200
    dispatched = dispatch_res.json()
    assert dispatched["status"] == "SHIPPING"
    assert dispatched["carrier"] == "HANOI_DRONE"
    assert dispatched["tracking_code"].startswith("DRONE-HN-")

    # 4. Giao hàng thành công và tự động khấu trừ kho COD
    deliver_res = client.post(f"/api/orders/{order_id}/delivered")
    assert deliver_res.status_code == 200
    assert deliver_res.json()["status"] == "DELIVERED"


# ==================== 11. KIỂM THỬ TRỢ LÝ ẢO AI CHATBOT (RAG GROUNDING BR08 & INTENT) ====================
def test_chatbot_rag_service():
    res = client.post("/api/chatbot/message", json={"message": "Tôi muốn tìm sách về lập trình và công nghệ"})
    assert res.status_code == 200
    chat_data = res.json()
    assert "reply" in chat_data
    assert len(chat_data["reply"]) > 5

def test_chatbot_technical_model_identity():
    """Kiểm thử chatbot trả lời danh tính kỹ thuật (Meta LLaMA 3.1) và không đính kèm sách rác."""
    res = client.post("/api/chatbot/message", json={"message": "bạn là mô hình nào"})
    assert res.status_code == 200
    chat_data = res.json()
    assert "reply" in chat_data
    assert any(k in chat_data["reply"].lower() for k in ["llama", "bookie", "mô hình"])
    assert len(chat_data["suggested_books"]) == 0

def test_chatbot_drone_policy_inquiry():
    """Kiểm thử chatbot giải đáp chính sách giao Drone mà không đính kèm thẻ sách ngẫu nhiên."""
    res = client.post("/api/chatbot/message", json={"message": "shop có giao drone không"})
    assert res.status_code == 200
    chat_data = res.json()
    assert "reply" in chat_data
    assert any(k in chat_data["reply"].lower() for k in ["drone", "máy bay", "2kg", "60.000"])
    assert len(chat_data["suggested_books"]) == 0
