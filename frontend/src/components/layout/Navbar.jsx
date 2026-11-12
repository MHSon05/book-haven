import React, { useState, useRef, useEffect } from 'react';
import { ShoppingCart, User, ChevronDown, Package, Shield, LogOut } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { useCart } from '../../context/CartContext';
import MultiModalSearchBar from '../search/MultiModalSearchBar';

export default function Navbar({
  searchMode,
  setSearchMode,
  searchQuery,
  setSearchQuery,
  onSearch,
  onImageMatched,
  onNavigate,
}) {
  const { user, isAdmin, openAuthModal, logout } = useAuth();
  const { totalItemsCount, openCart } = useCart();
  const [isUserMenuOpen, setIsUserMenuOpen] = useState(false);

  const userMenuRef = useRef(null);

  useEffect(() => {
    function handleClickOutside(e) {
      if (userMenuRef.current && !userMenuRef.current.contains(e.target)) {
        setIsUserMenuOpen(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  return (
    <header className="sticky top-0 z-40 bg-[#FAF8F5]/90 backdrop-blur-md border-b border-stone-200 shadow-sm transition">
      <div className="max-w-7xl mx-auto px-4 py-3 flex items-center justify-between gap-4">
        {/* Logo */}
        <a
          href="#catalog"
          onClick={(e) => {
            e.preventDefault();
            onNavigate('catalog');
          }}
          className="flex items-center gap-3 shrink-0 group"
        >
          <span className="text-3xl filter drop-shadow-sm group-hover:scale-110 transition transform">⛩️</span>
          <div>
            <span className="font-serif-title font-bold text-2xl tracking-tight text-stone-900 group-hover:text-crimson-700 transition">
              BookHaven
            </span>
            <span className="block text-[10px] tracking-widest uppercase font-semibold text-stone-500">
              Hiệu Sách Tinh Hoa & Văn Học
            </span>
          </div>
        </a>

        {/* MultiModal Search Bar */}
        <MultiModalSearchBar
          onSearch={(q, mode) => {
            onNavigate('catalog');
            onSearch(q, mode);
          }}
          searchMode={searchMode}
          setSearchMode={setSearchMode}
          searchQuery={searchQuery}
          setSearchQuery={setSearchQuery}
          onImageMatched={onImageMatched}
        />

        {/* Right Action Icons (Cart & User) */}
        <div className="flex items-center gap-3 shrink-0">
          {/* Cart Button */}
          <button
            onClick={openCart}
            className="relative p-2.5 rounded-full bg-white border border-stone-200 text-stone-700 hover:text-crimson-700 hover:border-crimson-700 transition shadow-sm"
            title="Xem giỏ hàng"
          >
            <ShoppingCart className="w-5 h-5" />
            {totalItemsCount > 0 && (
              <span className="absolute -top-1 -right-1 min-w-[20px] h-5 px-1 rounded-full bg-crimson-700 text-white text-[11px] font-bold flex items-center justify-center shadow">
                {totalItemsCount}
              </span>
            )}
          </button>

          {/* User Menu */}
          <div className="relative" ref={userMenuRef}>
            {user ? (
              <div>
                <button
                  onClick={() => setIsUserMenuOpen(!isUserMenuOpen)}
                  className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-white border border-stone-200 hover:border-crimson-700 transition shadow-sm"
                >
                  <div className="w-6 h-6 rounded-full bg-crimson-100 text-crimson-700 flex items-center justify-center text-xs font-bold">
                    {user.full_name ? user.full_name.charAt(0) : 'U'}
                  </div>
                  <span className="text-xs font-bold text-stone-800 max-w-[100px] truncate hidden sm:inline">
                    {user.full_name || user.username}
                  </span>
                  <ChevronDown className="w-3 h-3 text-stone-400" />
                </button>

                {isUserMenuOpen && (
                  <div className="absolute right-0 mt-2 w-52 rounded-2xl bg-white border border-stone-200 shadow-xl py-2 z-50 animate-fadeIn">
                    <div className="px-4 py-2 border-b border-stone-100">
                      <p className="text-xs font-bold text-stone-900 truncate">{user.full_name}</p>
                      <p className="text-[10px] text-stone-500 font-medium">@{user.username} • {user.role}</p>
                    </div>

                    <button
                      onClick={() => {
                        setIsUserMenuOpen(false);
                        onNavigate('orders');
                      }}
                      className="w-full text-left px-4 py-2 text-xs font-medium text-stone-700 hover:bg-stone-50 flex items-center gap-2 transition"
                    >
                      <Package className="w-3.5 h-3.5 text-stone-500" />
                      <span>Đơn mua của tôi</span>
                    </button>

                    {isAdmin && (
                      <button
                        onClick={() => {
                          setIsUserMenuOpen(false);
                          onNavigate('admin');
                        }}
                        className="w-full text-left px-4 py-2 text-xs font-medium text-crimson-700 bg-crimson-50/50 hover:bg-crimson-50 flex items-center gap-2 transition"
                      >
                        <Shield className="w-3.5 h-3.5 text-crimson-700" />
                        <span>Trang Quản trị (Admin)</span>
                      </button>
                    )}

                    <div className="border-t border-stone-100 mt-1 pt-1">
                      <button
                        onClick={() => {
                          setIsUserMenuOpen(false);
                          logout();
                        }}
                        className="w-full text-left px-4 py-2 text-xs font-semibold text-crimson-700 hover:bg-red-50 flex items-center gap-2 transition"
                      >
                        <LogOut className="w-3.5 h-3.5" />
                        <span>Đăng xuất</span>
                      </button>
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <button
                onClick={openAuthModal}
                className="flex items-center gap-1.5 px-3.5 py-2 rounded-full bg-crimson-700 hover:bg-crimson-800 text-white text-xs font-semibold shadow transition"
              >
                <User className="w-3.5 h-3.5" />
                <span>Đăng nhập</span>
              </button>
            )}
          </div>
        </div>
      </div>
    </header>
  );
}
