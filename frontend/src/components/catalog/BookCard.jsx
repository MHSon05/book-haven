import React from 'react';
import { formatVND } from '../../api';

export default function BookCard({ book, onSelect }) {
  const isOutOfStock = ((book.total_available_stock ?? book.available_stock) || 0) <= 0;

  return (
    <div className="book-card bg-white rounded-2xl border border-stone-200 overflow-hidden shadow-sm flex flex-col p-4 group">
      {/* Cover Image */}
      <a
        href={`#book/${book.book_id}`}
        onClick={(e) => {
          e.preventDefault();
          onSelect(book.book_id);
        }}
        className="block relative aspect-[2/3] rounded-xl overflow-hidden mb-4 bg-stone-50"
      >
        <img
          src={book.cover_image || ''}
          alt={book.title}
          className="w-full h-full object-cover transition duration-300 group-hover:scale-105"
          loading="lazy"
        />
        <span className="absolute top-2.5 left-2.5 px-2.5 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider bg-crimson-700 text-white shadow-sm">
          {book.category_name || 'Văn học'}
        </span>
        {isOutOfStock && (
          <div className="absolute inset-0 bg-stone-900/60 flex items-center justify-center">
            <span className="px-3 py-1 rounded-full bg-stone-800 text-stone-200 text-xs font-bold">
              Hết hàng
            </span>
          </div>
        )}
      </a>

      {/* Book Info */}
      <div className="flex-1 flex flex-col">
        <p className="text-[11px] text-stone-500 font-medium truncate mb-1">
          Tác giả: {book.author_name || 'BookHaven'}
        </p>

        <a
          href={`#book/${book.book_id}`}
          onClick={(e) => {
            e.preventDefault();
            onSelect(book.book_id);
          }}
          className="font-serif-title font-bold text-stone-900 text-base leading-snug line-clamp-2 hover:text-crimson-700 transition mb-2"
        >
          {book.title}
        </a>

        <div className="flex items-center gap-1.5 text-[11px] text-stone-500 mb-3">
          <span className="px-2 py-0.5 rounded bg-stone-100 font-medium text-stone-700">
            {book.category_name || 'Ấn bản chuẩn'}
          </span>
          <span className="text-stone-300">•</span>
          <span className={isOutOfStock ? "text-stone-400 font-medium" : "text-emerald-700 font-medium"}>
            {isOutOfStock ? "Hết hàng" : "Còn hàng"}
          </span>
        </div>

        {/* Pricing & CTA */}
        <div className="mt-auto pt-3 border-t border-stone-100 flex items-baseline justify-between">
          <div>
            <span className="font-bold text-base text-crimson-700">{formatVND(book.min_price)}</span>
          </div>
          <button
            onClick={() => onSelect(book.book_id)}
            className="px-3.5 py-1.5 rounded-full bg-stone-100 hover:bg-crimson-700 hover:text-white text-stone-700 text-xs font-semibold transition"
          >
            Chi tiết →
          </button>
        </div>
      </div>
    </div>
  );
}
