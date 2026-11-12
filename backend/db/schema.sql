-- ============================================================================
-- BOOKHAVEN E-COMMERCE SYSTEM - PHYSICAL DATABASE SCHEMA (DDL)
-- Hệ thống Thương mại Điện tử Nhà sách BookHaven
-- Học viện Công nghệ Bưu chính Viễn thông (PTIT)
-- Sinh viên: Mai Hữu Sơn - MSSV: B23DCAT262 | GVHD: PGS. TS. Trần Đình Quế
-- Tiêu chuẩn: ANSI SQL / SQLite 3 / PostgreSQL Compatible
-- ============================================================================

-- Bật kiểm tra tính toàn vẹn khóa ngoại (Foreign Key Constraints)
PRAGMA foreign_keys = ON;

-- ----------------------------------------------------------------------------
-- 1. BẢNG USERS (Người dùng hệ thống - Single Table Inheritance)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS users (
    user_id TEXT PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    full_name TEXT NOT NULL,
    phone TEXT,
    role TEXT NOT NULL DEFAULT 'CUSTOMER' CHECK (role IN ('CUSTOMER', 'STAFF', 'ADMIN', 'MANAGER')),
    shipping_address TEXT,
    loyalty_points INTEGER DEFAULT 0 CHECK (loyalty_points >= 0),
    staff_role TEXT,
    department TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ----------------------------------------------------------------------------
-- 2. BẢNG AUTHORS (Tác giả tác phẩm)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS authors (
    author_id TEXT PRIMARY KEY,
    author_name TEXT NOT NULL,
    biography TEXT,
    nationality TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ----------------------------------------------------------------------------
-- 3. BẢNG PUBLISHERS (Nhà xuất bản đối tác)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS publishers (
    publisher_id TEXT PRIMARY KEY,
    publisher_name TEXT NOT NULL,
    address TEXT,
    contact_email TEXT,
    phone TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ----------------------------------------------------------------------------
-- 4. BẢNG CATEGORIES (Thể loại & Phân mục sách)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS categories (
    category_id TEXT PRIMARY KEY,
    category_name TEXT NOT NULL,
    description TEXT,
    slug TEXT UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ----------------------------------------------------------------------------
-- 5. BẢNG BOOKS (Tác phẩm chung)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS books (
    book_id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    author_id TEXT NOT NULL REFERENCES authors(author_id) ON DELETE RESTRICT,
    publisher_id TEXT NOT NULL REFERENCES publishers(publisher_id) ON DELETE RESTRICT,
    category_id TEXT NOT NULL REFERENCES categories(category_id) ON DELETE RESTRICT,
    publish_year INTEGER,
    description TEXT,
    cover_image TEXT,
    is_active INTEGER DEFAULT 1 CHECK (is_active IN (0, 1)),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ----------------------------------------------------------------------------
-- 6. BẢNG BOOK_EDITIONS (Ấn bản Bìa mềm / Bìa cứng - SKU & ISBN-13 độc lập)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS book_editions (
    edition_id TEXT PRIMARY KEY,
    book_id TEXT NOT NULL REFERENCES books(book_id) ON DELETE CASCADE,
    sku TEXT UNIQUE NOT NULL,
    isbn13 TEXT UNIQUE NOT NULL,
    binding_type TEXT NOT NULL CHECK (binding_type IN ('PAPERBACK', 'HARDCOVER')),
    unit_price INTEGER NOT NULL CHECK (unit_price >= 0),
    weight_gram INTEGER NOT NULL CHECK (weight_gram > 0),
    stock_on_hand INTEGER NOT NULL DEFAULT 0 CHECK (stock_on_hand >= 0),
    stock_reserved INTEGER NOT NULL DEFAULT 0 CHECK (stock_reserved >= 0),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CHECK (stock_on_hand >= stock_reserved)
);

-- ----------------------------------------------------------------------------
-- 7. BẢNG BOOK_EMBEDDINGS (Vector nhúng ngữ nghĩa AI d=384 - Chương 3)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS book_embeddings (
    embedding_id TEXT PRIMARY KEY,
    book_id TEXT UNIQUE NOT NULL REFERENCES books(book_id) ON DELETE CASCADE,
    vector_json TEXT NOT NULL,
    model_name TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ----------------------------------------------------------------------------
-- 8. BẢNG CARTS (Giỏ hàng độc giả)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS carts (
    cart_id TEXT PRIMARY KEY,
    customer_id TEXT UNIQUE NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ----------------------------------------------------------------------------
-- 9. BẢNG CART_ITEMS (Dòng sản phẩm chọn mua tạm thời)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS cart_items (
    cart_item_id TEXT PRIMARY KEY,
    cart_id TEXT NOT NULL REFERENCES carts(cart_id) ON DELETE CASCADE,
    edition_id TEXT NOT NULL REFERENCES book_editions(edition_id) ON DELETE RESTRICT,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(cart_id, edition_id)
);

-- ----------------------------------------------------------------------------
-- 10. BẢNG ORDERS (Đơn đặt hàng chính thức)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS orders (
    order_id TEXT PRIMARY KEY,
    customer_id TEXT NOT NULL REFERENCES users(user_id) ON DELETE RESTRICT,
    receiver_name TEXT NOT NULL,
    receiver_phone TEXT NOT NULL,
    shipping_address TEXT NOT NULL,
    payment_method TEXT NOT NULL CHECK (payment_method IN ('VIETQR', 'COD')),
    total_amount INTEGER NOT NULL CHECK (total_amount >= 0),
    shipping_fee INTEGER NOT NULL DEFAULT 0 CHECK (shipping_fee >= 0),
    discount_amount INTEGER NOT NULL DEFAULT 0 CHECK (discount_amount >= 0),
    final_amount INTEGER NOT NULL CHECK (final_amount >= 0),
    status TEXT NOT NULL DEFAULT 'AWAITING_PAYMENT' CHECK (status IN (
        'AWAITING_PAYMENT', 'PAID', 'PENDING_CASH', 'PACKED', 'SHIPPING', 'DELIVERED', 'CANCELLED'
    )),
    carrier TEXT CHECK (carrier IN ('GHN_STANDARD', 'GHN_EXPRESS', 'HANOI_DRONE')),
    tracking_code TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ----------------------------------------------------------------------------
-- 11. BẢNG ORDER_ITEMS (Snapshot bất biến tài chính tại thời điểm chốt đơn - BR03)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS order_items (
    order_item_id TEXT PRIMARY KEY,
    order_id TEXT NOT NULL REFERENCES orders(order_id) ON DELETE CASCADE,
    edition_id TEXT NOT NULL REFERENCES book_editions(edition_id) ON DELETE RESTRICT,
    title_snapshot TEXT NOT NULL,
    sku_snapshot TEXT NOT NULL,
    binding_type_snapshot TEXT NOT NULL,
    isbn13_snapshot TEXT NOT NULL,
    unit_price_at_purchase INTEGER NOT NULL CHECK (unit_price_at_purchase >= 0),
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    weight_gram_snapshot INTEGER NOT NULL CHECK (weight_gram_snapshot > 0),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ----------------------------------------------------------------------------
-- 12. BẢNG STOCK_RESERVATIONS (Bản ghi khóa giữ chỗ kho 15 phút - BR05)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS stock_reservations (
    reservation_id TEXT PRIMARY KEY,
    order_id TEXT NOT NULL REFERENCES orders(order_id) ON DELETE CASCADE,
    edition_id TEXT NOT NULL REFERENCES book_editions(edition_id) ON DELETE RESTRICT,
    reserved_quantity INTEGER NOT NULL CHECK (reserved_quantity > 0),
    expires_at TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'PENDING' CHECK (status IN ('PENDING', 'COMMITTED', 'RELEASED')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ----------------------------------------------------------------------------
-- 13. BẢNG PAYMENTS (Chứng từ dòng tiền thực thu - BR04)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS payments (
    payment_id TEXT PRIMARY KEY,
    order_id TEXT UNIQUE NOT NULL REFERENCES orders(order_id) ON DELETE RESTRICT,
    payment_method TEXT NOT NULL,
    amount INTEGER NOT NULL CHECK (amount >= 0),
    transaction_code TEXT,
    status TEXT NOT NULL DEFAULT 'PENDING' CHECK (status IN ('PENDING', 'SUCCESS', 'FAILED')),
    paid_at TIMESTAMP
);

-- ============================================================================
-- CHỈ MỤC HIỆU NĂNG (INDEXES)
-- ============================================================================
CREATE INDEX IF NOT EXISTS idx_books_category ON books(category_id);
CREATE INDEX IF NOT EXISTS idx_books_author ON books(author_id);
CREATE INDEX IF NOT EXISTS idx_editions_book ON book_editions(book_id);
CREATE INDEX IF NOT EXISTS idx_cart_items_cart ON cart_items(cart_id);
CREATE INDEX IF NOT EXISTS idx_orders_customer ON orders(customer_id);
CREATE INDEX IF NOT EXISTS idx_order_items_order ON order_items(order_id);
CREATE INDEX IF NOT EXISTS idx_reservations_status_expires ON stock_reservations(status, expires_at);
