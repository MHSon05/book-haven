import React, { useState, useEffect, useCallback, useMemo } from 'react';
import AnnouncementBar from './components/layout/AnnouncementBar';
import Navbar from './components/layout/Navbar';
import Footer from './components/layout/Footer';
import HeroBanner from './components/catalog/HeroBanner';
import CategorySidebar from './components/catalog/CategorySidebar';
import BookGrid from './components/catalog/BookGrid';
import SearchResultsBanner from './components/search/SearchResultsBanner';
import BookDetailView from './components/detail/BookDetailView';
import CheckoutView from './components/checkout/CheckoutView';
import PaymentView from './components/payment/PaymentView';
import OrderSuccessView from './components/orders/OrderSuccessView';
import OrdersView from './components/orders/OrdersView';
import AdminPortalView from './components/admin/AdminPortalView';
import CartDrawer from './components/cart/CartDrawer';
import BookieChatDrawer from './components/chatbot/BookieChatDrawer';
import AuthModal from './components/auth/AuthModal';
import { Bot } from 'lucide-react';

import { catalogApi, searchApi } from './api';
import { useToast } from './context/ToastContext';

export default function App() {
  const { showToast } = useToast();

  // Navigation State
  const [currentView, setCurrentView] = useState({ view: 'catalog', params: {} });

  // Catalog & Search State
  const [categories, setCategories] = useState([]);
  const [books, setBooks] = useState([]);
  const [activeCategory, setActiveCategory] = useState('');
  const [priceFilter, setPriceFilter] = useState({ preset: 'all', min: null, max: null });
  const [onlyDrone, setOnlyDrone] = useState(false);
  const [activeSort, setActiveSort] = useState('default');
  const [searchMode, setSearchMode] = useState('KEYWORD'); // 'KEYWORD' | 'SEMANTIC'
  const [searchQuery, setSearchQuery] = useState('');
  const [submittedSearch, setSubmittedSearch] = useState({ query: '', mode: 'KEYWORD' });
  const [hasSearched, setHasSearched] = useState(false);

  // Đếm số lượng sách theo thể loại
  const categoryCounts = useMemo(() => {
    const counts = { all: books.length };
    books.forEach((b) => {
      counts[b.category_id] = (counts[b.category_id] || 0) + 1;
    });
    return counts;
  }, [books]);

  const hasActiveFilters = Boolean(
    activeCategory ||
    priceFilter.preset !== 'all' ||
    onlyDrone ||
    hasSearched
  );

  const handleSelectPricePreset = (preset) => {
    if (preset === 'under100') {
      setPriceFilter({ preset, min: 0, max: 100000 });
    } else if (preset === '100to200') {
      setPriceFilter({ preset, min: 100000, max: 200000 });
    } else if (preset === 'above200') {
      setPriceFilter({ preset, min: 200000, max: null });
    } else {
      setPriceFilter({ preset: 'all', min: null, max: null });
    }
  };

  const handleApplyCustomPrice = (min, max) => {
    setPriceFilter({
      preset: 'custom',
      min: min !== null ? min : null,
      max: max !== null ? max : null,
    });
  };

  const handleToggleDrone = () => {
    setOnlyDrone((prev) => !prev);
  };

  // Chatbot Drawer State
  const [isChatOpen, setIsChatOpen] = useState(false);

  // Router parsing logic (Hỗ trợ cả HTML5 Clean URL pathname lẫn Hash route)
  const parseRoute = useCallback(() => {
    const rawPath = window.location.pathname.replace(/\/+$/, '') || '/';
    let hash = window.location.hash || '';
    if (hash.startsWith('#/')) {
      hash = '#' + hash.slice(2);
    }

    if (
      rawPath === '/admin' ||
      rawPath === '/admin/login' ||
      rawPath.startsWith('/admin/') ||
      hash === '#admin' ||
      hash === '#admin/login'
    ) {
      setCurrentView({ view: 'admin', params: {} });
    } else if (rawPath === '/orders' || hash === '#orders') {
      setCurrentView({ view: 'orders', params: {} });
    } else if (rawPath === '/checkout' || hash === '#checkout') {
      setCurrentView({ view: 'checkout', params: {} });
    } else if (rawPath.startsWith('/book/') || hash.startsWith('#book/')) {
      const bookId = rawPath.startsWith('/book/')
        ? rawPath.replace('/book/', '')
        : hash.replace('#book/', '');
      setCurrentView({ view: 'book-detail', params: { id: bookId } });
    } else if (rawPath.startsWith('/payment/') || hash.startsWith('#payment/')) {
      const orderId = rawPath.startsWith('/payment/')
        ? rawPath.replace('/payment/', '')
        : hash.replace('#payment/', '');
      setCurrentView({ view: 'payment', params: { orderId } });
    } else if (rawPath.startsWith('/order-success/') || hash.startsWith('#order-success/')) {
      const orderId = rawPath.startsWith('/order-success/')
        ? rawPath.replace('/order-success/', '')
        : hash.replace('#order-success/', '');
      setCurrentView({ view: 'order-success', params: { orderId } });
    } else {
      setCurrentView({ view: 'catalog', params: {} });
    }

    // Không ép cuộn lên đỉnh nếu đang nhảy đến neo nội bộ
    if (hash === '#books-grid' || hash === '#catalog-results-anchor') {
      return;
    }

    window.scrollTo({ top: 0, behavior: 'smooth' });
  }, []);

  useEffect(() => {
    window.addEventListener('hashchange', parseRoute);
    window.addEventListener('popstate', parseRoute);
    parseRoute();
    return () => {
      window.removeEventListener('hashchange', parseRoute);
      window.removeEventListener('popstate', parseRoute);
    };
  }, [parseRoute]);

  const navigate = useCallback((viewName, params = {}) => {
    let targetPath = '/';
    let targetHash = '#catalog';

    if (viewName === 'catalog') {
      targetPath = '/';
      targetHash = '#catalog';
    } else if (viewName === 'book-detail' && params.id) {
      targetPath = `/book/${params.id}`;
      targetHash = `#book/${params.id}`;
    } else if (viewName === 'checkout') {
      targetPath = '/checkout';
      targetHash = '#checkout';
    } else if (viewName === 'payment' && params.orderId) {
      targetPath = `/payment/${params.orderId}`;
      targetHash = `#payment/${params.orderId}`;
    } else if (viewName === 'order-success' && params.orderId) {
      targetPath = `/order-success/${params.orderId}`;
      targetHash = `#order-success/${params.orderId}`;
    } else if (viewName === 'orders') {
      targetPath = '/orders';
      targetHash = '#orders';
    } else if (viewName === 'admin') {
      targetPath = '/admin';
      targetHash = '#admin';
    }

    if (window.location.pathname !== targetPath) {
      window.history.pushState(null, '', targetPath);
    }
    window.location.hash = targetHash;
    parseRoute();
  }, [parseRoute]);

  // Initial Load: Categories & Books
  const loadInitialBooks = useCallback(async () => {
    try {
      const data = await catalogApi.getBooks({ limit: 500 });
      setBooks(data.books || []);
    } catch (err) {
      console.error('Error loading books:', err);
      showToast('Không thể kết nối đến máy chủ lấy danh mục sách', 'error');
    }
  }, [showToast]);

  useEffect(() => {
    catalogApi
      .getCategories()
      .then((data) => setCategories(data.categories || []))
      .catch(console.error);

    loadInitialBooks();
  }, [loadInitialBooks]);

  // Smooth scroll to catalog results
  const scrollToResults = () => {
    setTimeout(() => {
      const el = document.getElementById('catalog-results-anchor') || document.getElementById('books-grid');
      if (el) {
        el.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    }, 150);
  };

  // Search Action
  const handleSearch = async (query, mode) => {
    const q = (query || '').trim();
    if (!q) {
      resetFilters();
      return;
    }

    try {
      let results = [];
      if (mode === 'SEMANTIC') {
        const res = await searchApi.searchSemantic(q);
        results = res.results || [];
      } else {
        const res = await searchApi.searchKeyword(q, null, null);
        results = res.results || [];
      }

      navigate('catalog');
      setActiveCategory('');
      setPriceFilter({ preset: 'all', min: null, max: null });
      setOnlyDrone(false);
      setBooks(results);
      setSubmittedSearch({ query: q, mode: mode });
      setHasSearched(true);
      scrollToResults();
    } catch (err) {
      showToast(err.message, 'error');
    }
  };

  // Image Search Action
  const handleImageMatch = (book) => {
    navigate('catalog');
    setActiveCategory('');
    setPriceFilter({ preset: 'all', min: null, max: null });
    setOnlyDrone(false);
    setBooks(book ? [book] : []);
    setSubmittedSearch({ query: book?.title || 'Ảnh bìa tải lên', mode: 'IMAGE' });
    setHasSearched(true);
    scrollToResults();
  };

  // Reset Filters
  const resetFilters = () => {
    setActiveCategory('');
    setPriceFilter({ preset: 'all', min: null, max: null });
    setOnlyDrone(false);
    setActiveSort('default');
    setSearchQuery('');
    setSubmittedSearch({ query: '', mode: 'KEYWORD' });
    setHasSearched(false);
    loadInitialBooks();
  };

  // Nếu đang ở cổng Quản Trị: Trả về Khung giao diện Admin độc lập (Ẩn hoàn toàn Navbar khách, giỏ hàng, chatbot)
  if (currentView.view === 'admin') {
    return <AdminPortalView onNavigate={navigate} />;
  }

  return (
    <div className="min-h-screen flex flex-col bg-[#FAF8F5] text-stone-900 selection:bg-crimson-100 selection:text-crimson-900">
      {/* Top Banner & Header */}
      <AnnouncementBar />
      <Navbar
        searchMode={searchMode}
        setSearchMode={setSearchMode}
        searchQuery={searchQuery}
        setSearchQuery={setSearchQuery}
        onSearch={handleSearch}
        onImageMatched={handleImageMatch}
        onNavigate={navigate}
      />

      {/* Main View Router Content */}
      <main className="flex-1">
        {currentView.view === 'catalog' && (
          <div className="max-w-7xl mx-auto px-4 py-8 animate-fadeIn">
            {/* Hero banner */}
            <HeroBanner />

            {/* Anchor for auto-scroll to search results and catalog */}
            <div id="catalog-results-anchor" className="scroll-mt-24"></div>

            {/* Search results notice if applicable */}
            {hasSearched && (
              <SearchResultsBanner
                searchQuery={submittedSearch.query}
                searchMode={submittedSearch.mode}
                resultCount={books.length}
                onClear={resetFilters}
              />
            )}

            {/* Catalog Layout 2 columns */}
            <div className="flex flex-col lg:flex-row gap-8 items-start">
              <CategorySidebar
                categories={categories}
                categoryCounts={categoryCounts}
                activeCategory={activeCategory}
                onSelectCategory={setActiveCategory}
                priceFilter={priceFilter}
                onSelectPricePreset={handleSelectPricePreset}
                onApplyCustomPrice={handleApplyCustomPrice}
                onlyDrone={onlyDrone}
                onToggleDrone={handleToggleDrone}
                hasActiveFilters={hasActiveFilters}
                onResetFilters={resetFilters}
              />

              <BookGrid
                books={books}
                activeCategory={activeCategory}
                priceFilter={priceFilter}
                onlyDrone={onlyDrone}
                activeSort={activeSort}
                onSortChange={setActiveSort}
                onSelectBook={(bookId) => navigate('book-detail', { id: bookId })}
                onResetFilters={resetFilters}
              />
            </div>
          </div>
        )}

        {currentView.view === 'book-detail' && (
          <BookDetailView
            bookId={currentView.params.id}
            onNavigate={navigate}
          />
        )}

        {currentView.view === 'checkout' && (
          <CheckoutView onNavigate={navigate} />
        )}

        {currentView.view === 'payment' && (
          <PaymentView
            orderId={currentView.params.orderId}
            onNavigate={navigate}
          />
        )}

        {currentView.view === 'order-success' && (
          <OrderSuccessView
            orderId={currentView.params.orderId}
            onNavigate={navigate}
          />
        )}

        {currentView.view === 'orders' && (
          <OrdersView onNavigate={navigate} />
        )}
      </main>

      {/* Footer */}
      <Footer />

      {/* Modals & Drawers */}
      <CartDrawer onNavigate={navigate} />
      <BookieChatDrawer
        isOpen={isChatOpen}
        onClose={() => setIsChatOpen(false)}
        onSelectBook={(bookId) => navigate('book-detail', { id: bookId })}
      />
      <AuthModal />

      {/* Floating Modern Crimson AI Chat Assistant Button */}
      <button
        onClick={() => setIsChatOpen(true)}
        className="fixed bottom-6 right-6 z-30 w-14 h-14 rounded-full bg-crimson-700 hover:bg-crimson-800 text-white shadow-2xl flex items-center justify-center transition-all duration-300 hover:scale-110 active:scale-95 group border-2 border-white/20"
        title="Trò chuyện cùng Trợ lý AI BookHaven"
      >
        <Bot className="w-7 h-7 text-white transition-transform group-hover:rotate-6" />
        <span className="absolute -top-1 -right-1 flex h-4 w-4">
          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
          <span className="relative inline-flex rounded-full h-4 w-4 bg-emerald-500 border-2 border-white"></span>
        </span>
      </button>
    </div>
  );
}
