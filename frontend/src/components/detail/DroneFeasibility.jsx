import React from 'react';
import { Plane, AlertTriangle, CheckCircle } from 'lucide-react';

export default function DroneFeasibility({ weightGrams = 0 }) {
  const packageWeight = weightGrams + 150; // 150g shockproof packaging
  const isDroneEligible = packageWeight <= 2000;

  return (
    <div
      className={`rounded-2xl border p-4 text-xs transition ${
        isDroneEligible
          ? 'bg-emerald-50/70 border-emerald-200 text-emerald-900'
          : 'bg-amber-50/70 border-amber-200 text-amber-900'
      }`}
    >
      <div className="flex items-center gap-2 font-bold mb-1">
        <Plane className={`w-4 h-4 ${isDroneEligible ? 'text-emerald-600' : 'text-amber-600'}`} />
        <span>Khả Năng Vận Chuyển Bằng Hanoi Drone</span>
      </div>

      <p className="text-[11px] leading-relaxed mb-2 text-stone-600">
        Trọng lượng ấn bản: <strong>{weightGrams}g</strong> + Hộp chống sốc chuẩn bay: <strong>150g</strong> = Tổng kiện hàng: <strong>{packageWeight}g</strong>.
      </p>

      {isDroneEligible ? (
        <div className="flex items-center gap-1.5 text-emerald-700 font-bold">
          <CheckCircle className="w-4 h-4" />
          <span>✓ Đủ điều kiện bay siêu tốc Hanoi Drone (30 - 45 phút)</span>
        </div>
      ) : (
        <div className="flex items-center gap-1.5 text-amber-800 font-semibold">
          <AlertTriangle className="w-4 h-4 text-amber-600" />
          <span>⚠ Vượt quá tải trọng Drone (2kg). Đơn hàng sẽ tự động chọn giao GHN.</span>
        </div>
      )}
    </div>
  );
}
