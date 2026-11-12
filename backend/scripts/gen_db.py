"""
Scripts: gen_db.py
Kịch bản hợp nhất duy nhất để khởi tạo CSDL vật lý bookhaven.db, nạp tài khoản hệ thống,
thu thập sách thực tế từ Fahasa (5 chủ đề + 50 đầu Manga kinh điển), tải ảnh bìa,
sinh vector nhúng ngữ nghĩa AI d=384 (all-MiniLM-L6-v2) và kiểm tra tính toàn vẹn.

Sinh viên thực hiện: Mai Hữu Sơn - MSSV: B23DCAT262
GVHD: PGS. TS. Trần Đình Quế - Học viện Công nghệ Bưu chính Viễn thông (PTIT)
"""
import argparse
import hashlib
import html
import io
import json
import os
import random
import re
import sqlite3
import sys
import time
import urllib.request
from typing import Any, Dict, List, Optional, Tuple

import bcrypt
from PIL import Image

# Thiết lập đường dẫn thư mục dự án
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
if BACKEND_DIR not in sys.path:
    sys.path.append(BACKEND_DIR)

from src.infrastructure.adapters.sentence_transformer_adapter import SentenceTransformerAdapter

DB_DIR = os.path.join(BACKEND_DIR, "db")
DEFAULT_DB_PATH = os.path.join(DB_DIR, "bookhaven.db")
SCHEMA_PATH = os.path.join(DB_DIR, "schema.sql")
COVERS_DIR = os.path.join(BACKEND_DIR, "assets", "covers")

EXPECTED_TABLES = [
    "users",
    "authors",
    "publishers",
    "categories",
    "books",
    "book_editions",
    "book_embeddings",
    "carts",
    "cart_items",
    "orders",
    "order_items",
    "stock_reservations",
    "payments",
]

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7",
    "Referer": "https://www.fahasa.com/",
}

BASE_PUBLISHERS = [
    ("PUB_TRE", "NXB Trẻ", "161B Lý Chính Thắng, Phường Võ Thị Sáu, Quận 3, TP.HCM", "hopthu@nxbtre.com.vn", "02839316289"),
    ("PUB_KIMDONG", "NXB Kim Đồng", "55 Quang Trung, Nguyễn Du, Hai Bà Trưng, Hà Nội", "info@nxbkimdong.com.vn", "02439434730"),
    ("PUB_TH", "NXB Tổng Hợp TP.HCM", "62 Nguyễn Thị Minh Khai, Phường Đa Kao, Quận 1, TP.HCM", "tonghop@nxbhcm.com.vn", "02838225340"),
    ("PUB_DANTRI", "NXB Dân Trí", "Số 9, Ngõ 26 Phố Hoàng Cầu, Đống Đa, Hà Nội", "nxbdantri@gmail.com", "02435121234"),
]

PUBLISHER_BASE_ALIASES = {
    "tổng hợp tphcm": "Tổng Hợp TP.HCM",
    "tổng hợp tp.hcm": "Tổng Hợp TP.HCM",
    "tổng hợp thành phố hồ chí minh": "Tổng Hợp TP.HCM",
    "phụ nữ": "Phụ Nữ Việt Nam",
}

NON_NXB_MARKERS = ("công ty", "cty", "nhã nam", "alpha", "first news", "thaiha", "skybooks", "mcbooks")

CATEGORIES = [
    ("CAT_MANGA", "Manga & Truyện tranh", "Truyện tranh Nhật Bản, Manga, Comic, Graphic Novel phong phú dành cho mọi lứa tuổi.", "manga-truyen-tranh"),
    ("CAT_LIT", "Văn học & Nghệ thuật", "Tiểu thuyết kinh điển, văn học thiếu nhi bất hủ và tác phẩm đoạt giải quốc tế.", "van-hoc-nghe-thuat"),
    ("CAT_IT", "Khoa học & Công nghệ", "Sách kiến trúc phần mềm, Clean Code, DDD, AI, thuật toán và hệ thống phân tán.", "khoa-hoc-cong-nghe"),
    ("CAT_SKILL", "Kỹ năng sống & Phát triển", "Sách rèn luyện thói quen tốt, tư duy phản biện, tập trung sâu và năng suất.", "ky-nang-song"),
    ("CAT_ECO", "Kinh tế & Khởi nghiệp", "Sách tài chính cá nhân, khởi nghiệp đổi mới sáng tạo và đầu tư thông minh.", "kinh-te-khoi-nghiep"),
]

CATEGORY_SOURCES = [
    {"id": "CAT_MANGA", "name": "Manga & Truyện tranh", "base_url": "https://www.fahasa.com/sach-trong-nuoc/manga-comic.html"},
    {"id": "CAT_LIT", "name": "Văn học & Nghệ thuật", "base_url": "https://www.fahasa.com/sach-trong-nuoc/van-hoc-trong-nuoc.html"},
    {"id": "CAT_IT", "name": "Khoa học & Công nghệ", "base_url": "https://www.fahasa.com/sach-trong-nuoc/khoa-hoc-ky-thuat.html"},
    {"id": "CAT_SKILL", "name": "Kỹ năng sống & Phát triển", "base_url": "https://www.fahasa.com/sach-trong-nuoc/tam-ly-ky-nang-song.html"},
    {"id": "CAT_ECO", "name": "Kinh tế & Khởi nghiệp", "base_url": "https://www.fahasa.com/sach-trong-nuoc/kinh-te-chinh-tri-phap-ly.html"},
]

BAD_KEYWORDS = [
    "sách theo bộ",
    "sach theo bo",
    "combo",
    "fahasa.com",
    "fahasa",
    "boxset",
    "bộ bài tarot",
    "bài tarot",
    "lịch bloc",
    "văn phòng phẩm",
]

BAD_URL_SLUGS = ["sach-theo-bo", "combo", "fahasa-com", "boxset", "bo-bai-tarot"]

# Danh sách 50+ tập Manga kinh điển (kèm tập dự phòng nếu Fahasa hết hàng một số link lẻ)
SERIES_CONFIG = [
    {
        "series": "Thám Tử Lừng Danh Conan",
        "author": "Gosho Aoyama",
        "publisher": "NXB Kim Đồng",
        "synopsis": (
            "Cậu thám tử học sinh Kudo Shinichi trong một lần điều tra đã bị Tổ chức Áo Đen "
            "ép uống thuốc độc APTX 4869, khiến cơ thể bị teo nhỏ thành học sinh tiểu học dưới "
            "thân phận Edogawa Conan. Conan sống cùng Ran Mori và thám tử Mori Kogoro, âm thầm "
            "phá giải hàng loạt vụ án hóc búa để tìm ra tung tích Tổ chức Áo Đen."
        ),
        "urls": [f"https://www.fahasa.com/tham-tu-lung-danh-conan-tap-{i}.html" for i in range(1, 11)],
    },
    {
        "series": "Doraemon - Chú Mèo Máy Đến Từ Tương Lai",
        "author": "Fujiko F. Fujio",
        "publisher": "NXB Kim Đồng",
        "synopsis": (
            "Chú mèo máy thông minh Doraemon đến từ thế kỷ 22 với chiếc túi thần kỳ chứa đựng "
            "muôn vàn bảo bối tương lai. Cùng cậu bé Nobita hậu đậu nhưng giàu lòng nhân ái, "
            "nhóm bạn Shizuka, Jaian, Suneo trải qua những chuyến phiêu lưu kỳ thú và bài học "
            "cảm động về tình bạn."
        ),
        "urls": [f"https://www.fahasa.com/doraemon-truyen-ngan-tap-{i}.html" for i in range(1, 11)],
    },
    {
        "series": "Naruto",
        "author": "Masashi Kishimoto",
        "publisher": "NXB Kim Đồng",
        "synopsis": (
            "Uzumaki Naruto là cậu bé mồ côi mang trong mình phong ấn Cửu Vĩ Hồ Ly, bị cả làng "
            "Lá xa lánh. Với ý chí kiên định và ước mơ cháy bỏng trở thành Hokage vĩ đại, Naruto "
            "không ngừng nỗ lực rèn luyện nhẫn thuật, sát cánh cùng Đội 7 bảo vệ làng và thế giới ninja."
        ),
        "urls": [f"https://www.fahasa.com/naruto-tap-{i}.html" for i in range(1, 11)],
    },
    {
        "series": "Chú Thuật Hồi Chiến - Jujutsu Kaisen",
        "author": "Gege Akutami",
        "publisher": "NXB Kim Đồng",
        "synopsis": (
            "Itadori Yuji là học sinh trung học sở hữu thể chất phi thường. Sau khi nuốt phải ngón "
            "tay chứa lời nguyền của Vua Lời Nguyền Ryomen Sukuna để bảo vệ bạn bè, Yuji gia nhập "
            "trường Chú thuật Tokyo, dấn thân vào những cuộc chiến sinh tử chống lại các nguyền hồn tà ác."
        ),
        "urls": [f"https://www.fahasa.com/chu-thuat-hoi-chien-tap-{i}.html" for i in range(1, 11)],
    },
    {
        "series": "Spy x Family",
        "author": "Tatsuya Endo",
        "publisher": "NXB Kim Đồng",
        "synopsis": (
            "Điệp viên siêu hạng Twilight phải thành lập một gia đình giả để thực hiện Chiến dịch "
            "Strix nhằm duy trì hòa bình thế giới. Người vợ Yor Briar là nữ sát thủ ngầm, còn cô "
            "con gái nuôi Anya sở hữu năng lực ngoại cảm đọc suy nghĩ. Một gia đình kỳ lạ nhưng đầy ấm áp."
        ),
        "urls": [f"https://www.fahasa.com/spy-x-family-tap-{i}.html" for i in range(1, 11)],
    },
    {
        "series": "Death Note - Cuốn Sổ Tử Thần",
        "author": "Tsugumi Ohba",
        "publisher": "NXB Kim Đồng",
        "synopsis": (
            "Yagami Light, một học sinh thiên tài tình cờ nhặt được cuốn sổ tử thần Death Note của "
            "thần chết Ryuk. Bất kỳ ai bị ghi tên vào cuốn sổ sẽ phải chết. Light quyết định dùng "
            "nó để thanh trừng tội phạm, mở ra cuộc đối đầu trí tuệ đỉnh cao với thám tử lừng danh L."
        ),
        "urls": [f"https://www.fahasa.com/death-note-tap-{i}.html" for i in range(1, 7)],
    },
    {
        "series": "Đại Chiến Titan - Attack on Titan",
        "author": "Hajime Isayama",
        "publisher": "NXB Trẻ",
        "synopsis": (
            "Nhân loại phải sống ẩn mình sau ba bức tường khổng lồ để trốn tránh loài sinh vật ăn "
            "thịt người mang tên Titan. Khi bức tường ngoài cùng bị phá hủy, Eren Yeager thề sẽ gia "
            "nhập Trinh Sát Đoàn để bảo vệ nhân loại và khám phá bí mật thế giới."
        ),
        "urls": [
            "https://www.fahasa.com/dai-chien-titan-tap-2.html",
            "https://www.fahasa.com/dai-chien-titan-tap-5.html",
            "https://www.fahasa.com/dai-chien-titan-tap-7.html",
            "https://www.fahasa.com/dai-chien-titan-tap-9.html",
            "https://www.fahasa.com/dai-chien-titan-tap-10.html",
            "https://www.fahasa.com/dai-chien-titan-tap-11.html",
            "https://www.fahasa.com/dai-chien-titan-tap-14.html",
            "https://www.fahasa.com/dai-chien-titan-tap-15.html",
        ],
    },
]


def hash_pw(password: str) -> str:
    """Mã hóa mật khẩu chuẩn bcrypt với cost factor 12 (khớp AuthService)."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt(12)).decode("utf-8")


def clean_text(text: str) -> str:
    """Loại bỏ thẻ HTML và chuẩn hóa khoảng trắng."""
    if not text:
        return ""
    stripped = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", html.unescape(stripped)).strip()


def make_id(prefix: str, text: str) -> str:
    """Tạo định danh ổn định từ tiền tố và mã băm MD5."""
    digest = hashlib.md5(text.encode("utf-8")).hexdigest()[:8].upper()
    return f"{prefix}_{digest}"


def deterministic_isbn13(url: str) -> str:
    """Sinh mã ISBN-13 ổn định từ URL khi trang sản phẩm thiếu mã hàng 13 chữ số."""
    num = int(hashlib.md5(url.encode("utf-8")).hexdigest()[:12], 16) % 10_000_000_000
    return f"978{num:010d}"


def normalize_publisher_name(raw_name: str) -> str:
    """Chuẩn hóa tên NXB về dạng thống nhất ('NXB <Tên>') để tránh tạo bản ghi trùng lặp."""
    cleaned = clean_text(raw_name)
    if not cleaned:
        return "NXB Trẻ"
    base = re.sub(r"^(?:nhà\s+xuất\s+bản|nxb)\s+", "", cleaned, flags=re.IGNORECASE).strip()
    if not base:
        return "NXB Trẻ"
    if any(marker in base.lower() for marker in NON_NXB_MARKERS):
        return cleaned
    canonical_base = PUBLISHER_BASE_ALIASES.get(base.lower(), base)
    return f"NXB {canonical_base}"


def sanitize_description(raw_desc: str) -> str:
    """Loại bỏ nội dung quảng cáo của nguồn cào và chuẩn hóa thương hiệu BookHaven."""
    desc = re.sub(r"(?i)giá sản phẩm trên fahasa\.com[^\.\n]*[\.\n]?", "", raw_desc or "")
    desc = re.sub(r"(?i)fahasa\.com", "BookHaven", desc)
    desc = re.sub(r"(?i)fahasa", "BookHaven", desc)
    return clean_text(desc)


def is_valid_category_link(url: str, title: str) -> bool:
    """Kiểm tra ứng viên sách đơn lẻ hợp lệ, loại trừ combo/boxset/văn phòng phẩm."""
    url_lower = url.lower()
    if any(bad in url_lower for bad in BAD_URL_SLUGS):
        return False
    title_lower = title.lower()
    return not any(bad in title_lower for bad in BAD_KEYWORDS)


def http_fetch_bytes(url: str, timeout: int = 12, retries: int = 2) -> Optional[bytes]:
    """Tải dữ liệu nhị phân qua HTTP với header trình duyệt chuẩn và retry nhẹ."""
    for attempt in range(retries + 1):
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return resp.read()
        except Exception:
            if attempt < retries:
                time.sleep(0.4 * (attempt + 1))
    return None


def http_fetch_html(url: str, timeout: int = 15, retries: int = 2) -> Optional[str]:
    """Tải nội dung HTML UTF-8 từ URL."""
    raw = http_fetch_bytes(url, timeout=timeout, retries=retries)
    return raw.decode("utf-8", errors="ignore") if raw else None


def fetch_category_product_urls(category_url: str, min_needed: int = 80, max_pages: int = 15) -> List[str]:
    """Quét danh sách URL sản phẩm đơn lẻ theo từng trang danh mục Fahasa."""
    product_urls: List[str] = []
    seen = set()
    page = 1

    while len(product_urls) < min_needed and page <= max_pages:
        url = category_url if page == 1 else f"{category_url}?p={page}"
        content = http_fetch_html(url, timeout=15, retries=1)
        if not content:
            print(f"    [!] Cảnh báo không tải được trang {page}: {url}")
            break

        matches = re.findall(
            r'<a\s+href="(https://www\.fahasa\.com/[^"]+\.html[^"]*)"\s+title="([^"]+)"\s+class="product-image"',
            content,
        )
        if not matches:
            break

        for link, title in matches:
            clean_link = link.split("?")[0]
            if not is_valid_category_link(clean_link, title):
                continue
            if clean_link not in seen:
                seen.add(clean_link)
                product_urls.append(clean_link)

        page += 1
        time.sleep(0.25)

    return product_urls


def _extract_spec_table(page_html: str) -> Dict[str, str]:
    """Trích xuất bảng thông số kỹ thuật chuẩn từ HTML Fahasa."""
    specs: Dict[str, str] = {}
    pattern = (
        r'<th[^>]*class="[^"]*label[^"]*"[^>]*>(.*?)</th>\s*'
        r'<td[^>]*class="[^"]*data[^"]*"[^>]*>(.*?)</td>'
    )
    for th, td in re.findall(pattern, page_html, re.DOTALL):
        key = clean_text(th)
        if key:
            specs[key] = clean_text(td)
    return specs


def parse_fahasa_product(
    page_html: str,
    product_url: str,
    series_meta: Optional[Dict[str, Any]] = None,
) -> Optional[Dict[str, Any]]:
    """
    Bóc tách dữ liệu sách thật từ trang chi tiết Fahasa.
    Với nhóm Manga kinh điển nhiều tập (`series_meta`), dùng tóm tắt series khi trang tập lẻ không ghi cốt truyện dài.
    """
    og_title = re.search(r'<meta\s+property="og:title"\s+content="([^"]+)"', page_html)
    title = clean_text(og_title.group(1)) if og_title else ""
    if not title:
        h1 = re.search(r"<h1[^>]*>(.*?)</h1>", page_html, re.DOTALL)
        title = clean_text(h1.group(1)) if h1 else ""

    if not title or (not series_meta and any(bad in title.lower() for bad in BAD_KEYWORDS)):
        return None

    og_img = re.search(r'<meta\s+property="og:image"\s+content="([^"]+)"', page_html)
    img_url = og_img.group(1).strip() if og_img else ""
    if not img_url:
        img_match = re.search(r'https://cdn1\.fahasa\.com/media/catalog/product/[^\s"\'\<\>]+', page_html)
        img_url = img_match.group(0).strip() if img_match else ""
    if not img_url or "placeholder" in img_url.lower():
        return None

    specs = _extract_spec_table(page_html)

    author_name = specs.get("Tác giả") or specs.get("Tác giả:") or (series_meta or {}).get("author") or "Nhiều tác giả"
    if author_name.lower() in ["đang cập nhật", "n/a", ""]:
        author_name = (series_meta or {}).get("author") or "Nhiều tác giả"

    raw_pub = (
        specs.get("NXB")
        or specs.get("Nhà Xuất Bản")
        or specs.get("Tên Nhà Cung Cấp")
        or (series_meta or {}).get("publisher")
        or "NXB Trẻ"
    )
    publisher_name = normalize_publisher_name(raw_pub)

    year_match = re.search(r"\d{4}", str(specs.get("Năm XB", "2024")))
    publish_year = int(year_match.group(0)) if year_match else 2024

    default_weight = 180 if series_meta else 350
    weight_match = re.search(r"\d+", str(specs.get("Trọng lượng (gr)", default_weight)))
    weight_gram = max(100, int(weight_match.group(0))) if weight_match else default_weight

    raw_format = specs.get("Hình thức", "Bìa Mềm").lower()
    binding_type = "HARDCOVER" if ("cứng" in raw_format or "hardcover" in raw_format) else "PAPERBACK"

    raw_barcode = specs.get("Mã hàng") or specs.get("ISBN") or ""
    if not raw_barcode:
        b_match = re.search(r"Mã hàng.*?<td[^>]*>(.*?)</td>", page_html, re.DOTALL)
        raw_barcode = b_match.group(1) if b_match else ""
    barcode_digits = re.sub(r"\D", "", raw_barcode)
    if len(barcode_digits) != 13:
        barcode_digits = deterministic_isbn13(product_url)

    price_match = re.search(
        r'class="[^"]*special-price[^"]*"[^>]*>.*?(\d[\d\.\,]*)\s*(?:&nbsp;|\s)*đ',
        page_html,
        re.DOTALL,
    )
    if not price_match:
        price_match = re.search(
            r'class="[^"]*price[^"]*"[^>]*>.*?(\d[\d\.\,]*)\s*(?:&nbsp;|\s)*đ',
            page_html,
            re.DOTALL,
        )
    if not price_match:
        return None
    digits = price_match.group(1).replace(".", "").replace(",", "")
    unit_price = int(digits) if digits.isdigit() else 0
    if unit_price <= 0:
        return None

    desc_match = re.search(r'id="desc_content"[^>]*>(.*?)</div>', page_html, re.DOTALL)
    if not desc_match:
        desc_match = re.search(r'class="[^"]*product-tabs-content[^"]*"[^>]*>(.*?)</div>', page_html, re.DOTALL)
    desc = sanitize_description(desc_match.group(1) if desc_match else "")

    min_desc_len = 100 if series_meta else 120
    if len(desc) < min_desc_len or "sách theo bộ" in desc.lower():
        if series_meta:
            desc = (
                f"Tác phẩm {title} thuộc series kinh điển {series_meta['series']} "
                f"của tác giả {series_meta['author']}. {series_meta['synopsis']}"
            )
        else:
            meta_desc = re.search(r'<meta\s+name="description"\s+content="([^"]+)"', page_html)
            desc = sanitize_description(meta_desc.group(1) if meta_desc else "")

    if len(desc) < min_desc_len or "sách theo bộ" in desc.lower():
        return None

    return {
        "title": title,
        "author_name": author_name,
        "publisher_name": publisher_name,
        "publish_year": publish_year,
        "weight_gram": weight_gram,
        "binding_type": binding_type,
        "barcode": barcode_digits,
        "unit_price": unit_price,
        "img_url": img_url,
        "desc": desc,
        "product_url": product_url,
    }


def download_or_reuse_cover(
    img_url: str,
    book_id: str,
    covers_dir: str = COVERS_DIR,
    refresh: bool = False,
) -> Optional[str]:
    """Tải ảnh bìa JPG về assets/covers (tái sử dụng ảnh hợp lệ nếu đã tồn tại và không bật refresh)."""
    os.makedirs(covers_dir, exist_ok=True)
    filename = f"{book_id.lower()}.jpg"
    filepath = os.path.join(covers_dir, filename)
    relative_path = f"/static/covers/{filename}"

    if not refresh and os.path.exists(filepath) and os.path.getsize(filepath) > 1024:
        return relative_path

    raw = http_fetch_bytes(img_url, timeout=12, retries=2)
    if not raw:
        return None

    try:
        img = Image.open(io.BytesIO(raw))
        if img.mode != "RGB":
            img = img.convert("RGB")
        tmp_path = f"{filepath}.tmp"
        img.save(tmp_path, "JPEG", quality=90, optimize=True)
        os.replace(tmp_path, filepath)
        return relative_path
    except Exception as exc:
        print(f"      [!] Lỗi xử lý ảnh bìa ({exc})")
        return None


def get_or_create_author(
    conn: sqlite3.Connection,
    author_name: str,
    biography: str = "Tác giả tiêu biểu trong kho sách BookHaven.",
    nationality: str = "Việt Nam / Quốc tế",
) -> str:
    """Tìm hoặc thêm mới tác giả an toàn (tránh trùng tên và va chạm khóa)."""
    row = conn.execute("SELECT author_id FROM authors WHERE author_name = ?;", (author_name,)).fetchone()
    if row:
        return row[0]
    author_id = make_id("AUTH", author_name)
    conn.execute(
        """
        INSERT OR IGNORE INTO authors (author_id, author_name, biography, nationality)
        VALUES (?, ?, ?, ?);
        """,
        (author_id, author_name, biography, nationality),
    )
    return author_id


def get_or_create_publisher(conn: sqlite3.Connection, publisher_name: str) -> str:
    """Tìm hoặc thêm mới nhà xuất bản đã chuẩn hóa tên."""
    normalized = normalize_publisher_name(publisher_name)
    row = conn.execute("SELECT publisher_id FROM publishers WHERE publisher_name = ?;", (normalized,)).fetchone()
    if row:
        return row[0]
    pub_id = make_id("PUB", normalized)
    conn.execute(
        """
        INSERT OR IGNORE INTO publishers (publisher_id, publisher_name, address, contact_email, phone)
        VALUES (?, ?, ?, ?, ?);
        """,
        (pub_id, normalized, "Hà Nội / TP.HCM", "lienhe@nxb.vn", "19006401"),
    )
    return pub_id


def book_exists(conn: sqlite3.Connection, book_id: str, title: str, barcode: str, sku: str) -> bool:
    """Kiểm tra trùng lặp tác phẩm hoặc mã ấn bản ISBN/SKU trước khi tải ảnh và lưu."""
    if conn.execute("SELECT 1 FROM books WHERE book_id = ? OR title = ?;", (book_id, title)).fetchone():
        return True
    if conn.execute("SELECT 1 FROM book_editions WHERE isbn13 = ? OR sku = ?;", (barcode, sku)).fetchone():
        return True
    return False


def build_embedding_text(title: str, author_name: str, category_name: str, description: str) -> str:
    """Chuẩn hóa chuỗi đầu vào đồng nhất cho SentenceTransformerAdapter (d=384)."""
    return f"{title}. Tác giả: {author_name}. Thể loại: {category_name}. {(description or '')[:350]}"


def reembed_all_books(conn: sqlite3.Connection, transformer: SentenceTransformerAdapter) -> int:
    """Sinh lại toàn bộ vector nhúng AI d=384 trong book_embeddings bằng mô hình đang nạp."""
    rows = conn.execute(
        """
        SELECT b.book_id, b.title, a.author_name, c.category_name, b.description
        FROM books b
        JOIN authors a ON b.author_id = a.author_id
        JOIN categories c ON b.category_id = c.category_id
        WHERE b.is_active = 1;
        """
    ).fetchall()
    if not rows:
        return 0

    conn.execute("BEGIN TRANSACTION;")
    try:
        updated = 0
        for book_id, title, author_name, category_name, desc in rows:
            vector = transformer.encode(build_embedding_text(title, author_name, category_name, desc))
            conn.execute(
                """
                INSERT INTO book_embeddings (embedding_id, book_id, vector_json, model_name)
                VALUES (?, ?, ?, 'all-MiniLM-L6-v2')
                ON CONFLICT(book_id) DO UPDATE SET
                    vector_json = excluded.vector_json,
                    model_name = excluded.model_name;
                """,
                (f"EMB_{book_id}", book_id, json.dumps(vector)),
            )
            updated += 1
        conn.execute("COMMIT;")
        return updated
    except Exception:
        conn.execute("ROLLBACK;")
        raise


def insert_book_bundle(
    conn: sqlite3.Connection,
    cat_id: str,
    cat_name: str,
    book_data: Dict[str, Any],
    covers_dir: str,
    transformer: SentenceTransformerAdapter,
    refresh_covers: bool = False,
    author_bio: str = "Tác giả tiêu biểu trong kho sách BookHaven.",
    nationality: str = "Việt Nam / Quốc tế",
    stock_range: Tuple[int, int] = (35, 95),
) -> Optional[str]:
    """Lưu trọn bộ 1 đầu sách gồm author/publisher/books/book_editions/book_embeddings trong 1 giao dịch."""
    book_id = make_id("BOOK", f"{cat_id}_{book_data['barcode']}")
    sku = f"SKU-{book_data['barcode']}"
    if book_exists(conn, book_id, book_data["title"], book_data["barcode"], sku):
        return None

    cover_path = download_or_reuse_cover(book_data["img_url"], book_id, covers_dir, refresh=refresh_covers)
    if not cover_path:
        return None

    edition_id = f"ED_{sku}"
    stock_qty = random.randint(stock_range[0], stock_range[1])
    embed_text = build_embedding_text(
        book_data["title"], book_data["author_name"], cat_name, book_data["desc"]
    )
    vector = transformer.encode(embed_text)
    emb_id = f"EMB_{book_id}"

    conn.execute("BEGIN TRANSACTION;")
    try:
        author_id = get_or_create_author(conn, book_data["author_name"], author_bio, nationality)
        publisher_id = get_or_create_publisher(conn, book_data["publisher_name"])

        conn.execute(
            """
            INSERT INTO books (book_id, title, author_id, publisher_id, category_id,
                               publish_year, description, cover_image, is_active)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1);
            """,
            (
                book_id,
                book_data["title"],
                author_id,
                publisher_id,
                cat_id,
                book_data["publish_year"],
                book_data["desc"],
                cover_path,
            ),
        )
        conn.execute(
            """
            INSERT INTO book_editions (edition_id, book_id, sku, isbn13, binding_type,
                                         unit_price, weight_gram, stock_on_hand, stock_reserved)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0);
            """,
            (
                edition_id,
                book_id,
                sku,
                book_data["barcode"],
                book_data["binding_type"],
                book_data["unit_price"],
                book_data["weight_gram"],
                stock_qty,
            ),
        )
        conn.execute(
            """
            INSERT INTO book_embeddings (embedding_id, book_id, vector_json, model_name)
            VALUES (?, ?, ?, 'all-MiniLM-L6-v2');
            """,
            (emb_id, book_id, json.dumps(vector)),
        )
        conn.execute("COMMIT;")
        return book_id
    except Exception as exc:
        conn.execute("ROLLBACK;")
        print(f"      [!] Lỗi lưu sách ({exc}), bỏ qua...")
        return None


def cleanup_orphan_wal_files(db_path: str) -> None:
    """Dọn tệp -wal/-shm mồ côi khi file .db chính chưa tồn tại hoặc vừa bị xóa."""
    if os.path.exists(db_path):
        return
    for suffix in ("-wal", "-shm"):
        sidecar = f"{db_path}{suffix}"
        if os.path.exists(sidecar):
            try:
                os.remove(sidecar)
            except OSError:
                pass


def apply_schema(conn: sqlite3.Connection, schema_path: str, reset: bool = True) -> bool:
    """Đọc và thực thi DDL schema.sql (13 bảng & 7 chỉ mục)."""
    if not os.path.exists(schema_path):
        print(f"[!] Lỗi: Không tìm thấy tệp DDL schema tại: {schema_path}")
        return False

    with open(schema_path, "r", encoding="utf-8") as f:
        schema_sql = f.read()

    if reset:
        print("[*] Đang làm sạch toàn bộ bảng và chỉ mục cũ trong CSDL (Clean Slate)...")
        conn.execute("PRAGMA foreign_keys = OFF;")
        existing_tables = [
            r[0]
            for r in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';"
            ).fetchall()
        ]
        for tbl in existing_tables:
            conn.execute(f'DROP TABLE IF EXISTS "{tbl}";')
        existing_indexes = [
            r[0]
            for r in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='index' AND name NOT LIKE 'sqlite_%';"
            ).fetchall()
        ]
        for idx in existing_indexes:
            conn.execute(f'DROP INDEX IF EXISTS "{idx}";')
        print(f"    -> Đã xóa {len(existing_tables)} bảng cũ và {len(existing_indexes)} chỉ mục cũ.")

    conn.execute("PRAGMA foreign_keys = ON;")
    conn.executescript(schema_sql)
    conn.execute("PRAGMA foreign_keys = ON;")
    print("[+] Khởi tạo thành công 13 bảng DDL và các chỉ mục (indexes) từ schema.sql.")
    return True


def seed_accounts_and_metadata(conn: sqlite3.Connection) -> None:
    """Nạp đồng bộ tài khoản hệ thống (admin, user, user_sonmh), giỏ hàng, NXB và 5 thể loại."""
    print("[*] Đồng bộ tài khoản người dùng hệ thống (bcrypt 12 rounds)...")
    seed_users = [
        (
            "USER_ADMIN",
            "admin",
            hash_pw("admin123"),
            "admin@bookhaven.vn",
            "Quản Trị Viên",
            "0912345678",
            "ADMIN",
            "BookHaven HQ, Hà Nội",
            0,
            "Tổng quản lý",
            "Ban Giám Đốc",
        ),
        (
            "USER_USER",
            "user",
            hash_pw("user123"),
            "user@bookhaven.vn",
            "Người Dùng BookHaven",
            "0987654321",
            "CUSTOMER",
            "Km10 Nguyễn Trãi, Hà Đông, Hà Nội",
            100,
            None,
            None,
        ),
        (
            "USER_SONMH",
            "user_sonmh",
            hash_pw("sonmh123"),
            "sonmh.b23dcat262@ptit.edu.vn",
            "Mai Hữu Sơn",
            "0987654321",
            "CUSTOMER",
            "Học viện CNBCVT (PTIT), Km10 Nguyễn Trãi, Hà Đông, Hà Nội",
            150,
            None,
            None,
        ),
    ]

    for row in seed_users:
        user_id, username, pw_hash, email = row[0], row[1], row[2], row[3]
        conn.execute(
            """
            INSERT INTO users (
                user_id, username, password_hash, email, full_name, phone, role,
                shipping_address, loyalty_points, staff_role, department
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(user_id) DO NOTHING;
            """,
            row,
        )
        # Nếu trước đó bị tự tạo ở chế độ GUEST_NO_AUTH thì nâng cấp lại hash chuẩn bcrypt
        conn.execute(
            """
            UPDATE users
            SET username = ?, password_hash = ?, email = ?, full_name = ?, phone = ?,
                role = ?, shipping_address = ?, loyalty_points = ?, staff_role = ?, department = ?
            WHERE user_id = ? AND password_hash = 'GUEST_NO_AUTH';
            """,
            (username, pw_hash, email, row[4], row[5], row[6], row[7], row[8], row[9], row[10], user_id),
        )
        conn.execute(
            "INSERT OR IGNORE INTO carts (cart_id, customer_id) VALUES (?, ?);",
            (f"CART_{user_id}", user_id),
        )

    print("    -> Tài khoản chuẩn: 'admin' (admin123), 'user' (user123), 'user_sonmh' (sonmh123).")

    print("[*] Đồng bộ 4 Nhà xuất bản nền tảng và 5 Thể loại sách...")
    conn.executemany(
        """
        INSERT INTO publishers (publisher_id, publisher_name, address, contact_email, phone)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(publisher_id) DO NOTHING;
        """,
        BASE_PUBLISHERS,
    )
    conn.executemany(
        """
        INSERT INTO categories (category_id, category_name, description, slug)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(category_id) DO NOTHING;
        """,
        CATEGORIES,
    )


def crawl_categories_phase(
    conn: sqlite3.Connection,
    transformer: SentenceTransformerAdapter,
    covers_dir: str,
    target_per_cat: int = 40,
    refresh_covers: bool = False,
) -> int:
    """Giai đoạn 1: Thu thập sách theo 5 danh mục chính từ Fahasa (mặc định 40 cuốn/thể loại)."""
    if target_per_cat <= 0:
        return 0

    added_total = 0
    for idx, cat in enumerate(CATEGORY_SOURCES, 1):
        cat_id, cat_name, base_url = cat["id"], cat["name"], cat["base_url"]
        existing = conn.execute("SELECT COUNT(*) FROM books WHERE category_id = ?;", (cat_id,)).fetchone()[0]
        needed = max(0, target_per_cat - existing)

        print(f"\n[{idx}/{len(CATEGORY_SOURCES)}] Thể loại: {cat_name.upper()} ({cat_id}) | Hiện có: {existing}, Cần thêm: {needed}")
        if needed == 0:
            print("    -> Đã đạt chỉ tiêu danh mục, bỏ qua.")
            continue

        candidate_urls = fetch_category_product_urls(base_url, min_needed=max(needed * 4 + 20, 70), max_pages=15)
        print(f"    -> Quét được {len(candidate_urls)} link ứng viên đơn lẻ.")

        added_in_cat = 0
        for p_url in candidate_urls:
            if added_in_cat >= needed:
                break
            page_html = http_fetch_html(p_url, timeout=15, retries=1)
            if not page_html:
                continue
            book_data = parse_fahasa_product(page_html, p_url, series_meta=None)
            if not book_data:
                continue

            book_id = insert_book_bundle(
                conn=conn,
                cat_id=cat_id,
                cat_name=cat_name,
                book_data=book_data,
                covers_dir=covers_dir,
                transformer=transformer,
                refresh_covers=refresh_covers,
                stock_range=(35, 95),
            )
            if book_id:
                added_in_cat += 1
                added_total += 1
                short_title = book_data["title"][:36] + "..." if len(book_data["title"]) > 36 else book_data["title"]
                print(
                    f"      [✓] #{added_total:<3} ({added_in_cat}/{needed}) | {short_title:<40} | "
                    f"{book_data['unit_price']:>7,} đ | {book_data['weight_gram']:>4}g"
                )
                time.sleep(0.15)

    return added_total


def crawl_popular_manga_phase(
    conn: sqlite3.Connection,
    transformer: SentenceTransformerAdapter,
    covers_dir: str,
    per_cat_base: int = 40,
    manga_target: int = 50,
    refresh_covers: bool = False,
) -> int:
    """Giai đoạn 2: Bổ sung các tập Manga kinh điển nổi tiếng vào CAT_MANGA (mục tiêu tổng 40 + 50 = 90 cuốn)."""
    if manga_target <= 0:
        return 0

    existing_manga = conn.execute("SELECT COUNT(*) FROM books WHERE category_id = 'CAT_MANGA';").fetchone()[0]
    goal_total_manga = per_cat_base + manga_target
    needed_manga = max(0, goal_total_manga - existing_manga)
    needed_manga = min(needed_manga, manga_target) if existing_manga >= per_cat_base else max(needed_manga, manga_target)

    print(f"\n[Manga Kinh Điển] Hiện có {existing_manga} Manga | Mục tiêu tổng CAT_MANGA: {goal_total_manga} (cần nạp thêm: {needed_manga})")
    if existing_manga >= goal_total_manga:
        print("    -> CAT_MANGA đã đủ cả danh mục và 50 tựa kinh điển, bỏ qua.")
        return 0

    added_count = 0
    for config in SERIES_CONFIG:
        if added_count >= needed_manga:
            break
        print(f"  [*] Series: {config['series']} ({config['author']})")
        for url in config["urls"]:
            if added_count >= needed_manga:
                break
            page_html = http_fetch_html(url, timeout=12, retries=1)
            if not page_html:
                continue
            book_data = parse_fahasa_product(page_html, url, series_meta=config)
            if not book_data:
                continue

            book_id = insert_book_bundle(
                conn=conn,
                cat_id="CAT_MANGA",
                cat_name="Manga & Truyện tranh",
                book_data=book_data,
                covers_dir=covers_dir,
                transformer=transformer,
                refresh_covers=refresh_covers,
                author_bio=f"Tác giả manga huyền thoại ({config['author']}).",
                nationality="Nhật Bản",
                stock_range=(45, 99),
            )
            if book_id:
                added_count += 1
                short_title = book_data["title"][:38] + "..." if len(book_data["title"]) > 38 else book_data["title"]
                print(f"   [✓] Manga #{added_count:02d}/{needed_manga} | {short_title:<42} | {book_data['unit_price']:>7,} đ")
                time.sleep(0.12)

    return added_count


def prune_orphan_covers(conn: sqlite3.Connection, covers_dir: str) -> int:
    """Dọn các file ảnh bìa mồ côi trong assets/covers không còn được bản ghi books nào tham chiếu."""
    if not os.path.exists(covers_dir):
        return 0
    referenced = {
        os.path.basename(r[0])
        for r in conn.execute("SELECT cover_image FROM books WHERE cover_image IS NOT NULL;").fetchall()
    }
    removed = 0
    for fname in os.listdir(covers_dir):
        if fname.startswith("book_") and fname.endswith(".jpg") and fname not in referenced:
            try:
                os.remove(os.path.join(covers_dir, fname))
                removed += 1
            except OSError:
                pass
    return removed


def verify_database(conn: sqlite3.Connection) -> bool:
    """Kiểm tra PRAGMA integrity_check, PRAGMA foreign_key_check và thống kê 13 bảng + 7 chỉ mục."""
    print("\n" + "=" * 78)
    print("  KIỂM TRA TÍNH TOÀN VẸN CƠ SỞ DỮ LIỆU (INTEGRITY, FOREIGN KEYS & SCHEMA)")
    print("=" * 78)

    integrity = conn.execute("PRAGMA integrity_check;").fetchone()[0]
    fk_violations = conn.execute("PRAGMA foreign_key_check;").fetchall()
    print(f"[*] PRAGMA integrity_check   : {integrity.upper()}")
    print(f"[*] PRAGMA foreign_key_check : {'OK (0 violations)' if not fk_violations else f'FAIL ({len(fk_violations)} violations)'}")

    tables_found = {
        r[0]
        for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';").fetchall()
    }
    indexes_found = [
        r[0]
        for r in conn.execute("SELECT name FROM sqlite_master WHERE type='index' AND name NOT LIKE 'sqlite_%';").fetchall()
    ]

    print(f"[*] Số bảng: {len(tables_found)}/{len(EXPECTED_TABLES)} | Số chỉ mục (custom indexes): {len(indexes_found)}")
    print("-" * 78)
    print(f"{'STT':<4} | {'Tên Bảng (Physical Table)':<24} | {'Số Cột':<8} | {'Số Bản Ghi':<12} | {'Trạng Thái'}")
    print("-" * 78)

    all_ok = (integrity.lower() == "ok") and (len(fk_violations) == 0)
    for idx, table in enumerate(EXPECTED_TABLES, 1):
        if table in tables_found:
            col_count = len(conn.execute(f"PRAGMA table_info({table});").fetchall())
            row_count = conn.execute(f"SELECT COUNT(*) FROM {table};").fetchone()[0]
            status = "EMPTY" if row_count == 0 else f"{row_count} records"
            print(f"{idx:<4} | {table:<24} | {col_count:<8} | {row_count:<12} | [OK] {status}")
        else:
            print(f"{idx:<4} | {table:<24} | {'-':<8} | {'-':<12} | [FAIL] THIẾU BẢNG")
            all_ok = False
    print("-" * 78)

    if all_ok:
        print("[SUCCESS] CSDL bookhaven.db đạt chuẩn 100% (13 bảng, toàn vẹn B-tree & Khóa ngoại)!")
    else:
        print("[WARNING] Phát hiện sai lệch cấu trúc hoặc toàn vẹn dữ liệu.")
    return all_ok


def build_database(
    db_path: str = DEFAULT_DB_PATH,
    schema_path: str = SCHEMA_PATH,
    covers_dir: str = COVERS_DIR,
    reset: bool = True,
    schema_only: bool = False,
    crawl: bool = True,
    per_cat: int = 40,
    manga_target: int = 50,
    refresh_covers: bool = False,
    prune_covers: bool = False,
    reembed: bool = False,
) -> bool:
    """Điều phối trọn gói quy trình khởi tạo DB + Tài khoản + Cào dữ liệu + Embedding + Kiểm tra."""
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(line_buffering=True)

    print("=" * 78)
    print("  BOOKHAVEN E-COMMERCE - UNIFIED DATABASE & DATA GENERATOR (gen_db.py)")
    print("  Học viện Công nghệ Bưu chính Viễn thông (PTIT) - MSSV: B23DCAT262")
    print("=" * 78)

    os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
    cleanup_orphan_wal_files(db_path)

    conn = sqlite3.connect(db_path, isolation_level=None)
    try:
        if not apply_schema(conn, schema_path, reset=reset):
            return False

        if not schema_only:
            seed_accounts_and_metadata(conn)
            transformer: Optional[SentenceTransformerAdapter] = None

            if crawl:
                start_ts = time.time()
                print("\n[*] Đang nạp mô hình AI Sentence-Transformers (all-MiniLM-L6-v2)...")
                transformer = SentenceTransformerAdapter()

                added_cat = crawl_categories_phase(
                    conn=conn,
                    transformer=transformer,
                    covers_dir=covers_dir,
                    target_per_cat=per_cat,
                    refresh_covers=refresh_covers,
                )
                added_manga = crawl_popular_manga_phase(
                    conn=conn,
                    transformer=transformer,
                    covers_dir=covers_dir,
                    per_cat_base=per_cat,
                    manga_target=manga_target,
                    refresh_covers=refresh_covers,
                )

                total_books = conn.execute("SELECT COUNT(*) FROM books;").fetchone()[0]
                is_default_db = os.path.abspath(db_path) == os.path.abspath(DEFAULT_DB_PATH)
                expected_min = per_cat * len(CATEGORY_SOURCES) + manga_target
                if (prune_covers or (reset and is_default_db)) and total_books >= expected_min:
                    pruned = prune_orphan_covers(conn, covers_dir)
                    if pruned:
                        print(f"[*] Đã dọn {pruned} ảnh bìa mồ côi khỏi {covers_dir}.")

                print(
                    f"\n[+] Hoàn tất thu thập: +{added_cat} sách danh mục, +{added_manga} Manga kinh điển "
                    f"(Tổng hiện có: {total_books} sách trong {time.time() - start_ts:.1f}s)."
                )

            if reembed:
                if transformer is None:
                    print("\n[*] Đang nạp mô hình AI Sentence-Transformers (all-MiniLM-L6-v2)...")
                    transformer = SentenceTransformerAdapter()
                t0 = time.time()
                updated = reembed_all_books(conn, transformer)
                print(f"[+] Đã cập nhật lại {updated} vector AI trong book_embeddings ({time.time() - t0:.1f}s).")
        else:
            print("[*] Chế độ --schema-only: Chỉ thực thi DDL & kiểm tra tính toàn vẹn.")

        return verify_database(conn)
    finally:
        conn.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Tạo CSDL BookHaven (13 bảng), tài khoản mẫu, cào dữ liệu Fahasa và sinh AI embeddings."
    )
    parser.add_argument("--no-reset", action="store_true", help="Giữ lại bảng & dữ liệu hiện có, chỉ bổ sung phần thiếu.")
    parser.add_argument("--schema-only", action="store_true", help="Chỉ tạo/kiểm tra schema 13 bảng, không nạp tài khoản hay sách.")
    parser.add_argument("--no-crawl", action="store_true", help="Tạo schema và tài khoản/danh mục, bỏ qua bước cào sách từ Fahasa.")
    parser.add_argument("--reembed", action="store_true", help="Sinh lại toàn bộ vector AI 384 chiều cho các sách đang có trong DB.")
    parser.add_argument("--per-cat", type=int, default=40, help="Số đầu sách mỗi thể loại ở giai đoạn 1 (mặc định: 40 -> 200 cuốn).")
    parser.add_argument("--manga-target", type=int, default=50, help="Số tập Manga kinh điển bổ sung ở giai đoạn 2 (mặc định: 50).")
    parser.add_argument("--refresh-covers", action="store_true", help="Tải lại toàn bộ ảnh bìa kể cả khi file đã tồn tại cục bộ.")
    parser.add_argument("--prune-covers", action="store_true", help="Xóa các ảnh bìa mồ côi không còn bản ghi sách tham chiếu.")
    parser.add_argument("--covers-dir", default=COVERS_DIR, help="Thư mục lưu ảnh bìa (mặc định: backend/assets/covers).")
    parser.add_argument("--db-path", default=DEFAULT_DB_PATH, help="Đường dẫn file SQLite đích (mặc định: backend/db/bookhaven.db).")

    args = parser.parse_args()
    ok = build_database(
        db_path=args.db_path,
        schema_path=SCHEMA_PATH,
        covers_dir=args.covers_dir,
        reset=not args.no_reset,
        schema_only=args.schema_only,
        crawl=not args.no_crawl,
        per_cat=args.per_cat,
        manga_target=args.manga_target,
        refresh_covers=args.refresh_covers,
        prune_covers=args.prune_covers,
        reembed=args.reembed,
    )
    sys.exit(0 if ok else 1)
