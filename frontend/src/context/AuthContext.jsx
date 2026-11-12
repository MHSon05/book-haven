import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { authApi } from '../api';
import { useToast } from './ToastContext';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const { showToast } = useToast();
  const [token, setToken] = useState(() => localStorage.getItem('bookhaven_token') || null);
  const [user, setUser] = useState(() => {
    try {
      return JSON.parse(localStorage.getItem('bookhaven_user') || 'null');
    } catch {
      return null;
    }
  });
  const [isAuthModalOpen, setIsAuthModalOpen] = useState(false);

  // Phiên đăng nhập Quản trị viên (ADMIN) độc lập hoàn toàn
  const [adminToken, setAdminToken] = useState(() => localStorage.getItem('bookhaven_admin_token') || null);
  const [adminUser, setAdminUser] = useState(() => {
    try {
      return JSON.parse(localStorage.getItem('bookhaven_admin_user') || 'null');
    } catch {
      return null;
    }
  });

  // Validate session on mount
  useEffect(() => {
    if (token) {
      authApi
        .getMe()
        .then((me) => {
          setUser(me);
          localStorage.setItem('bookhaven_user', JSON.stringify(me));
        })
        .catch(() => {
          logout();
        });
    } else {
      setUser(null);
      localStorage.removeItem('bookhaven_user');
    }
  }, [token]);

  const login = useCallback(
    async (username, password) => {
      try {
        const res = await authApi.login(username, password);
        setToken(res.access_token);
        localStorage.setItem('bookhaven_token', res.access_token);
        localStorage.removeItem('bookhaven_guest_id');

        // Lấy đầy đủ thông tin tài khoản (gồm địa chỉ nhận hàng, số điện thoại, điểm thưởng)
        const me = await authApi.getMe().catch(() => ({
          user_id: res.user_id,
          username: res.username,
          full_name: res.full_name,
          role: res.role,
        }));

        setUser(me);
        localStorage.setItem('bookhaven_user', JSON.stringify(me));
        setIsAuthModalOpen(false);
        showToast(`Đăng nhập thành công! Xin chào ${me.full_name || res.username}`, 'success');
        return me;
      } catch (err) {
        showToast(err.message, 'error');
        throw err;
      }
    },
    [showToast]
  );

  const logout = useCallback(() => {
    setToken(null);
    setUser(null);
    localStorage.removeItem('bookhaven_token');
    localStorage.removeItem('bookhaven_user');
    localStorage.removeItem('bookhaven_guest_id');
  }, []);

  // Admin Auth Methods
  const adminLogin = useCallback(
    async (username, password) => {
      try {
        const res = await authApi.login(username, password);
        if (res.role?.toUpperCase() !== 'ADMIN') {
          throw new Error('Tài khoản này không có quyền Quản trị viên (ADMIN)!');
        }
        setAdminToken(res.access_token);
        localStorage.setItem('bookhaven_admin_token', res.access_token);
        const adminProfile = {
          user_id: res.user_id,
          username: res.username,
          full_name: res.full_name,
          role: res.role,
        };
        setAdminUser(adminProfile);
        localStorage.setItem('bookhaven_admin_user', JSON.stringify(adminProfile));
        showToast(`Chào mừng Quản trị viên ${res.full_name || res.username}!`, 'success');
        return adminProfile;
      } catch (err) {
        showToast(err.message, 'error');
        throw err;
      }
    },
    [showToast]
  );

  const adminLogout = useCallback(() => {
    setAdminToken(null);
    setAdminUser(null);
    localStorage.removeItem('bookhaven_admin_token');
    localStorage.removeItem('bookhaven_admin_user');
  }, []);

  const openAuthModal = useCallback(() => setIsAuthModalOpen(true), []);
  const closeAuthModal = useCallback(() => setIsAuthModalOpen(false), []);

  return (
    <AuthContext.Provider
      value={{
        token,
        user,
        isAdmin: user?.role === 'ADMIN' || adminUser?.role === 'ADMIN',
        login,
        logout,
        // Admin Isolated Session
        adminToken,
        adminUser,
        isAdminLoggedIn: Boolean(adminToken && adminUser?.role === 'ADMIN'),
        adminLogin,
        adminLogout,
        isAuthModalOpen,
        openAuthModal,
        closeAuthModal,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}
