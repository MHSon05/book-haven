import React, { useState, useEffect } from 'react';
import { Package, Clock, Truck, CheckCircle2, XCircle, ArrowLeft, Plane, Eye } from 'lucide-react';
import { authApi, formatVND } from '../../api';
import { useAuth } from '../../context/AuthContext';
import { useToast } from '../../context/ToastContext';
import UnifiedOrderTrackingModal from './UnifiedOrderTrackingModal';

export default function OrdersView({ onNavigate }) {
  const { user, openAuthModal } = useAuth();
  const { showToast } = useToast();
  const [orders, setOrders] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [activeTrackingOrder, setActiveTrackingOrder] = useState(null);

  useEffect(() => {
    if (!user) {
      setIsLoading(false);
      return;
    }

    setIsLoading(true);
    authApi
      .getUserOrders()
      .then((data) => {
        setOrders(Array.isArray(data) ? data : (data.orders || []));
      })
      .catch((err) => {
        showToast('Lỗi nạp danh sách đơn hàng: ' + err.message, 'error');
      })
      .finally(() => setIsLoading(false));
  }, [user, showToast]);

  const getStatusBadge = (status) => {
    switch (status) {
      case 'PAID':
        return (
          <span className="px-2.5 py-1 rounded-full text-[10px] font-bold bg-emerald-100 text-emerald-800 flex items-center gap-1">
            <CheckCircle2 className="w-3 h-3" /> Đã Thanh Toán
          </span>
        );
      case 'PENDING_CASH':
        return (
          <span className="px-2.5 py-1 rounded-full text-[10px] font-bold bg-amber-100 text-amber-900 border border-amber-300 flex items-center gap-1">
            <Clock className="w-3 h-3 text-amber-700" /> Chờ Thu Tiền Mặt (COD)
          </span>
        );
      case 'SHIPPING':
        return (
          <span className="px-2.5 py-1 rounded-full text-[10px] font-bold bg-blue-100 text-blue-800 flex items-center gap-1">
            <Truck className="w-3 h-3" /> Đang Giao Hàng
          </span>
        );
      case 'DELIVERED':
        return (
          <span className="px-2.5 py-1 rounded-full text-[10px] font-bold bg-purple-100 text-purple-800 flex items-center gap-1">
            <CheckCircle2 className="w-3 h-3" /> Giao Thành Công
          </span>
        );
      case 'CANCELLED':
        return (
          <span className="px-2.5 py-1 rounded-full text-[10px] font-bold bg-red-100 text-red-800 flex items-center gap-1">
            <XCircle className="w-3 h-3" /> Đã Hủy
          </span>
        );
      default:
        return (
          <span className="px-2.5 py-1 rounded-full text-[10px] font-bold bg-amber-100 text-amber-800 flex items-center gap-1">
            <Clock className="w-3 h-3" /> Chờ Thanh Toán
          </span>
        );
    }
  };

  if (!user) {
    return (
      <div className="max-w-xl mx-auto px-4 py-20 text-center animate-fadeIn">
        <Package className="w-12 h-12 text-stone-400 mx-auto mb-4" />
        <h2 className="font-serif-title font-bold text-2xl text-stone-900 mb-2">
          Bạn Chưa Đăng Nhập
        </h2>
        <p className="text-xs text-stone-500 mb-6">
          Vui lòng đăng nhập để xem lịch sử mua sách và theo dõi tiến độ đơn hàng.
        </p>
        <button
          onClick={openAuthModal}
          className="px-6 py-2.5 rounded-full bg-crimson-700 hover:bg-crimson-800 text-white text-xs font-bold transition shadow"
        >
          Đăng nhập ngay
        </button>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto px-4 py-8 animate-fadeIn">
      {/* Top Header */}
      <div className="flex items-center justify-between pb-4 mb-6 border-b border-stone-200">
        <div>
          <h1 className="font-serif-title font-bold text-2xl text-stone-900">
            Lịch Sử Đơn Mua Của Bạn
          </h1>
          <p className="text-xs text-stone-500 mt-0.5">
            Tài khoản: <strong>{user.full_name}</strong> (@{user.username})
          </p>
        </div>
        <button
          onClick={() => onNavigate('catalog')}
          className="flex items-center gap-1.5 text-xs font-semibold text-stone-600 hover:text-crimson-700 transition"
        >
          <ArrowLeft className="w-3.5 h-3.5" />
          <span>Về trang chủ</span>
        </button>
      </div>

      {isLoading ? (
        <div className="py-20 text-center">
          <div className="w-8 h-8 border-3 border-crimson-700 border-t-transparent rounded-full animate-spin mx-auto mb-3"></div>
          <p className="text-xs font-semibold text-stone-500">Đang tải lịch sử đơn hàng...</p>
        </div>
      ) : orders.length === 0 ? (
        <div className="py-16 text-center bg-white rounded-3xl border border-stone-200 text-stone-400">
          <Package className="w-10 h-10 mx-auto mb-2 opacity-50" />
          <p className="text-xs font-semibold text-stone-600">Bạn chưa có đơn đặt hàng nào</p>
          <button
            onClick={() => onNavigate('catalog')}
            className="mt-4 px-5 py-2 rounded-full border border-stone-300 text-xs font-bold text-stone-700 hover:bg-stone-50"
          >
            Bắt đầu mua sách ngay
          </button>
        </div>
      ) : (
        <div className="space-y-4">
          {orders.map((ord) => (
            <div
              key={ord.order_id}
              className="bg-white rounded-2xl border border-stone-200 p-5 shadow-sm space-y-3"
            >
              <div className="flex flex-wrap items-center justify-between gap-2 pb-3 border-b border-stone-100">
                <div className="flex items-center gap-3">
                  <span className="font-mono font-bold text-xs text-stone-900">
                    {ord.order_id}
                  </span>
                  <span className="text-[11px] text-stone-400">
                    {new Date(ord.created_at).toLocaleString('vi-VN')}
                  </span>
                </div>
                {getStatusBadge(ord.status)}
              </div>

              {/* Order Items */}
              <div className="divide-y divide-stone-100">
                {(ord.items || []).map((item, idx) => (
                  <div key={idx} className="py-2 flex items-center justify-between text-xs">
                    <div>
                      <p className="font-bold text-stone-800">{item.book_title || item.title}</p>
                      <p className="text-[10px] text-stone-500">
                        {item.binding_type === 'PAPERBACK' ? 'Bìa Mềm' : 'Bìa Cứng'} x {item.quantity}
                      </p>
                    </div>
                    <span className="font-semibold text-stone-800">
                      {formatVND(item.price * item.quantity)}
                    </span>
                  </div>
                ))}
              </div>

              {/* Bottom details & Actions */}
              <div className="pt-2 border-t border-stone-100 flex flex-wrap items-center justify-between text-xs gap-3">
                <div className="text-[11px] text-stone-500">
                  <span>Vận chuyển: </span>
                  <strong className="text-stone-700">
                    {ord.carrier === 'HANOI_DRONE' || ord.shipping_carrier === 'HANOI_DRONE'
                      ? '🚁 Hanoi Drone'
                      : '🚚 GHN Standard'}
                  </strong>
                  {ord.tracking_code && (
                    <span className="ml-2 font-mono text-crimson-700">
                      (Mã: {ord.tracking_code})
                    </span>
                  )}
                </div>

                <div className="flex items-center gap-3">
                  <button
                    onClick={() => setActiveTrackingOrder(ord)}
                    className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-stone-900 hover:bg-black text-white text-[11px] font-bold transition shadow-sm"
                  >
                    {ord.carrier === 'HANOI_DRONE' || ord.shipping_carrier === 'HANOI_DRONE' ? (
                      <>
                        <Plane className="w-3.5 h-3.5 text-emerald-400" />
                        <span>Radar Bay Drone</span>
                      </>
                    ) : (
                      <>
                        <Truck className="w-3.5 h-3.5 text-amber-400" />
                        <span>Lộ Trình GHN</span>
                      </>
                    )}
                  </button>

                  <div className="flex items-center gap-1.5">
                    <span className="text-stone-500">Tổng:</span>
                    <span className="font-bold text-sm text-crimson-700">
                      {formatVND(ord.final_amount || ord.final_total || ord.total_amount)}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Unified Order Tracking Modal */}
      {activeTrackingOrder && (
        <UnifiedOrderTrackingModal
          orderId={activeTrackingOrder.order_id}
          initialOrder={activeTrackingOrder}
          onClose={() => setActiveTrackingOrder(null)}
          onDelivered={() => {
            // Re-fetch orders to reflect delivered state
            authApi
              .getUserOrders()
              .then((data) => setOrders(Array.isArray(data) ? data : (data.orders || [])))
              .catch(console.error);
          }}
        />
      )}
    </div>
  );
}
