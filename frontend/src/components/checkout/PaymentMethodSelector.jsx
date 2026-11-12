import React from 'react';
import { QrCode, Banknote, AlertTriangle } from 'lucide-react';

export default function PaymentMethodSelector({ selectedMethod, onSelectMethod, isDroneSelected = false }) {
  const methods = [
    {
      id: 'VIETQR',
      name: 'Chuyển Khoản Ngân Hàng VietQR (MBBank)',
      desc: 'Quét mã VietQR tiện lợi, giữ chỗ kho 15 phút an toàn (BR03)',
      icon: <QrCode className="w-5 h-5 text-crimson-700" />,
      badge: 'Khuyên Dùng',
      disabled: false,
    },
    {
      id: 'COD',
      name: 'Thanh Toán Tiền Mặt Khi Nhận Hàng (COD)',
      desc: isDroneSelected
        ? 'Drone tự hành không người lái không thể thu tiền mặt. Vui lòng thanh toán VietQR.'
        : 'Nhận sách, kiểm tra quy cách ấn bản rồi thanh toán',
      icon: <Banknote className="w-5 h-5 text-stone-700" />,
      disabled: isDroneSelected,
      badge: isDroneSelected ? 'Không Khả Dụng Với Drone' : null,
      badgeColor: 'bg-amber-100 text-amber-800 border border-amber-300',
    },
  ];

  return (
    <div className="bg-white rounded-3xl border border-stone-200 p-6 shadow-sm space-y-4">
      <div className="flex items-center gap-2 pb-3 border-b border-stone-100">
        <QrCode className="w-5 h-5 text-crimson-700" />
        <h3 className="font-serif-title font-bold text-base text-stone-900">
          3. Phương Thức Thanh Toán
        </h3>
      </div>

      <div className="space-y-3">
        {methods.map((m) => {
          const isSelected = selectedMethod === m.id;
          const isDisabled = m.disabled;

          return (
            <div
              key={m.id}
              onClick={() => {
                if (!isDisabled) {
                  onSelectMethod(m.id);
                }
              }}
              className={`p-4 rounded-2xl border transition relative flex items-center justify-between ${
                isDisabled
                  ? 'border-dashed border-stone-300 bg-stone-50/80 opacity-60 cursor-not-allowed select-none'
                  : isSelected
                  ? 'border-crimson-700 bg-crimson-50/30 ring-2 ring-crimson-700/20 cursor-pointer'
                  : 'border-stone-200 bg-white hover:border-stone-300 cursor-pointer'
              }`}
            >
              <div className="flex items-center gap-3">
                <div className={`w-10 h-10 rounded-xl flex items-center justify-center shrink-0 ${
                  isDisabled ? 'bg-stone-200 text-stone-400' : 'bg-stone-100'
                }`}>
                  {m.icon}
                </div>
                <div>
                  <div className="flex flex-wrap items-center gap-2">
                    <span className={`font-bold text-xs ${isDisabled ? 'text-stone-500' : 'text-stone-900'}`}>
                      {m.name}
                    </span>
                    {m.badge && (
                      <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                        m.badgeColor || 'bg-crimson-100 text-crimson-700'
                      }`}>
                        {m.badge}
                      </span>
                    )}
                  </div>
                  <p className={`text-[11px] mt-0.5 ${isDisabled ? 'text-amber-700 font-medium' : 'text-stone-500'}`}>
                    {m.desc}
                  </p>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
