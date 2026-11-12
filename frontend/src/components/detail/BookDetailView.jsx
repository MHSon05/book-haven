import React, { useState, useEffect } from 'react';
import {
  ChevronRight,
  ShoppingCart,
  Zap,
  ZoomIn,
  ShieldCheck,
  Clock,
  Minus,
  Plus,
  ChevronDown,
  ChevronUp,
  BookOpen
} from 'lucide-react';
import { catalogApi, formatVND } from '../../api';
import { useCart } from '../../context/CartContext';
import { useToast } from '../../context/ToastContext';
import LightboxModal from './LightboxModal';
import DroneFeasibility from './DroneFeasibility';
import SpecsTable from './SpecsTable';

export default function BookDetailView({ bookId, onNavigate }) {
  const { addToCart } = useCart();
  const { showToast } = useToast();

  const [book, setBook] = useState(null);
  const [selectedEdition, setSelectedEdition] = useState(null);
  const [detailQty, setDetailQty] = useState(1);
  const [isLightboxOpen, setIsLightboxOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [isDescExpanded, setIsDescExpanded] = useState(false);
  const [flashTime, setFlashTime] = useState(1800); // 30 minutes in seconds

  useEffect(() => {
    let timer = setInterval(() => {
      setFlashTime((t) => (t > 0 ? t - 1 : 1800));
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  const formatTimer = (secs) => {
    const m = Math.floor(secs / 60).toString().padStart(2, '0');
    const s = (secs % 60).toString().padStart(2, '0');
    return `00 : ${m} : ${s}`;
  };

  useEffect(() => {
    if (!bookId) return;
    setIsLoading(true);
    catalogApi
      .getBookDetail(bookId)
      .then((data) => {
        setBook(data);
        const eds = data.editions || [];
        const initialEd = eds.find((e) => e.binding_type === 'PAPERBACK') || eds[0];
        setSelectedEdition(initialEd);
        setDetailQty(1);
        setIsDescExpanded(false);
      })
      .catch((err) => {
        showToast('Lỗi tải chi tiết tác phẩm: ' + err.message, 'error');
        onNavigate('catalog');
      })
      .finally(() => setIsLoading(false));
  }, [bookId, onNavigate, showToast]);

  if (isLoading || !book) {
    return (
      <div className="py-24 text-center">
        <div className="w-10 h-10 border-4 border-crimson-700 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
        <p className="text-xs font-semibold text-stone-500">Đang tải thông tin ấn phẩm...</p>
      </div>
    );
  }

  const isOutOfStock = !selectedEdition || (selectedEdition.available_stock || 0) <= 0;

  const handleQtyMinus = () => {
    if (detailQty > 1) setDetailQty(detailQty - 1);
  };

  const handleQtyPlus = () => {
    if (selectedEdition && detailQty < selectedEdition.available_stock) {
      setDetailQty(detailQty + 1);
    }
  };

  const handleAddToCart = async () => {
    if (!selectedEdition) return;
    await addToCart(selectedEdition.edition_id, detailQty);
  };

  const handleBuyNow = async () => {
    if (!selectedEdition) return;
    await addToCart(selectedEdition.edition_id, detailQty);
    onNavigate('checkout');
  };

  return (
    <div className="max-w-7xl mx-auto px-4 py-8 animate-fadeIn">
      {/* Breadcrumb */}
      <nav className="flex items-center gap-2 text-xs text-stone-500 mb-6">
        <button
          onClick={() => onNavigate('catalog')}
          className="hover:text-crimson-700 transition font-medium"
        >
          Trang chủ
        </button>
        <ChevronRight className="w-3.5 h-3.5" />
        <span className="text-stone-700 font-medium">{book.category_name || 'Văn học'}</span>
        <ChevronRight className="w-3.5 h-3.5" />
        <span className="text-stone-900 font-bold truncate max-w-xs">{book.title}</span>
      </nav>

      {/* Main Detail Grid (Matching Fahasa 2-column layout) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-10 bg-white rounded-3xl border border-stone-200 p-6 md:p-10 shadow-sm">
        {/* Left Column: Image & Lightbox (5 cols) */}
        <div className="lg:col-span-5 flex flex-col items-center">
          <div
            onClick={() => setIsLightboxOpen(true)}
            className="relative aspect-[2/3] w-full max-w-sm rounded-2xl overflow-hidden bg-stone-100 shadow-md cursor-zoom-in group border border-stone-200"
          >
            <img
              src={book.cover_image || ''}
              alt={book.title}
              className="w-full h-full object-cover transition duration-300 group-hover:scale-105"
            />
            <div className="absolute inset-0 bg-stone-950/20 opacity-0 group-hover:opacity-100 transition flex items-center justify-center">
              <span className="px-3.5 py-2 rounded-full bg-stone-900/80 text-white text-xs font-bold flex items-center gap-1.5 backdrop-blur-sm">
                <ZoomIn className="w-4 h-4" />
                <span>Xem ảnh lớn</span>
              </span>
            </div>
          </div>

          <div className="mt-4 flex items-center gap-4 text-xs text-stone-500">
            <span className="flex items-center gap-1">
              <ShieldCheck className="w-4 h-4 text-emerald-600" />
              <span>Bản quyền 100% NXB</span>
            </span>
            <span>•</span>
            <span>Bọc xốp chống va đập</span>
          </div>
        </div>

        {/* Right Column: Title, Format Switcher, Specs, CTA (7 cols) */}
        <div className="lg:col-span-7 flex flex-col space-y-6">
          <div>
            <span className="inline-block px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider bg-crimson-50 text-crimson-700 border border-crimson-200 mb-3">
              {book.category_name || 'Ấn phẩm tinh hoa'}
            </span>
            <h1 className="font-serif-title text-2xl md:text-3xl font-bold text-stone-900 mb-2 leading-tight">
              {book.title}
            </h1>
            <p className="text-xs text-stone-500">
              Tác giả: <strong className="text-stone-800">{book.author_name}</strong> • Nhà xuất bản:{' '}
              <strong className="text-stone-800">{book.publisher_name}</strong>
            </p>
          </div>

          {/* Flash Sale Banner */}
          <div className="rounded-2xl bg-gradient-to-r from-red-600 via-crimson-700 to-red-800 text-white p-4 flex flex-wrap items-center justify-between gap-3 shadow-md">
            <div className="flex items-center gap-2">
              <span className="text-xl">⚡</span>
              <div>
                <span className="font-bold text-xs uppercase tracking-wider block">Ưu Đãi Độc Quyền</span>
                <span className="text-[11px] text-red-100">Giá tốt nhất cho độc giả đặt trước</span>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <Clock className="w-4 h-4 text-red-200" />
              <span className="font-mono font-bold text-sm bg-black/30 px-3 py-1 rounded-lg">
                {formatTimer(flashTime)}
              </span>
            </div>
          </div>

          {/* Pricing display */}
          <div className="space-y-2">
            <div className="flex items-baseline gap-3">
              <span className="text-3xl font-bold text-crimson-700">
                {formatVND(selectedEdition?.unit_price || selectedEdition?.price)}
              </span>
              {selectedEdition && (
                <span className="text-xs text-stone-500 font-medium">
                  (Đã bao gồm thuế VAT & Hộp niêm phong)
                </span>
              )}
            </div>

            <div className="flex items-center gap-2 pt-1">
              <span
                className={`text-xs font-bold px-2.5 py-0.5 rounded-full ${
                  isOutOfStock
                    ? 'bg-stone-200 text-stone-600'
                    : 'bg-emerald-100 text-emerald-800'
                }`}
              >
                {isOutOfStock ? 'Hết hàng' : `Còn ${selectedEdition?.available_stock || 0} cuốn trong kho`}
              </span>
              <span className="text-stone-300">•</span>
              <span className="text-xs text-stone-600 font-medium">
                Quy cách: {selectedEdition?.binding_type === 'HARDCOVER' ? 'Bìa Cứng' : 'Bìa Mềm'}
              </span>
            </div>
          </div>

          {/* Drone Feasibility */}
          <DroneFeasibility weightGrams={selectedEdition?.weight_grams || 350} />

          {/* Specs Table */}
          <SpecsTable book={book} selectedEdition={selectedEdition} />

          {/* Description Section with Collapsible Read More */}
          {(() => {
            const descText = book.description || 'Tuyển tập tác phẩm giá trị kinh điển được xuất bản với quy cách tiêu chuẩn cao.';
            const isLong = descText.length > 260;
            return (
              <div className="p-5 rounded-2xl bg-stone-50 border border-stone-200 text-xs text-stone-700 shadow-sm">
                <div className="flex items-center gap-2 font-bold uppercase tracking-wider text-[11px] text-stone-900 pb-2.5 border-b border-stone-200/80 mb-3">
                  <div className="w-6 h-6 rounded-lg bg-crimson-100 flex items-center justify-center text-crimson-700 shrink-0">
                    <BookOpen className="w-3.5 h-3.5" />
                  </div>
                  <span>Tóm tắt nội dung tác phẩm</span>
                </div>

                <div className="relative">
                  <div
                    className={`leading-relaxed text-stone-600 transition-all duration-300 ${
                      !isDescExpanded && isLong ? 'max-h-24 overflow-hidden' : ''
                    }`}
                  >
                    {descText}
                  </div>

                  {!isDescExpanded && isLong && (
                    <div className="absolute inset-x-0 bottom-0 h-12 bg-gradient-to-t from-stone-50 via-stone-50/90 to-transparent pointer-events-none" />
                  )}
                </div>

                {isLong && (
                  <div className="pt-2">
                    <button
                      type="button"
                      onClick={() => setIsDescExpanded(!isDescExpanded)}
                      className="inline-flex items-center gap-1.5 text-[11px] font-bold text-crimson-700 hover:text-crimson-800 transition py-1 px-2.5 rounded-lg hover:bg-crimson-50 select-none cursor-pointer -ml-2.5"
                    >
                      <span>{isDescExpanded ? 'Thu gọn nội dung' : 'Đọc thêm nội dung'}</span>
                      {isDescExpanded ? (
                        <ChevronUp className="w-3.5 h-3.5" />
                      ) : (
                        <ChevronDown className="w-3.5 h-3.5" />
                      )}
                    </button>
                  </div>
                )}
              </div>
            );
          })()}

          {/* Quantity and Action Buttons */}
          <div className="pt-4 border-t border-stone-200 flex flex-wrap items-center gap-4">
            {/* Quantity Stepper */}
            <div className="flex items-center border border-stone-300 rounded-full overflow-hidden bg-stone-50">
              <button
                type="button"
                onClick={handleQtyMinus}
                disabled={detailQty <= 1}
                className="p-2.5 text-stone-600 hover:bg-stone-200 transition disabled:opacity-30"
              >
                <Minus className="w-3.5 h-3.5" />
              </button>
              <input
                type="text"
                readOnly
                value={detailQty}
                className="w-12 text-center text-xs font-bold bg-transparent text-stone-900 focus:outline-none"
              />
              <button
                type="button"
                onClick={handleQtyPlus}
                disabled={!selectedEdition || detailQty >= selectedEdition.available_stock}
                className="p-2.5 text-stone-600 hover:bg-stone-200 transition disabled:opacity-30"
              >
                <Plus className="w-3.5 h-3.5" />
              </button>
            </div>

            {/* Add to Cart */}
            <button
              type="button"
              disabled={isOutOfStock}
              onClick={handleAddToCart}
              className="flex-1 min-w-[160px] flex items-center justify-center gap-2 px-6 py-3 rounded-full border-2 border-crimson-700 text-crimson-700 hover:bg-crimson-50 text-xs font-bold transition disabled:opacity-40 disabled:border-stone-300 disabled:text-stone-400"
            >
              <ShoppingCart className="w-4 h-4" />
              <span>+ Thêm Vào Giỏ Hàng</span>
            </button>

            {/* Buy Now */}
            <button
              type="button"
              disabled={isOutOfStock}
              onClick={handleBuyNow}
              className="flex-1 min-w-[140px] flex items-center justify-center gap-2 px-6 py-3 rounded-full bg-crimson-700 hover:bg-crimson-800 text-white text-xs font-bold transition shadow-lg hover:shadow-crimson-900/30 disabled:opacity-40 disabled:bg-stone-400"
            >
              <Zap className="w-4 h-4 fill-white" />
              <span>Mua Ngay</span>
            </button>
          </div>
        </div>
      </div>

      {/* Lightbox Modal */}
      <LightboxModal
        isOpen={isLightboxOpen}
        onClose={() => setIsLightboxOpen(false)}
        imageSrc={book.cover_image || '/static/covers/test.png'}
        title={book.title}
      />
    </div>
  );
}
