import React from 'react';
import { Minus, Plus, Trash2 } from 'lucide-react';
import { formatVND } from '../../api';

export default function CartItemRow({ item, onUpdateQty, onRemove }) {
  const isPaperback = item.binding_type === 'PAPERBACK';

  return (
    <div className="flex items-center gap-3 py-3 border-b border-stone-100 last:border-0">
      {/* Thumbnail */}
      <img
        src={item.cover_image || ''}
        alt={item.title}
        className="w-14 h-20 object-cover rounded-lg bg-stone-100 shrink-0 border border-stone-200"
      />

      {/* Info */}
      <div className="flex-1 min-w-0">
        <h4 className="text-xs font-bold text-stone-900 truncate">{item.title}</h4>
        <div className="flex items-center gap-1.5 mt-0.5 mb-1.5 text-[10px] text-stone-500">
          <span className="px-1.5 py-0.5 rounded bg-stone-100 font-semibold text-stone-700">
            {isPaperback ? 'Bìa Mềm' : 'Bìa Cứng'}
          </span>
          <span>•</span>
          <span>{item.weight_gram || item.weight_grams || 350}g / cuốn</span>
        </div>

        <div className="flex items-center justify-between">
          <span className="text-xs font-bold text-crimson-700">
            {formatVND(item.unit_price || item.price || 0)}
          </span>

          {/* Stepper */}
          <div className="flex items-center border border-stone-200 rounded-lg overflow-hidden bg-stone-50">
            <button
              onClick={() => onUpdateQty(item.edition_id, item.quantity - 1)}
              disabled={item.quantity <= 1}
              className="px-2 py-1 text-stone-600 hover:bg-stone-200 transition disabled:opacity-30"
            >
              <Minus className="w-3 h-3" />
            </button>
            <span className="w-6 text-center text-xs font-bold text-stone-800">
              {item.quantity}
            </span>
            <button
              onClick={() => onUpdateQty(item.edition_id, item.quantity + 1)}
              className="px-2 py-1 text-stone-600 hover:bg-stone-200 transition"
            >
              <Plus className="w-3 h-3" />
            </button>
          </div>
        </div>
      </div>

      {/* Delete */}
      <button
        onClick={() => onRemove(item.edition_id)}
        className="p-1.5 text-stone-400 hover:text-crimson-700 hover:bg-red-50 rounded-lg transition shrink-0"
        title="Xóa ấn bản"
      >
        <Trash2 className="w-4 h-4" />
      </button>
    </div>
  );
}
