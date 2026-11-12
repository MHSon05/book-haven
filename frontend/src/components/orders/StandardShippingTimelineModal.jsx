import React, { useState, useEffect } from 'react';
import { Truck, CheckCircle2, Package, MapPin, Clock, X, ShieldCheck } from 'lucide-react';
import { paymentApi, formatVND } from '../../api';

export default function StandardShippingTimelineModal({ orderId, initialOrder, onClose, onDelivered }) {
  const [order, setOrder] = useState(initialOrder || null);
  const [isLoading, setIsLoading] = useState(!initialOrder);
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    if (orderId) {
      paymentApi
        .getOrderStatus(orderId)
        .then((data) => setOrder(data))
        .catch(console.error)
        .finally(() => setIsLoading(false));
    }
  }, [orderId]);

  const handleConfirmReceived = async () => {
    if (!order?.order_id) return;
    setIsSubmitting(true);
    try {
      await paymentApi.markDelivered(order.order_id);
      setOrder((prev) => ({ ...prev, status: 'DELIVERED' }));
      onDelivered?.(order.order_id);
    } catch (err) {
      console.error(err);
    } finally {
      setIsSubmitting(false);
    }
  };

  const isDelivered = order?.status === 'DELIVERED';
  const isShipping = order?.status === 'SHIPPING';

  // 5 steps for GHN Logistics
  const steps = [
    {
      title: 'Đã Tiếp Nhận & Đóng Gói Chống Sốc',
      desc: 'Bọc xốp 3 lớp tại Kho Sách BookHaven (PTIT Km10 Nguyễn Trãi, Hà Đông)',
      time: order?.created_at ? order.created_at.slice(0, 16) : 'Đã hoàn tất',
      completed: true,
      current: false,
    },
    {
      title: 'Đã Bàn Giao Bưu Tá GHN',
      desc: `Mã vận đơn: ${order?.tracking_code || 'GHN-STD-DEFAULT'}`,
      time: isShipping || isDelivered ? 'Đã xuất kho' : 'Chờ lấy hàng',
      completed: isShipping || isDelivered,
      current: isShipping,
    },
    {
      title: 'Đang Trung Chuyển Kho Tổng Hà Nội',
      desc: 'Bưu cục GHN Hà Đông chuyển tiếp đến điểm phát hàng khu vực',
      time: isShipping || isDelivered ? 'Trong ngày' : 'Dự kiến',
      completed: isShipping || isDelivered,
      current: false,
    },
    {
      title: 'Shipper GHN Đang Giao Hàng',
      desc: 'Tài xế đang liên hệ theo số điện thoại nhận hàng của bạn',
      time: isDelivered ? 'Đã liên hệ' : isShipping ? 'Đang trên đường phát' : 'Chờ phát',
      completed: isDelivered,
      current: isShipping,
    },
    {
      title: 'Giao Hàng Thành Công',
      desc: 'Độc giả đã ký nhận sách và hoàn tất đơn hàng',
      time: isDelivered ? 'Giao thành công' : 'Dự kiến 2-3 ngày',
      completed: isDelivered,
      current: isDelivered,
    },
  ];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-stone-950/70 backdrop-blur-sm animate-fadeIn">
      <div className="relative w-full max-w-xl bg-white rounded-3xl shadow-2xl border border-stone-200 overflow-hidden flex flex-col">
        {/* Header */}
        <div className="p-6 bg-stone-50 border-b border-stone-200 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-2xl bg-amber-100 text-amber-800 flex items-center justify-center text-lg">
              🚚
            </div>
            <div>
              <h3 className="font-serif-title font-bold text-base text-stone-900">
                Lộ Trình Giao Hàng Nhanh (GHN)
              </h3>
              <p className="text-xs text-stone-500 font-mono">
                Vận đơn: <strong className="text-crimson-700">{order?.tracking_code || 'Chờ bàn giao'}</strong>
              </p>
            </div>
          </div>

          <button
            onClick={onClose}
            className="p-2 rounded-full text-stone-400 hover:text-stone-700 hover:bg-stone-100 transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content: Timeline */}
        <div className="p-6 overflow-y-auto max-h-[60vh] space-y-6">
          {/* Destination Summary Card */}
          <div className="p-4 rounded-2xl bg-stone-50 border border-stone-200 space-y-1.5 text-xs">
            <div className="flex items-center gap-2 text-stone-500 font-medium">
              <MapPin className="w-3.5 h-3.5 text-crimson-700" />
              <span>Địa chỉ nhận sách:</span>
            </div>
            <p className="font-bold text-stone-800">{order?.receiver_name || order?.recipient_name} ({order?.receiver_phone || order?.recipient_phone})</p>
            <p className="text-stone-600">{order?.shipping_address}</p>
          </div>

          {/* Stepper Timeline */}
          <div className="relative pl-6 space-y-6 before:absolute before:left-2.5 before:top-3 before:bottom-3 before:w-0.5 before:bg-stone-200">
            {steps.map((s, idx) => (
              <div key={idx} className="relative flex items-start gap-4 text-xs">
                {/* Step Circle Indicator */}
                <div
                  className={`absolute -left-6 top-0 w-5 h-5 rounded-full flex items-center justify-center text-[10px] font-bold z-10 ${
                    s.completed
                      ? 'bg-emerald-600 text-white shadow-sm'
                      : 'bg-stone-200 text-stone-500'
                  }`}
                >
                  {s.completed ? '✓' : idx + 1}
                </div>

                <div className="min-w-0 flex-1">
                  <div className="flex items-center justify-between gap-2">
                    <h4 className={`font-bold ${s.completed ? 'text-stone-900' : 'text-stone-500'}`}>
                      {s.title}
                    </h4>
                    <span className="text-[10px] text-stone-400 shrink-0 font-mono">{s.time}</span>
                  </div>
                  <p className="text-stone-500 text-[11px] mt-0.5">{s.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Footer Actions */}
        <div className="p-4 bg-stone-50 border-t border-stone-200 flex items-center justify-between gap-3">
          <div className="flex items-center gap-1.5 text-[11px] text-stone-500">
            <ShieldCheck className="w-4 h-4 text-emerald-600" />
            <span>Đối tác vận chuyển GHN Standard • Cam kết nguyên vẹn</span>
          </div>

          {isShipping && (
            <button
              onClick={handleConfirmReceived}
              disabled={isSubmitting}
              className="px-4 py-2 rounded-full bg-emerald-700 hover:bg-emerald-800 text-white text-xs font-bold transition shadow"
            >
              {isSubmitting ? 'Đang xác nhận...' : 'Đã Nhận Được Sách'}
            </button>
          )}

          {isDelivered && (
            <span className="px-3 py-1.5 rounded-full bg-emerald-100 text-emerald-800 text-xs font-bold">
              Đã Giao Thành Công
            </span>
          )}
        </div>
      </div>
    </div>
  );
}
