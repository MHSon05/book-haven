import React, { useState } from 'react';
import { Shield, Lock, User, ArrowLeft, KeyRound, AlertCircle } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

export default function AdminLoginView({ onNavigate }) {
  const { adminLogin } = useAuth();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!username.trim() || !password) return;

    setIsSubmitting(true);
    setErrorMsg('');
    try {
      await adminLogin(username.trim(), password);
    } catch (err) {
      setErrorMsg(err.message || 'Tài khoản hoặc mật khẩu quản trị không chính xác.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-stone-900 flex flex-col justify-center items-center p-4 selection:bg-crimson-600 selection:text-white">
      {/* Background decoration elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none opacity-20">
        <div className="absolute -top-40 -left-40 w-96 h-96 rounded-full bg-crimson-600 blur-3xl"></div>
        <div className="absolute -bottom-40 -right-40 w-96 h-96 rounded-full bg-amber-600 blur-3xl"></div>
      </div>

      <div className="relative z-10 w-full max-w-md bg-stone-950/80 backdrop-blur-xl border border-stone-800 rounded-3xl p-8 shadow-2xl space-y-6">
        {/* Brand & Security Header */}
        <div className="text-center space-y-3">
          <div className="w-16 h-16 mx-auto rounded-2xl bg-crimson-900/40 border border-crimson-700/50 text-crimson-400 flex items-center justify-center shadow-inner">
            <Shield className="w-8 h-8 text-crimson-400" />
          </div>
          <div>
            <h1 className="font-serif-title text-2xl font-bold text-white tracking-tight">
              Cổng Quản Trị Hệ Thống
            </h1>
            <p className="text-xs text-stone-400 mt-1">
              BookHaven — Back-Office Management Portal
            </p>
          </div>
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-stone-900 border border-stone-800 text-[11px] text-stone-400">
            <KeyRound className="w-3.5 h-3.5 text-amber-500" />
            <span>Khu vực bảo mật • Yêu cầu tài khoản Quản trị</span>
          </div>
        </div>

        {/* Error Alert if any */}
        {errorMsg && (
          <div className="p-3.5 rounded-xl bg-red-950/60 border border-red-800/80 text-red-300 text-xs flex items-start gap-2.5 animate-fadeIn">
            <AlertCircle className="w-4 h-4 text-red-400 shrink-0 mt-0.5" />
            <span>{errorMsg}</span>
          </div>
        )}

        {/* Login Form */}
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold text-stone-300 mb-1.5">
              Tên tài khoản Quản trị (Admin Username)
            </label>
            <div className="relative">
              <input
                type="text"
                required
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="Nhập username quản trị..."
                className="w-full bg-stone-900/90 border border-stone-700 rounded-xl px-3.5 py-2.5 text-xs text-white placeholder-stone-500 focus:outline-none focus:border-crimson-500 focus:ring-1 focus:ring-crimson-500 transition"
              />
              <User className="w-4 h-4 text-stone-500 absolute right-3.5 top-3 pointer-events-none" />
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-stone-300 mb-1.5">
              Mật khẩu xác thực (Password)
            </label>
            <div className="relative">
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Nhập mật khẩu..."
                className="w-full bg-stone-900/90 border border-stone-700 rounded-xl px-3.5 py-2.5 text-xs text-white placeholder-stone-500 focus:outline-none focus:border-crimson-500 focus:ring-1 focus:ring-crimson-500 transition"
              />
              <Lock className="w-4 h-4 text-stone-500 absolute right-3.5 top-3 pointer-events-none" />
            </div>
          </div>

          <button
            type="submit"
            disabled={isSubmitting || !username.trim() || !password}
            className="w-full py-3.5 rounded-xl bg-crimson-700 hover:bg-crimson-600 disabled:opacity-40 disabled:cursor-not-allowed text-white text-xs font-bold transition shadow-lg shadow-crimson-950 flex items-center justify-center gap-2"
          >
            <Shield className="w-4 h-4" />
            <span>{isSubmitting ? 'Đang xác thực hệ thống...' : 'Đăng Nhập Cổng Quản Trị'}</span>
          </button>
        </form>

        {/* Back to store navigation */}
        <div className="pt-2 border-t border-stone-800/80 text-center">
          <button
            type="button"
            onClick={() => onNavigate('catalog')}
            className="inline-flex items-center gap-1.5 text-xs text-stone-400 hover:text-white transition font-medium"
          >
            <ArrowLeft className="w-3.5 h-3.5" />
            <span>Quay lại Cửa Hàng BookHaven</span>
          </button>
        </div>
      </div>
    </div>
  );
}
