"""
BookHaven E-Commerce System - Main FastAPI Entrypoint
Điều phối toàn bộ Hệ thống Backend 4 tầng và Background Worker thời gian thực.
Phục vụ Tiểu luận môn Phân tích và Thiết kế Hệ thống Thông tin (ISAD).
"""

import asyncio
import os

from dotenv import load_dotenv

# Nạp cấu hình từ .env
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from src.application.services.inventory_service import InventoryService
from src.infrastructure.database import DatabaseSession
from src.infrastructure.repositories.book_repository import BookRepository
from src.infrastructure.repositories.order_repository import OrderRepository
from src.presentation.api.admin_router import router as admin_router
from src.presentation.api.auth_router import router as auth_router
from src.presentation.api.book_router import router as book_router
from src.presentation.api.cart_router import router as cart_router
from src.presentation.api.chatbot_router import router as chatbot_router
from src.presentation.api.checkout_router import router as checkout_router
from src.presentation.api.payment_router import router as payment_router
from src.presentation.api.search_router import router as search_router

MEDIA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "assets"))
FRONTEND_DIST = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "frontend", "dist")
)
ASSETS_DIR = os.path.join(FRONTEND_DIST, "assets")


# ==================== REAL BACKGROUND WORKER ====================
async def reservation_cleanup_worker():
    """
    Background Worker chạy thời gian thực mỗi 30 giây:
    Quét bản ghi giữ chỗ stock_reservations quá hạn 15 phút (BR05)
    và hoàn trả tồn kho khả dụng cho độc giả khác.
    """
    print(
        "[Background Worker] Real reservation cleanup worker started (Interval: 30s)."
    )
    while True:
        try:
            session = DatabaseSession()
            book_repo = BookRepository(session)
            order_repo = OrderRepository(session)
            inventory_service = InventoryService(session, book_repo, order_repo)

            released = inventory_service.cleanup_expired_reservations()
            if released > 0:
                print(
                    f"[Background Worker] Automatically released {released} expired reservation(s) and canceled unpaid orders."
                )
        except Exception as e:
            print(f"[Background Worker Warning] Error during cleanup check: {e}")

        await asyncio.sleep(30)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Khởi động background task
    worker_task = asyncio.create_task(reservation_cleanup_worker())
    yield
    # Dừng task khi tắt server
    worker_task.cancel()
    try:
        await worker_task
    except asyncio.CancelledError:
        print("[Background Worker] Real reservation worker gracefully shut down.")


# ==================== FASTAPI APP SETUP ====================
app = FastAPI(
    title="BookHaven E-Commerce API",
    description="Backend Hệ thống Thương mại Điện tử Nhà sách BookHaven - Báo cáo PTTKHTTT (Chương 5)",
    version="2.0.0",
    lifespan=lifespan,
)

# Cấu hình CORS mở cho Frontend SPA và các công cụ kiểm thử
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Đăng ký các Router vào tiền tố /api
app.include_router(auth_router, prefix="/api")
app.include_router(book_router, prefix="/api")
app.include_router(cart_router, prefix="/api")
app.include_router(checkout_router, prefix="/api")
app.include_router(search_router, prefix="/api")
app.include_router(chatbot_router, prefix="/api")
app.include_router(payment_router, prefix="/api")
app.include_router(admin_router, prefix="/api")

# Mount thư mục assets phục vụ ảnh bìa sách và sản phẩm
os.makedirs(MEDIA_DIR, exist_ok=True)
app.mount("/static", StaticFiles(directory=MEDIA_DIR), name="static")
app.mount("/media", StaticFiles(directory=MEDIA_DIR), name="media")
COVERS_DIR = os.path.join(MEDIA_DIR, "covers")
if os.path.exists(COVERS_DIR):
    app.mount("/covers", StaticFiles(directory=COVERS_DIR), name="covers")

# Mount thư mục assets của React Frontend build (nếu có)
if os.path.exists(ASSETS_DIR):
    app.mount("/assets", StaticFiles(directory=ASSETS_DIR), name="assets")


@app.get("/api/status")
def get_system_status():
    return {
        "system": "BookHaven E-Commerce API",
        "author": "Mai Hữu Sơn - B23DCAT262",
        "institution": "Học viện Công nghệ Bưu chính Viễn thông (PTIT)",
        "advisor": "PGS. TS. Trần Đình Quế",
        "status": "Operational",
        "version": "2.0.0",
        "docs_url": "/docs",
    }


@app.get("/")
def read_root():
    """Phục vụ file index.html của gói build React 18 hoặc thông tin hệ thống."""
    react_index = os.path.join(FRONTEND_DIST, "index.html")
    if os.path.exists(react_index):
        return FileResponse(react_index)
    return JSONResponse(get_system_status())


@app.get("/{full_path:path}")
def serve_spa_fallback(full_path: str):
    """
    HTML5 History Mode Fallback cho React SPA (tương đương app.get('*') của Express):
    Nếu không phải request API hay tài nguyên tĩnh, trả về index.html để React Router tự điều phối.
    """
    # Nếu client gọi API hoặc tài nguyên tĩnh không tồn tại, trả về 404 chuẩn
    if full_path.startswith(("api/", "assets/", "static/", "media/")):
        return JSONResponse(
            status_code=404, content={"detail": f"Resource /{full_path} not found"}
        )

    react_index = os.path.join(FRONTEND_DIST, "index.html")
    if os.path.exists(react_index):
        return FileResponse(react_index)
    return JSONResponse(
        status_code=404, content={"detail": "Frontend index.html not found"}
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
