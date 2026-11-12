import React from 'react';
import { formatVND } from '../../api';

export default function EditionSwitcher({ editions = [], selectedEdition, onSelectEdition }) {
  return (
    <div className="space-y-3">
      <label className="block text-xs font-bold uppercase tracking-wider text-stone-700">
        Chọn Quy Cách Ấn Bản (Collector Format)
      </label>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        {editions.map((ed) => {
          const isSelected = selectedEdition?.edition_id === ed.edition_id;
          const isOutOfStock = (ed.available_stock || 0) <= 0;
          const isPaperback = ed.binding_type === 'PAPERBACK';

          return (
            <button
              key={ed.edition_id}
              type="button"
              disabled={isOutOfStock}
              onClick={() => onSelectEdition(ed)}
              className={`p-3.5 rounded-2xl border text-left transition relative flex flex-col justify-between ${
                isSelected
                  ? 'border-crimson-700 bg-crimson-50/40 ring-2 ring-crimson-700/20 shadow-sm'
                  : isOutOfStock
                  ? 'border-stone-200 bg-stone-100 opacity-60 cursor-not-allowed'
                  : 'border-stone-200 bg-white hover:border-stone-300'
              }`}
            >
              <div className="flex items-center justify-between gap-2 mb-2">
                <span className="font-bold text-xs text-stone-900 flex items-center gap-1.5">
                  <span>{isPaperback ? '📖' : '📕'}</span>
                  <span>{isPaperback ? 'Bìa Mềm (Paperback)' : 'Bìa Cứng (Collector)'}</span>
                </span>
                <span
                  className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                    isOutOfStock
                      ? 'bg-stone-200 text-stone-600'
                      : 'bg-emerald-100 text-emerald-800'
                  }`}
                >
                  {isOutOfStock ? 'Hết hàng' : `Còn ${ed.available_stock} cuốn`}
                </span>
              </div>

              <div className="flex items-baseline justify-between mt-auto">
                <span className="text-sm font-bold text-crimson-700">
                  {formatVND(ed.unit_price || ed.price)}
                </span>
                <span className="text-[11px] text-stone-500 font-medium">
                  {ed.weight_gram || ed.weight_grams}g • SKU: {ed.sku}
                </span>
              </div>
            </button>
          );
        })}
      </div>
    </div>
  );
}
