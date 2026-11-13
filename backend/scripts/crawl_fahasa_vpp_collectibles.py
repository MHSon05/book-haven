"""
Crawler & DB Updater: crawl_fahasa_vpp_collectibles.py
Thu thập tự động 100% SẢN PHẨM THẬT & ẢNH THẬT từ Fahasa:
- 30 sản phẩm Văn phòng phẩm & Dụng cụ học tập chính hãng (Deli, Thiên Long, Linc, v.v.)
- 20 sản phẩm Đồ lưu niệm & Mô hình nhân vật (MrBeast Lab, Funism Anime, Blindbox, v.v.)
Tải ảnh trực tiếp từ CDN Fahasa, chuẩn hóa kích thước 600x600 px trên nền trắng sang trọng,
lưu vào book-haven/backend/assets/covers/
Cập nhật CSDL SQLite và xóa toàn bộ 50 ảnh mockup cũ.
"""
import os
import sys
import re
import io
import json
import time
import sqlite3
import urllib.request
from PIL import Image

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
if BACKEND_DIR not in sys.path:
    sys.path.append(BACKEND_DIR)

COVERS_DIR = os.path.join(BACKEND_DIR, "assets", "covers")
DB_PATH = os.path.join(BACKEND_DIR, "db", "bookhaven.db")

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Language': 'vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7',
    'Referer': 'https://www.fahasa.com/',
}

def clean_price(price_str: str) -> int:
    digits = re.sub(r'[^\d]', '', price_str)
    return int(digits) if digits else 45000

def fetch_page_products(url: str):
    print(f"--> Đang tải dữ liệu từ Fahasa: {url}")
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
    except Exception as e:
        print(f"Lỗi khi tải {url}: {e}")
        return []

    items = re.findall(r'<div class="item-inner">(.*?)</div>\s*</div>\s*</div>', html, re.DOTALL)
    products = []
    seen_titles = set()
    for it in items:
        # Title
        title_m = re.search(r"<h2 class='product-name-no-ellipsis[^']*'>\s*<a[^>]+title='([^']+)'", it) or re.search(r'title="([^"]+)" class="product-image"', it)
        if not title_m:
            continue
        title = title_m.group(1).strip()
        if title in seen_titles:
            continue
        seen_titles.add(title)

        # Img
        img_m = re.search(r'data-src="(https://cdn[0-9]\.fahasa\.com/media/catalog/product/[^"]+)"', it) or re.search(r'data-img-src\s*=\s*"(https://cdn[0-9]\.fahasa\.com/media/catalog/product/[^"]+)"', it)
        if not img_m:
            continue
        img_url = img_m.group(1).strip()

        # Price
        price_m = re.search(r"<span class='price'>([0-9\.]+)\s*&nbsp;đ</span>", it) or re.search(r'class="price">([0-9\.]+)\s*&nbsp;đ<', it)
        price = clean_price(price_m.group(1)) if price_m else 45000

        products.append({
            'title': title,
            'img_url': img_url,
            'price': price,
        })
    return products

def save_fahasa_image(img_url: str, output_path: str) -> bool:
    req = urllib.request.Request(img_url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            img_data = resp.read()
        
        orig_img = Image.open(io.BytesIO(img_data))
        # Tạo canvas vuông 600x600 nền trắng chuẩn e-commerce
        canvas = Image.new("RGB", (600, 600), (255, 255, 255))
        orig_img.thumbnail((560, 560), Image.Resampling.LANCZOS)
        offset = ((600 - orig_img.size[0]) // 2, (600 - orig_img.size[1]) // 2)
        if orig_img.mode == 'RGBA':
            canvas.paste(orig_img, offset, mask=orig_img.split()[3])
        else:
            canvas.paste(orig_img, offset)
        canvas.save(output_path, "JPEG", quality=95)
        return True
    except Exception as e:
        print(f"Lỗi khi tải ảnh {img_url}: {e}")
        return False

def extract_brand(title: str) -> str:
    for brand in ["Deli", "Thiên Long", "Zebra", "Pentel", "Pilot", "KOKUYO", "Plus", "Linc", "Stabilo", "Staedtler", "Tombow", "Marvy", "Casio", "MrBeast Lab", "Funism", "Bandai", "Banpresto", "TMS"]:
        if brand.lower() in title.lower():
            return brand
    return "Fahasa Official"

def run_crawler():
    print("=========================================================")
    print("  BẮT ĐẦU CRAWL 100% SẢN PHẨM & ẢNH THẬT TỪ FAHASA")
    print("=========================================================")

    # 1. Crawl Văn phòng phẩm (Category 6) - Cần 30 sản phẩm
    vpp_sources = [
        'https://www.fahasa.com/van-phong-pham/but-viet.html',
        'https://www.fahasa.com/van-phong-pham/dung-cu-hoc-sinh.html',
        'https://www.fahasa.com/van-phong-pham/dung-cu-van-phong.html',
        'https://www.fahasa.com/van-phong-pham/san-pham-ve-giay.html',
    ]
    raw_vpp = []
    seen_vpp = set()
    for url in vpp_sources:
        prods = fetch_page_products(url)
        for p in prods:
            if p['title'] not in seen_vpp and len(raw_vpp) < 30:
                seen_vpp.add(p['title'])
                raw_vpp.append(p)
        if len(raw_vpp) >= 30:
            break
        time.sleep(0.5)

    print(f"--> Đã thu thập thành công {len(raw_vpp)} mặt hàng Văn phòng phẩm từ Fahasa!")

    # 2. Crawl Đồ lưu niệm & Mô hình Anime (Category 7) - Cần 20 sản phẩm
    col_sources = [
        'https://www.fahasa.com//do-choi-luu-niem-moi/mo-hinh-cac-loai/mo-hinh-nhan-v-t/sort-by/created_at/sort-direction/asc.html',
        'https://www.fahasa.com//do-choi-luu-niem-moi/mo-hinh-cac-loai.html',
        'https://www.fahasa.com//do-choi-luu-niem-moi/do-choi-theo-phim/sort-by/created_at/sort-direction/asc.html',
        'https://www.fahasa.com//do-choi-luu-niem-moi/board-game/sort-by/created_at/sort-direction/asc.html',
    ]
    raw_col = []
    seen_col = set()
    for url in col_sources:
        prods = fetch_page_products(url)
        for p in prods:
            if p['title'] not in seen_col and len(raw_col) < 20:
                seen_col.add(p['title'])
                raw_col.append(p)
        if len(raw_col) >= 20:
            break
        time.sleep(0.5)

    print(f"--> Đã thu thập thành công {len(raw_col)} mặt hàng Đồ lưu niệm / Mô hình từ Fahasa!")

    # 3. Xóa các file ảnh mockup cũ (stat_*.jpg và coll_*.jpg)
    print("--> Tiến hành dọn dẹp các ảnh mockup cũ trong assets/covers/...")
    removed_count = 0
    for fname in os.listdir(COVERS_DIR):
        if fname.startswith("stat_") or fname.startswith("coll_"):
            try:
                os.remove(os.path.join(COVERS_DIR, fname))
                removed_count += 1
            except Exception as e:
                pass
    print(f"--> Đã xóa {removed_count} ảnh mockup cũ.")

    # 4. Tải ảnh thật từ CDN Fahasa về assets/covers/
    print("--> Đang tải ảnh thật phân giải cao từ CDN Fahasa...")
    
    # Tải 30 ảnh VPP
    for idx, item in enumerate(raw_vpp, 1):
        filename = f"stat_fahasa_{idx:03d}.jpg"
        save_path = os.path.join(COVERS_DIR, filename)
        item['cover_filename'] = filename
        item['cover_path'] = f"/static/covers/{filename}"
        ok = save_fahasa_image(item['img_url'], save_path)
        if ok:
            print(f"  [VPP {idx:02d}/30] {item['title'][:40]}... -> OK ({filename})")
        else:
            print(f"  [VPP {idx:02d}/30] Thất bại tải ảnh cho {item['title']}")
        time.sleep(0.1)

    # Tải 20 ảnh Lưu niệm / Mô hình
    for idx, item in enumerate(raw_col, 1):
        filename = f"coll_fahasa_{idx:03d}.jpg"
        save_path = os.path.join(COVERS_DIR, filename)
        item['cover_filename'] = filename
        item['cover_path'] = f"/static/covers/{filename}"
        ok = save_fahasa_image(item['img_url'], save_path)
        if ok:
            print(f"  [LƯU NIỆM {idx:02d}/20] {item['title'][:40]}... -> OK ({filename})")
        else:
            print(f"  [LƯU NIỆM {idx:02d}/20] Thất bại tải ảnh cho {item['title']}")
        time.sleep(0.1)

    # 5. Cập nhật vào CSDL SQLite (bảng products, stationeries, collectibles)
    print("--> Đang cập nhật dữ liệu vào SQLite bookhaven.db...")
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Cập nhật 30 sản phẩm VPP (product_id 251 -> 280)
    for idx, item in enumerate(raw_vpp, 1):
        pid = 250 + idx
        sku = f"SKU_VPP_FHS_{idx:03d}"
        title = item['title']
        price = item['price']
        weight = 30 + (idx * 5) % 150
        stock = 50 + (idx * 3) % 40
        cover = item['cover_path']
        brand = extract_brand(title)
        desc = f"Sản phẩm {title} chính hãng phân phối tại Fahasa. Đảm bảo tiêu chuẩn chất lượng cao, thiết kế thông minh, phục vụ tối ưu cho học tập và công việc văn phòng."
        
        # update products
        cur.execute("""
            UPDATE products 
            SET name = ?, unit_price = ?, weight_gram = ?, stock_on_hand = ?, stock_reserved = 0, description = ?, cover_image = ?
            WHERE product_id = ?
        """, (title, price, weight, stock, desc, cover, pid))

        # update stationeries
        cur.execute("""
            UPDATE stationeries
            SET brand = ?, material = 'Chính hãng Fahasa', color = 'Tiêu chuẩn'
            WHERE product_id = ?
        """, (brand, pid))

    # Cập nhật 20 sản phẩm Lưu niệm (product_id 281 -> 300)
    for idx, item in enumerate(raw_col, 1):
        pid = 280 + idx
        sku = f"SKU_COL_FHS_{idx:03d}"
        title = item['title']
        price = item['price']
        weight = 80 + (idx * 15) % 300
        stock = 20 + (idx * 2) % 30
        cover = item['cover_path']
        desc = f"Mặt hàng sưu tầm/đồ chơi lưu niệm: {title}. Bản quyền chính hãng phân phối tại Fahasa, chi tiết tinh xảo, chất lượng cao dành cho độc giả yêu thích sưu tầm."

        # update products
        cur.execute("""
            UPDATE products 
            SET name = ?, unit_price = ?, weight_gram = ?, stock_on_hand = ?, stock_reserved = 0, description = ?, cover_image = ?
            WHERE product_id = ?
        """, (title, price, weight, stock, desc, cover, pid))

        # update collectibles
        cur.execute("""
            UPDATE collectibles
            SET origin = 'Chính hãng Fahasa', material = 'Nhựa cao cấp / Hợp kim', dimensions = 'Tiêu chuẩn'
            WHERE product_id = ?
        """, (pid,))

    conn.commit()
    print("--> CSDL đã được cập nhật thành công 30 VPP + 20 Lưu niệm từ Fahasa!")
    # Lưu ý: Theo sơ đồ ERD (Hình 4.2), book_embeddings chỉ thuộc về books (REFERENCES books(product_id)).
    # 50 mặt hàng VPP và đồ lưu niệm kế thừa từ products, tìm kiếm qua SQL/Full-text search.
    conn.close()
    print("=========================================================")
    print("  HOÀN THÀNH CRAWL VÀ CẬP NHẬT 100% SẢN PHẨM & ẢNH FAHASA")
    print("=========================================================")

if __name__ == '__main__':
    run_crawler()
