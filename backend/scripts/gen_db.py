"""
Scripts: gen_db.py
Kịch bản tạo lập CSDL vật lý bookhaven.db chuẩn 100% theo sơ đồ ERD 17 bảng (Figure 4.2).
Bao gồm:
- 250 sách in Fahasa (Manga, Văn học, Công nghệ, Kỹ năng, Kinh tế) + 250 Vector nhúng AI d=384
- 30 mặt hàng Văn phòng phẩm (Stationery) chính hãng Fahasa (Thiên Long, KOKUYO, Pentel, Deli, Moleskine...)
- 20 đồ lưu niệm văn hóa / Manga & Anime Collectibles (Conan, One Piece, Naruto, Ghibli, Jujutsu Kaisen...)
Tổng cộng: 300 sản phẩm (Products) chuẩn Table-per-Subclass.

Sinh viên: Mai Hữu Sơn - MSSV: B23DCAT262
GVHD: PGS. TS. Trần Đình Quế - Học viện Công nghệ Bưu chính Viễn thông (PTIT)
"""
import os
import sys
import sqlite3
import shutil
import json
import bcrypt

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
if BACKEND_DIR not in sys.path:
    sys.path.append(BACKEND_DIR)

DB_DIR = os.path.join(BACKEND_DIR, "db")
DEFAULT_DB_PATH = os.path.join(DB_DIR, "bookhaven.db")
BACKUP_PATH = os.path.join(DB_DIR, "bookhaven_backup_13tables.db")
SCHEMA_PATH = os.path.join(DB_DIR, "schema.sql")

EXPECTED_TABLES = [
    "users",
    "customers",
    "staffs",
    "categories",
    "publishers",
    "authors",
    "products",
    "books",
    "stationeries",
    "collectibles",
    "book_embeddings",
    "carts",
    "cart_items",
    "orders",
    "order_items",
    "payments",
    "stock_reservations",
]

def hash_pw(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt(12)).decode("utf-8")

# 30 MẶT HÀNG VĂN PHÒNG PHẨM FAHASA
STATIONERY_CATALOG = [
    ("SKU_STAT_001", "Bút máy LAMY Safari Charcoal (Ngòi F)", 650000, 18, 50, 0, "Bút máy cao cấp phong cách Bauhaus nhập khẩu Đức ngòi F mượt mà", "/static/covers/stat_lamy.jpg", "LAMY", "Nhựa ABS cao cấp", "Charcoal Black"),
    ("SKU_STAT_002", "Bút máy Pilot Kakuno ngòi F Nhật Bản", 280000, 15, 60, 0, "Bút máy mặt cười dễ thương ngòi êm ái chống tắc mực", "/static/covers/stat_pilot_kakuno.jpg", "Pilot", "Nhựa Resin trong suốt", "Pastel Mint"),
    ("SKU_STAT_003", "Set 10 Bút bi gel Zebra Sarasa Clip 0.5 Vintage", 320000, 130, 80, 0, "Bút bi gel cao cấp 10 màu mực cổ điển kháng nước", "/static/covers/stat_zebra_vintage.jpg", "Zebra", "Nhựa PP đệm cao su", "Vintage 10 Colors"),
    ("SKU_STAT_004", "Bút bi gel xóa được Pilot Frixion Ball 0.5mm", 650000 // 10, 14, 120, 0, "Mực nhiệt biến mất khi ma sát không để lại dấu vết", "/static/covers/stat_frixion.jpg", "Pilot", "Nhựa PP mực nhiệt", "Blue Xanh"),
    ("SKU_STAT_005", "Bút bi cao cấp Thiên Long Bizner BIZ-01 mạ vàng", 180000, 32, 50, 0, "Thân kim loại sơn tĩnh điện cài bút mạ vàng sang trọng", "/static/covers/stat_bizner.jpg", "Thiên Long", "Hợp kim kim loại", "Black & Gold"),
    ("SKU_STAT_006", "Bút lông kim đi nét Marvy Uchida Drawing Pen 0.3", 32000, 11, 150, 0, "Bút vẽ truyện tranh đi nét kỹ thuật mực kháng cồn và nước", "/static/covers/stat_marvy.jpg", "Marvy Uchida", "Nhựa Polypropylene", "Black"),
    ("SKU_STAT_007", "Set 6 Bút dạ quang Pastel Stabilo Boss Original", 175000, 180, 90, 0, "Mực dạ quang gốc nước bảo vệ mắt chống khô đầu bút 4 giờ", "/static/covers/stat_stabilo.jpg", "Stabilo", "Nhựa PP tái chế", "Set 6 Pastel"),
    ("SKU_STAT_008", "Bút dạ quang dạng bấm Pentel Handy-line S SXS15", 42000, 16, 110, 0, "Cơ chế bấm thụt thông minh không cần mở nắp bảo vệ ngòi", "/static/covers/stat_pentel_highlighter.jpg", "Pentel", "Nhựa tái chế 50%", "Fluorescent Yellow"),
    ("SKU_STAT_009", "Bút chì kim kỹ thuật Pentel GraphGear 1000 0.5mm", 260000, 25, 40, 0, "Thân kim loại vân sọc đệm cao su đầu ngòi thụt thông minh", "/static/covers/stat_graphgear.jpg", "Pentel", "Thân nhôm kẹp cao su", "Silver Mờ"),
    ("SKU_STAT_010", "Bút chì kim chống gãy ngòi Tombow Mono Graph 0.5", 95000, 17, 100, 0, "Cơ chế lắc sinh ngòi và gôm tẩy Mono xoay tiện dụng", "/static/covers/stat_tombow_graph.jpg", "Tombow", "Polycarbonate", "Mono Tricolor"),
    ("SKU_STAT_011", "Hộp 12 Bút chì gỗ Staedtler Noris 2B cao cấp", 110000, 85, 70, 0, "Chì than Đức 2B viết êm dễ tẩy ruột chì chống gãy cao", "/static/covers/stat_staedtler.jpg", "Staedtler", "Gỗ tuyết tùng tự nhiên", "Vàng sọc đen"),
    ("SKU_STAT_012", "Sổ tay Moleskine Classic Dotted Hardcover Large (A5)", 480000, 320, 45, 0, "Sổ tay biểu tượng châu Âu giấy Acid-free kẻ chấm bìa cứng", "/static/covers/stat_moleskine.jpg", "Moleskine", "Giấy Acid-free 70gsm", "Black"),
    ("SKU_STAT_013", "Lốc 5 Sổ tay KOKUYO Campus B5 kẻ ngang 80 trang", 145000, 480, 120, 0, "Sổ tay quốc dân giấy tráng phủ mượt mà không lem mực", "/static/covers/stat_campus_b5.jpg", "KOKUYO", "Giấy tráng phủ chống lóa", "Set 5 Pastel"),
    ("SKU_STAT_014", "Sổ tay còng thông minh KOKUYO Smart Ring Binder B5", 125000, 160, 75, 0, "Sổ còng siêu mỏng mở gập 360 độ thay ruột giấy dễ dàng", "/static/covers/stat_smart_ring.jpg", "KOKUYO", "Nhựa PP mờ dẻo dai", "Xanh lam nhạt"),
    ("SKU_STAT_015", "Sổ tay bìa da cao cấp Deli A5 200 trang cài bút", 160000, 290, 65, 0, "Bìa da PU mềm mại giấy vàng kem chống cận định lượng 80gsm", "/static/covers/stat_deli_a5.jpg", "Deli", "Bìa da PU cao cấp", "Nâu Vintage"),
    ("SKU_STAT_016", "Sổ tay lập kế hoạch Planner Midori MD Notebook A5", 340000, 240, 35, 0, "Giấy MD Nhật Bản chuyên biệt cho bút máy không thấm mực", "/static/covers/stat_midori_md.jpg", "Midori", "Giấy MD Cotton Nhật", "Trắng ngà"),
    ("SKU_STAT_017", "Giấy ghi chú Post-it Super Sticky 3M 76x76mm (Set 5)", 135000, 210, 95, 0, "Keo dán chắc gấp 2 lần bám dính trên gỗ tường và kim loại", "/static/covers/stat_postit.jpg", "3M Post-it", "Giấy bám dính đa bề mặt", "Neon 5 màu"),
    ("SKU_STAT_018", "Thước kẻ đồng thau Midori Brass Ruler 15cm", 220000, 35, 50, 0, "Đồng thau nguyên khối cổ điển số đo khắc laser chuẩn xác", "/static/covers/stat_midori_ruler.jpg", "Midori", "Đồng thau nguyên khối", "Vàng Vintage"),
    ("SKU_STAT_019", "Thước nhôm kỹ thuật Deli 30cm đế cao su chống trượt", 45000, 60, 130, 0, "Vạch chia khắc laser đế cao su bám giấy không bị xê dịch", "/static/covers/stat_deli_ruler.jpg", "Deli", "Hợp kim nhôm siêu nhẹ", "Bạc nhôm mờ"),
    ("SKU_STAT_020", "Set 3 Gôm tẩy bút chì Tombow Mono PE-04A", 42000, 55, 200, 0, "Gôm tẩy sạch không làm rách giấy bụi gom dính gọn gàng", "/static/covers/stat_mono_pe04.jpg", "Tombow", "Nhựa Vinyl cao cấp", "Trắng Mono"),
    ("SKU_STAT_021", "Gôm tẩy dạng bút bấm Pentel Clic Eraser ZE32", 48000, 22, 110, 0, "Thân bút bấm gôm tròn 5mm tẩy chi tiết chính xác", "/static/covers/stat_pentel_eraser.jpg", "Pentel", "Nhựa Polycarbonate", "Xanh trong suốt"),
    ("SKU_STAT_022", "Băng xóa kéo Plus Whiper MR 5mm x 6m (Kèm 1 lõi)", 52000, 38, 140, 0, "Băng xóa màng polymer mỏng dai viết êm ngay lập tức", "/static/covers/stat_plus_whiper.jpg", "Plus", "Polymer che phủ cao", "Xanh lá Green"),
    ("SKU_STAT_023", "Kéo cắt giấy chống dính Plus Fitcut Curve SC-175SF", 78000, 75, 85, 0, "Lưỡi kéo cong Bernoulli cắt nhẹ bén phủ Fluorine chống keo", "/static/covers/stat_plus_scissors.jpg", "Plus", "Thép không gỉ Fluorine", "Trắng xanh"),
    ("SKU_STAT_024", "Máy bấm kim số 10 Deli kèm 1000 kim bấm", 55000, 95, 120, 0, "Khung thép cán nguội bấm nhẹ gập gọn cho học sinh văn phòng", "/static/covers/stat_deli_stapler.jpg", "Deli", "Thép bọc nhựa ABS", "Đen Black"),
    ("SKU_STAT_025", "Dao rọc giấy mini tự khóa Olfa SVR-1 thép không gỉ", 145000, 32, 60, 0, "Lưỡi thép siêu bén tự khóa an toàn chuyên nghiệp Nhật Bản", "/static/covers/stat_olfa.jpg", "Olfa", "Thép không gỉ mạ bóng", "Bạc Stainless"),
    ("SKU_STAT_026", "Hộp 12 Kẹp bướm kim loại Thiên Long 25mm", 28000, 65, 180, 0, "Kẹp giữ tài liệu chắc chắn sơn tĩnh điện chống rỉ sét", "/static/covers/stat_thienlong_clip.jpg", "Thiên Long", "Thép lò xo đàn hồi", "Đen bóng"),
    ("SKU_STAT_027", "Bảng kẹp tài liệu A4 KOKUYO Clipboard nhựa cứng", 65000, 180, 90, 0, "Nhựa ABS siêu bền kẹp giữ tài liệu chắc chắn có móc treo", "/static/covers/stat_kokuyo_board.jpg", "KOKUYO", "Nhựa ABS đúc khối", "Xanh than Navy"),
    ("SKU_STAT_028", "Giá đỡ đọc sách gỗ thông tự nhiên BookHaven Stand", 290000, 680, 35, 0, "Điều chỉnh 5 nấc độ nghiêng giải phóng đôi tay bảo vệ cổ gáy", "/static/covers/stat_stand.jpg", "BookHaven Wood", "Gỗ thông tự nhiên", "Màu gỗ mộc"),
    ("SKU_STAT_029", "Đèn LED đọc sách kẹp gáy BookHaven EyeCare USB", 185000, 95, 50, 0, "3 chế độ màu ấm sáng dịu pin sạc 1000mAh kẹp êm ái", "/static/covers/stat_lamp.jpg", "BookHaven Gear", "Nhựa ABS & Nhôm dẻo", "Trắng Matte"),
    ("SKU_STAT_030", "Túi bọc sách da PU cao cấp BookHaven Book Sleeve A5", 160000, 85, 75, 0, "Chống trầy chống nước lót nhung mềm mại vừa vặn sách A5", "/static/covers/stat_sleeve.jpg", "BookHaven Gear", "Da PU cao cấp lót nhung", "Nâu Cà phê"),
]

# 20 MẶT HÀNG ĐỒ LƯU NIỆM / MANGA COLLECTIBLES FAHASA
COLLECTIBLE_CATALOG = [
    ("SKU_COLL_001", "Mô hình đứng Acrylic Thám tử Conan Edogawa (TMS)", 150000, 45, 60, 0, "Bản quyền chính hãng TMS Entertainment chân đế mica vững chắc", "/static/covers/coll_conan.jpg", "Nhật Bản (TMS)", "Mica Acrylic cao cấp in UV", "Cao 15cm x Dày 4mm"),
    ("SKU_COLL_002", "Mô hình đứng Acrylic Kaito Kid Ánh Trăng", 160000, 50, 55, 0, "Siêu đạo chích Kaito Kid tung tà áo choàng trắng dưới trăng", "/static/covers/coll_kid.jpg", "Nhật Bản (TMS)", "Mica Acrylic hiệu ứng bóng", "Cao 16cm x Dày 4mm"),
    ("SKU_COLL_003", "Mô hình đứng Acrylic Gojo Satoru Chú Thuật Hồi Chiến", 170000, 52, 70, 0, "Thầy Gojo thi triển Vô Lượng Không Xứ phản quang huyền ảo", "/static/covers/coll_gojo.jpg", "Nhật Bản (MAPPA)", "Mica Acrylic Hologram", "Cao 17cm x Rộng 8cm"),
    ("SKU_COLL_004", "Mô hình đứng Acrylic Anya Forger & Loid (Spy x Family)", 165000, 48, 65, 0, "Cô bé Anya biểu cảm ngộ nghĩnh bên cạnh ba Loid lịch lãm", "/static/covers/coll_anya.jpg", "Nhật Bản (Wit Studio)", "Mica Acrylic đế đôi", "Cao 14cm x Dày 4mm"),
    ("SKU_COLL_005", "Mô hình Chibi Naruto Uzumaki Cửu Vĩ Rasengan (Bandai)", 380000, 220, 25, 0, "Mô hình đúc đặc sơn tay sắc nét tạo hình tuyệt chiêu Rasengan", "/static/covers/coll_naruto.jpg", "Bandai Spirits JP", "Nhựa PVC đúc đặc sơn tay", "Cao 10cm x Rộng 7cm"),
    ("SKU_COLL_006", "Mô hình Chibi Monkey D. Luffy Gear 5 Nika Banpresto", 420000, 250, 20, 0, "Luffy Thần Mặt Trời tóc mây trắng cười thả ga phong cách Nika", "/static/covers/coll_luffy_g5.jpg", "Banpresto Toei JP", "Nhựa PVC & ABS cao cấp", "Cao 12cm x Rộng 9cm"),
    ("SKU_COLL_007", "Mô hình Doraemon Cửa Thần Kỳ Kỷ Niệm 50 Năm", 320000, 260, 30, 0, "Doraemon bước qua cánh cửa hồng thần kỳ đầy xúc động", "/static/covers/coll_doraemon.jpg", "Fujiko Pro JP", "Nhựa PVC & Resin bóng", "14cm x 12cm x 8cm"),
    ("SKU_COLL_008", "Bookmark kim loại mạ vàng Mũ Rơm Luffy (One Piece)", 95000, 20, 150, 0, "Mạ vàng 18K chạm khắc laser biểu tượng cướp biển Mũ Rơm", "/static/covers/coll_luffy_bm.jpg", "Toei Animation JP", "Hợp kim đồng mạ vàng 18K", "12cm x 4.5cm"),
    ("SKU_COLL_009", "Bookmark kim loại mạ bạc Trái Snitch Vàng (Harry Potter)", 135000, 28, 90, 0, "Cánh dang rộng mạ bạc ánh kim tinh tế cho tín đồ Hogwarts", "/static/covers/coll_snitch.jpg", "Wizarding World UK", "Hợp kim kẽm mạ bạc", "9.5cm x 6cm"),
    ("SKU_COLL_010", "Bookmark kim loại khắc laser Cỏ Ba Lá May Mắn BookHaven", 75000, 18, 120, 0, "Đồng thau chạm lộng hoa văn cổ điển kèm dây tua rua xanh", "/static/covers/coll_clover.jpg", "BookHaven Craft VN", "Đồng thau nguyên tấm", "10cm x 3.5cm"),
    ("SKU_COLL_011", "Set 4 Bookmark nam châm Manga Demon Slayer Tanjiro", 65000, 35, 140, 0, "Kẹp sách nam châm 4 nhân vật Tanjiro, Nezuko, Zenitsu, Inosuke", "/static/covers/coll_kny_bm.jpg", "Aniplex JP", "Nam châm dẻo phủ bóng", "6cm x 2cm mỗi cái"),
    ("SKU_COLL_012", "Túi Canvas Totoro Dạo Phố Ghibli Eco Tote Bag", 195000, 180, 80, 0, "Vải bố dệt thô dày dặn quai đeo vai êm ái in hình Totoro che dù", "/static/covers/coll_totoro_tote.jpg", "Studio Ghibli JP", "Vải Canvas 12oz dệt thô", "38cm x 42cm"),
    ("SKU_COLL_013", "Túi Canvas Thám tử Conan Silhouette Kudo Shinichi", 185000, 175, 75, 0, "Thiết kế bóng lưng Kudo Shinichi in nhũ bạc tinh tế trên nền đen", "/static/covers/coll_conan_tote.jpg", "TMS Animation JP", "Vải Canvas đen dày 10oz", "36cm x 40cm"),
    ("SKU_COLL_014", "Móc khóa Thanh kiếm Diệt Quỷ Nichirin Tanjiro 1:12", 85000, 50, 110, 0, "Thanh kiếm thu nhỏ bằng kim loại có thể rút bao kiếm mượt mà", "/static/covers/coll_sword_tanjiro.jpg", "Aniplex JP", "Hợp kim kẽm đúc nguyên khối", "Dài 17cm"),
    ("SKU_COLL_015", "Móc khóa phi tiêu Kunai Ninja Naruto hợp kim kẽm", 75000, 42, 95, 0, "Vũ khí ninja trứ danh chuôi quấn vải đỏ phong trần", "/static/covers/coll_kunai.jpg", "Pierrot JP", "Hợp kim kẽm phủ đen nhám", "Dài 13.5cm"),
    ("SKU_COLL_016", "Huy hiệu Enamel Pin Đội Thám tử Nhí Detective Boys", 65000, 18, 140, 0, "Huy hiệu đính áo mô phỏng máy bộ đàm truyền tin của nhóm bạn", "/static/covers/coll_badge_db.jpg", "TMS Animation JP", "Kim loại dập nổi tráng men", "Đường kính 3.5cm"),
    ("SKU_COLL_017", "Huy hiệu Trinh Sát Đoàn Survey Corps (Attack on Titan)", 70000, 20, 100, 0, "Biểu tượng Đôi Cánh Tự Do tráng men xanh hải quân dũng mãnh", "/static/covers/coll_aot_pin.jpg", "Kodansha JP", "Hợp kim tráng men cứng", "3.8cm x 2.8cm"),
    ("SKU_COLL_018", "Bộ 16 Bưu thiếp Nghệ thuật Spirited Away (Studio Ghibli)", 140000, 160, 40, 0, "16 khung hình kinh điển đoạt giải Oscar đóng hộp thiếc lưu niệm", "/static/covers/coll_spirited_cards.jpg", "Studio Ghibli Official", "Giấy mỹ thuật 350gsm", "10cm x 15cm"),
    ("SKU_COLL_019", "Bộ 20 Thẻ sưu tầm Hologram Jujutsu Kaisen Special Box", 180000, 90, 50, 0, "Thẻ bo góc phủ màng lấp lánh ánh kim nhân vật Chú Thuật", "/static/covers/coll_jjk_cards.jpg", "MAPPA Official", "Nhựa PET phủ Hologram 3D", "6.3cm x 8.8cm"),
    ("SKU_COLL_020", "Huy hiệu tráng men BookHaven Limited 'Reader Crown'", 55000, 15, 200, 0, "Huy hiệu độc quyền dành cho độc giả xuất sắc của BookHaven", "/static/covers/coll_bookhaven_pin.jpg", "BookHaven Studio VN", "Hợp kim mạ vàng tráng men", "3cm x 2.8cm"),
]

def generate_full_database(db_path: str = DEFAULT_DB_PATH):
    print(f"=== BẮT ĐẦU TẠO LẬP CSDL BOOKHAVEN 17 BẢNG TẠI: {db_path} ===")
    
    # 1. Khởi tạo schema từ schema.sql
    if os.path.exists(db_path):
        os.remove(db_path)
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON;")
    cur = conn.cursor()
    
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        cur.executescript(f.read())
    conn.commit()
    print("[1/6] Đã khởi tạo cấu trúc 17 bảng từ schema.sql.")
    
    # 2. Đọc dữ liệu sách gốc từ backup
    if not os.path.exists(BACKUP_PATH):
        raise FileNotFoundError(f"Không tìm thấy file backup dữ liệu sách: {BACKUP_PATH}")
        
    old_conn = sqlite3.connect(BACKUP_PATH)
    old_conn.row_factory = sqlite3.Row
    old_cur = old_conn.cursor()
    
    old_users = old_cur.execute("SELECT * FROM users").fetchall()
    old_categories = old_cur.execute("SELECT * FROM categories").fetchall()
    old_publishers = old_cur.execute("SELECT * FROM publishers").fetchall()
    old_authors = old_cur.execute("SELECT * FROM authors").fetchall()
    old_books = old_cur.execute("SELECT * FROM books").fetchall()
    old_editions = old_cur.execute("SELECT * FROM book_editions").fetchall()
    old_embeddings = old_cur.execute("SELECT * FROM book_embeddings").fetchall()
    old_orders = old_cur.execute("SELECT * FROM orders").fetchall()
    old_order_items = old_cur.execute("SELECT * FROM order_items").fetchall()
    old_payments = old_cur.execute("SELECT * FROM payments").fetchall()
    old_reservations = old_cur.execute("SELECT * FROM stock_reservations").fetchall()
    old_conn.close()
    
    # 3. Nạp Users, Customers, Staffs
    user_id_map = {}
    for u in old_users:
        cur.execute("""
            INSERT INTO users (username, password_hash, email, full_name, phone, role, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (u['username'], u['password_hash'], u['email'], u['full_name'], u['phone'], u['role'], u['created_at']))
        new_uid = cur.lastrowid
        user_id_map[u['user_id']] = new_uid
        
        if u['role'] == 'CUSTOMER':
            cur.execute("""
                INSERT INTO customers (user_id, shipping_address, loyalty_points)
                VALUES (?, ?, ?)
            """, (new_uid, u['shipping_address'] or "Số 10 Phạm Văn Đồng, Cầu Giấy, Hà Nội", u['loyalty_points'] or 120))
        else:
            cur.execute("""
                INSERT INTO staffs (user_id, staff_role, department)
                VALUES (?, ?, ?)
            """, (new_uid, u['staff_role'] or f"{u['role']} Lead", u['department'] or "Quản trị Hệ thống"))
    print(f"[2/6] Đã nạp {len(old_users)} tài khoản Users, Customers, Staffs.")
    
    # 4. Nạp Thể loại (5 cũ + 2 mới)
    cat_id_map = {}
    for c in old_categories:
        cur.execute("""
            INSERT INTO categories (category_name, description, slug, created_at)
            VALUES (?, ?, ?, ?)
        """, (c['category_name'], c['description'], c['slug'], c['created_at']))
        cat_id_map[c['category_id']] = cur.lastrowid
        
    cur.execute("""
        INSERT INTO categories (category_name, description, slug)
        VALUES ('Văn phòng phẩm & Dụng cụ học tập', 'Bút ký, sổ tay, thước kẻ, gôm tẩy và phụ kiện đọc sách chính hãng Fahasa.', 'van-phong-pham-dung-cu')
    """)
    cat_stat_id = cur.lastrowid
    
    cur.execute("""
        INSERT INTO categories (category_name, description, slug)
        VALUES ('Đồ lưu niệm & Quà tặng Manga/Anime', 'Mô hình nhân vật, standee acrylic, bookmark mạ vàng, túi canvas và huy hiệu.', 'do-luu-niem-manga-anime')
    """)
    cat_coll_id = cur.lastrowid
    
    # Nạp Nhà xuất bản & Tác giả
    pub_id_map = {}
    for p in old_publishers:
        cur.execute("""
            INSERT INTO publishers (publisher_name, address, contact_email, phone, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (p['publisher_name'], p['address'], p['contact_email'], p['phone'], p['created_at']))
        pub_id_map[p['publisher_id']] = cur.lastrowid
        
    author_id_map = {}
    for a in old_authors:
        cur.execute("""
            INSERT INTO authors (author_name, biography, nationality, created_at)
            VALUES (?, ?, ?, ?)
        """, (a['author_name'], a['biography'], a['nationality'], a['created_at']))
        author_id_map[a['author_id']] = cur.lastrowid
    print(f"[3/6] Đã nạp 7 Categories, {len(old_publishers)} Publishers, {len(old_authors)} Authors.")
    
    # 5. Nạp 250 SÁCH THẬT FAHASA VÀO PRODUCTS & BOOKS
    old_books_by_id = {b['book_id']: b for b in old_books}
    old_embeddings_by_book = {e['book_id']: e for e in old_embeddings}
    edition_to_product_map = {}
    
    for ed in old_editions:
        bk = old_books_by_id.get(ed['book_id'])
        if not bk:
            continue
        new_cat_id = cat_id_map.get(bk['category_id'])
        new_author_id = author_id_map.get(bk['author_id'])
        new_pub_id = pub_id_map.get(bk['publisher_id'])
        
        cur.execute("""
            INSERT INTO products (category_id, sku, name, unit_price, weight_gram, stock_on_hand, stock_reserved, description, cover_image, is_active, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            new_cat_id,
            ed['sku'],
            bk['title'],
            ed['unit_price'],
            ed['weight_gram'],
            ed['stock_on_hand'],
            ed['stock_reserved'],
            bk['description'],
            bk['cover_image'],
            bk['is_active'],
            ed['created_at']
        ))
        new_pid = cur.lastrowid
        edition_to_product_map[ed['edition_id']] = new_pid
        
        cur.execute("""
            INSERT INTO books (product_id, isbn13, author_id, publisher_id, publish_year, binding_type)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            new_pid,
            ed['isbn13'],
            new_author_id,
            new_pub_id,
            bk['publish_year'] or 2024,
            ed['binding_type']
        ))
        
        emb = old_embeddings_by_book.get(bk['book_id'])
        if emb:
            cur.execute("""
                INSERT INTO book_embeddings (product_id, vector_json, model_name, created_at)
                VALUES (?, ?, ?, ?)
            """, (new_pid, emb['vector_json'], emb['model_name'], emb['created_at']))
    print(f"[4/6] Đã nạp thành công 250 Sách in Fahasa kèm 250 Vector nhúng AI d=384.")
    
    # 6. Nạp 30 VĂN PHÒNG PHẨM & 20 ĐỒ LƯU NIỆM
    for sku, name, price, weight, stock, reserved, desc, img, brand, material, color in STATIONERY_CATALOG:
        cur.execute("""
            INSERT INTO products (category_id, sku, name, unit_price, weight_gram, stock_on_hand, stock_reserved, description, cover_image, is_active)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
        """, (cat_stat_id, sku, name, price, weight, stock, reserved, desc, img))
        stat_pid = cur.lastrowid
        cur.execute("""
            INSERT INTO stationeries (product_id, brand, material, color)
            VALUES (?, ?, ?, ?)
        """, (stat_pid, brand, material, color))
    print(f"[5/6] Đã nạp thành công 30 mặt hàng Văn phòng phẩm chính hãng.")
    
    for sku, name, price, weight, stock, reserved, desc, img, origin, material, dims in COLLECTIBLE_CATALOG:
        cur.execute("""
            INSERT INTO products (category_id, sku, name, unit_price, weight_gram, stock_on_hand, stock_reserved, description, cover_image, is_active)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
        """, (cat_coll_id, sku, name, price, weight, stock, reserved, desc, img))
        coll_pid = cur.lastrowid
        cur.execute("""
            INSERT INTO collectibles (product_id, origin, material, dimensions)
            VALUES (?, ?, ?, ?)
        """, (coll_pid, origin, material, dims))
    print(f"[6/6] Đã nạp thành công 20 đồ lưu niệm / Manga Anime Collectibles.")
    
    # 7. Nạp Giỏ hàng & Đơn hàng mẫu
    cur.execute("SELECT user_id FROM customers")
    customers = [r[0] for r in cur.fetchall()]
    
    sample_book_id = 1
    sample_stat_id = 251
    sample_coll_id = 281
    
    for cust_id in customers:
        cur.execute("INSERT INTO carts (customer_id) VALUES (?)", (cust_id,))
        cart_id = cur.lastrowid
        if cust_id == customers[0]:
            cur.execute("INSERT INTO cart_items (cart_id, product_id, quantity) VALUES (?, ?, 2)", (cart_id, sample_book_id))
            cur.execute("INSERT INTO cart_items (cart_id, product_id, quantity) VALUES (?, ?, 1)", (cart_id, sample_stat_id))
            cur.execute("INSERT INTO cart_items (cart_id, product_id, quantity) VALUES (?, ?, 1)", (cart_id, sample_coll_id))
            
    order_id_map = {}
    for o in old_orders:
        new_cust_id = user_id_map.get(o['customer_id'], customers[0])
        carrier = 'HANOI_DRONE_EXPRESS' if 'DRONE' in o['carrier'] else 'GHN'
        cur.execute("""
            INSERT INTO orders (customer_id, receiver_name, receiver_phone, shipping_address, payment_method, carrier, tracking_code, total_amount, shipping_fee, discount_amount, final_amount, status, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            new_cust_id, o['receiver_name'], o['receiver_phone'], o['shipping_address'],
            o['payment_method'], carrier, o['tracking_code'], o['total_amount'],
            o['shipping_fee'], o['discount_amount'], o['final_amount'], o['status'],
            o['created_at'], o['updated_at']
        ))
        order_id_map[o['order_id']] = cur.lastrowid
        
    for oi in old_order_items:
        new_oid = order_id_map.get(oi['order_id'])
        new_pid = edition_to_product_map.get(oi['edition_id'])
        if new_oid and new_pid:
            cur.execute("""
                INSERT INTO order_items (order_id, product_id, product_name_snapshot, sku_snapshot, product_kind_snapshot, unit_price_at_purchase, quantity, weight_gram_snapshot, created_at)
                VALUES (?, ?, ?, ?, 'BOOK', ?, ?, ?, ?)
            """, (
                new_oid, new_pid, oi['title_snapshot'], oi['sku_snapshot'],
                oi['unit_price_at_purchase'], oi['quantity'], oi['weight_gram_snapshot'], oi['created_at']
            ))
            
    for p in old_payments:
        new_oid = order_id_map.get(p['order_id'])
        if new_oid:
            cur.execute("""
                INSERT INTO payments (order_id, payment_method, amount, transaction_code, status, paid_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (new_oid, p['payment_method'], p['amount'], p['transaction_code'], p['status'], p['paid_at']))
            
    for r in old_reservations:
        new_oid = order_id_map.get(r['order_id'])
        new_pid = edition_to_product_map.get(r['edition_id'])
        if new_oid and new_pid:
            cur.execute("""
                INSERT INTO stock_reservations (order_id, product_id, reserved_quantity, expires_at, status, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (new_oid, new_pid, r['reserved_quantity'], r['expires_at'], r['status'], r['created_at']))
            
    conn.commit()
    conn.close()
    print("=== TẠO LẬP CSDL HOÀN TẤT THÀNH CÔNG 100%! ===")

if __name__ == "__main__":
    generate_full_database()
