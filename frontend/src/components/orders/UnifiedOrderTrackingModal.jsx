import React, { useState, useEffect } from 'react';
import DroneFlightRadarModal from './DroneFlightRadarModal';
import StandardShippingTimelineModal from './StandardShippingTimelineModal';
import { paymentApi } from '../../api';

export default function UnifiedOrderTrackingModal({ orderId, initialOrder, onClose, onDelivered }) {
  const [order, setOrder] = useState(initialOrder || null);
  const [loading, setLoading] = useState(!initialOrder);

  useEffect(() => {
    if (!initialOrder && orderId) {
      paymentApi
        .getOrderStatus(orderId)
        .then((data) => setOrder(data))
        .catch(console.error)
        .finally(() => setLoading(false));
    }
  }, [orderId, initialOrder]);

  if (loading) {
    return (
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-stone-950/70 backdrop-blur-sm">
        <div className="bg-stone-900 border border-stone-800 text-white px-6 py-4 rounded-2xl flex items-center gap-3">
          <div className="w-5 h-5 border-2 border-emerald-400 border-t-transparent rounded-full animate-spin"></div>
          <span className="text-xs font-semibold">Đang nạp dữ liệu điều hướng không lưu & vận chuyển...</span>
        </div>
      </div>
    );
  }

  const carrier = order?.carrier || order?.shipping_carrier || 'GHN_STANDARD';
  const isDrone = carrier === 'HANOI_DRONE';

  if (isDrone) {
    return (
      <DroneFlightRadarModal
        orderId={orderId || order?.order_id}
        initialOrder={order}
        onClose={onClose}
        onDelivered={onDelivered}
      />
    );
  }

  return (
    <StandardShippingTimelineModal
      orderId={orderId || order?.order_id}
      initialOrder={order}
      onClose={onClose}
      onDelivered={onDelivered}
    />
  );
}
