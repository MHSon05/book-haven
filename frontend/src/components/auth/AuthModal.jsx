import React, { useState } from 'react';
import { X, Lock, User, ShieldCheck } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

export default function AuthModal() {
  const { isAuthModalOpen, closeAuthModal, login } = useAuth();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  if (!isAuthModalOpen) return null;

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!username.trim() || !password) return;

    setIsSubmitting(true);
    try {
      await login(username.trim(), password);
    } catch {
      // Error handled in context toast
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-stone-950/60 backdrop-blur-sm transition-opacity"
        onClick={closeAuthModal}
      ></div>

      {/* Modal Dialog */}
      <div className="relative z-10 w-full max-w-md bg-white rounded-3xl shadow-2xl border border-stone-200 p-6 md:p-8 space-y-6 animate-fadeIn">
        {/* Header */}
        <div className="flex items-center justify-between pb-4 border-b border-stone-100">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-2xl bg-crimson-50 text-crimson-700 flex items-center justify-center text-xl shadow-inner border border-crimson-100">
              ⛩️
            </div>
            <div>
              <h3 className="font-serif-title font-bold text-lg text-stone-900">
                Đăng Nhập Tài Khoản
              </h3>
              <p className="text-xs text-stone-500">BookHaven — Hiệu Sách Tinh Hoa & Sưu Tầm</p>
            </div>
          </div>
          <button
            type="button"
            onClick={closeAuthModal}
            className="p-2 rounded-full text-stone-400 hover:text-stone-700 hover:bg-stone-100 transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Login Form */}
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-bold text-stone-700 mb-1.5">
              Tên tài khoản (Username):
            </label>
            <div className="relative">
              <input
                type="text"
                required
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className="w-full bg-stone-50 border border-stone-300 rounded-xl px-3.5 py-2.5 text-xs text-stone-800 placeholder-stone-400 focus:outline-none focus:ring-2 focus:ring-crimson-700/20 focus:bg-white transition"
                placeholder="Nhập tên tài khoản của bạn..."
              />
              <User className="w-4 h-4 text-stone-400 absolute right-3.5 top-3 pointer-events-none" />
            </div>
          </div>

          <div>
            <label className="block text-xs font-bold text-stone-700 mb-1.5">
              Mật khẩu (Password):
            </label>
            <div className="relative">
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full bg-stone-50 border border-stone-300 rounded-xl px-3.5 py-2.5 text-xs text-stone-800 placeholder-stone-400 focus:outline-none focus:ring-2 focus:ring-crimson-700/20 focus:bg-white transition"
                placeholder="Nhập mật khẩu..."
              />
              <Lock className="w-4 h-4 text-stone-400 absolute right-3.5 top-3 pointer-events-none" />
            </div>
          </div>

          <button
            type="submit"
            disabled={isSubmitting || !username.trim() || !password}
            className="w-full py-3.5 rounded-full bg-crimson-700 hover:bg-crimson-800 text-white text-xs font-bold transition shadow-lg hover:shadow-crimson-900/30 disabled:opacity-40 disabled:cursor-not-allowed"
          >
            {isSubmitting ? 'Đang Đăng Nhập...' : 'Xác Nhận Đăng Nhập'}
          </button>

          <div className="pt-2 flex items-center justify-center gap-1.5 text-[11px] text-stone-400 text-center">
            <ShieldCheck className="w-3.5 h-3.5 text-emerald-600" />
            <span>Kết nối an toàn • Bảo mật thông tin phiên giao dịch</span>
          </div>
        </form>
      </div>
    </div>
  );
}
