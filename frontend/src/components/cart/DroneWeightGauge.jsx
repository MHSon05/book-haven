import React from 'react';
import { Plane, AlertTriangle, CheckCircle2 } from 'lucide-react';

export default function DroneWeightGauge({ totalWeightGrams = 0 }) {
  const packageWeight = totalWeightGrams + 150; // includes 150g shockproof packaging
  const maxWeight = 2000; // 2kg limit
  const percentage = Math.min(100, Math.round((packageWeight / maxWeight) * 100));
  const isDroneEligible = packageWeight <= maxWeight;

  return (
    <div className="p-4 rounded-2xl bg-stone-50 border border-stone-200 text-xs space-y-2">
      <div className="flex items-center justify-between">
        <span className="font-bold text-stone-800 flex items-center gap-1.5">
          <Plane className={`w-3.5 h-3.5 ${isDroneEligible ? 'text-emerald-600' : 'text-amber-600'}`} />
          <span>Tải Trọng Hanoi Drone</span>
        </span>
        <span className={`font-mono font-bold ${isDroneEligible ? 'text-emerald-700' : 'text-amber-600'}`}>
          {packageWeight}g / 2.000g
        </span>
      </div>

      {/* Progress Bar */}
      <div className="w-full h-2 rounded-full bg-stone-200 overflow-hidden">
        <div
          className={`h-full transition-all duration-300 rounded-full ${
            isDroneEligible ? 'bg-emerald-500' : 'bg-amber-500'
          }`}
          style={{ width: `${percentage}%` }}
        ></div>
      </div>

      {/* Status Notice */}
      {isDroneEligible ? (
        <p className="text-[11px] text-emerald-700 font-medium flex items-center gap-1">
          <CheckCircle2 className="w-3.5 h-3.5 shrink-0" />
          <span>✓ Đủ điều kiện giao hỏa tốc bằng Hanoi Drone (30 - 45 phút)</span>
        </p>
      ) : (
        <p className="text-[11px] text-amber-700 font-medium flex items-center gap-1">
          <AlertTriangle className="w-3.5 h-3.5 shrink-0 text-amber-600" />
          <span>⚠ Vượt tải trọng Drone (2kg). Đơn hàng sẽ tự động chọn giao GHN</span>
        </p>
      )}
    </div>
  );
}
