"""
Scripts: gen_db.py
Kịch bản tạo lập CSDL vật lý bookhaven.db chuẩn 100% theo sơ đồ ERD 17 bảng (Figure 4.2).
Bao gồm:
- 250 sách in Fahasa (Manga, Văn học, Công nghệ, Kỹ năng, Kinh tế) + 250 Vector nhúng AI d=384
- 25 mặt hàng Văn phòng phẩm (Stationery) chính hãng Fahasa (Deli, Thiên Long, Pilot, Stacom...)
- 25 đồ lưu niệm văn hóa / Manga & Anime Collectibles (Doraemon, Jujutsu Kaisen, Marvel, Conan...)
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

# 25 MẶT HÀNG VĂN PHÒNG PHẨM FAHASA CHÍNH HÃNG
STATIONERY_CATALOG = [
    ('SKU_STAT_001', 'Bút Gel 0.5 mm - Deli EG67-BL-01 - Mực Xanh', 7000, 27, 45, 0, 'Sản phẩm Bút Gel 0.5 mm - Deli EG67-BL-01 - Mực Xanh chính hãng phân phối tại Fahasa. Đạt tiêu chuẩn chất lượng cao, bền đẹp, tiện lợi cho học sinh, sinh viên và nhân viên văn phòng.', '/static/covers/stat_fahasa_001.jpg', 'Deli', 'Nhựa ABS & Mực Cao Cấp', 'Xanh'),
    ('SKU_STAT_002', 'Bút Bi Bấm Xtream Màu Pastel 0.7 mm - Deli Q033 - Mực Xanh (Màu Thân Bút Giao Ngẫu Nhiên)', 5000, 34, 50, 0, 'Sản phẩm Bút Bi Bấm Xtream Màu Pastel 0.7 mm - Deli Q033 - Mực Xanh (Màu Thân Bút Giao Ngẫu Nhiên) chính hãng phân phối tại Fahasa. Đạt tiêu chuẩn chất lượng cao, bền đẹp, tiện lợi cho học sinh, sinh viên và nhân viên văn phòng.', '/static/covers/stat_fahasa_002.jpg', 'Deli', 'Nhựa ABS & Mực Cao Cấp', 'Xanh'),
    ('SKU_STAT_003', 'Hộp 20 Bút Bi Pro 027 0.5 mm - Thiên Long TL-105 - Mực Xanh', 135000, 41, 55, 0, 'Sản phẩm Hộp 20 Bút Bi Pro 027 0.5 mm - Thiên Long TL-105 - Mực Xanh chính hãng phân phối tại Fahasa. Đạt tiêu chuẩn chất lượng cao, bền đẹp, tiện lợi cho học sinh, sinh viên và nhân viên văn phòng.', '/static/covers/stat_fahasa_003.jpg', 'Thiên Long', 'Nhựa ABS & Mực Cao Cấp', 'Xanh'),
    ('SKU_STAT_004', 'Bút Bi Linc Glycer 0.7 - Mực Đỏ', 6500, 48, 60, 0, 'Sản phẩm Bút Bi Linc Glycer 0.7 - Mực Đỏ chính hãng phân phối tại Fahasa. Đạt tiêu chuẩn chất lượng cao, bền đẹp, tiện lợi cho học sinh, sinh viên và nhân viên văn phòng.', '/static/covers/stat_fahasa_004.jpg', 'Linc', 'Nhựa ABS & Mực Cao Cấp', 'Đỏ'),
    ('SKU_STAT_005', 'Bút Lông Dầu Thiên Long PM-09 - Mực Xanh', 14400, 55, 65, 0, 'Sản phẩm Bút Lông Dầu Thiên Long PM-09 - Mực Xanh chính hãng phân phối tại Fahasa. Đạt tiêu chuẩn chất lượng cao, bền đẹp, tiện lợi cho học sinh, sinh viên và nhân viên văn phòng.', '/static/covers/stat_fahasa_005.jpg', 'Thiên Long', 'Nhựa ABS & Mực Cao Cấp', 'Xanh'),
    ('SKU_STAT_006', 'Bút Bi Claro Arrow 0.7 mm - Mực Đỏ', 4275, 62, 70, 0, 'Sản phẩm Bút Bi Claro Arrow 0.7 mm - Mực Đỏ chính hãng phân phối tại Fahasa. Đạt tiêu chuẩn chất lượng cao, bền đẹp, tiện lợi cho học sinh, sinh viên và nhân viên văn phòng.', '/static/covers/stat_fahasa_006.jpg', 'Fahasa Stationery', 'Nhựa ABS & Mực Cao Cấp', 'Đỏ'),
    ('SKU_STAT_007', 'Bút Máy Chipy - Thiên Long FTC-019 - Mực Tím', 15300, 69, 75, 0, 'Sản phẩm Bút Máy Chipy - Thiên Long FTC-019 - Mực Tím chính hãng phân phối tại Fahasa. Đạt tiêu chuẩn chất lượng cao, bền đẹp, tiện lợi cho học sinh, sinh viên và nhân viên văn phòng.', '/static/covers/stat_fahasa_007.jpg', 'Thiên Long', 'Nhựa ABS & Mực Cao Cấp', 'Tím'),
    ('SKU_STAT_008', 'Vỉ 5 + 1 Bút Chì Gỗ 2B - Stacom VPC107 - Thân Vàng', 18000, 76, 80, 0, 'Sản phẩm Vỉ 5 + 1 Bút Chì Gỗ 2B - Stacom VPC107 - Thân Vàng chính hãng phân phối tại Fahasa. Đạt tiêu chuẩn chất lượng cao, bền đẹp, tiện lợi cho học sinh, sinh viên và nhân viên văn phòng.', '/static/covers/stat_fahasa_008.jpg', 'Stacom', 'Gỗ Tự Nhiên & Than Chì', 'Vàng'),
    ('SKU_STAT_009', 'Hộp 12 Bút Gel Xóa Được Dino 0.5 mm - Smart Kids EG02 - Mực Tím', 45000, 83, 85, 0, 'Sản phẩm Hộp 12 Bút Gel Xóa Được Dino 0.5 mm - Smart Kids EG02 - Mực Tím chính hãng phân phối tại Fahasa. Đạt tiêu chuẩn chất lượng cao, bền đẹp, tiện lợi cho học sinh, sinh viên và nhân viên văn phòng.', '/static/covers/stat_fahasa_009.jpg', 'Smart Kids', 'Nhựa ABS & Mực Cao Cấp', 'Tím'),
    ('SKU_STAT_010', 'Bút Bi Crown 0.7mm OA-300 - Mực Đỏ', 9025, 90, 90, 0, 'Sản phẩm Bút Bi Crown 0.7mm OA-300 - Mực Đỏ chính hãng phân phối tại Fahasa. Đạt tiêu chuẩn chất lượng cao, bền đẹp, tiện lợi cho học sinh, sinh viên và nhân viên văn phòng.', '/static/covers/stat_fahasa_010.jpg', 'Fahasa Stationery', 'Nhựa ABS & Mực Cao Cấp', 'Đỏ'),
    ('SKU_STAT_011', 'Bút Bi 0.5 mm Laris - Thiên Long TL-095 - Mực Xanh', 11700, 97, 95, 0, 'Sản phẩm Bút Bi 0.5 mm Laris - Thiên Long TL-095 - Mực Xanh chính hãng phân phối tại Fahasa. Đạt tiêu chuẩn chất lượng cao, bền đẹp, tiện lợi cho học sinh, sinh viên và nhân viên văn phòng.', '/static/covers/stat_fahasa_011.jpg', 'Thiên Long', 'Nhựa ABS & Mực Cao Cấp', 'Xanh'),
    ('SKU_STAT_012', 'Bút Gel Thiên Long Gel-08 - Mực Đỏ', 10000, 104, 40, 0, 'Sản phẩm Bút Gel Thiên Long Gel-08 - Mực Đỏ chính hãng phân phối tại Fahasa. Đạt tiêu chuẩn chất lượng cao, bền đẹp, tiện lợi cho học sinh, sinh viên và nhân viên văn phòng.', '/static/covers/stat_fahasa_012.jpg', 'Thiên Long', 'Nhựa ABS & Mực Cao Cấp', 'Đỏ'),
    ('SKU_STAT_013', 'Bút Lông Bảng Nhân Vật Akooland Thế Giới Học Cụ Thần Kỳ - Thiên Long TP-WB016/AK - Mực Xanh', 10800, 111, 45, 0, 'Sản phẩm Bút Lông Bảng Nhân Vật Akooland Thế Giới Học Cụ Thần Kỳ - Thiên Long TP-WB016/AK - Mực Xanh chính hãng phân phối tại Fahasa. Đạt tiêu chuẩn chất lượng cao, bền đẹp, tiện lợi cho học sinh, sinh viên và nhân viên văn phòng.', '/static/covers/stat_fahasa_013.jpg', 'Thiên Long', 'Nhựa ABS & Mực Cao Cấp', 'Xanh'),
    ('SKU_STAT_014', 'Bút Lông Dầu - Thiên Long PM-04 - Mực Xanh', 13050, 118, 50, 0, 'Sản phẩm Bút Lông Dầu - Thiên Long PM-04 - Mực Xanh chính hãng phân phối tại Fahasa. Đạt tiêu chuẩn chất lượng cao, bền đẹp, tiện lợi cho học sinh, sinh viên và nhân viên văn phòng.', '/static/covers/stat_fahasa_014.jpg', 'Thiên Long', 'Nhựa ABS & Mực Cao Cấp', 'Xanh'),
    ('SKU_STAT_015', 'Bút Gel 0.5 mm - Thiên Long Gel-068 - Mực Tím', 5400, 125, 55, 0, 'Sản phẩm Bút Gel 0.5 mm - Thiên Long Gel-068 - Mực Tím chính hãng phân phối tại Fahasa. Đạt tiêu chuẩn chất lượng cao, bền đẹp, tiện lợi cho học sinh, sinh viên và nhân viên văn phòng.', '/static/covers/stat_fahasa_015.jpg', 'Thiên Long', 'Nhựa ABS & Mực Cao Cấp', 'Tím'),
    ('SKU_STAT_016', 'Bút Chì Gỗ 2B - Deli HC805-2B', 2989, 132, 60, 0, 'Sản phẩm Bút Chì Gỗ 2B - Deli HC805-2B chính hãng phân phối tại Fahasa. Đạt tiêu chuẩn chất lượng cao, bền đẹp, tiện lợi cho học sinh, sinh viên và nhân viên văn phòng.', '/static/covers/stat_fahasa_016.jpg', 'Deli', 'Gỗ Tự Nhiên & Than Chì', 'Tiêu Chuẩn'),
    ('SKU_STAT_017', 'Bút Gel 0.5 mm - Thiên Long Gel-068 - Mực Đỏ', 5400, 139, 65, 0, 'Sản phẩm Bút Gel 0.5 mm - Thiên Long Gel-068 - Mực Đỏ chính hãng phân phối tại Fahasa. Đạt tiêu chuẩn chất lượng cao, bền đẹp, tiện lợi cho học sinh, sinh viên và nhân viên văn phòng.', '/static/covers/stat_fahasa_017.jpg', 'Thiên Long', 'Nhựa ABS & Mực Cao Cấp', 'Đỏ'),
    ('SKU_STAT_018', 'Bút Đánh Dấu Highlight Macaron - Deli  ES621S-XD-01 - Màu Xanh Dương', 12600, 26, 70, 0, 'Sản phẩm Bút Đánh Dấu Highlight Macaron - Deli  ES621S-XD-01 - Màu Xanh Dương chính hãng phân phối tại Fahasa. Đạt tiêu chuẩn chất lượng cao, bền đẹp, tiện lợi cho học sinh, sinh viên và nhân viên văn phòng.', '/static/covers/stat_fahasa_018.jpg', 'Deli', 'Nhựa ABS & Mực Cao Cấp', 'Xanh Dương'),
    ('SKU_STAT_019', 'Bút Bi Plastic 0.7 mm - Pilot BP-1RT-F-R - Mực Đỏ', 7650, 33, 75, 0, 'Sản phẩm Bút Bi Plastic 0.7 mm - Pilot BP-1RT-F-R - Mực Đỏ chính hãng phân phối tại Fahasa. Đạt tiêu chuẩn chất lượng cao, bền đẹp, tiện lợi cho học sinh, sinh viên và nhân viên văn phòng.', '/static/covers/stat_fahasa_019.jpg', 'Pilot', 'Nhựa ABS & Mực Cao Cấp', 'Đỏ'),
    ('SKU_STAT_020', 'Hộp 20 Bút Bi 0.5 mm Treeden - Thiên Long TL-079 - Mực Xanh', 78000, 40, 80, 0, 'Sản phẩm Hộp 20 Bút Bi 0.5 mm Treeden - Thiên Long TL-079 - Mực Xanh chính hãng phân phối tại Fahasa. Đạt tiêu chuẩn chất lượng cao, bền đẹp, tiện lợi cho học sinh, sinh viên và nhân viên văn phòng.', '/static/covers/stat_fahasa_020.jpg', 'Thiên Long', 'Nhựa ABS & Mực Cao Cấp', 'Xanh'),
    ('SKU_STAT_021', 'Bút Lông Kim Thiên Long - FL-04/DO - Mực Tím', 11000, 47, 85, 0, 'Sản phẩm Bút Lông Kim Thiên Long - FL-04/DO - Mực Tím chính hãng phân phối tại Fahasa. Đạt tiêu chuẩn chất lượng cao, bền đẹp, tiện lợi cho học sinh, sinh viên và nhân viên văn phòng.', '/static/covers/stat_fahasa_021.jpg', 'Thiên Long', 'Nhựa ABS & Mực Cao Cấp', 'Tím'),
    ('SKU_STAT_022', 'Bút Bi Plastic 0.7 mm - Pilot BP-1RT-F-L - Mực Xanh', 7650, 54, 90, 0, 'Sản phẩm Bút Bi Plastic 0.7 mm - Pilot BP-1RT-F-L - Mực Xanh chính hãng phân phối tại Fahasa. Đạt tiêu chuẩn chất lượng cao, bền đẹp, tiện lợi cho học sinh, sinh viên và nhân viên văn phòng.', '/static/covers/stat_fahasa_022.jpg', 'Pilot', 'Nhựa ABS & Mực Cao Cấp', 'Xanh'),
    ('SKU_STAT_023', 'Bút Lông Dầu Thiên Long PM-09 - Mực Đen', 13950, 61, 95, 0, 'Sản phẩm Bút Lông Dầu Thiên Long PM-09 - Mực Đen chính hãng phân phối tại Fahasa. Đạt tiêu chuẩn chất lượng cao, bền đẹp, tiện lợi cho học sinh, sinh viên và nhân viên văn phòng.', '/static/covers/stat_fahasa_023.jpg', 'Thiên Long', 'Nhựa ABS & Mực Cao Cấp', 'Đen'),
    ('SKU_STAT_024', 'Bút Gel Ngòi ST Nét 0.5 mm - Deli G104-BK - Mực Xanh', 17550, 68, 40, 0, 'Sản phẩm Bút Gel Ngòi ST Nét 0.5 mm - Deli G104-BK - Mực Xanh chính hãng phân phối tại Fahasa. Đạt tiêu chuẩn chất lượng cao, bền đẹp, tiện lợi cho học sinh, sinh viên và nhân viên văn phòng.', '/static/covers/stat_fahasa_024.jpg', 'Deli', 'Nhựa ABS & Mực Cao Cấp', 'Xanh'),
    ('SKU_STAT_025', 'Thước Thẳng 20cm WinQ - C-20', 4000, 75, 45, 0, 'Sản phẩm Thước Thẳng 20cm WinQ - C-20 chính hãng phân phối tại Fahasa. Đạt tiêu chuẩn chất lượng cao, bền đẹp, tiện lợi cho học sinh, sinh viên và nhân viên văn phòng.', '/static/covers/stat_fahasa_025.jpg', 'Fahasa Stationery', 'Nhựa ABS & Mực Cao Cấp', 'Tiêu Chuẩn')
]

COLLECTIBLE_CATALOG = [
    ('SKU_COLL_001', 'Mô Hình Kỷ Niệm 45 Năm Phim Điện Ảnh Doraemon (Mẫu Sản Phẩm Giao Ngẫu Nhiên)', 123000, 72, 18, 0, 'Vật phẩm sưu tầm chính hãng: Mô Hình Kỷ Niệm 45 Năm Phim Điện Ảnh Doraemon (Mẫu Sản Phẩm Giao Ngẫu Nhiên). Chi tiết sắc nét, bản quyền chuẩn, là món quà lưu niệm độc đáo dành cho người yêu thích manga, anime và văn hóa đại chúng.', '/static/covers/coll_fahasa_001.jpg', 'Nhật Bản Bản Quyền (Doraemon)', 'Nhựa PVC & ABS Đúc Tinh Xảo', 'Cao 8 - 12cm'),
    ('SKU_COLL_002', 'Blindbox Đồ Chơi Mô Hình Marvel - Infinity Saga Series Vol.01 - ZD Toys ZC64', 53100, 84, 21, 0, 'Vật phẩm sưu tầm chính hãng: Blindbox Đồ Chơi Mô Hình Marvel - Infinity Saga Series Vol.01 - ZD Toys ZC64. Chi tiết sắc nét, bản quyền chuẩn, là món quà lưu niệm độc đáo dành cho người yêu thích manga, anime và văn hóa đại chúng.', '/static/covers/coll_fahasa_002.jpg', 'Bản Quyền Quốc Tế (Marvel)', 'Nhựa PVC & ABS Đúc Tinh Xảo', 'Cao 8 - 12cm'),
    ('SKU_COLL_003', 'Đồ Chơi Sưu Tầm Fifa Ballers Global - Zuru Toys 77792 (Mẫu Sản Phẩm Giao Ngẫu Nhiên)', 147000, 96, 24, 0, 'Vật phẩm sưu tầm chính hãng: Đồ Chơi Sưu Tầm Fifa Ballers Global - Zuru Toys 77792 (Mẫu Sản Phẩm Giao Ngẫu Nhiên). Chi tiết sắc nét, bản quyền chuẩn, là món quà lưu niệm độc đáo dành cho người yêu thích manga, anime và văn hóa đại chúng.', '/static/covers/coll_fahasa_003.jpg', 'Chính Hãng Fahasa', 'Vật Liệu Đồ Chơi Cao Cấp', 'Kích Thước Tiêu Chuẩn'),
    ('SKU_COLL_004', 'Đồ Chơi Mô Hình Sưu Tầm Minecraft 1.65 Inch - Nano Metalfigs Blind Bag - Jada Toys (Bao Bìa Giao Ngẫu Nhiên) (Mẫu Sản Phẩm Bên Trong Là Ngẫu Nhiên)', 53100, 108, 27, 0, 'Vật phẩm sưu tầm chính hãng: Đồ Chơi Mô Hình Sưu Tầm Minecraft 1.65 Inch - Nano Metalfigs Blind Bag - Jada Toys (Bao Bìa Giao Ngẫu Nhiên) (Mẫu Sản Phẩm Bên Trong Là Ngẫu Nhiên). Chi tiết sắc nét, bản quyền chuẩn, là món quà lưu niệm độc đáo dành cho người yêu thích manga, anime và văn hóa đại chúng.', '/static/covers/coll_fahasa_004.jpg', 'Bản Quyền Quốc Tế (Minecraft)', 'Hợp Kim Kẽm Tráng Men / Đúc Kim Loại', 'Cao 1.65 inch'),
    ('SKU_COLL_005', 'Đồ Chơi Lắp Ráp Mô Hình Siêu Xe Transformers - Wheels C02 - Blokees ET60', 89100, 120, 30, 0, 'Vật phẩm sưu tầm chính hãng: Đồ Chơi Lắp Ráp Mô Hình Siêu Xe Transformers - Wheels C02 - Blokees ET60. Chi tiết sắc nét, bản quyền chuẩn, là món quà lưu niệm độc đáo dành cho người yêu thích manga, anime và văn hóa đại chúng.', '/static/covers/coll_fahasa_005.jpg', 'Bản Quyền Quốc Tế (Transformers)', 'Nhựa PVC & ABS Đúc Tinh Xảo', 'Cao 8 - 12cm'),
    ('SKU_COLL_006', 'Đồ Chơi Bóng Pokeball Với Pokemon 4 Biểu Cảm Series 2 - Pokemon Toys 8104 (Mẫu Sản Phẩm Bên Trong Là Ngẫu Nhiên)', 109000, 132, 33, 0, 'Vật phẩm sưu tầm chính hãng: Đồ Chơi Bóng Pokeball Với Pokemon 4 Biểu Cảm Series 2 - Pokemon Toys 8104 (Mẫu Sản Phẩm Bên Trong Là Ngẫu Nhiên). Chi tiết sắc nét, bản quyền chuẩn, là món quà lưu niệm độc đáo dành cho người yêu thích manga, anime và văn hóa đại chúng.', '/static/covers/coll_fahasa_006.jpg', 'Nhật Bản Bản Quyền (Pokemon)', 'Vật Liệu Đồ Chơi Cao Cấp', 'Kích Thước Tiêu Chuẩn'),
    ('SKU_COLL_007', 'Huy Hiệu Nhân Vật - Phim Điện Ảnh Thám Tử Lừng Danh Conan 2026 - Tagger - Mẫu 2 (Sản Phẩm Bên Trong Là Ngẫu Nhiên)', 49500, 144, 36, 0, 'Vật phẩm sưu tầm chính hãng: Huy Hiệu Nhân Vật - Phim Điện Ảnh Thám Tử Lừng Danh Conan 2026 - Tagger - Mẫu 2 (Sản Phẩm Bên Trong Là Ngẫu Nhiên). Chi tiết sắc nét, bản quyền chuẩn, là món quà lưu niệm độc đáo dành cho người yêu thích manga, anime và văn hóa đại chúng.', '/static/covers/coll_fahasa_007.jpg', 'Nhật Bản Bản Quyền (Conan)', 'Hợp Kim Kẽm Tráng Men / Đúc Kim Loại', 'Đường Kính 4.5 - 6cm'),
    ('SKU_COLL_008', 'Đồ Chơi Mô Hình Marvel - Avengers - Hulk 4 Inch - ZD Toys ZC14', 107100, 156, 39, 0, 'Vật phẩm sưu tầm chính hãng: Đồ Chơi Mô Hình Marvel - Avengers - Hulk 4 Inch - ZD Toys ZC14. Chi tiết sắc nét, bản quyền chuẩn, là món quà lưu niệm độc đáo dành cho người yêu thích manga, anime và văn hóa đại chúng.', '/static/covers/coll_fahasa_008.jpg', 'Bản Quyền Quốc Tế (Marvel)', 'Nhựa PVC & ABS Đúc Tinh Xảo', 'Cao 4 inch'),
    ('SKU_COLL_009', 'Blindbox Đồ Chơi Mô Hình Nhân Vật  Fuggler Dẻo - DC Và Gremlins - PMI Kids’ World FG4208G', 169000, 168, 42, 0, 'Vật phẩm sưu tầm chính hãng: Blindbox Đồ Chơi Mô Hình Nhân Vật  Fuggler Dẻo - DC Và Gremlins - PMI Kids’ World FG4208G. Chi tiết sắc nét, bản quyền chuẩn, là món quà lưu niệm độc đáo dành cho người yêu thích manga, anime và văn hóa đại chúng.', '/static/covers/coll_fahasa_009.jpg', 'Bản Quyền Quốc Tế (Fuggler)', 'Nhựa PVC & ABS Đúc Tinh Xảo', 'Cao 8 - 12cm'),
    ('SKU_COLL_010', 'Đồ Chơi Mô Hình Nhân Vật Minecraft Phiên Bản Đặc Biệt - Mojang Studios MC2007M (Mẫu Sản Phẩm Bên Trong Là Ngẫu Nhiên)', 139000, 180, 45, 0, 'Vật phẩm sưu tầm chính hãng: Đồ Chơi Mô Hình Nhân Vật Minecraft Phiên Bản Đặc Biệt - Mojang Studios MC2007M (Mẫu Sản Phẩm Bên Trong Là Ngẫu Nhiên). Chi tiết sắc nét, bản quyền chuẩn, là món quà lưu niệm độc đáo dành cho người yêu thích manga, anime và văn hóa đại chúng.', '/static/covers/coll_fahasa_010.jpg', 'Bản Quyền Quốc Tế (Minecraft)', 'Nhựa PVC & ABS Đúc Tinh Xảo', 'Cao 8 - 12cm'),
    ('SKU_COLL_011', 'Đồ Chơi Dẻo Series 6 - Lankybox LB2003S6 (Sản Phẩm Bên Trong Là Ngẫu Nhiên)', 159000, 192, 48, 0, 'Vật phẩm sưu tầm chính hãng: Đồ Chơi Dẻo Series 6 - Lankybox LB2003S6 (Sản Phẩm Bên Trong Là Ngẫu Nhiên). Chi tiết sắc nét, bản quyền chuẩn, là món quà lưu niệm độc đáo dành cho người yêu thích manga, anime và văn hóa đại chúng.', '/static/covers/coll_fahasa_011.jpg', 'Chính Hãng Fahasa', 'Vật Liệu Đồ Chơi Cao Cấp', 'Kích Thước Tiêu Chuẩn'),
    ('SKU_COLL_012', 'Đồ Chơi Mô Hình My Little Pony - Mini Little Pony - ToTy DP11 (Mẫu Sản Phẩm Bên Trong Là Ngẫu Nhiên)', 71100, 204, 16, 0, 'Vật phẩm sưu tầm chính hãng: Đồ Chơi Mô Hình My Little Pony - Mini Little Pony - ToTy DP11 (Mẫu Sản Phẩm Bên Trong Là Ngẫu Nhiên). Chi tiết sắc nét, bản quyền chuẩn, là món quà lưu niệm độc đáo dành cho người yêu thích manga, anime và văn hóa đại chúng.', '/static/covers/coll_fahasa_012.jpg', 'Nhật Bản Bản Quyền (ToTy)', 'Nhựa PVC & ABS Đúc Tinh Xảo', 'Cao 8 - 12cm'),
    ('SKU_COLL_013', 'Đồ Chơi Thú Nhồi Bông 6 Inch Aphmau Ice Cream - Aphmau 6027IC (Sản Phẩm Bên Trong Là Ngẫu Nhiên)', 369000, 216, 19, 0, 'Vật phẩm sưu tầm chính hãng: Đồ Chơi Thú Nhồi Bông 6 Inch Aphmau Ice Cream - Aphmau 6027IC (Sản Phẩm Bên Trong Là Ngẫu Nhiên). Chi tiết sắc nét, bản quyền chuẩn, là món quà lưu niệm độc đáo dành cho người yêu thích manga, anime và văn hóa đại chúng.', '/static/covers/coll_fahasa_013.jpg', 'Chính Hãng Fahasa', 'Vật Liệu Đồ Chơi Cao Cấp', 'Cao 6 inch'),
    ('SKU_COLL_014', 'Blindbox Đồ Chơi Mô Hình Jujutsu Kaisen - Starfish - Nullset - ToTy NJ10', 269100, 228, 22, 0, 'Vật phẩm sưu tầm chính hãng: Blindbox Đồ Chơi Mô Hình Jujutsu Kaisen - Starfish - Nullset - ToTy NJ10. Chi tiết sắc nét, bản quyền chuẩn, là món quà lưu niệm độc đáo dành cho người yêu thích manga, anime và văn hóa đại chúng.', '/static/covers/coll_fahasa_014.jpg', 'Nhật Bản Bản Quyền (Jujutsu Kaisen)', 'Nhựa PVC & ABS Đúc Tinh Xảo', 'Cao 8 - 12cm'),
    ('SKU_COLL_015', 'Blindbox Đồ Chơi Lắp Ráp Mô Hình Transformers - Galaxy Version GV11 - The Lost Light - Blokees  ET69', 161100, 240, 25, 0, 'Vật phẩm sưu tầm chính hãng: Blindbox Đồ Chơi Lắp Ráp Mô Hình Transformers - Galaxy Version GV11 - The Lost Light - Blokees  ET69. Chi tiết sắc nét, bản quyền chuẩn, là món quà lưu niệm độc đáo dành cho người yêu thích manga, anime và văn hóa đại chúng.', '/static/covers/coll_fahasa_015.jpg', 'Bản Quyền Quốc Tế (Transformers)', 'Nhựa PVC & ABS Đúc Tinh Xảo', 'Cao 8 - 12cm'),
    ('SKU_COLL_016', 'Đồ Chơi Mô Hình Bí Ẩn Sakamoto Days - Sunrisepop SDBB001 (Mẫu Sản Phẩm Giao Ngẫu Nhiên)', 129000, 252, 28, 0, 'Vật phẩm sưu tầm chính hãng: Đồ Chơi Mô Hình Bí Ẩn Sakamoto Days - Sunrisepop SDBB001 (Mẫu Sản Phẩm Giao Ngẫu Nhiên). Chi tiết sắc nét, bản quyền chuẩn, là món quà lưu niệm độc đáo dành cho người yêu thích manga, anime và văn hóa đại chúng.', '/static/covers/coll_fahasa_016.jpg', 'Nhật Bản Bản Quyền (Sakamoto Days)', 'Nhựa PVC & ABS Đúc Tinh Xảo', 'Cao 8 - 12cm'),
    ('SKU_COLL_017', 'Đồ Chơi Mô Hình Emma - Coffee Shop - MJ Studio RE41 (Mẫu Bên Trong Là Ngẫu Nhiên)', 260100, 264, 31, 0, 'Vật phẩm sưu tầm chính hãng: Đồ Chơi Mô Hình Emma - Coffee Shop - MJ Studio RE41 (Mẫu Bên Trong Là Ngẫu Nhiên). Chi tiết sắc nét, bản quyền chuẩn, là món quà lưu niệm độc đáo dành cho người yêu thích manga, anime và văn hóa đại chúng.', '/static/covers/coll_fahasa_017.jpg', 'Chính Hãng Fahasa', 'Nhựa PVC & ABS Đúc Tinh Xảo', 'Cao 8 - 12cm'),
    ('SKU_COLL_018', 'Đồ Chơi Roblox - Mô Hình Nhân Vật Bí Ẩn Fisch  - PhatMojo MB5901', 169000, 276, 34, 0, 'Vật phẩm sưu tầm chính hãng: Đồ Chơi Roblox - Mô Hình Nhân Vật Bí Ẩn Fisch  - PhatMojo MB5901. Chi tiết sắc nét, bản quyền chuẩn, là món quà lưu niệm độc đáo dành cho người yêu thích manga, anime và văn hóa đại chúng.', '/static/covers/coll_fahasa_018.jpg', 'Chính Hãng Fahasa', 'Nhựa PVC & ABS Đúc Tinh Xảo', 'Cao 8 - 12cm'),
    ('SKU_COLL_019', 'Đồ Chơi Bóp Mềm Squishy Kpop Demon Hunters Derpy - Cinereplicas YM17899', 299000, 288, 37, 0, 'Vật phẩm sưu tầm chính hãng: Đồ Chơi Bóp Mềm Squishy Kpop Demon Hunters Derpy - Cinereplicas YM17899. Chi tiết sắc nét, bản quyền chuẩn, là món quà lưu niệm độc đáo dành cho người yêu thích manga, anime và văn hóa đại chúng.', '/static/covers/coll_fahasa_019.jpg', 'Chính Hãng Fahasa', 'Nhựa PVC & ABS Đúc Tinh Xảo', 'Kích Thước Tiêu Chuẩn'),
    ('SKU_COLL_020', 'Blindbox Mô Hình Hello Kitty - Childhood Fun Time Series - Moetch MA07', 224100, 300, 40, 0, 'Vật phẩm sưu tầm chính hãng: Blindbox Mô Hình Hello Kitty - Childhood Fun Time Series - Moetch MA07. Chi tiết sắc nét, bản quyền chuẩn, là món quà lưu niệm độc đáo dành cho người yêu thích manga, anime và văn hóa đại chúng.', '/static/covers/coll_fahasa_020.jpg', 'Nhật Bản Bản Quyền (Hello Kitty)', 'Nhựa PVC & ABS Đúc Tinh Xảo', 'Cao 8 - 12cm'),
    ('SKU_COLL_021', 'Đồ Chơi Mô Hình Jujutsu Kaisen Acrylic Stand - Yuji Itadori - YuMe 11250-11252', 119000, 62, 43, 0, 'Vật phẩm sưu tầm chính hãng: Đồ Chơi Mô Hình Jujutsu Kaisen Acrylic Stand - Yuji Itadori - YuMe 11250-11252. Chi tiết sắc nét, bản quyền chuẩn, là món quà lưu niệm độc đáo dành cho người yêu thích manga, anime và văn hóa đại chúng.', '/static/covers/coll_fahasa_021.jpg', 'Nhật Bản Bản Quyền (Jujutsu Kaisen)', 'Mica Acrylic In UV Sắc Nét', 'Cao 14 - 16cm x Rộng 8cm'),
    ('SKU_COLL_022', 'Đồ Chơi Mô Hình Jujutsu Kaisen Acrylic Stand - Nobara Kugisaki - YuMe 11250-11254', 119000, 74, 46, 0, 'Vật phẩm sưu tầm chính hãng: Đồ Chơi Mô Hình Jujutsu Kaisen Acrylic Stand - Nobara Kugisaki - YuMe 11250-11254. Chi tiết sắc nét, bản quyền chuẩn, là món quà lưu niệm độc đáo dành cho người yêu thích manga, anime và văn hóa đại chúng.', '/static/covers/coll_fahasa_022.jpg', 'Nhật Bản Bản Quyền (Jujutsu Kaisen)', 'Mica Acrylic In UV Sắc Nét', 'Cao 14 - 16cm x Rộng 8cm'),
    ('SKU_COLL_023', 'Đồ Chơi Mô Hình Nhân Vật Hermione 4.5 inch - Wizarding World 6074619', 49000, 86, 49, 0, 'Vật phẩm sưu tầm chính hãng: Đồ Chơi Mô Hình Nhân Vật Hermione 4.5 inch - Wizarding World 6074619. Chi tiết sắc nét, bản quyền chuẩn, là món quà lưu niệm độc đáo dành cho người yêu thích manga, anime và văn hóa đại chúng.', '/static/covers/coll_fahasa_023.jpg', 'Bản Quyền Quốc Tế (Hermione)', 'Nhựa PVC & ABS Đúc Tinh Xảo', 'Cao 4.5 inch'),
    ('SKU_COLL_024', 'Blindbox Đồ Chơi Mô Hình Tom And Jerry Inseparable Chaos Series - 52Toys', 280000, 98, 17, 0, 'Vật phẩm sưu tầm chính hãng: Blindbox Đồ Chơi Mô Hình Tom And Jerry Inseparable Chaos Series - 52Toys. Chi tiết sắc nét, bản quyền chuẩn, là món quà lưu niệm độc đáo dành cho người yêu thích manga, anime và văn hóa đại chúng.', '/static/covers/coll_fahasa_024.jpg', 'Bản Quyền Quốc Tế (Tom And Jerry)', 'Nhựa PVC & ABS Đúc Tinh Xảo', 'Cao 8 - 12cm'),
    ('SKU_COLL_025', 'Đồ Chơi Sưu Tầm Quái Thú Nổi Loạn Fuggler Baddies Fuggs 9 Inch - Zuru Toys 15784 - Annoyed Alien Leopar', 512100, 110, 20, 0, 'Vật phẩm sưu tầm chính hãng: Đồ Chơi Sưu Tầm Quái Thú Nổi Loạn Fuggler Baddies Fuggs 9 Inch - Zuru Toys 15784 - Annoyed Alien Leopar. Chi tiết sắc nét, bản quyền chuẩn, là món quà lưu niệm độc đáo dành cho người yêu thích manga, anime và văn hóa đại chúng.', '/static/covers/coll_fahasa_025.jpg', 'Bản Quyền Quốc Tế (Fuggler)', 'Vật Liệu Đồ Chơi Cao Cấp', 'Cao 9 inch')
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
    
    # 6. Nạp 25 VĂN PHÒNG PHẨM & 25 ĐỒ LƯU NIỆM
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
    print(f"[5/6] Đã nạp thành công 25 mặt hàng Văn phòng phẩm chính hãng.")
    
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
    print(f"[6/6] Đã nạp thành công 25 đồ lưu niệm / Manga Anime Collectibles.")
    
    # 7. Nạp Giỏ hàng & Đơn hàng mẫu
    cur.execute("SELECT user_id FROM customers")
    customers = [r[0] for r in cur.fetchall()]
    
    sample_book_id = 1
    sample_stat_id = 251
    sample_coll_id = 276
    
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
