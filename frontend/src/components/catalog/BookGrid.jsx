import React, { useState, useEffect, useMemo } from 'react';
import { ArrowUpDown, ChevronLeft, ChevronRight } from 'lucide-react';
import BookCard from './BookCard';

const PAGE_SIZE = 12;

export default function BookGrid({
  books = [],
  activeCategory,
  priceFilter,
  onlyDrone = false,
  activeSort,
  onSortChange,
  onSelectBook,
  onResetFilters,
}) {
  const [currentPage, setCurrentPage] = useState(1);

  // 1. Lọc và sắp xếp sách
  const filteredBooks = useMemo(() => {
    let result = [...books];

    // Lọc theo thể loại
    if (activeCategory) {
      result = result.filter((b) => b.category_id === activeCategory);
    }

    // Lọc theo khoảng giá
    if (priceFilter) {
      if (priceFilter.min !== null && priceFilter.min !== undefined) {
        result = result.filter((b) => (b.min_price || 0) >= priceFilter.min);
      }
      if (priceFilter.max !== null && priceFilter.max !== undefined) {
        result = result.filter((b) => (b.min_price || 0) <= priceFilter.max);
      }
    }

    // Lọc theo chuẩn Drone (< 2000g)
    if (onlyDrone) {
      result = result.filter((b) => {
        const weight = b.weight_gram || b.weight_grams || 350;
        return weight < 2000;
      });
    }

    // Sắp xếp
    if (activeSort === 'price_asc') {
      result.sort((a, b) => (a.min_price || 0) - (b.min_price || 0));
    } else if (activeSort === 'price_desc') {
      result.sort((a, b) => (b.min_price || 0) - (a.min_price || 0));
    } else if (activeSort === 'title_asc') {
      result.sort((a, b) => (a.title || '').localeCompare(b.title || ''));
    }

    return result;
  }, [books, activeCategory, priceFilter, onlyDrone, activeSort]);

  // Tự động reset về trang 1 khi đổi bộ lọc
  useEffect(() => {
    setCurrentPage(1);
  }, [activeCategory, priceFilter, onlyDrone, activeSort, books.length]);

  // 2. Tính toán phân trang động (Dynamic Pagination)
  const totalPages = Math.max(1, Math.ceil(filteredBooks.length / PAGE_SIZE));
  const validPage = Math.min(currentPage, totalPages);
  const startIndex = (validPage - 1) * PAGE_SIZE;
  const endIndex = Math.min(startIndex + PAGE_SIZE, filteredBooks.length);
  const paginatedBooks = filteredBooks.slice(startIndex, endIndex);

  const handlePageChange = (newPage) => {
    if (newPage >= 1 && newPage <= totalPages && newPage !== validPage) {
      setCurrentPage(newPage);
      const gridElem = document.getElementById('books-grid');
      if (gridElem) {
        gridElem.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    }
  };

  // Cửa sổ trượt sinh danh sách trang động không hardcode
  const getPaginationRange = (current, total) => {
    if (total <= 7) {
      return Array.from({ length: total }, (_, i) => i + 1);
    }
    if (current <= 4) {
      return [1, 2, 3, 4, 5, '...', total];
    }
    if (current >= total - 3) {
      return [1, '...', total - 4, total - 3, total - 2, total - 1, total];
    }
    return [1, '...', current - 1, current, current + 1, '...', total];
  };

  return (
    <div className="flex-1" id="books-grid">
      {/* Top Bar with Count & Sort */}
      <div className="flex flex-wrap items-center justify-between pb-4 mb-6 border-b border-stone-200 gap-4">
        <div className="flex items-center gap-2">
          <h2 className="font-serif-title font-bold text-xl text-stone-900">Danh Mục Ấn Phẩm Tuyển Chọn</h2>
          <span className="px-2.5 py-0.5 rounded-full bg-stone-200 text-stone-700 text-xs font-bold">
            {filteredBooks.length} cuốn
          </span>
          {totalPages > 1 && (
            <span className="text-xs text-stone-400 font-medium">
              (Trang {validPage}/{totalPages})
            </span>
          )}
        </div>

        {/* Sort Select */}
        <div className="flex items-center gap-2">
          <ArrowUpDown className="w-4 h-4 text-stone-400" />
          <select
            value={activeSort}
            onChange={(e) => onSortChange(e.target.value)}
            className="bg-white border border-stone-300 rounded-xl px-3 py-1.5 text-xs text-stone-700 font-semibold focus:outline-none focus:ring-2 focus:ring-crimson-700/20"
          >
            <option value="default">Sắp xếp: Mặc định</option>
            <option value="price_asc">Giá: Thấp đến Cao</option>
            <option value="price_desc">Giá: Cao đến Thấp</option>
            <option value="title_asc">Tên sách: A - Z</option>
          </select>
        </div>
      </div>

      {/* Books Grid */}
      {filteredBooks.length === 0 ? (
        <div className="py-20 text-center text-stone-400 bg-white rounded-3xl border border-stone-200 shadow-sm">
          <span className="text-5xl block mb-3">📚</span>
          <p className="text-sm font-semibold text-stone-700">Không tìm thấy tác phẩm nào phù hợp với bộ lọc hiện tại</p>
          <p className="text-xs text-stone-400 mt-1">Hãy thử chọn khoảng giá rộng hơn hoặc chọn danh mục khác</p>
          <button
            onClick={onResetFilters}
            className="mt-4 px-5 py-2 rounded-full border border-stone-300 text-xs text-stone-700 hover:bg-stone-50 font-bold transition shadow-sm"
          >
            Xóa bộ lọc & Tải lại toàn bộ
          </button>
        </div>
      ) : (
        <>
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 xl:grid-cols-4 gap-6">
            {paginatedBooks.map((book) => (
              <BookCard key={book.book_id} book={book} onSelect={onSelectBook} />
            ))}
          </div>

          {/* Dynamic Pagination Controls */}
          {totalPages > 1 && (
            <div className="mt-10 pt-6 border-t border-stone-200 flex flex-col sm:flex-row items-center justify-between gap-4">
              <div className="text-xs text-stone-500 font-medium">
                Hiển thị <span className="font-bold text-stone-800">{startIndex + 1}</span> -{' '}
                <span className="font-bold text-stone-800">{endIndex}</span> trên{' '}
                <span className="font-bold text-stone-800">{filteredBooks.length}</span> cuốn (Trang{' '}
                <span className="font-bold text-stone-800">{validPage}</span>/{totalPages})
              </div>

              <div className="flex items-center gap-1.5">
                <button
                  onClick={() => handlePageChange(validPage - 1)}
                  disabled={validPage <= 1}
                  className="flex items-center gap-1 px-3 py-1.5 rounded-xl border border-stone-200 bg-white text-xs font-semibold text-stone-700 hover:bg-stone-50 disabled:opacity-40 disabled:pointer-events-none transition shadow-sm"
                >
                  <ChevronLeft className="w-4 h-4" />
                  <span>Trước</span>
                </button>

                <div className="flex items-center gap-1">
                  {getPaginationRange(validPage, totalPages).map((p, idx) => {
                    if (p === '...') {
                      return (
                        <span key={`dots-${idx}`} className="w-8 h-8 flex items-center justify-center text-stone-400 text-xs">
                          ...
                        </span>
                      );
                    }
                    const isActive = p === validPage;
                    return (
                      <button
                        key={p}
                        onClick={() => handlePageChange(p)}
                        className={`w-8 h-8 rounded-xl text-xs font-bold transition flex items-center justify-center ${
                          isActive
                            ? 'bg-crimson-700 text-white shadow-sm'
                            : 'bg-white border border-stone-200 text-stone-700 hover:bg-stone-50'
                        }`}
                      >
                        {p}
                      </button>
                    );
                  })}
                </div>

                <button
                  onClick={() => handlePageChange(validPage + 1)}
                  disabled={validPage >= totalPages}
                  className="flex items-center gap-1 px-3 py-1.5 rounded-xl border border-stone-200 bg-white text-xs font-semibold text-stone-700 hover:bg-stone-50 disabled:opacity-40 disabled:pointer-events-none transition shadow-sm"
                >
                  <span>Sau</span>
                  <ChevronRight className="w-4 h-4" />
                </button>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}
