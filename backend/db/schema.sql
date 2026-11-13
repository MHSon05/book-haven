-- ============================================================================
-- BOOKHAVEN E-COMMERCE SYSTEM - PHYSICAL DATABASE SCHEMA (DDL)
-- Hệ thống Thương mại Điện tử Nhà sách BookHaven
-- Học viện Công nghệ Bưu chính Viễn thông (PTIT)
-- Sinh viên: Mai Hữu Sơn - MSSV: B23DCAT262 | GVHD: PGS. TS. Trần Đình Quế
-- 100% Đồng bộ với Lược đồ ERD Chương 4 (Figure 4.2 - 17 Tables ORM Persistable)
-- ============================================================================

-- Bắt buộc kích hoạt toàn vẹn khóa ngoại trong SQLite
PRAGMA foreign_keys = ON;

-- ----------------------------------------------------------------------------
-- 1. BẢNG USERS (Lớp người dùng cơ sở / Base Identity)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    phone VARCHAR(20),
    role VARCHAR(20) NOT NULL DEFAULT 'CUSTOMER' CHECK (role IN ('CUSTOMER', 'STAFF', 'ADMIN', 'MANAGER')),
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ----------------------------------------------------------------------------
-- 2. BẢNG CUSTOMERS (Lớp con kế thừa từ Users - Khách hàng)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS customers (
    user_id INTEGER PRIMARY KEY REFERENCES users(user_id) ON DELETE CASCADE,
    shipping_address VARCHAR(255),
    loyalty_points INTEGER DEFAULT 0 CHECK (loyalty_points >= 0)
);

-- ----------------------------------------------------------------------------
-- 3. BẢNG STAFFS (Lớp con kế thừa từ Users - Nhân viên)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS staffs (
    user_id INTEGER PRIMARY KEY REFERENCES users(user_id) ON DELETE CASCADE,
    staff_role VARCHAR(50) NOT NULL,
    department VARCHAR(50) NOT NULL
);

-- ----------------------------------------------------------------------------
-- 4. BẢNG CATEGORIES (Thể loại & Phân mục sản phẩm)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS categories (
    category_id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_name VARCHAR(100) NOT NULL,
    description TEXT,
    slug VARCHAR(100) UNIQUE NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ----------------------------------------------------------------------------
-- 5. BẢNG PUBLISHERS (Nhà xuất bản đối tác)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS publishers (
    publisher_id INTEGER PRIMARY KEY AUTOINCREMENT,
    publisher_name VARCHAR(150) NOT NULL,
    address VARCHAR(255),
    contact_email VARCHAR(100),
    phone VARCHAR(20),
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ----------------------------------------------------------------------------
-- 6. BẢNG AUTHORS (Tác giả)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS authors (
    author_id INTEGER PRIMARY KEY AUTOINCREMENT,
    author_name VARCHAR(150) NOT NULL,
    biography TEXT,
    nationality VARCHAR(50),
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ----------------------------------------------------------------------------
-- 7. BẢNG PRODUCTS (Lớp cha trừu tượng - Quản lý tồn kho chung)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS products (
    product_id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_id INTEGER REFERENCES categories(category_id) ON DELETE RESTRICT,
    sku VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    unit_price INTEGER NOT NULL CHECK (unit_price >= 0),
    weight_gram INTEGER NOT NULL CHECK (weight_gram > 0),
    stock_on_hand INTEGER NOT NULL DEFAULT 0 CHECK (stock_on_hand >= 0),
    stock_reserved INTEGER NOT NULL DEFAULT 0 CHECK (stock_reserved >= 0),
    description TEXT,
    cover_image VARCHAR(255),
    is_active INTEGER NOT NULL DEFAULT 1 CHECK (is_active IN (0, 1)),
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CHECK (stock_on_hand >= stock_reserved)
);

-- ----------------------------------------------------------------------------
-- 8. BẢNG BOOKS (Lớp con kế thừa từ Products - Sách in)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS books (
    product_id INTEGER PRIMARY KEY REFERENCES products(product_id) ON DELETE CASCADE,
    isbn13 VARCHAR(13) UNIQUE NOT NULL,
    author_id INTEGER REFERENCES authors(author_id) ON DELETE RESTRICT,
    publisher_id INTEGER REFERENCES publishers(publisher_id) ON DELETE RESTRICT,
    publish_year INTEGER NOT NULL,
    binding_type VARCHAR(30) NOT NULL CHECK (binding_type IN ('Paperback', 'Hardcover', 'PAPERBACK', 'HARDCOVER'))
);

-- ----------------------------------------------------------------------------
-- 9. BẢNG STATIONERIES (Lớp con kế thừa từ Products - Văn phòng phẩm)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS stationeries (
    product_id INTEGER PRIMARY KEY REFERENCES products(product_id) ON DELETE CASCADE,
    brand VARCHAR(100) NOT NULL,
    material VARCHAR(100),
    color VARCHAR(50)
);

-- ----------------------------------------------------------------------------
-- 10. BẢNG COLLECTIBLES (Lớp con kế thừa từ Products - Quà tặng, Đồ sưu tầm)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS collectibles (
    product_id INTEGER PRIMARY KEY REFERENCES products(product_id) ON DELETE CASCADE,
    origin VARCHAR(100),
    material VARCHAR(100),
    dimensions VARCHAR(50)
);

-- ----------------------------------------------------------------------------
-- 11. BẢNG BOOK_EMBEDDINGS (Vector nhúng ngữ nghĩa AI d=384 - Chương 3)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS book_embeddings (
    product_id INTEGER PRIMARY KEY REFERENCES books(product_id) ON DELETE CASCADE,
    vector_json TEXT NOT NULL,
    model_name VARCHAR(100) NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ----------------------------------------------------------------------------
-- 12. BẢNG CARTS (Giỏ hàng khách hàng)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS carts (
    cart_id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER UNIQUE NOT NULL REFERENCES customers(user_id) ON DELETE CASCADE,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ----------------------------------------------------------------------------
-- 13. BẢNG CART_ITEMS (Sản phẩm trong giỏ hàng - trỏ về Products)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS cart_items (
    cart_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
    cart_id INTEGER NOT NULL REFERENCES carts(cart_id) ON DELETE CASCADE,
    product_id INTEGER NOT NULL REFERENCES products(product_id) ON DELETE RESTRICT,
    quantity INTEGER NOT NULL DEFAULT 1 CHECK (quantity > 0),
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(cart_id, product_id)
);

-- ----------------------------------------------------------------------------
-- 14. BẢNG ORDERS (Đơn đặt hàng chính thức)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS orders (
    order_id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER NOT NULL REFERENCES customers(user_id) ON DELETE RESTRICT,
    receiver_name VARCHAR(100) NOT NULL,
    receiver_phone VARCHAR(20) NOT NULL,
    shipping_address VARCHAR(255) NOT NULL,
    payment_method VARCHAR(30) NOT NULL CHECK (payment_method IN ('VIETQR', 'COD')),
    carrier VARCHAR(50) NOT NULL CHECK (carrier IN ('GHN', 'GHN_STANDARD', 'GHN_EXPRESS', 'HANOI_DRONE', 'HANOI_DRONE_EXPRESS')),
    tracking_code VARCHAR(50),
    total_amount INTEGER NOT NULL CHECK (total_amount >= 0),
    shipping_fee INTEGER NOT NULL DEFAULT 0 CHECK (shipping_fee >= 0),
    discount_amount INTEGER DEFAULT 0 CHECK (discount_amount >= 0),
    final_amount INTEGER NOT NULL CHECK (final_amount >= 0),
    status VARCHAR(30) NOT NULL DEFAULT 'AWAITING_PAYMENT' CHECK (status IN (
        'AWAITING_PAYMENT', 'PENDING_PAYMENT', 'PAID', 'PENDING_CASH', 'PACKED', 'SHIPPING', 'DELIVERED', 'CANCELLED'
    )),
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ----------------------------------------------------------------------------
-- 15. BẢNG ORDER_ITEMS (Snapshot bất biến tài chính & định lượng tại checkout)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS order_items (
    order_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER NOT NULL REFERENCES orders(order_id) ON DELETE CASCADE,
    product_id INTEGER NOT NULL REFERENCES products(product_id) ON DELETE RESTRICT,
    product_name_snapshot VARCHAR(255) NOT NULL,
    sku_snapshot VARCHAR(50) NOT NULL,
    product_kind_snapshot VARCHAR(30) NOT NULL,
    unit_price_at_purchase INTEGER NOT NULL CHECK (unit_price_at_purchase >= 0),
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    weight_gram_snapshot INTEGER NOT NULL CHECK (weight_gram_snapshot > 0),
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ----------------------------------------------------------------------------
-- 16. BẢNG PAYMENTS (Chứng từ thanh toán)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS payments (
    payment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER UNIQUE NOT NULL REFERENCES orders(order_id) ON DELETE CASCADE,
    payment_method VARCHAR(30) NOT NULL,
    amount INTEGER NOT NULL CHECK (amount >= 0),
    transaction_code VARCHAR(100),
    status VARCHAR(30) NOT NULL DEFAULT 'PENDING' CHECK (status IN ('PENDING', 'SUCCESS', 'FAILED')),
    paid_at DATETIME
);

-- ----------------------------------------------------------------------------
-- 17. BẢNG STOCK_RESERVATIONS (Bản ghi khóa giữ chỗ kho 15 phút - BR03)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS stock_reservations (
    reservation_id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER NOT NULL REFERENCES orders(order_id) ON DELETE CASCADE,
    product_id INTEGER NOT NULL REFERENCES products(product_id) ON DELETE RESTRICT,
    reserved_quantity INTEGER NOT NULL CHECK (reserved_quantity > 0),
    expires_at DATETIME NOT NULL,
    status VARCHAR(30) NOT NULL DEFAULT 'PENDING' CHECK (status IN ('PENDING', 'COMMITTED', 'RELEASED')),
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- CHỈ MỤC TỐI ƯU TRUY VẤN (INDEXES)
-- ============================================================================
CREATE INDEX IF NOT EXISTS idx_products_category ON products(category_id);
CREATE INDEX IF NOT EXISTS idx_products_sku ON products(sku);
CREATE INDEX IF NOT EXISTS idx_books_isbn ON books(isbn13);
CREATE INDEX IF NOT EXISTS idx_books_author ON books(author_id);
CREATE INDEX IF NOT EXISTS idx_books_publisher ON books(publisher_id);
CREATE INDEX IF NOT EXISTS idx_cart_items_cart ON cart_items(cart_id);
CREATE INDEX IF NOT EXISTS idx_orders_customer ON orders(customer_id);
CREATE INDEX IF NOT EXISTS idx_order_items_order ON order_items(order_id);
CREATE INDEX IF NOT EXISTS idx_reservations_status_expires ON stock_reservations(status, expires_at);
