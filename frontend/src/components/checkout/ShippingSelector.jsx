import React from 'react';
import { Truck, Plane, AlertTriangle } from 'lucide-react';
import { formatVND } from '../../api';

export default function ShippingSelector({
  shippingOptions = [],
  selectedCarrier,
  onSelectCarrier,
  packageWeight = 0,
}) {
  const isDroneAllowed = packageWeight <= 2000;

  return (
    <div className="bg-white rounded-3xl border border-stone-200 p-6 shadow-sm space-y-4">
      <div className="flex items-center gap-2 pb-3 border-b border-stone-100">
        <Truck className="w-5 h-5 text-crimson-700" />
        <h3 className="font-serif-title font-bold text-base text-stone-900">
          2. Phương Thức Vận Chuyển
        </h3>
      </div>

      <div className="space-y-3">
        {shippingOptions.map((opt) => {
          const isDrone = opt.carrier_code === 'HANOI_DRONE';
          const isOptionDisabled = isDrone && !isDroneAllowed;
          const isSelected = selectedCarrier === opt.carrier_code;

          return (
            <div
              key={opt.carrier_code}
              onClick={() => {
                if (!isOptionDisabled) onSelectCarrier(opt.carrier_code);
              }}
              className={`p-4 rounded-2xl border transition relative flex items-center justify-between cursor-pointer ${
                isSelected
                  ? 'border-crimson-700 bg-crimson-50/30 ring-2 ring-crimson-700/20'
                  : isOptionDisabled
                  ? 'border-stone-200 bg-stone-100 opacity-60 cursor-not-allowed'
                  : 'border-stone-200 bg-white hover:border-stone-300'
              }`}
            >
              <div className="flex items-center gap-3">
                <div
                  className={`w-10 h-10 rounded-xl flex items-center justify-center shrink-0 ${
                    isDrone ? 'bg-emerald-100 text-emerald-700' : 'bg-stone-100 text-stone-700'
                  }`}
                >
                  {isDrone ? <Plane className="w-5 h-5" /> : <Truck className="w-5 h-5" />}
                </div>

                <div>
                  <div className="flex items-center gap-2">
                    <span className="font-bold text-xs text-stone-900">{opt.carrier_name}</span>
                    {isDrone && (
                      <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-100 text-emerald-800">
                        ⚡ Siêu tốc 30-45 phút
                      </span>
                    )}
                  </div>
                  <p className="text-[11px] text-stone-500 mt-0.5">{opt.estimated_time || opt.estimated_delivery}</p>
                  {isOptionDisabled && (
                    <p className="text-[10px] font-semibold text-amber-700 flex items-center gap-1 mt-1">
                      <AlertTriangle className="w-3 h-3" /> Vượt tải trọng bay của Drone ({packageWeight}g &gt; 2.000g)
                    </p>
                  )}
                </div>
              </div>

              <div className="text-right">
                <span className="font-bold text-xs text-stone-900 block">
                  {formatVND(opt.fee)}
                </span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
