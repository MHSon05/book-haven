import React, { useState } from 'react';
import {
  LayoutDashboard,
  DollarSign,
  Truck,
  Layers,
  LogOut,
  ExternalLink,
  Shield,
  Activity,
  Menu,
  X,
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import AdminOverviewTab from './AdminOverviewTab';
import RevenueTab from './RevenueTab';
import OrdersDispatchTab from './OrdersDispatchTab';
import InventoryRestockTab from './InventoryRestockTab';

export default function AdminLayout({ onNavigate }) {
  const { adminUser, user, adminLogout } = useAuth();
  const [activeTab, setActiveTab] = useState('overview');
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  const currentAdmin = adminUser || (user?.role === 'ADMIN' ? user : { full_name: 'Quản Trị Viên', username: 'admin' });

  const navItems = [
    {
      id: 'overview',
      label: 'Tổng Quan Hệ Thống',
      icon: LayoutDashboard,
      badge: 'Realtime',
    },
    {
      id: 'reports',
      label: 'Báo Cáo Doanh Thu',
      sublabel: 'Quy tắc BR06',
      icon: DollarSign,
    },
    {
      id: 'orders',
      label: 'Điều Phối & Bàn Giao Drone',
      sublabel: 'Tải trọng 2000g (BR05)',
      icon: Truck,
    },
    {
      id: 'inventory',
      label: 'Quản Lý Tồn & Nhập Kho',
      sublabel: 'Nghiệp vụ UC12',
      icon: Layers,
    },
  ];

  const handleLogout = () => {
    adminLogout();
  };

  return (
    <div className="min-h-screen bg-stone-100 flex flex-col md:flex-row text-stone-900 font-sans selection:bg-crimson-600 selection:text-white">
      {/* Mobile Top Header */}
      <div className="md:hidden flex items-center justify-between p-4 bg-stone-950 text-white border-b border-stone-800 sticky top-0 z-50">
        <div className="flex items-center gap-2.5">
          <span className="text-xl">⛩️</span>
          <div>
            <h1 className="font-serif-title font-bold text-sm tracking-tight text-white">BookHaven Admin</h1>
            <p className="text-[10px] text-stone-400">Back-Office Suite</p>
          </div>
        </div>
        <button
          onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
          className="p-2 rounded-lg bg-stone-900 text-stone-300 hover:text-white"
        >
          {isMobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
        </button>
      </div>

      {/* Sidebar Navigation */}
      <aside
        className={`fixed inset-y-0 left-0 z-40 w-64 bg-stone-950 text-stone-300 flex flex-col justify-between border-r border-stone-800 transition-transform duration-300 md:static md:translate-x-0 ${
          isMobileMenuOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        {/* Brand Area */}
        <div>
          <div className="p-6 border-b border-stone-800/80 flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-crimson-700 text-white flex items-center justify-center text-xl shadow-lg shadow-crimson-950">
              ⛩️
            </div>
            <div>
              <h1 className="font-serif-title font-bold text-base tracking-tight text-white">
                BookHaven Admin
              </h1>
              <span className="inline-block text-[10px] font-mono uppercase tracking-wider text-crimson-400 font-semibold">
                Back-Office Portal
              </span>
            </div>
          </div>

          {/* Navigation Links */}
          <nav className="p-4 space-y-1.5">
            <div className="px-3 py-2 text-[10px] font-bold uppercase tracking-wider text-stone-500">
              Phân Hệ Quản Trị
            </div>
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = activeTab === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => {
                    setActiveTab(item.id);
                    setIsMobileMenuOpen(false);
                  }}
                  className={`w-full flex items-center justify-between px-3.5 py-3 rounded-xl text-xs font-semibold transition ${
                    isActive
                      ? 'bg-crimson-700 text-white shadow-md shadow-crimson-950'
                      : 'text-stone-400 hover:text-white hover:bg-stone-900'
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <Icon className={`w-4 h-4 ${isActive ? 'text-white' : 'text-stone-400'}`} />
                    <div className="text-left">
                      <div>{item.label}</div>
                      {item.sublabel && (
                        <div className={`text-[10px] ${isActive ? 'text-crimson-200' : 'text-stone-500'}`}>
                          {item.sublabel}
                        </div>
                      )}
                    </div>
                  </div>
                  {item.badge && (
                    <span className="text-[9px] uppercase px-1.5 py-0.5 rounded bg-emerald-500/20 text-emerald-400 font-bold border border-emerald-500/30">
                      {item.badge}
                    </span>
                  )}
                </button>
              );
            })}
          </nav>
        </div>

        {/* Bottom Profile & Actions Area */}
        <div className="p-4 border-t border-stone-800/80 space-y-3 bg-stone-950/80">
          {/* Admin Profile Card */}
          <div className="p-3 rounded-xl bg-stone-900/90 border border-stone-800 flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-crimson-900/50 text-crimson-300 border border-crimson-700/40 flex items-center justify-center text-xs font-bold shrink-0">
              {currentAdmin.full_name ? currentAdmin.full_name.charAt(0) : 'A'}
            </div>
            <div className="min-w-0 flex-1">
              <p className="text-xs font-bold text-white truncate">{currentAdmin.full_name}</p>
              <div className="flex items-center gap-1.5 text-[10px] text-stone-400">
                <Shield className="w-3 h-3 text-crimson-500" />
                <span>@{currentAdmin.username} • ADMIN</span>
              </div>
            </div>
          </div>

          {/* Action Buttons */}
          <div>
            <button
              onClick={handleLogout}
              className="w-full py-2.5 px-3 rounded-xl bg-red-950/40 hover:bg-red-900/50 text-red-400 hover:text-red-300 text-xs font-semibold transition flex items-center justify-center gap-2 border border-red-900/40 shadow-sm"
            >
              <LogOut className="w-3.5 h-3.5" />
              <span>Đăng Xuất Admin</span>
            </button>
          </div>
        </div>
      </aside>

      {/* Main Content Area */}
      <main className="flex-1 flex flex-col min-w-0 overflow-y-auto">
        {/* Top Header */}
        <header className="bg-white border-b border-stone-200 px-6 py-4 flex items-center justify-between sticky top-0 z-30 shadow-sm">
          <div>
            <div className="text-[11px] font-semibold text-stone-400 uppercase tracking-wider">
              BookHaven Back-Office / {navItems.find((n) => n.id === activeTab)?.label}
            </div>
            <h2 className="text-lg font-bold font-serif-title text-stone-900">
              {navItems.find((n) => n.id === activeTab)?.label}
            </h2>
          </div>

          <div className="flex items-center gap-3">
            <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-full bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs font-medium">
              <Activity className="w-3.5 h-3.5 text-emerald-600 animate-pulse" />
              <span>FastAPI Daemon Operational (2.0.0)</span>
            </div>

            <button
              onClick={() => onNavigate('catalog')}
              className="flex items-center gap-1.5 px-3.5 py-1.5 rounded-full bg-stone-100 hover:bg-stone-200 text-stone-700 text-xs font-semibold transition border border-stone-200"
            >
              <ExternalLink className="w-3.5 h-3.5" />
              <span className="hidden sm:inline">Cửa hàng</span>
            </button>
          </div>
        </header>

        {/* Tab Work Area */}
        <div className="p-6 md:p-8 flex-1">
          {activeTab === 'overview' && <AdminOverviewTab onSelectTab={setActiveTab} />}
          {activeTab === 'reports' && <RevenueTab />}
          {activeTab === 'orders' && <OrdersDispatchTab />}
          {activeTab === 'inventory' && <InventoryRestockTab />}
        </div>
      </main>
    </div>
  );
}
