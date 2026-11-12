import React from 'react';
import { X, Sparkles, Search, Camera } from 'lucide-react';

export default function SearchResultsBanner({
  searchQuery,
  searchMode,
  resultCount,
  onClear,
  onReset,
}) {
  const handleClear = onClear || onReset;
  if (!searchQuery) return null;

  return (
    <div className="mb-6 p-4 rounded-2xl bg-white border border-stone-200 shadow-sm flex flex-wrap items-center justify-between gap-4 animate-fadeIn">
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-xl bg-crimson-50 text-crimson-700 flex items-center justify-center shrink-0">
          {searchMode === 'SEMANTIC' ? (
            <Sparkles className="w-5 h-5 text-amber-500 fill-amber-500" />
          ) : searchMode === 'IMAGE' ? (
            <Camera className="w-5 h-5 text-emerald-600" />
          ) : (
            <Search className="w-5 h-5" />
          )}
        </div>
        <div>
          <h2 className="text-sm font-bold text-stone-900">
            {searchMode === 'IMAGE' ? (
              <>
                Kết quả tìm kiếm ảnh bìa: <span className="text-crimson-700 font-serif-title text-base">"{searchQuery}"</span>
              </>
            ) : (
              <>
                Kết quả tìm kiếm cho: <span className="text-crimson-700 font-serif-title text-base">"{searchQuery}"</span>
              </>
            )}
          </h2>
          <p className="text-xs text-stone-500">
            {searchMode === 'SEMANTIC'
              ? `Tìm kiếm cốt truyện AI • Tìm thấy ${resultCount} tác phẩm tương đồng cao`
              : searchMode === 'IMAGE'
              ? `Nhận diện thị giác bìa sách • Tìm thấy ${resultCount} tác phẩm khớp chính xác`
              : `Tìm thấy ${resultCount} tác phẩm khớp từ khóa`}
          </p>
        </div>
      </div>
      <button
        type="button"
        onClick={handleClear}
        className="flex items-center gap-1.5 px-3.5 py-1.5 rounded-full border border-stone-300 hover:border-crimson-700 hover:text-crimson-700 text-stone-600 text-xs font-semibold transition"
      >
        <X className="w-3.5 h-3.5" />
        <span>Xóa tìm kiếm & Hiện tất cả</span>
      </button>
    </div>
  );
}
