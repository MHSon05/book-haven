import React, { useState, useEffect } from 'react';
import { DollarSign, Truck, Layers, AlertTriangle, ArrowRight, CheckCircle2, TrendingUp, RefreshCw } from 'lucide-react';
import { adminApi, formatVND } from '../../api';

export default function AdminOverviewTab({ onSelectTab }) {
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({
    totalRevenue: 0,
    completedOrdersCount: 0,
    dronePendingCount: 0,
    lowStockItems: [],
    recentOrders: [],
    totalStockCount: 0,
  });

  const loadDashboardData = async () => {
    setLoading(true);
    try {
      const [revData, ordersData, invData] = await Promise.all([
        adminApi.getRevenueReport().catch(() => ({ total_revenue: 0, completed_orders_count: 0 })),
        adminApi.getOrders().catch(() => ({ orders: [] })),
        adminApi.getInventory().catch(() => ({ inventory: [] })),
      ]);

      const ordersList = ordersData.orders || [];
      const inventoryList = invData.inventory || [];

      // Đơn hàng chờ điều phối Drone
      const dronePending = ordersList.filter(
        (o) => o.carrier === 'HANOI_DRONE' && ['PAID', 'PENDING_CASH', 'PACKED'].includes(o.status)
      ).length;

      // Ấn bản có tồn kho khả dụng thấp (< 5)
      const lowStock = inventoryList.filter((item) => (item.available_stock || 0) < 5);

      // Tổng lượng sách tồn trong kho
      const totalStock = inventoryList.reduce((acc, cur) => acc + (cur.stock_on_hand || 0), 0);

      setStats({
        totalRevenue: revData.total_revenue || 0,
        completedOrdersCount: revData.completed_orders_count || ordersList.filter((o) => o.status === 'DELIVERED').length,
        dronePendingCount: dronePending,
        lowStockItems: lowStock,
        recentOrders: ordersList.slice(0, 5),
        totalStockCount: totalStock,
      });
    } catch (err) {
      console.error('Failed to load admin overview:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDashboardData();
  }, []);

  return (
    <div className="space-y-6 animate-fadeIn">
      {/* Top Banner & Quick Refresh */}
      <div className="flex flex-wrap items-center justify-between gap-4 p-5 rounded-2xl bg-gradient-to-r from-stone-900 to-stone-800 text-white shadow-md">
        <div>
          <h2 className="text-lg font-bold font-serif-title flex items-center gap-2">
            <span>Bảng Điều Khiển Tổng Quan</span>
            <span className="text-[10px] uppercase tracking-wider px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-400 font-sans border border-emerald-500/30">
              Live Realtime
            </span>
          </h2>
          <p className="text-xs text-stone-300 mt-1">
            Theo dõi KPIs kinh doanh, vận hành giao hàng Drone và cảnh báo tồn kho thời gian thực.
          </p>
        </div>
        <button
          onClick={loadDashboardData}
          disabled={loading}
          className="flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-stone-700/60 hover:bg-stone-700 text-xs font-semibold transition border border-stone-600 disabled:opacity-50"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          <span>Làm mới dữ liệu</span>
        </button>
      </div>

      {/* 4 Metric KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Metric 1: Doanh thu */}
        <div className="p-5 rounded-2xl bg-white border border-stone-200 shadow-sm flex flex-col justify-between">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-stone-500">Doanh Thu Thực Tế (BR06)</span>
            <div className="w-8 h-8 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center">
              <DollarSign className="w-4 h-4" />
            </div>
          </div>
          <div className="my-3">
            <div className="text-2xl font-bold font-serif-title text-stone-900">
              {formatVND(stats.totalRevenue)}
            </div>
            <p className="text-[11px] text-stone-400 mt-0.5 flex items-center gap-1">
              <TrendingUp className="w-3 h-3 text-emerald-600" />
              <span>Đã khấu trừ Voucher & Phí vận chuyển</span>
            </p>
          </div>
          <button
            onClick={() => onSelectTab('reports')}
            className="text-[11px] font-bold text-crimson-700 hover:text-crimson-800 flex items-center gap-1 group"
          >
            <span>Chi tiết báo cáo</span>
            <ArrowRight className="w-3 h-3 group-hover:translate-x-0.5 transition" />
          </button>
        </div>

        {/* Metric 2: Đơn hoàn tất */}
        <div className="p-5 rounded-2xl bg-white border border-stone-200 shadow-sm flex flex-col justify-between">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-stone-500">Đơn Hàng Hoàn Tất</span>
            <div className="w-8 h-8 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center">
              <CheckCircle2 className="w-4 h-4" />
            </div>
          </div>
          <div className="my-3">
            <div className="text-2xl font-bold font-serif-title text-stone-900">
              {stats.completedOrdersCount} <span className="text-xs font-normal text-stone-500">đơn</span>
            </div>
            <p className="text-[11px] text-stone-400 mt-0.5">Đã giao thành công đến độc giả</p>
          </div>
          <button
            onClick={() => onSelectTab('orders')}
            className="text-[11px] font-bold text-crimson-700 hover:text-crimson-800 flex items-center gap-1 group"
          >
            <span>Quản lý đơn hàng</span>
            <ArrowRight className="w-3 h-3 group-hover:translate-x-0.5 transition" />
          </button>
        </div>

        {/* Metric 3: Chờ Drone */}
        <div className="p-5 rounded-2xl bg-white border border-stone-200 shadow-sm flex flex-col justify-between">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-stone-500">Chờ Bàn Giao Drone</span>
            <div className="w-8 h-8 rounded-xl bg-purple-50 text-purple-600 flex items-center justify-center">
              <Truck className="w-4 h-4" />
            </div>
          </div>
          <div className="my-3">
            <div className="text-2xl font-bold font-serif-title text-stone-900">
              {stats.dronePendingCount} <span className="text-xs font-normal text-stone-500">đơn</span>
            </div>
            <p className="text-[11px] text-stone-400 mt-0.5">Tải trọng &le; 2000g (Hanoi Drone)</p>
          </div>
          <button
            onClick={() => onSelectTab('orders')}
            className="text-[11px] font-bold text-crimson-700 hover:text-crimson-800 flex items-center gap-1 group"
          >
            <span>Bàn giao Drone</span>
            <ArrowRight className="w-3 h-3 group-hover:translate-x-0.5 transition" />
          </button>
        </div>

        {/* Metric 4: Tồn kho & Cảnh báo */}
        <div className="p-5 rounded-2xl bg-white border border-stone-200 shadow-sm flex flex-col justify-between">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-stone-500">Cảnh Báo Sắp Hết Hàng</span>
            <div className="w-8 h-8 rounded-xl bg-amber-50 text-amber-600 flex items-center justify-center">
              <AlertTriangle className="w-4 h-4" />
            </div>
          </div>
          <div className="my-3">
            <div className="text-2xl font-bold font-serif-title text-stone-900">
              {stats.lowStockItems.length} <span className="text-xs font-normal text-stone-500">ấn bản</span>
            </div>
            <p className="text-[11px] text-stone-400 mt-0.5">Tồn kho khả dụng &lt; 5 cuốn</p>
          </div>
          <button
            onClick={() => onSelectTab('inventory')}
            className="text-[11px] font-bold text-crimson-700 hover:text-crimson-800 flex items-center gap-1 group"
          >
            <span>Nhập kho ngay (UC12)</span>
            <ArrowRight className="w-3 h-3 group-hover:translate-x-0.5 transition" />
          </button>
        </div>
      </div>

      {/* Two Column Section: Low Stock Warning & Recent Orders */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Low Stock Table */}
        <div className="bg-white rounded-2xl border border-stone-200 p-5 shadow-sm space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="font-bold text-sm text-stone-900 flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 text-amber-500" />
              <span>Ấn Bản Cần Bổ Sung Tồn Kho</span>
            </h3>
            <span className="text-xs text-stone-400">
              Tổng kho: <strong>{stats.totalStockCount}</strong> cuốn
            </span>
          </div>

          {stats.lowStockItems.length === 0 ? (
            <p className="text-xs text-stone-400 py-6 text-center italic">
              Tất cả ấn bản đều đảm bảo số lượng tồn kho khả dụng dồi dào.
            </p>
          ) : (
            <div className="divide-y divide-stone-100 max-h-64 overflow-y-auto pr-1">
              {stats.lowStockItems.map((item) => (
                <div key={item.edition_id} className="py-2.5 flex items-center justify-between gap-3">
                  <div className="min-w-0">
                    <p className="text-xs font-semibold text-stone-800 truncate">
                      {item.title || item.sku}
                    </p>
                    <p className="text-[10px] text-stone-400 font-mono">
                      SKU: {item.sku} • {item.binding_type}
                    </p>
                  </div>
                  <div className="text-right shrink-0">
                    <span className="inline-block px-2 py-0.5 rounded-md bg-amber-50 text-amber-700 border border-amber-200 text-xs font-bold font-mono">
                      Còn {item.available_stock}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}

          <button
            onClick={() => onSelectTab('inventory')}
            className="w-full py-2.5 rounded-xl bg-stone-100 hover:bg-stone-200 text-stone-800 text-xs font-bold transition flex items-center justify-center gap-2"
          >
            <Layers className="w-3.5 h-3.5" />
            <span>Mở Bảng Nhập Kho & Quản Lý Tồn (UC12)</span>
          </button>
        </div>

        {/* Project Architecture & Operational Notice */}
        <div className="bg-white rounded-2xl border border-stone-200 p-5 shadow-sm flex flex-col justify-between space-y-4">
          <div>
            <h3 className="font-bold text-sm text-stone-900 flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-600" />
              <span>Hệ Thống Nghiệp Vụ Tiểu Luận ISAD</span>
            </h3>
            <p className="text-xs text-stone-500 mt-1">
              Phục vụ Báo cáo môn Phân tích và Thiết kế Hệ thống Thông tin (Chương 5):
            </p>

            <ul className="mt-3 space-y-2 text-xs text-stone-600">
              <li className="flex items-start gap-2">
                <span className="w-1.5 h-1.5 rounded-full bg-crimson-600 mt-1.5 shrink-0"></span>
                <span><strong>BR05 (Giao vận Drone)</strong>: Kiểm soát giới hạn tải trọng &le; 2000g cho tuyến bay nội đô Hà Nội.</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-600 mt-1.5 shrink-0"></span>
                <span><strong>BR06 (Báo cáo Doanh thu)</strong>: Tính toán dòng tiền thực sau chiết khấu voucher và doanh thu thực nhận.</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="w-1.5 h-1.5 rounded-full bg-amber-600 mt-1.5 shrink-0"></span>
                <span><strong>BR03 (Giữ chỗ 15 phút)</strong>: Background worker tự động giải phóng tồn kho cho đơn hàng quá hạn thanh toán.</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="w-1.5 h-1.5 rounded-full bg-blue-600 mt-1.5 shrink-0"></span>
                <span><strong>UC12 (Quản lý Nhập kho)</strong>: Cập nhật biến động số lượng tồn kho theo thời gian thực.</span>
              </li>
            </ul>
          </div>

          <div className="p-3 rounded-xl bg-stone-50 border border-stone-200 text-[11px] text-stone-500 flex items-center justify-between">
            <span>Sinh viên: <strong>Mai Hữu Sơn - B23DCAT262</strong></span>
            <span>GVHD: <strong>PGS. TS. Trần Đình Quế</strong></span>
          </div>
        </div>
      </div>
    </div>
  );
}
