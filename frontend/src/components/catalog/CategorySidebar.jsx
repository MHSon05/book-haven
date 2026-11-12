import React, { useState } from 'react';
import { Filter, RotateCcw, Zap, Tag, DollarSign } from 'lucide-react';

const PRICE_PRESETS = [
  { id: 'all', label: 'Tất cả mức giá' },
  { id: 'under100', label: 'Dưới 100.000 đ' },
  { id: '100to200', label: '100.000 đ - 200.000 đ' },
  { id: 'above200', label: 'Trên 200.000 đ' },
];

export default function CategorySidebar({
  categories = [],
  categoryCounts = {},
  activeCategory = '',
  onSelectCategory,
  priceFilter = { preset: 'all', min: null, max: null },
  onSelectPricePreset,
  onApplyCustomPrice,
  onlyDrone = false,
  onToggleDrone,
  hasActiveFilters = false,
  onResetFilters,
}) {
  const [customMin, setCustomMin] = useState('');
  const [customMax, setCustomMax] = useState('');

  const handleApplyCustom = (e) => {
    e.preventDefault();
    onApplyCustomPrice(customMin ? Number(customMin) : null, customMax ? Number(customMax) : null);
  };

  return (
    <aside className="w-full lg:w-64 shrink-0 space-y-5">
      {/* 1. Header with Active Filter Count & Reset */}
      <div className="flex items-center justify-between px-1">
        <div className="flex items-center gap-2">
          <Filter className="w-4 h-4 text-crimson-700" />
          <h3 className="text-xs font-bold uppercase tracking-wider text-stone-900">
            Bộ Lọc Tìm Kiếm
          </h3>
        </div>
        {hasActiveFilters && (
          <button
            onClick={() => {
              setCustomMin('');
              setCustomMax('');
              onResetFilters();
            }}
            title="Đặt lại toàn bộ bộ lọc"
            className="flex items-center gap-1 text-[11px] font-bold text-stone-400 hover:text-crimson-700 transition"
          >
            <RotateCcw className="w-3 h-3" />
            <span>Đặt lại</span>
          </button>
        )}
      </div>

      {/* 2. Category Chips Section */}
      <div className="bg-white rounded-2xl border border-stone-200 p-5 shadow-sm space-y-3">
        <div className="flex items-center gap-2 pb-2 border-b border-stone-100">
          <Tag className="w-3.5 h-3.5 text-crimson-700" />
          <h4 className="text-xs font-bold uppercase tracking-wider text-stone-900">
            Thể Loại Sách
          </h4>
        </div>

        <div className="flex flex-wrap gap-2 pt-1">
          {/* Chip Tất cả */}
          <button
            type="button"
            onClick={() => onSelectCategory('')}
            className={`px-3 py-1.5 rounded-xl text-xs font-medium transition-all duration-200 flex items-center gap-1.5 border ${
              !activeCategory
                ? 'bg-crimson-700 text-white font-bold border-crimson-700 shadow-sm shadow-crimson-900/20 scale-[1.02]'
                : 'bg-stone-50 hover:bg-stone-100 text-stone-700 border-stone-200'
            }`}
          >
            <span>Tất cả</span>
            <span
              className={`text-[10px] px-1.5 py-0.5 rounded-full font-bold ${
                !activeCategory
                  ? 'bg-white/20 text-white'
                  : 'bg-stone-200 text-stone-600'
              }`}
            >
              {categoryCounts.all || 0}
            </span>
          </button>

          {/* Chips Thể Loại */}
          {categories.map((c) => {
            const isSelected = activeCategory === c.category_id;
            const count = categoryCounts[c.category_id] || 0;
            return (
              <button
                key={c.category_id}
                type="button"
                onClick={() => onSelectCategory(c.category_id)}
                className={`px-3 py-1.5 rounded-xl text-xs font-medium transition-all duration-200 flex items-center gap-1.5 border text-left ${
                  isSelected
                    ? 'bg-crimson-700 text-white font-bold border-crimson-700 shadow-sm shadow-crimson-900/20 scale-[1.02]'
                    : 'bg-stone-50 hover:bg-stone-100 text-stone-700 border-stone-200'
                }`}
              >
                <span>{c.category_name}</span>
                <span
                  className={`text-[10px] px-1.5 py-0.5 rounded-full font-bold ${
                    isSelected
                      ? 'bg-white/20 text-white'
                      : 'bg-stone-200 text-stone-600'
                  }`}
                >
                  {count}
                </span>
              </button>
            );
          })}
        </div>
      </div>

      {/* 3. Drone Express Delivery Toggle Card */}
      <div
        className={`p-4 rounded-2xl border transition-all duration-200 flex items-center justify-between gap-3 shadow-sm ${
          onlyDrone
            ? 'border-emerald-500 bg-emerald-50/70 ring-2 ring-emerald-500/20'
            : 'border-stone-200 bg-white hover:border-stone-300'
        }`}
      >
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-1.5 mb-0.5">
            <Zap className={`w-3.5 h-3.5 ${onlyDrone ? 'text-emerald-600 fill-emerald-600' : 'text-amber-500'}`} />
            <h4 className="text-xs font-bold text-stone-900">
              Giao Hỏa Tốc Drone
            </h4>
          </div>
          <p className="text-[10px] text-stone-500 truncate">
            Chỉ sách &lt; 2kg đủ chuẩn bay
          </p>
        </div>

        <button
          type="button"
          onClick={onToggleDrone}
          className={`w-11 h-6 shrink-0 flex items-center rounded-full p-1 transition-colors duration-300 ${
            onlyDrone ? 'bg-emerald-500' : 'bg-stone-300'
          }`}
          title={onlyDrone ? 'Tắt lọc Drone' : 'Bật lọc Drone'}
        >
          <div
            className={`bg-white w-4 h-4 rounded-full shadow-md transform transition-transform duration-300 ${
              onlyDrone ? 'translate-x-5' : 'translate-x-0'
            }`}
          />
        </button>
      </div>

      {/* 4. Price Range Filter Card */}
      <div className="bg-white rounded-2xl border border-stone-200 p-5 shadow-sm space-y-3.5">
        <div className="flex items-center gap-2 pb-2 border-b border-stone-100">
          <DollarSign className="w-3.5 h-3.5 text-crimson-700" />
          <h4 className="text-xs font-bold uppercase tracking-wider text-stone-900">
            Khoảng Giá
          </h4>
        </div>

        {/* Quick Presets */}
        <div className="space-y-2 text-xs">
          {PRICE_PRESETS.map((p) => {
            const isSelected = priceFilter.preset === p.id;
            return (
              <label
                key={p.id}
                className="flex items-center gap-2.5 cursor-pointer text-stone-700 hover:text-crimson-700 group select-none"
              >
                <input
                  type="radio"
                  name="price-preset"
                  checked={isSelected}
                  onChange={() => {
                    setCustomMin('');
                    setCustomMax('');
                    onSelectPricePreset(p.id);
                  }}
                  className="text-crimson-700 focus:ring-crimson-700 rounded-full"
                />
                <span className={isSelected ? 'font-bold text-crimson-700' : 'font-medium group-hover:text-stone-900'}>
                  {p.label}
                </span>
              </label>
            );
          })}
        </div>

        {/* Custom Min - Max inputs */}
        <div className="pt-3 border-t border-stone-100">
          <p className="text-[10px] font-bold text-stone-500 uppercase tracking-wider mb-2">
            Hoặc tự nhập khoảng giá:
          </p>
          <form onSubmit={handleApplyCustom} className="space-y-2">
            <div className="grid grid-cols-2 gap-2">
              <input
                type="number"
                placeholder="Từ (đ)"
                value={customMin}
                onChange={(e) => setCustomMin(e.target.value)}
                className="w-full bg-stone-50 border border-stone-200 rounded-xl px-2.5 py-1.5 text-xs text-stone-800 placeholder-stone-400 focus:bg-white focus:outline-none focus:ring-1 focus:ring-crimson-700"
              />
              <input
                type="number"
                placeholder="Đến (đ)"
                value={customMax}
                onChange={(e) => setCustomMax(e.target.value)}
                className="w-full bg-stone-50 border border-stone-200 rounded-xl px-2.5 py-1.5 text-xs text-stone-800 placeholder-stone-400 focus:bg-white focus:outline-none focus:ring-1 focus:ring-crimson-700"
              />
            </div>
            <button
              type="submit"
              disabled={!customMin && !customMax}
              className="w-full py-1.5 rounded-xl bg-stone-800 hover:bg-crimson-700 disabled:opacity-40 text-white text-[11px] font-bold transition shadow-sm"
            >
              Áp dụng
            </button>
          </form>
        </div>
      </div>
    </aside>
  );
}
