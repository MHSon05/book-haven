import React from 'react';

export default function Footer() {
  return (
    <footer className="bg-stone-900 text-stone-300 border-t border-stone-800 mt-auto">
      <div className="max-w-7xl mx-auto px-4 py-10">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-8">
          {/* Brand Info */}
          <div className="md:col-span-2 space-y-3">
            <div className="flex items-center gap-2">
              <span className="text-2xl">⛩️</span>
              <span className="font-serif-title font-bold text-xl text-white">BookHaven</span>
            </div>
            <p className="text-xs text-stone-400 leading-relaxed max-w-md">
              Hệ thống Thương mại Điện tử Nhà sách Tinh hoa & Văn học Á Đông.
              Hiện thực hóa đồ án môn Phân tích và Thiết kế Hệ thống Thông tin (ISAD),
              Học viện Công nghệ Bưu chính Viễn thông (PTIT).
            </p>
            <div className="flex flex-wrap gap-2 pt-2 text-[11px]">
              <span className="px-2.5 py-1 rounded-full bg-stone-800 text-emerald-400 border border-stone-700 font-medium">
                ✓ Hanoi Drone Hỏa Tốc
              </span>
              <span className="px-2.5 py-1 rounded-full bg-stone-800 text-blue-400 border border-stone-700 font-medium">
                ✓ VietQR MBBank Động
              </span>
              <span className="px-2.5 py-1 rounded-full bg-stone-800 text-amber-400 border border-stone-700 font-medium">
                ✓ AI Semantic & dHash Visual
              </span>
            </div>
          </div>

          {/* Student Info */}
          <div className="space-y-2">
            <h4 className="text-xs font-bold uppercase tracking-wider text-white">Thành Viên Thực Hiện</h4>
            <ul className="text-xs space-y-1.5 text-stone-400">
              <li><strong className="text-stone-200">Sinh viên:</strong> Mai Hữu Sơn</li>
              <li><strong className="text-stone-200">MSSV:</strong> B23DCAT262</li>
              <li><strong className="text-stone-200">Lớp:</strong> D23CQAT01-B</li>
              <li><strong className="text-stone-200">Khoa:</strong> An toàn Thông tin (PTIT)</li>
            </ul>
          </div>

          {/* Advisor Info */}
          <div className="space-y-2">
            <h4 className="text-xs font-bold uppercase tracking-wider text-white">Giảng Viên Hướng Dẫn</h4>
            <ul className="text-xs space-y-1.5 text-stone-400">
              <li><strong className="text-stone-200">Cố vấn:</strong> PGS. TS. Trần Đình Quế</li>
              <li><strong className="text-stone-200">Học viện:</strong> CN Bưu chính Viễn thông</li>
              <li><strong className="text-stone-200">Học kỳ:</strong> Học kỳ I - Năm học 2026-2027</li>
            </ul>
          </div>
        </div>

        <div className="border-t border-stone-800 pt-6 flex flex-col sm:flex-row items-center justify-between text-xs text-stone-500 gap-2">
          <p>© 2026 BookHaven E-Commerce System. All rights reserved.</p>
          <p>Phục vụ Báo cáo Tiểu luận Phân tích & Thiết kế HTTT</p>
        </div>
      </div>
    </footer>
  );
}
