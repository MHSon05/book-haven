# 📚 BookHaven - Hệ Thống Thương Mại Điện Tử Nhà Sách

Hệ thống thương mại điện tử nhà sách tuyển chọn phục vụ Báo cáo môn **Phân tích & Thiết kế Hệ thống Thông tin (ISAD)**.

---

## 🚀 Giới Thiệu & Điểm Nổi Bật

- **Kiến trúc 4 tầng chuẩn mực**: Domain-Driven Design (Domain, Application, Infrastructure, Presentation).
- **Kho dữ liệu thực tế**: 250 đầu sách chất lượng cao cào trực tiếp từ CDN Fahasa (gồm 90 tập Manga kinh điển: Conan, Doraemon, Naruto, Jujutsu Kaisen, Spy x Family, Death Note, Attack on Titan,...).
- **Tìm kiếm đa phương thức**: Tìm theo từ khóa và Tìm kiếm ngữ nghĩa bằng vector nhúng AI 384 chiều (`all-MiniLM-L6-v2`).
- **Giao vận Drone hỏa tốc**: Tích hợp Hanoi Drone Express cho đơn hàng $\le 2.000$g, theo dõi không lưu thời gian thực qua Live Flight Radar.
- **Ràng buộc nghiệp vụ chặt chẽ**:
  - Giữ chỗ tồn kho 15 phút (BR05) với Background Worker tự động hoàn kho khi quá hạn.
  - Drone tự hành không người lái bắt buộc trả trước qua VietQR (khóa COD ở cả 2 tầng Frontend và Backend).
- **Phân trang động mượt mà**: 12 cuốn/trang với thuật toán Sliding Window không hardcode số trang.

---

## 🛠 Công Nghệ Sử Dụng

- **Backend**: Python 3.15, FastAPI, SQLite3, Uvicorn, Pydantic v2, PyJWT, Bcrypt, Pytest.
- **Frontend**: React 18, Vite 6, Tailwind CSS, Lucide Icons, Leaflet (Bản đồ Radar Drone), Canvas-Confetti.
- **Thanh toán & Giao vận**: VietQR (MBBank), Hanoi Drone Express, Giao Hàng Nhanh (GHN).

---

## 🔑 Tài Khoản Demo

| Vai trò | Tên đăng nhập | Email | Mật khẩu | Phạm vi quyền hạn |
| :--- | :--- | :--- | :--- | :--- |
| **Quản trị viên (Admin)** | `admin` | `admin@bookhaven.vn` | `admin123` | Cổng Quản trị (`#admin`): Duyệt đơn, điều phối bàn giao Drone/GHN, thống kê doanh thu, nhập hàng kho |
| **Khách hàng (User)** | `user` | `user@bookhaven.vn` | `user123` | Giao diện mua sách, giỏ hàng, thanh toán VietQR, đặt giao Drone, theo dõi đơn hàng |

---

## ⚡ Hướng Dẫn Cài Đặt & Khởi Chạy

### Yêu cầu môi trường
- **Python** 3.10+ (dự án phát triển trên Python 3.15)
- **Node.js** 18+ & **npm**
- **PowerShell** (Windows, nếu dùng script chạy tự động `run.ps1`)

---

### Bước 1: Thiết lập dự án lần đầu (sau khi tải / `git clone`)

> Chỉ cần thực hiện **1 lần duy nhất** ở lần đầu thiết lập máy mới.

#### 1.1. Tạo môi trường ảo & cài thư viện Backend
Mở terminal tại thư mục gốc `book-haven/`:
```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

#### 1.2. Tạo file cấu hình biến môi trường (`.env`)
Đứng tại thư mục `backend/`:
```powershell
Copy-Item .env.example .env
```
Mở `backend/.env` và cập nhật:
- `CF_ACCOUNT_ID`, `CF_API_TOKEN`: điền thông tin Cloudflare Workers AI nếu sử dụng tính năng Chatbot AI.
- `SECRET_KEY`: giữ nguyên khi chạy local hoặc đổi sang chuỗi bí mật riêng.

#### 1.3. Khởi tạo Cơ sở dữ liệu (`backend/db/bookhaven.db`)
*(Bỏ qua bước này nếu thư mục `backend/db/` đã có sẵn file `bookhaven.db` và `backend/assets/covers/`.)*

Đứng tại thư mục `backend/`, chạy kịch bản khởi tạo hợp nhất:
```powershell
.\.venv\Scripts\python.exe scripts/gen_db.py
```
Lệnh này tự động tạo 13 bảng từ `db/schema.sql`, nạp 2 tài khoản mẫu, cào 250 đầu sách & tải ảnh bìa vào `assets/covers/`, đồng thời sinh vector AI (`all-MiniLM-L6-v2`).
- Nếu chỉ muốn tạo schema + tài khoản mẫu nhanh mà không cào sách:
  ```powershell
  .\.venv\Scripts\python.exe scripts/gen_db.py --no-crawl
  ```

#### 1.4. Cài đặt thư viện Frontend
```powershell
cd ..\frontend
npm install
```
*(Nếu dùng `run.ps1` ở bước sau, script cũng sẽ tự chạy `npm install` khi phát hiện chưa có `node_modules`.)*

---

### Bước 2: Khởi chạy hệ thống

#### Cách 1: Chạy tự động bằng PowerShell (`run.ps1` — Khuyên dùng)
Mở terminal tại thư mục gốc `book-haven/`:
```powershell
powershell -ExecutionPolicy Bypass -File .\run.ps1
```
*Script tự động giải phóng cổng `8000` / `5173`, kiểm tra `node_modules`, khởi chạy Backend FastAPI + Frontend Vite trong 2 cửa sổ riêng, chờ mô hình AI nạp xong và tự mở trình duyệt.*

#### Cách 2: Chạy thủ công từng phần (Manual)

**Terminal 1 — Backend (FastAPI `:8000`)**
```powershell
cd backend

# Chạy 1 tiến trình (khuyên dùng, tránh nạp mô hình AI 2 lần)
.\.venv\Scripts\python.exe -m uvicorn main:app --host 0.0.0.0 --port 8000

# Hoặc chạy kèm auto-reload khi chỉnh sửa code Python:
.\.venv\Scripts\python.exe main.py
```
- API Cổng chính: `http://localhost:8000`
- Tài liệu API Swagger UI: `http://localhost:8000/docs`

**Terminal 2 — Frontend (React + Vite `:5173`)**
```powershell
cd frontend
npm run dev
```
- Giao diện người dùng: `http://localhost:5173`
- Trang Quản trị Admin: `http://localhost:5173/#admin`

*(Tuỳ chọn Production Build)*: Nếu muốn phục vụ luôn giao diện React qua cổng `8000` mà không cần chạy `npm run dev`:
```powershell
cd frontend
npm run build
```
Sau khi có `frontend/dist/`, chỉ cần bật Backend (`:8000`) và mở `http://localhost:8000/`.

#### Chạy kiểm thử Backend (Pytest)
```powershell
cd backend
.\.venv\Scripts\pytest.exe
```

---

## 📂 Cấu Trúc Dự Án

```text
book-haven/
├── backend/
│   ├── assets/covers/            # Ảnh bìa sách tải từ CDN Fahasa
│   ├── db/
│   │   ├── bookhaven.db          # CSDL SQLite chuẩn hóa (250 sách, AI vectors)
│   │   └── schema.sql            # Định nghĩa DDL toàn bộ thực thể
│   ├── scripts/
│   │   └── gen_db.py             # Kịch bản hợp nhất: DDL, tài khoản, cào Fahasa & AI vectors
│   ├── src/
│   │   ├── domain/               # Thực thể, Enum, Invariant nghiệp vụ
│   │   ├── application/          # Services: Checkout, Inventory, Auth, Search
│   │   ├── infrastructure/       # Repositories, Database, VietQR, AI Adapter
│   │   └── presentation/api/     # FastAPI Routers
│   ├── tests/                    # 20 kịch bản kiểm thử toàn diện (Pytest)
│   ├── main.py                   # Điểm nạp FastAPI & Background Cleanup Worker
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/           # Admin, Catalog, Checkout, Orders, Detail...
│   │   ├── context/              # AuthContext, CartContext, ToastContext
│   │   ├── App.jsx               # Điều phối Routing SPA
│   │   └── api.js                # Tầng gọi REST API Backend
│   ├── package.json
│   └── vite.config.js
├── run.ps1                       # Trình khởi chạy song song Windows PowerShell
└── README.md
```
