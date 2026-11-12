import React from 'react';
import { useAuth } from '../../context/AuthContext';
import AdminLayout from './AdminLayout';
import AdminLoginView from './AdminLoginView';

export default function AdminPortalView({ onNavigate }) {
  const { isAdminLoggedIn, user } = useAuth();

  // Cho phép truy cập nếu đã đăng nhập phiên admin độc lập HOẶC user hiện tại có role ADMIN
  const hasAdminAccess = isAdminLoggedIn || user?.role?.toUpperCase() === 'ADMIN';

  if (!hasAdminAccess) {
    return <AdminLoginView onNavigate={onNavigate} />;
  }

  return <AdminLayout onNavigate={onNavigate} />;
}
