import React from 'react';
import { Lock, ShieldCheck } from 'lucide-react';
import { formatVND } from '../../api';

export default function OrderSummaryCard({
  cart,
  shippingFee = 0,
  discountAmount = 0,
  isSubmitting,
  onSubmit,
}) {
  const items = cart.items || [];
  const finalTotal = Math.max(0, (cart.subtotal || 0) + shippingFee - discountAmount);

  return (
    <div className="bg-white rounded-3xl border border-stone-200 p-6 shadow-sm space-y-5 sticky top-24">
      <h3 className="font-serif-title font-bold text-base text-stone-900 pb-3 border-b border-stone-100">
        4. Tóm Tắt Đơn Hàng
      </h3>

      {/* Mini Item List */}
      <div className="max-h-60 overflow-y-auto divide-y divide-stone-100 pr-1 space-y-2">
        {items.map((item) => (
          <div key={item.edition_id} className="pt-2 flex items-center justify-between text-xs">
            <div className="flex-1 min-w-0 pr-2">
              <p className="font-bold text-stone-800 truncate">{item.title}</p>
              <p className="text-[10px] text-stone-500">
                {item.binding_type === 'PAPERBACK' ? 'Bìa Mềm' : 'Bìa Cứng'} x {item.quantity}
              </p>
            </div>
            <span className="font-semibold text-stone-800 shrink-0">
              {formatVND(item.subtotal || ((item.unit_price || item.price || 0) * item.quantity))}
            </span>
          </div>
        ))}
      </div>

      {/* Calculations */}
      <div className="pt-3 border-t border-stone-100 space-y-2 text-xs">
        <div className="flex justify-between text-stone-600">
          <span>Tiền sách tạm tính:</span>
          <span className="font-medium text-stone-900">{formatVND(cart.subtotal)}</span>
        </div>

        <div className="flex justify-between text-stone-600">
          <span>Phí vận chuyển:</span>
          <span className="font-medium text-stone-900">{formatVND(shippingFee)}</span>
        </div>

        {discountAmount > 0 && (
          <div className="flex justify-between text-emerald-700 font-semibold">
            <span>Ưu đãi giảm giá:</span>
            <span>-{formatVND(discountAmount)}</span>
          </div>
        )}

        <div className="pt-3 border-t border-stone-200 flex justify-between items-baseline">
          <span className="font-bold text-sm text-stone-900">Tổng thanh toán:</span>
          <span className="font-bold text-xl text-crimson-700">{formatVND(finalTotal)}</span>
        </div>
      </div>

      {/* Submit Button */}
      <button
        onClick={onSubmit}
        disabled={isSubmitting || items.length === 0}
        className="w-full flex items-center justify-center gap-2 px-6 py-3.5 rounded-full bg-crimson-700 hover:bg-crimson-800 text-white text-xs font-bold transition shadow-lg hover:shadow-crimson-900/30 disabled:opacity-40 disabled:cursor-not-allowed"
      >
        <Lock className="w-4 h-4" />
        <span>{isSubmitting ? 'Đang Xử Lý Giao Dịch...' : '🔒 Xác Nhận Đặt Hàng'}</span>
      </button>

      <div className="flex items-center justify-center gap-1.5 text-[11px] text-stone-400 text-center">
        <ShieldCheck className="w-3.5 h-3.5 text-emerald-600" />
        <span>Bảo vệ quyền lợi độc giả • Hoàn tiền 100% nếu sách lỗi</span>
      </div>
    </div>
  );
}
