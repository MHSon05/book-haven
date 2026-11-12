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

### Cách 1: Khởi chạy nhanh song song bằng PowerShell (Khuyên dùng)

Mở terminal tại thư mục `book-haven`:
```powershell
powershell -ExecutionPolicy Bypass -File .\run.ps1
```
*Script tự động dọn cổng 8000/5173, khởi động Backend + Frontend trong 2 cửa sổ riêng và tự mở trình duyệt web.*

---

### Cách 2: Khởi chạy thủ công từng phần

#### 1. Khởi động Backend (FastAPI :8000)
```powershell
cd backend

# Kích hoạt virtualenv và chạy máy chủ
.\.venv\Scripts\python.exe main.py
```
- API Cổng chính: `http://localhost:8000`
- Tài liệu API Swagger UI: `http://localhost:8000/docs`
- Kiểm thử toàn bộ 20 unit test:
  ```powershell
  .\.venv\Scripts\pytest.exe
  ```

#### 2. Khởi động Frontend (React + Vite :5173)
```powershell
cd frontend

# Chạy môi trường Dev
npm run dev

# Hoặc build production
npm run build
```
- Giao diện người dùng: `http://localhost:5173`
- Trang Quản trị Admin: `http://localhost:5173/#admin`

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
