"""
Migration & Seeding Script: migrate_to_17_tables.py
Migrates the existing 13-table SQLite database to the 17-table ERD architecture:
- users (base) -> customers & staffs
- products (abstract superclass) -> books, stationeries, collectibles
- book_embeddings (linked to books.product_id)
- carts & cart_items (linked to products.product_id)
- orders & order_items (snapshots + product_id)
- payments & stock_reservations
"""
import os
import sys
import sqlite3
import shutil
import json

BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DB_DIR = os.path.join(BACKEND_DIR, "db")
DB_PATH = os.path.join(DB_DIR, "bookhaven.db")
BACKUP_PATH = os.path.join(DB_DIR, "bookhaven_backup_13tables.db")
SCHEMA_PATH = os.path.join(DB_DIR, "schema.sql")

def migrate():
    print(f"Starting migration to 17-table ERD architecture on {DB_PATH}...")
    
    if not os.path.exists(DB_PATH):
        print(f"Error: Database {DB_PATH} does not exist!")
        return

    # 1. Backup old database
    if not os.path.exists(BACKUP_PATH):
        print(f"Backing up old 13-table database to: {BACKUP_PATH}...")
        shutil.copy2(DB_PATH, BACKUP_PATH)
    else:
        print(f"Backup already exists at: {BACKUP_PATH}")

    old_conn = sqlite3.connect(BACKUP_PATH)
    old_conn.row_factory = sqlite3.Row
    old_cur = old_conn.cursor()

    # Load existing data
    print("Reading legacy records from backup...")
    old_users = old_cur.execute("SELECT * FROM users").fetchall()
    old_authors = old_cur.execute("SELECT * FROM authors").fetchall()
    old_publishers = old_cur.execute("SELECT * FROM publishers").fetchall()
    old_categories = old_cur.execute("SELECT * FROM categories").fetchall()
    old_books = old_cur.execute("SELECT * FROM books").fetchall()
    old_editions = old_cur.execute("SELECT * FROM book_editions").fetchall()
    old_embeddings = old_cur.execute("SELECT * FROM book_embeddings").fetchall()
    old_orders = old_cur.execute("SELECT * FROM orders").fetchall()
    old_order_items = old_cur.execute("SELECT * FROM order_items").fetchall()
    old_reservations = old_cur.execute("SELECT * FROM stock_reservations").fetchall()
    old_payments = old_cur.execute("SELECT * FROM payments").fetchall()
    print(f"Found {len(old_books)} books, {len(old_editions)} editions, {len(old_embeddings)} embeddings, {len(old_orders)} orders.")

    old_conn.close()

    # 2. Reset and recreate DB with 17 tables from schema.sql
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    cur = conn.cursor()

    print(f"Executing schema from {SCHEMA_PATH}...")
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        schema_sql = f.read()
    cur.executescript(schema_sql)
    conn.commit()
    print("17 tables created successfully.")

    # 3. Migrate Users, Customers, Staffs
    print("Migrating Users, Customers, Staffs...")
    user_id_map = {} # old_id -> new_id
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
            """, (new_uid, u['shipping_address'] or "Ha Noi, Viet Nam", u['loyalty_points'] or 0))
        else:
            cur.execute("""
                INSERT INTO staffs (user_id, staff_role, department)
                VALUES (?, ?, ?)
            """, (new_uid, u['staff_role'] or f"{u['role']} Operations", u['department'] or "Administration"))

    # 4. Migrate Categories
    print("Migrating Categories...")
    category_id_map = {} # old_cat_id -> new_cat_id
    for c in old_categories:
        cur.execute("""
            INSERT INTO categories (category_name, description, slug, created_at)
            VALUES (?, ?, ?, ?)
        """, (c['category_name'], c['description'], c['slug'], c['created_at']))
        category_id_map[c['category_id']] = cur.lastrowid

    # Add 2 new categories for Stationery and Collectibles
    cur.execute("""
        INSERT INTO categories (category_name, description, slug)
        VALUES ('Văn phòng phẩm & Quà tặng', 'Bút ký cao cấp, sổ tay, thước kẻ và dụng cụ học tập chính hãng.', 'van-phong-pham')
    """)
    cat_stat_id = cur.lastrowid

    cur.execute("""
        INSERT INTO categories (category_name, description, slug)
        VALUES ('Đồ sưu tầm & Phụ kiện Manga', 'Mô hình nhân vật, bookmark kim loại, huy hiệu và túi canvas.', 'do-suu-tam-anime')
    """)
    cat_coll_id = cur.lastrowid

    # 5. Migrate Publishers & Authors
    print("Migrating Publishers and Authors...")
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

    # Map old book_id -> old book record
    old_books_by_id = {b['book_id']: b for b in old_books}
    old_embeddings_by_book = {e['book_id']: e for e in old_embeddings}

    # 6. Migrate Products and Books (250 titles)
    print("Migrating 250 Books into Products & Books tables...")
    edition_to_product_map = {} # old_edition_id -> new_product_id
    book_to_product_map = {}    # old_book_id -> new_product_id

    for ed in old_editions:
        bk = old_books_by_id.get(ed['book_id'])
        if not bk:
            continue
            
        new_cat_id = category_id_map.get(bk['category_id'])
        new_author_id = author_id_map.get(bk['author_id'])
        new_pub_id = pub_id_map.get(bk['publisher_id'])

        # Insert superclass Product
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
        new_product_id = cur.lastrowid
        edition_to_product_map[ed['edition_id']] = new_product_id
        book_to_product_map[bk['book_id']] = new_product_id

        # Insert subclass Book
        cur.execute("""
            INSERT INTO books (product_id, isbn13, author_id, publisher_id, publish_year, binding_type)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            new_product_id,
            ed['isbn13'],
            new_author_id,
            new_pub_id,
            bk['publish_year'] or 2024,
            ed['binding_type']
        ))

        # Insert BookEmbedding
        emb = old_embeddings_by_book.get(bk['book_id'])
        if emb:
            cur.execute("""
                INSERT INTO book_embeddings (product_id, vector_json, model_name, created_at)
                VALUES (?, ?, ?, ?)
            """, (new_product_id, emb['vector_json'], emb['model_name'], emb['created_at']))

    print(f"Migrated {len(edition_to_product_map)} physical books and embeddings.")

    # 7. Seed Sample Stationeries (10 items)
    print("Seeding 10 Stationery items...")
    stationery_samples = [
        ("SKU_STAT_001", "Bút máy LAMY Safari Charcoal (Ngòi F)", 650000, 18, 50, 0, "Bút máy cao cấp phong cách Bauhaus nhập khẩu Đức", "/covers/stat_lamy.jpg", "LAMY", "Nhựa ABS", "Charcoal Black"),
        ("SKU_STAT_002", "Sổ tay Moleskine Classic Dotted Hardcover", 480000, 320, 45, 0, "Sổ tay cao cấp kẻ chấm bìa cứng giấy 70gsm không nhòe", "/covers/stat_moleskine.jpg", "Moleskine", "Giấy Acid-free", "Black"),
        ("SKU_STAT_003", "Thước kẻ kim loại kiêm Bookmark Midori Brass", 220000, 35, 80, 0, "Thước đồng thau cổ điển khắc laser số đo chuẩn xác", "/covers/stat_midori.jpg", "Midori", "Đồng thau nguyên khối", "Vintage Gold"),
        ("SKU_STAT_004", "Set 5 Sổ tay KOKUYO Campus B5 (50 trang)", 125000, 450, 120, 0, "Sổ tay học tập quốc dân giấy kẻ ngang mượt mà", "/covers/stat_kokuyo.jpg", "KOKUYO", "Giấy tráng phủ", "Pastel Rainbow"),
        ("SKU_STAT_005", "Bút bi gel kim loại Zebra Sarasa Grand Vintage 0.5", 210000, 24, 75, 0, "Thân kim loại sang trọng mực gel gốc nước kháng nước", "/covers/stat_zebra.jpg", "Zebra", "Hợp kim nhôm", "Bordeaux Black"),
        ("SKU_STAT_006", "Bút chì kim Tombow Mono Graph 0.5mm", 95000, 17, 100, 0, "Cơ chế lắc sinh ngòi và tẩy gôm xoay độc quyền Nhật Bản", "/covers/stat_tombow.jpg", "Tombow", "Polycarbonate", "Classic Mono Tricolor"),
        ("SKU_STAT_007", "Đèn đọc sách kẹp gáy sách LED BookHaven Clip", 185000, 95, 60, 0, "3 chế độ nhiệt màu bảo vệ mắt pin sạc USB-C 1000mAh", "/covers/stat_lamp.jpg", "BookHaven Gear", "Nhựa ABS & Nhôm dẻo", "Matte White"),
        ("SKU_STAT_008", "Túi bọc sách da PU BookHaven Book Sleeve A5", 160000, 85, 90, 0, "Chống trầy xước chống nước nhẹ vừa vặn khổ A5 tiêu chuẩn", "/covers/stat_sleeve.jpg", "BookHaven Gear", "Da PU cao cấp", "Coffee Brown"),
        ("SKU_STAT_009", "Giá đỡ đọc sách gỗ thông tự nhiên Book Stand", 290000, 680, 35, 0, "Điều chỉnh 5 góc nghiêng giải phóng đôi tay khi đọc", "/covers/stat_stand.jpg", "BookHaven Wood", "Gỗ thông tự nhiên", "Natural Pine"),
        ("SKU_STAT_010", "Hộp bút cuộn vải Canvas Vintage phong cách Nhật", 110000, 70, 85, 0, "Chứa 10 bút ký và dụng cụ cuộn gọn gàng phong cách thư sinh", "/covers/stat_case.jpg", "BookHaven Textile", "Vải Canvas dệt thô", "Forest Green"),
    ]

    for sku, name, price, weight, stock, reserved, desc, img, brand, material, color in stationery_samples:
        cur.execute("""
            INSERT INTO products (category_id, sku, name, unit_price, weight_gram, stock_on_hand, stock_reserved, description, cover_image, is_active)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
        """, (cat_stat_id, sku, name, price, weight, stock, reserved, desc, img))
        stat_pid = cur.lastrowid
        cur.execute("""
            INSERT INTO stationeries (product_id, brand, material, color)
            VALUES (?, ?, ?, ?)
        """, (stat_pid, brand, material, color))

    # 8. Seed Sample Collectibles (10 items)
    print("Seeding 10 Cultural Collectible items...")
    collectible_samples = [
        ("SKU_COLL_001", "Mô hình đứng Acrylic Thám tử Conan Edogawa", 150000, 45, 60, 0, "Bản quyền chính hãng TMS Entertainment chân đế vững chắc", "/covers/coll_conan.jpg", "Nhật Bản", "Mica Acrylic cao cấp", "Cao 15cm x Dày 4mm"),
        ("SKU_COLL_002", "Bookmark kim loại mạ vàng Mũ Rơm Luffy (One Piece)", 95000, 20, 150, 0, "Mạ vàng 18K chạm khắc tinh xảo dây tua rua đỏ", "/covers/coll_luffy.jpg", "Toei Animation JP", "Hợp kim đồng mạ vàng", "12cm x 4.5cm"),
        ("SKU_COLL_003", "Mô hình Chibi Naruto Cửu Vĩ Rasengan", 380000, 220, 25, 0, "Mô hình để bàn sơn tay chi tiết sắc sảo biểu cảm sống động", "/covers/coll_naruto.jpg", "Bandai Spirits JP", "Nhựa PVC đúc đặc", "Cao 10cm"),
        ("SKU_COLL_004", "Túi Canvas Totoro Dạo Phố Ghibli Eco Bag", 195000, 180, 80, 0, "Túi vải bố dày dặn in mực thân thiện môi trường quai êm ái", "/covers/coll_totoro.jpg", "Ghibli Studio", "Vải Canvas 12oz", "38cm x 42cm"),
        ("SKU_COLL_005", "Móc khóa Thanh Kiếm Diệt Quỷ Nichirin Tanjiro", 85000, 50, 110, 0, "Thu nhỏ 1:12 có bao kiếm rút mượt mà", "/covers/coll_tanjiro.jpg", "Aniplex", "Hợp kim kẽm chống gỉ", "Dài 17cm"),
        ("SKU_COLL_006", "Bookmark Kim loại Trái Snitch Vàng (Harry Potter)", 135000, 28, 90, 0, "Cánh dang rộng mạ bạc ánh kim tinh tế cho tín đồ Hogwarts", "/covers/coll_snitch.jpg", "Wizarding World", "Hợp kim kẽm mạ bạc", "9.5cm x 6cm"),
        ("SKU_COLL_007", "Huy hiệu Kim loại Đội Thám tử Nhí (Detective Conan)", 65000, 18, 140, 0, "Huy hiệu đính áo hoặc cặp sách mô phỏng máy phát tín hiệu", "/covers/coll_badge.jpg", "TMS Japan", "Kim loại dập nổi", "Đường kính 3.5cm"),
        ("SKU_COLL_008", "Set 16 Bưu thiếp Nghệ thuật Vùng Đất Linh Hồn Ghibli", 140000, 160, 40, 0, "Tranh in gốc chất lượng bảo tàng hộp thiếc sang trọng", "/covers/coll_spirited.jpg", "Ghibli Official", "Giấy mỹ thuật 350gsm", "10cm x 15cm"),
        ("SKU_COLL_009", "Mô hình Doraemon Cửa Thần Kỳ Kỷ Niệm 50 Năm", 320000, 260, 30, 0, "Doraemon tươi cười bước qua cánh cửa hồng thần kỳ", "/covers/coll_doraemon.jpg", "Fujiko Pro JP", "Nhựa PVC & Resin", "14cm x 12cm x 8cm"),
        ("SKU_COLL_010", "Huy hiệu Tráng men Enamel Pin BookHaven 'Bookworm'", 55000, 15, 200, 0, "Biểu tượng mọt sách đội vương miện thiết kế độc quyền", "/covers/coll_bookhaven.jpg", "BookHaven Exclusive", "Hợp kim tráng men cứng", "3cm x 2.8cm"),
    ]

    for sku, name, price, weight, stock, reserved, desc, img, origin, material, dims in collectible_samples:
        cur.execute("""
            INSERT INTO products (category_id, sku, name, unit_price, weight_gram, stock_on_hand, stock_reserved, description, cover_image, is_active)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
        """, (cat_coll_id, sku, name, price, weight, stock, reserved, desc, img))
        coll_pid = cur.lastrowid
        cur.execute("""
            INSERT INTO collectibles (product_id, origin, material, dimensions)
            VALUES (?, ?, ?, ?)
        """, (coll_pid, origin, material, dims))

    # 9. Create Carts for Customers
    print("Creating Carts and Cart Items for customers...")
    cur.execute("SELECT user_id FROM customers")
    customers = cur.fetchall()
    
    # Grab 2 sample products for the default cart
    sample_prod_1 = cur.execute("SELECT product_id FROM products LIMIT 1").fetchone()[0]
    sample_prod_2 = cur.execute("SELECT product_id FROM stationeries LIMIT 1").fetchone()[0]

    for cust in customers:
        cur.execute("""
            INSERT INTO carts (customer_id) VALUES (?)
        """, (cust[0],))
        cart_id = cur.lastrowid
        
        # Add sample cart items for customer 1
        if cust[0] == user_id_map.get("CUST_001", customers[0][0]):
            cur.execute("""
                INSERT INTO cart_items (cart_id, product_id, quantity)
                VALUES (?, ?, 2)
            """, (cart_id, sample_prod_1))
            cur.execute("""
                INSERT INTO cart_items (cart_id, product_id, quantity)
                VALUES (?, ?, 1)
            """, (cart_id, sample_prod_2))

    # 10. Migrate Orders, OrderItems, Payments, StockReservations
    print("Migrating Orders, OrderItems, Payments, StockReservations...")
    order_id_map = {}
    for o in old_orders:
        new_customer_id = user_id_map.get(o['customer_id'])
        if not new_customer_id:
            # Fallback to first customer
            new_customer_id = customers[0][0]
            
        carrier = o['carrier']
        if carrier == 'HANOI_DRONE':
            carrier = 'HANOI_DRONE_EXPRESS'
        elif carrier in ('GHN_STANDARD', 'GHN_EXPRESS'):
            carrier = 'GHN'
            
        cur.execute("""
            INSERT INTO orders (customer_id, receiver_name, receiver_phone, shipping_address, payment_method, carrier, tracking_code, total_amount, shipping_fee, discount_amount, final_amount, status, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            new_customer_id,
            o['receiver_name'],
            o['receiver_phone'],
            o['shipping_address'],
            o['payment_method'],
            carrier,
            o['tracking_code'],
            o['total_amount'],
            o['shipping_fee'],
            o['discount_amount'],
            o['final_amount'],
            o['status'],
            o['created_at'],
            o['updated_at']
        ))
        new_oid = cur.lastrowid
        order_id_map[o['order_id']] = new_oid

    for oi in old_order_items:
        new_oid = order_id_map.get(oi['order_id'])
        new_pid = edition_to_product_map.get(oi['edition_id'])
        if new_oid and new_pid:
            cur.execute("""
                INSERT INTO order_items (order_id, product_id, product_name_snapshot, sku_snapshot, product_kind_snapshot, unit_price_at_purchase, quantity, weight_gram_snapshot, created_at)
                VALUES (?, ?, ?, ?, 'BOOK', ?, ?, ?, ?)
            """, (
                new_oid,
                new_pid,
                oi['title_snapshot'],
                oi['sku_snapshot'],
                oi['unit_price_at_purchase'],
                oi['quantity'],
                oi['weight_gram_snapshot'],
                oi['created_at']
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
    print("Database migration completed successfully!")

if __name__ == "__main__":
    migrate()
