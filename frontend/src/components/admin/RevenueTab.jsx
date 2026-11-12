import React, { useState, useEffect } from 'react';
import { DollarSign, ShoppingBag, TrendingUp, Award } from 'lucide-react';
import { adminApi, formatVND } from '../../api';
import { useToast } from '../../context/ToastContext';

export default function RevenueTab() {
  const { showToast } = useToast();
  const [report, setReport] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    adminApi
      .getRevenueReport()
      .then((data) => setReport(data))
      .catch((err) => showToast('Lỗi nạp báo cáo doanh thu: ' + err.message, 'error'))
      .finally(() => setIsLoading(false));
  }, [showToast]);

  if (isLoading) {
    return (
      <div className="py-16 text-center text-xs text-stone-500">
        Đang tính toán dòng tiền thực thu...
      </div>
    );
  }

  const topBooks = report?.top_selling_books || report?.top_books || [];

  return (
    <div className="space-y-6 animate-fadeIn">
      {/* Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="bg-white p-5 rounded-2xl border border-stone-200 shadow-sm flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-emerald-100 text-emerald-700 flex items-center justify-center shrink-0">
            <DollarSign className="w-6 h-6" />
          </div>
          <div>
            <span className="text-[11px] font-bold uppercase tracking-wider text-stone-400 block">
              Doanh Thu Thực Thu (BR06)
            </span>
            <span className="text-xl font-bold text-stone-900">
              {formatVND(report?.total_revenue || 0)}
            </span>
            <span className="block text-[10px] text-stone-500 mt-0.5">
              Chỉ tính các đơn PAID & DELIVERED
            </span>
          </div>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-stone-200 shadow-sm flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-blue-100 text-blue-700 flex items-center justify-center shrink-0">
            <ShoppingBag className="w-6 h-6" />
          </div>
          <div>
            <span className="text-[11px] font-bold uppercase tracking-wider text-stone-400 block">
              Đơn Khớp Tiền MBBank
            </span>
            <span className="text-xl font-bold text-stone-900">
              {report?.paid_orders_count || 0} đơn
            </span>
            <span className="block text-[10px] text-stone-500 mt-0.5">
              Đã ghi nhận giao dịch thành công
            </span>
          </div>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-stone-200 shadow-sm flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-amber-100 text-amber-700 flex items-center justify-center shrink-0">
            <TrendingUp className="w-6 h-6" />
          </div>
          <div>
            <span className="text-[11px] font-bold uppercase tracking-wider text-stone-400 block">
              Tổng Sản Phẩm Xuất Kho
            </span>
            <span className="text-xl font-bold text-stone-900">
              {report?.total_items_sold || 0} ấn bản
            </span>
            <span className="block text-[10px] text-stone-500 mt-0.5">
              Bìa mềm & bìa cứng sưu tầm
            </span>
          </div>
        </div>
      </div>

      {/* Top 5 Best Sellers */}
      <div className="bg-white rounded-2xl border border-stone-200 p-6 shadow-sm space-y-4">
        <div className="flex items-center gap-2 pb-3 border-b border-stone-100">
          <Award className="w-5 h-5 text-crimson-700" />
          <h3 className="font-serif-title font-bold text-base text-stone-900">
            Top 5 Tựa Sách Bán Chạy Nhất (Theo Dòng Tiền Thực Tế)
          </h3>
        </div>

        {topBooks.length === 0 ? (
          <p className="text-xs text-stone-400 py-6 text-center">Chưa có dữ liệu bán sách</p>
        ) : (
          <div className="divide-y divide-stone-100">
            {topBooks.map((b, idx) => (
              <div key={idx} className="py-3 flex items-center justify-between text-xs">
                <div className="flex items-center gap-3">
                  <span
                    className={`w-6 h-6 rounded-full flex items-center justify-center font-bold text-[11px] shrink-0 ${
                      idx === 0
                        ? 'bg-amber-100 text-amber-800'
                        : idx === 1
                        ? 'bg-stone-200 text-stone-700'
                        : idx === 2
                        ? 'bg-amber-700/20 text-amber-900'
                        : 'bg-stone-100 text-stone-500'
                    }`}
                  >
                    {idx + 1}
                  </span>
                  <div>
                    <h4 className="font-bold text-stone-900">{b.title}</h4>
                    <p className="text-[11px] text-stone-500">Đã bán: {b.total_sold ?? b.sold_quantity ?? 0} ấn phẩm</p>
                  </div>
                </div>

                <span className="font-bold text-crimson-700 text-sm">
                  {formatVND(b.revenue)}
                </span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
