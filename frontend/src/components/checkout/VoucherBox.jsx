import React, { useState } from 'react';
import { Tag, Check } from 'lucide-react';
import { useToast } from '../../context/ToastContext';

export default function VoucherBox({
  subtotal = 0,
  shippingFee = 0,
  appliedVoucher,
  onApplyVoucher,
}) {
  const { showToast } = useToast();
  const [code, setCode] = useState('');

  const handleApply = (e) => {
    e.preventDefault();
    const cleanCode = code.trim().toUpperCase();

    if (!cleanCode) return;

    if (cleanCode === 'VOUCHER10' || cleanCode === 'BOOKHAVEN10') {
      const discount = Math.min(50000, Math.round(subtotal * 0.1));
      onApplyVoucher(cleanCode, discount);
      showToast(`Áp dụng voucher ${cleanCode} thành công! Giảm 10% (tối đa 50k)`, 'success');
    } else if (cleanCode === 'FREESHIP') {
      onApplyVoucher(cleanCode, shippingFee);
      showToast('Áp dụng mã FREESHIP thành công! Miễn phí vận chuyển', 'success');
    } else {
      showToast('Mã ưu đãi không hợp lệ!', 'error');
    }
  };

  return (
    <div className="bg-white rounded-3xl border border-stone-200 p-6 shadow-sm space-y-3">
      <div className="flex items-center gap-2 pb-2 border-b border-stone-100">
        <Tag className="w-4 h-4 text-crimson-700" />
        <h3 className="font-serif-title font-bold text-sm text-stone-900">
          Mã Ưu Đãi / Voucher Độc Quyền
        </h3>
      </div>

      <form onSubmit={handleApply} className="flex gap-2">
        <input
          type="text"
          placeholder="Nhập mã (BOOKHAVEN10, FREESHIP)..."
          value={code}
          onChange={(e) => setCode(e.target.value)}
          className="flex-1 bg-stone-50 border border-stone-300 rounded-xl px-3 py-2 text-xs text-stone-800 uppercase font-mono font-bold focus:outline-none focus:ring-2 focus:ring-crimson-700/20"
        />
        <button
          type="submit"
          className="px-4 py-2 rounded-xl bg-stone-900 hover:bg-black text-white text-xs font-bold transition shadow shrink-0"
        >
          Áp dụng
        </button>
      </form>

      {appliedVoucher && (
        <div className="flex items-center gap-1.5 text-xs text-emerald-700 font-bold bg-emerald-50 border border-emerald-200 px-3 py-1.5 rounded-xl">
          <Check className="w-4 h-4" />
          <span>Đã áp dụng mã: {appliedVoucher}</span>
        </div>
      )}

      <p className="text-[11px] text-stone-400">
        Gợi ý: Dùng mã <strong>BOOKHAVEN10</strong> để giảm 10% hoặc <strong>FREESHIP</strong> để miễn phí ship.
      </p>
    </div>
  );
}
