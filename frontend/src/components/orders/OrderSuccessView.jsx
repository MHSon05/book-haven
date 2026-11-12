import React, { useEffect, useState } from 'react';
import { CheckCircle, Package, Home, Plane, Truck } from 'lucide-react';
import { paymentApi, formatVND } from '../../api';
import UnifiedOrderTrackingModal from './UnifiedOrderTrackingModal';

export default function OrderSuccessView({ orderId, onNavigate }) {
  const [order, setOrder] = useState(null);
  const [isTrackingOpen, setIsTrackingOpen] = useState(false);

  useEffect(() => {
    if (orderId) {
      paymentApi
        .getOrderStatus(orderId)
        .then((data) => setOrder(data))
        .catch(console.error);
    }
  }, [orderId]);

  const isDrone = order?.carrier === 'HANOI_DRONE' || order?.shipping_carrier === 'HANOI_DRONE';

  return (
    <div className="max-w-2xl mx-auto px-4 py-16 text-center animate-fadeIn">
      {/* Celebration Icon */}
      <div className="w-20 h-20 rounded-full bg-emerald-100 text-emerald-600 flex items-center justify-center mx-auto mb-6 shadow-inner">
        <CheckCircle className="w-10 h-10" />
      </div>

      <h1 className="font-serif-title font-bold text-2xl md:text-3xl text-stone-900 mb-2">
        Đặt Hàng Thành Công!
      </h1>
      <p className="text-xs text-stone-500 mb-8 max-w-md mx-auto">
        Cảm ơn bạn đã tin tưởng BookHaven. Đơn hàng của bạn đã được tiếp nhận và hệ thống đang xử lý chuẩn bị xuất kho.
      </p>

      {/* Special Drone/GHN Live Tracker Promotion Card */}
      <div className="mb-6 p-4 rounded-3xl bg-gradient-to-r from-stone-900 to-stone-800 text-white shadow-xl text-left flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 border border-stone-700">
        <div className="flex items-center gap-3">
          <div className={`w-12 h-12 rounded-2xl flex items-center justify-center text-2xl shadow-inner ${
            isDrone ? 'bg-emerald-950 border border-emerald-500/40 text-emerald-400' : 'bg-amber-950 border border-amber-500/40 text-amber-400'
          }`}>
            {isDrone ? '🚁' : '🚚'}
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-bold text-sm text-white">
                {isDrone ? 'Không Gian Không Lưu Hanoi Drone' : 'Đơn Vị Giao Hàng Nhanh (GHN)'}
              </span>
              <span className="px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-400 text-[10px] font-mono font-bold border border-emerald-500/30">
                LIVE
              </span>
            </div>
            <p className="text-xs text-stone-300 mt-0.5">
              {isDrone
                ? 'Drone sẽ tự động cất cánh trên bản đồ ngay khi Thủ kho PTIT duyệt xuất kho.'
                : 'Theo dõi 5 chặng hành trình vận chuyển tiêu chuẩn đến tay bạn.'}
            </p>
          </div>
        </div>

        <button
          onClick={() => setIsTrackingOpen(true)}
          className="shrink-0 px-4 py-2.5 rounded-xl bg-emerald-700 hover:bg-emerald-600 text-white font-bold text-xs flex items-center gap-2 transition shadow-lg shadow-emerald-950 animate-pulse"
        >
          {isDrone ? <Plane className="w-4 h-4" /> : <Truck className="w-4 h-4" />}
          <span>{isDrone ? 'Mở Bản Đồ Không Lưu' : 'Xem Lộ Trình GHN'}</span>
        </button>
      </div>

      {/* Order Info Card */}
      <div className="bg-white rounded-3xl border border-stone-200 p-6 shadow-sm text-left mb-8 space-y-3 text-xs">
        <div className="flex justify-between py-2 border-b border-stone-100">
          <span className="text-stone-500">Mã đơn hàng:</span>
          <span className="font-mono font-bold text-stone-900">{orderId}</span>
        </div>

        <div className="flex justify-between py-2 border-b border-stone-100">
          <span className="text-stone-500">Hình thức thanh toán:</span>
          <span className="font-bold text-stone-800">
            {order?.payment_method === 'COD'
              ? '💵 Thanh toán tiền mặt khi nhận hàng (COD)'
              : '💳 Chuyển khoản ngân hàng (VietQR)'}
          </span>
        </div>

        <div className="flex justify-between py-2 border-b border-stone-100">
          <span className="text-stone-500">Trạng thái đơn hàng:</span>
          <span className={`font-bold ${
            order?.status === 'PAID' || order?.status === 'DELIVERED'
              ? 'text-emerald-700'
              : order?.status === 'PENDING_CASH'
              ? 'text-amber-700'
              : order?.status === 'SHIPPING'
              ? 'text-blue-700'
              : 'text-stone-700'
          }`}>
            {order?.status === 'PAID'
              ? '✓ ĐÃ THANH TOÁN (PAID)'
              : order?.status === 'PENDING_CASH'
              ? '⏳ CHỜ THU TIỀN MẶT KHI GIAO (COD)'
              : order?.status === 'SHIPPING'
              ? '🚁 ĐANG VẬN CHUYỂN (SHIPPING)'
              : order?.status === 'DELIVERED'
              ? '✓ ĐÃ GIAO THÀNH CÔNG'
              : 'ĐANG XỬ LÝ (PENDING)'}
          </span>
        </div>

        <div className="flex justify-between py-2 border-b border-stone-100">
          <span className="text-stone-500">Đơn vị vận chuyển:</span>
          <span className="font-semibold text-stone-900">
            {isDrone ? '🚁 Hanoi Drone Express (Hỏa Tốc 30 - 45 Phút)' : '🚚 Giao Hàng Nhanh (GHN)'}
          </span>
        </div>

        <div className="flex justify-between py-2 border-b border-stone-100">
          <span className="text-stone-500">Mã vận đơn bưu kiện:</span>
          <span className="font-mono font-bold text-crimson-700">
            {order?.tracking_code || 'Chờ bàn giao xuất kho...'}
          </span>
        </div>

        <div className="flex justify-between py-2">
          <span className="text-stone-500">Tổng thanh toán:</span>
          <span className="font-bold text-base text-crimson-700">
            {formatVND(order?.final_amount ?? order?.final_total ?? order?.total_amount)}
          </span>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex flex-wrap items-center justify-center gap-4">
        <button
          onClick={() => onNavigate('orders')}
          className="flex items-center gap-2 px-6 py-3 rounded-full bg-stone-900 hover:bg-black text-white text-xs font-bold transition shadow"
        >
          <Package className="w-4 h-4" />
          <span>Xem Lịch Sử Đơn Mua</span>
        </button>

        <button
          onClick={() => onNavigate('catalog')}
          className="flex items-center gap-2 px-6 py-3 rounded-full border border-stone-300 hover:border-crimson-700 hover:text-crimson-700 text-stone-700 text-xs font-bold transition"
        >
          <Home className="w-4 h-4" />
          <span>Tiếp Tục Mua Sách</span>
        </button>
      </div>

      {/* Tracking Modal */}
      {isTrackingOpen && (
        <UnifiedOrderTrackingModal
          orderId={orderId}
          initialOrder={order}
          onClose={() => setIsTrackingOpen(false)}
          onDelivered={(id) => {
            paymentApi.getOrderStatus(id).then(setOrder);
          }}
        />
      )}
    </div>
  );
}
