import React, { useState, useEffect } from 'react';
import { Plane, Truck, Check, RefreshCw, Clock, History, AlertCircle, Eye } from 'lucide-react';
import { adminApi, formatVND } from '../../api';
import { useToast } from '../../context/ToastContext';
import UnifiedOrderTrackingModal from '../orders/UnifiedOrderTrackingModal';

export default function OrdersDispatchTab() {
  const { showToast } = useToast();
  const [orders, setOrders] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [subTab, setSubTab] = useState('active'); // 'active' | 'history'
  const [trackingModalOrder, setTrackingModalOrder] = useState(null);
  const [flyingDrones, setFlyingDrones] = useState({}); // { [orderId]: remainingSeconds }

  const fetchOrders = () => {
    setIsLoading(true);
    adminApi
      .getOrders()
      .then((data) => setOrders(data.orders || []))
      .catch((err) => showToast('Lỗi tải danh sách đơn: ' + err.message, 'error'))
      .finally(() => setIsLoading(false));
  };

  useEffect(() => {
    fetchOrders();
  }, []);

  // Bắt đầu hành trình Drone bay và tự động hoàn tất
  const startDroneFlightCountdown = (orderId) => {
    setFlyingDrones((prev) => ({ ...prev, [orderId]: 20 }));

    const interval = setInterval(() => {
      setFlyingDrones((prev) => {
        const current = prev[orderId];
        if (current === undefined) {
          clearInterval(interval);
          return prev;
        }
        if (current <= 1) {
          clearInterval(interval);
          const next = { ...prev };
          delete next[orderId];

          // Tự động chuyển DELIVERED khi kết thúc hành trình bay
          adminApi
            .markDelivered(orderId)
            .then(() => {
              showToast(`🚁 Drone đã hạ cánh thành công đơn ${orderId}! Tự động chuyển vào Lịch sử hoàn tất.`, 'success');
              fetchOrders();
            })
            .catch((err) => {
              console.error(err);
              fetchOrders();
            });

          return next;
        }
        return { ...prev, [orderId]: current - 1 };
      });
    }, 1000);
  };

  const handleDispatch = async (orderId, carrier) => {
    try {
      if (carrier === 'HANOI_DRONE') {
        localStorage.setItem(`bookhaven_drone_takeoff_${orderId}`, Date.now().toString());
      }
      const res = await adminApi.dispatchOrder(orderId, carrier);
      showToast(
        `Đã xuất kho bàn giao ${carrier === 'HANOI_DRONE' ? 'Drone' : 'GHN'}! Vận đơn: ${res.tracking_code}`,
        'success'
      );
      fetchOrders();

      // Nếu là Drone: Kích hoạt hành trình bay và tự động chuyển hoàn tất
      if (carrier === 'HANOI_DRONE') {
        startDroneFlightCountdown(orderId);
      }
    } catch (err) {
      showToast(err.message, 'error');
    }
  };

  const handleMarkDelivered = async (orderId) => {
    try {
      await adminApi.markDelivered(orderId);
      showToast(`Đã xác nhận giao thành công đơn ${orderId}!`, 'success');
      fetchOrders();
    } catch (err) {
      showToast(err.message, 'error');
    }
  };

  // Phân chia 2 danh sách theo trạng thái
  const activeOrders = orders.filter((o) =>
    ['PAID', 'PENDING_CASH', 'PACKED', 'SHIPPING', 'AWAITING_PAYMENT'].includes(o.status)
  );
  const historyOrders = orders.filter((o) => o.status === 'DELIVERED' || o.status === 'CANCELLED');
  const displayOrders = subTab === 'active' ? activeOrders : historyOrders;

  return (
    <div className="bg-white rounded-2xl border border-stone-200 p-6 shadow-sm space-y-5 animate-fadeIn">
      {/* Header & Sub-Tab Switcher */}
      <div className="flex flex-wrap items-center justify-between gap-4 pb-4 border-b border-stone-100">
        <div>
          <h3 className="font-serif-title font-bold text-base text-stone-900">
            Quản Lý Đơn Hàng & Điều Phối Vận Chuyển (BR05 / UC11)
          </h3>
          <p className="text-xs text-stone-500 mt-0.5">
            Bàn giao xuất kho đúng đơn vị vận chuyển độc giả đã chọn (Hanoi Drone hoặc GHN)
          </p>
        </div>

        <button
          onClick={fetchOrders}
          disabled={isLoading}
          className="p-2 text-stone-500 hover:text-crimson-700 rounded-lg hover:bg-stone-50 transition border border-stone-200"
          title="Tải lại danh sách"
        >
          <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
        </button>
      </div>

      {/* Sub-tab Navigation */}
      <div className="flex items-center gap-2">
        <button
          onClick={() => setSubTab('active')}
          className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold transition ${
            subTab === 'active'
              ? 'bg-stone-900 text-white shadow-sm'
              : 'bg-stone-100 text-stone-600 hover:bg-stone-200'
          }`}
        >
          <Clock className="w-3.5 h-3.5" />
          <span>Cần Xử Lý</span>
          {activeOrders.length > 0 && (
            <span
              className={`px-1.5 py-0.5 rounded-full text-[10px] font-extrabold ${
                subTab === 'active' ? 'bg-crimson-600 text-white' : 'bg-crimson-100 text-crimson-800'
              }`}
            >
              {activeOrders.length}
            </span>
          )}
        </button>

        <button
          onClick={() => setSubTab('history')}
          className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold transition ${
            subTab === 'history'
              ? 'bg-stone-900 text-white shadow-sm'
              : 'bg-stone-100 text-stone-600 hover:bg-stone-200'
          }`}
        >
          <History className="w-3.5 h-3.5" />
          <span>Lịch Sử Đơn Hàng</span>
          <span
            className={`px-1.5 py-0.5 rounded-full text-[10px] font-bold ${
              subTab === 'history' ? 'bg-stone-700 text-white' : 'bg-stone-200 text-stone-600'
            }`}
          >
            {historyOrders.length}
          </span>
        </button>
      </div>

      {/* Table Content */}
      {isLoading ? (
        <div className="py-16 text-center text-xs text-stone-500">Đang tải dữ liệu đơn hàng...</div>
      ) : displayOrders.length === 0 ? (
        <div className="py-12 text-center text-xs text-stone-400 space-y-1">
          <p className="font-semibold text-stone-600">
            {subTab === 'active' ? 'Không có đơn hàng nào cần xử lý lúc này' : 'Chưa có đơn hàng trong lịch sử'}
          </p>
          <p className="text-[11px] text-stone-400">
            {subTab === 'active'
              ? 'Mọi đơn hàng mới phát sinh (PAID) sẽ tự động xuất hiện tại đây để điều phối xuất kho.'
              : 'Các đơn hàng đã hoàn tất giao hàng hoặc hủy đơn sẽ được lưu trữ tại đây.'}
          </p>
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-stone-200 text-stone-400 font-semibold uppercase text-[10px]">
                <th className="py-3 px-2">Mã Đơn</th>
                <th className="py-3 px-2">Người Nhận & Địa Chỉ</th>
                <th className="py-3 px-2">Phương Thức Đã Đặt</th>
                <th className="py-3 px-2">Trạng Thái</th>
                <th className="py-3 px-2">Tổng Tiền</th>
                <th className="py-3 px-2 text-right">
                  {subTab === 'active' ? 'Thao Tác Điều Phối' : 'Ghi Chú'}
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-stone-100">
              {displayOrders.map((ord) => {
                const carrier = ord.carrier || ord.shipping_carrier || 'GHN_STANDARD';
                const isDrone = carrier === 'HANOI_DRONE';
                const canDispatch = ord.status === 'PAID' || ord.status === 'PENDING' || ord.status === 'PENDING_CASH';
                const canDeliver = ord.status === 'SHIPPING';

                return (
                  <tr key={ord.order_id} className="hover:bg-stone-50/80 transition">
                    {/* Mã Đơn */}
                    <td className="py-3 px-2 font-mono font-bold text-stone-900">
                      <div>{ord.order_id}</div>
                      <div className="text-[10px] text-stone-400 font-sans font-normal">
                        {ord.created_at ? ord.created_at.slice(0, 16) : ''}
                      </div>
                    </td>

                    {/* Khách hàng & Địa chỉ */}
                    <td className="py-3 px-2 max-w-[200px]">
                      <span className="font-bold text-stone-800 block truncate">{ord.receiver_name || ord.recipient_name}</span>
                      <span className="text-[10px] text-stone-500 block">{ord.receiver_phone || ord.recipient_phone}</span>
                      <span className="text-[10px] text-stone-400 block truncate" title={ord.shipping_address}>
                        {ord.shipping_address}
                      </span>
                    </td>

                    {/* Phương thức đã đặt */}
                    <td className="py-3 px-2 font-medium">
                      {isDrone ? (
                        <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-emerald-50 text-emerald-800 border border-emerald-200 text-[11px] font-bold">
                          <Plane className="w-3.5 h-3.5 text-emerald-600" />
                          <span>Hanoi Drone</span>
                        </div>
                      ) : (
                        <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-stone-100 text-stone-800 border border-stone-200 text-[11px] font-bold">
                          <Truck className="w-3.5 h-3.5 text-stone-600" />
                          <span>GHN Standard</span>
                        </div>
                      )}

                      {ord.tracking_code && (
                        <span className="block text-[10px] font-mono text-crimson-700 mt-0.5">
                          Mã: {ord.tracking_code}
                        </span>
                      )}
                    </td>

                    {/* Trạng thái */}
                    <td className="py-3 px-2">
                      <span
                        className={`px-2.5 py-0.5 rounded-full text-[10px] font-bold ${
                          ord.status === 'PAID'
                            ? 'bg-emerald-100 text-emerald-800'
                            : ord.status === 'SHIPPING'
                            ? 'bg-blue-100 text-blue-800'
                            : ord.status === 'DELIVERED'
                            ? 'bg-purple-100 text-purple-800'
                            : ord.status === 'CANCELLED'
                            ? 'bg-red-100 text-red-800'
                            : 'bg-amber-100 text-amber-800'
                        }`}
                      >
                        {ord.status}
                      </span>
                    </td>

                    {/* Tổng tiền */}
                    <td className="py-3 px-2 font-bold text-crimson-700">
                      {formatVND(ord.final_amount || ord.final_total || ord.total_amount)}
                    </td>

                    {/* Cột Thao tác */}
                    <td className="py-3 px-2 text-right">
                      <div className="flex items-center justify-end gap-1.5">
                        {subTab === 'active' ? (
                          <>
                            {canDispatch && isDrone && (
                              flyingDrones[ord.order_id] !== undefined ? (
                                <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-emerald-950 border border-emerald-500/50 text-emerald-300 font-bold text-xs shadow-sm animate-pulse">
                                  <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping"></span>
                                  <span>🚁 Đang Bay ({flyingDrones[ord.order_id]}s)</span>
                                  <button
                                    onClick={() => setTrackingModalOrder(ord)}
                                    className="ml-1 p-1 rounded-lg bg-emerald-900 hover:bg-emerald-800 text-emerald-200"
                                    title="Mở Radar Không Lưu"
                                  >
                                    <Eye className="w-3 h-3" />
                                  </button>
                                </div>
                              ) : (
                                <button
                                  onClick={() => handleDispatch(ord.order_id, 'HANOI_DRONE')}
                                  className="px-3 py-1.5 rounded-xl bg-emerald-700 hover:bg-emerald-800 text-white font-bold text-xs flex items-center gap-1.5 transition shadow-sm"
                                  title="Bàn giao đơn hàng cho Hanoi Drone (BR05: giới hạn tải trọng 2000g)"
                                >
                                  <Plane className="w-3.5 h-3.5" />
                                  <span>Bàn Giao Drone</span>
                                </button>
                              )
                            )}

                            {canDispatch && !isDrone && (
                              <button
                                onClick={() => handleDispatch(ord.order_id, carrier.includes('EXPRESS') ? 'GHN_EXPRESS' : 'GHN_STANDARD')}
                                className="px-3 py-1.5 rounded-xl bg-stone-900 hover:bg-stone-800 text-white font-bold text-xs flex items-center gap-1.5 transition shadow-sm"
                                title="Bàn giao đơn hàng cho GHN"
                              >
                                <Truck className="w-3.5 h-3.5" />
                                <span>Bàn Giao GHN</span>
                              </button>
                            )}

                            {canDeliver && isDrone && (
                              flyingDrones[ord.order_id] !== undefined ? (
                                <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-emerald-950 border border-emerald-500/50 text-emerald-300 font-bold text-xs shadow-sm animate-pulse">
                                  <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping"></span>
                                  <span>🚁 Đang Bay</span>
                                  <button
                                    onClick={() => setTrackingModalOrder(ord)}
                                    className="ml-1 p-1 rounded-lg bg-emerald-900 hover:bg-emerald-800 text-emerald-200"
                                    title="Mở Radar Không Lưu"
                                  >
                                    <Eye className="w-3 h-3" />
                                  </button>
                                </div>
                              ) : (
                                <div className="flex items-center gap-1.5">
                                  <button
                                    onClick={() => setTrackingModalOrder(ord)}
                                    className="px-2.5 py-1.5 rounded-xl bg-emerald-950 hover:bg-emerald-900 text-emerald-300 border border-emerald-700 text-xs font-bold transition flex items-center gap-1"
                                    title="Mở Radar Không Lưu"
                                  >
                                    <Plane className="w-3.5 h-3.5" />
                                    <span>Radar Bay</span>
                                  </button>
                                  <button
                                    onClick={() => handleMarkDelivered(ord.order_id)}
                                    className="px-2.5 py-1.5 rounded-xl bg-purple-700 hover:bg-purple-800 text-white font-bold text-xs flex items-center gap-1 transition shadow-sm"
                                  >
                                    <Check className="w-3 h-3" />
                                    <span>Đã Giao</span>
                                  </button>
                                </div>
                              )
                            )}

                            {canDeliver && !isDrone && (
                              <div className="flex items-center gap-1.5">
                                <button
                                  onClick={() => setTrackingModalOrder(ord)}
                                  className="p-1.5 rounded-xl bg-stone-100 hover:bg-stone-200 text-stone-700 transition"
                                  title="Xem Lộ Trình GHN"
                                >
                                  <Eye className="w-3.5 h-3.5" />
                                </button>
                                <button
                                  onClick={() => handleMarkDelivered(ord.order_id)}
                                  className="px-3 py-1.5 rounded-xl bg-purple-700 hover:bg-purple-800 text-white font-bold text-xs flex items-center gap-1.5 transition shadow-sm"
                                  title="Xác nhận giao thành công"
                                >
                                  <Check className="w-3.5 h-3.5" />
                                  <span>Xác Nhận Đã Giao</span>
                                </button>
                              </div>
                            )}
                          </>
                        ) : (
                          // Tab Lịch sử: không hiển thị nút bấm thừa
                          <div className="flex items-center gap-2">
                            {ord.status === 'DELIVERED' ? (
                              <span className="inline-flex items-center gap-1 text-[11px] font-semibold text-emerald-700 bg-emerald-50 px-2.5 py-1 rounded-lg border border-emerald-200">
                                <Check className="w-3 h-3 text-emerald-600" />
                                <span>Đã Hoàn Tất</span>
                              </span>
                            ) : (
                              <span className="inline-flex items-center gap-1 text-[11px] font-semibold text-stone-500 bg-stone-100 px-2.5 py-1 rounded-lg border border-stone-200">
                                <span>Đã Hủy</span>
                              </span>
                            )}
                            <button
                              onClick={() => setTrackingModalOrder(ord)}
                              className="p-1 rounded-lg hover:bg-stone-200 text-stone-400 hover:text-stone-700 transition"
                              title="Xem lại lộ trình vận chuyển"
                            >
                              <Eye className="w-3.5 h-3.5" />
                            </button>
                          </div>
                        )}
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}

      {/* Tracking Modal (Radar cho Drone hoặc Timeline cho GHN) */}
      {trackingModalOrder && (
        <UnifiedOrderTrackingModal
          orderId={trackingModalOrder.order_id}
          initialOrder={trackingModalOrder}
          onClose={() => setTrackingModalOrder(null)}
          onDelivered={() => {
            fetchOrders();
          }}
        />
      )}
    </div>
  );
}
