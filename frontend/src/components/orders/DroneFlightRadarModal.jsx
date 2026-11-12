import React, { useState, useEffect, useRef } from 'react';
import L from 'leaflet';
import { X, Navigation, Play, CheckCircle2, Gauge, Clock, Package, MapPin, Building2, ShieldCheck, RefreshCw, Send } from 'lucide-react';
import { paymentApi, adminApi, formatVND } from '../../api';

// Coordinates (Hanoi City)
const ORIGIN_COORDS = [20.9806, 105.7874]; // PTIT Km10 Nguyễn Trãi, Hà Đông
const DEST_COORDS = [20.9982, 105.8028];   // Khách nhận (Khu vực Thanh Xuân - Nguyễn Trãi)
const FLIGHT_DURATION_SECONDS = 25;

const getStoredTakeoffTime = (orderObj, fallbackOrderId) => {
  const oid = orderObj?.order_id || fallbackOrderId;
  const key = `bookhaven_drone_takeoff_${oid}`;
  const stored = localStorage.getItem(key);
  if (stored) {
    const num = Number(stored);
    if (!isNaN(num) && num > 0) return num;
  }
  if (orderObj?.updated_at) {
    const parsed = new Date(orderObj.updated_at.replace(' ', 'T')).getTime();
    if (!isNaN(parsed) && parsed > 0) {
      localStorage.setItem(key, parsed.toString());
      return parsed;
    }
  }
  const now = Date.now();
  localStorage.setItem(key, now.toString());
  return now;
};

export default function DroneFlightRadarModal({ orderId, initialOrder, onClose, onDelivered }) {
  const [order, setOrder] = useState(initialOrder || null);
  const [isLoading, setIsLoading] = useState(!initialOrder);
  const [flightSeconds, setFlightSeconds] = useState(() => {
    if (initialOrder?.status === 'DELIVERED') return FLIGHT_DURATION_SECONDS;
    if (initialOrder?.status === 'SHIPPING') {
      const t = getStoredTakeoffTime(initialOrder, orderId);
      return Math.min(FLIGHT_DURATION_SECONDS, Math.max(0, (Date.now() - t) / 1000));
    }
    return 0;
  });
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [isDispatching, setIsDispatching] = useState(false);

  // Check if current session has Admin privileges
  const isAdmin = Boolean(localStorage.getItem('bookhaven_admin_token'));

  const mapContainerRef = useRef(null);
  const mapInstanceRef = useRef(null);
  const droneMarkerRef = useRef(null);
  const traveledLineRef = useRef(null);
  const timerRef = useRef(null);

  const isDelivered = order?.status === 'DELIVERED';
  const isShipping = order?.status === 'SHIPPING';
  const isWaitingDispatch = order?.status === 'PENDING_CASH' || order?.status === 'PAID' || order?.status === 'AWAITING_PAYMENT' || order?.status === 'PACKED';

  // Fetch / Refresh Order Status from backend
  const fetchOrderStatus = async () => {
    if (!orderId) return;
    try {
      const data = await paymentApi.getOrderStatus(orderId);
      setOrder(data);
      if (data.status === 'DELIVERED') {
        setFlightSeconds(FLIGHT_DURATION_SECONDS);
        onDelivered?.(orderId);
      }
    } catch (err) {
      console.error('Error fetching order status in Drone Radar:', err);
    } finally {
      setIsLoading(false);
      setIsRefreshing(false);
    }
  };

  // Initial load
  useEffect(() => {
    fetchOrderStatus();
  }, [orderId]);

  // Polling every 2.5s while waiting for Admin to dispatch, or while in flight
  useEffect(() => {
    if (isDelivered) return;

    const pollInterval = setInterval(() => {
      fetchOrderStatus();
    }, 2500);

    return () => clearInterval(pollInterval);
  }, [orderId, isDelivered]);

  // Bearing calculation (degrees) from Origin to Destination
  const dLat = DEST_COORDS[0] - ORIGIN_COORDS[0];
  const dLng = DEST_COORDS[1] - ORIGIN_COORDS[1];
  const bearingAngle = Math.round((Math.atan2(dLng, dLat) * 180) / Math.PI);

  // 1. Initialize Leaflet Map
  useEffect(() => {
    if (!mapContainerRef.current) return;

    // Create Map
    const map = L.map(mapContainerRef.current, {
      center: [(ORIGIN_COORDS[0] + DEST_COORDS[0]) / 2, (ORIGIN_COORDS[1] + DEST_COORDS[1]) / 2],
      zoom: 14,
      zoomControl: false,
      attributionControl: false,
    });
    mapInstanceRef.current = map;

    // OpenStreetMap Standard Tiles (100% Free, No Watermark, No API Key)
    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 19,
    }).addTo(map);

    // Zoom control at bottom-right
    L.control.zoom({ position: 'bottomright' }).addTo(map);

    // Origin Marker (Kho BookHaven - PTIT)
    const originIcon = L.divIcon({
      className: 'custom-map-pin',
      html: `
        <div class="relative flex items-center justify-center -translate-x-1/2 -translate-y-1/2 cursor-pointer group">
          <div class="w-9 h-9 rounded-2xl bg-emerald-700 border-2 border-white shadow-xl flex items-center justify-center text-white text-base font-bold transition-transform group-hover:scale-110">
            🏢
          </div>
          <div class="absolute -bottom-6 whitespace-nowrap bg-stone-900/90 text-emerald-300 border border-emerald-500/40 px-2 py-0.5 rounded-full text-[10px] font-bold shadow-md">
            Kho PTIT (Hà Đông)
          </div>
        </div>
      `,
      iconSize: [36, 36],
      iconAnchor: [18, 18],
    });
    L.marker(ORIGIN_COORDS, { icon: originIcon }).addTo(map);

    // Destination Marker (Khách nhận)
    const destIcon = L.divIcon({
      className: 'custom-map-pin',
      html: `
        <div class="relative flex items-center justify-center -translate-x-1/2 -translate-y-1/2 cursor-pointer group">
          <div class="w-9 h-9 rounded-2xl bg-crimson-700 border-2 border-white shadow-xl flex items-center justify-center text-white text-base font-bold transition-transform group-hover:scale-110">
            📍
          </div>
          <div class="absolute -bottom-6 whitespace-nowrap bg-stone-900/90 text-rose-300 border border-rose-500/40 px-2 py-0.5 rounded-full text-[10px] font-bold shadow-md">
            ${order?.shipping_address?.full_name || order?.receiver_name || 'Điểm Nhận Hàng'}
          </div>
        </div>
      `,
      iconSize: [36, 36],
      iconAnchor: [18, 18],
    });
    L.marker(DEST_COORDS, { icon: destIcon }).addTo(map);

    // Planned Flight Path (Direct dashed line)
    L.polyline([ORIGIN_COORDS, DEST_COORDS], {
      color: '#059669',
      weight: 3,
      dashArray: '6, 8',
      opacity: 0.5,
    }).addTo(map);

    // Traveled Flight Path (Active glowing green)
    let initialT = 0;
    if (order?.status === 'DELIVERED') {
      initialT = 1.0;
    } else if (order?.status === 'SHIPPING') {
      const t = getStoredTakeoffTime(order, orderId);
      const elapsed = (Date.now() - t) / 1000;
      initialT = Math.min(1.0, Math.max(0, elapsed / FLIGHT_DURATION_SECONDS));
    }
    const initialPos = [
      ORIGIN_COORDS[0] + dLat * initialT,
      ORIGIN_COORDS[1] + dLng * initialT,
    ];
    traveledLineRef.current = L.polyline([ORIGIN_COORDS, initialPos], {
      color: '#10b981',
      weight: 4,
      opacity: 0.95,
    }).addTo(map);

    // Top-down Drone Marker (Quadcopter SVG viewed from straight above)
    const isStationary = order?.status !== 'SHIPPING';
    const droneIcon = L.divIcon({
      className: 'custom-drone-icon',
      html: `
        <div id="drone-animated-wrapper" class="relative w-14 h-14 flex items-center justify-center -translate-x-1/2 -translate-y-1/2 pointer-events-none">
          <!-- Sonar Radar Ping Wave -->
          <div class="absolute w-14 h-14 rounded-full border-2 border-emerald-400/80 drone-sonar-ping"></div>

          <!-- Rotating Quadcopter Body Oriented to Heading -->
          <div class="relative w-12 h-12 flex items-center justify-center" style="transform: rotate(${bearingAngle}deg); transition: transform 0.2s ease-out;">
            <svg viewBox="0 0 100 100" class="w-full h-full drop-shadow-2xl">
              <!-- Drone Shadow -->
              <ellipse cx="50" cy="50" rx="38" ry="38" fill="rgba(0,0,0,0.25)" />

              <!-- 4 Carbon Fiber Diagonal Arms -->
              <line x1="22" y1="22" x2="78" y2="78" stroke="#1c1917" stroke-width="6" stroke-linecap="round" />
              <line x1="22" y1="78" x2="78" y2="22" stroke="#1c1917" stroke-width="6" stroke-linecap="round" />
              <line x1="22" y1="22" x2="78" y2="78" stroke="#38bdf8" stroke-width="1.5" stroke-linecap="round" opacity="0.6" />
              <line x1="22" y1="78" x2="78" y2="22" stroke="#38bdf8" stroke-width="1.5" stroke-linecap="round" opacity="0.6" />

              <!-- 4 Motors -->
              <circle cx="22" cy="22" r="7" fill="#0f172a" stroke="#0ea5e9" stroke-width="1.5" />
              <circle cx="78" cy="22" r="7" fill="#0f172a" stroke="#0ea5e9" stroke-width="1.5" />
              <circle cx="22" cy="78" r="7" fill="#0f172a" stroke="#0ea5e9" stroke-width="1.5" />
              <circle cx="78" cy="78" r="7" fill="#0f172a" stroke="#0ea5e9" stroke-width="1.5" />

              <!-- 4 Spinning Rotor Discs (High-Speed Blur Animation when active) -->
              <g class="${isStationary ? '' : 'drone-rotor-spin'}" style="transform-origin: 22px 22px;">
                <circle cx="22" cy="22" r="15" fill="rgba(16, 185, 129, 0.22)" stroke="#10b981" stroke-width="1" stroke-dasharray="8 6" />
                <line x1="10" y1="22" x2="34" y2="22" stroke="#ffffff" stroke-width="2" stroke-linecap="round" />
              </g>
              <g class="${isStationary ? '' : 'drone-rotor-spin'}" style="transform-origin: 78px 22px;">
                <circle cx="78" cy="22" r="15" fill="rgba(16, 185, 129, 0.22)" stroke="#10b981" stroke-width="1" stroke-dasharray="8 6" />
                <line x1="66" y1="22" x2="90" y2="22" stroke="#ffffff" stroke-width="2" stroke-linecap="round" />
              </g>
              <g class="${isStationary ? '' : 'drone-rotor-spin'}" style="transform-origin: 22px 78px;">
                <circle cx="22" cy="78" r="15" fill="rgba(16, 185, 129, 0.22)" stroke="#10b981" stroke-width="1" stroke-dasharray="8 6" />
                <line x1="10" y1="78" x2="34" y2="78" stroke="#ffffff" stroke-width="2" stroke-linecap="round" />
              </g>
              <g class="${isStationary ? '' : 'drone-rotor-spin'}" style="transform-origin: 78px 78px;">
                <circle cx="78" cy="78" r="15" fill="rgba(16, 185, 129, 0.22)" stroke="#10b981" stroke-width="1" stroke-dasharray="8 6" />
                <line x1="66" y1="78" x2="90" y2="78" stroke="#ffffff" stroke-width="2" stroke-linecap="round" />
              </g>

              <!-- Central Aerodynamic Fuselage -->
              <rect x="36" y="32" width="28" height="36" rx="8" fill="#0f172a" stroke="#10b981" stroke-width="2" />
              <circle cx="50" cy="42" r="5" fill="#10b981" />
              <rect x="42" y="52" width="16" height="10" rx="2" fill="#1e293b" stroke="#64748b" stroke-width="0.8" />
              <text x="50" y="59" fill="#38bdf8" font-size="6" font-family="monospace" font-weight="bold" text-anchor="middle">PTIT</text>

              <!-- Front Directional Arrow Indicator -->
              <polygon points="50,26 44,32 56,32" fill="#ef4444" />

              <!-- Aviation Nav Lights (Front Green, Rear Red) -->
              <circle cx="22" cy="18" r="2" fill="#22c55e" />
              <circle cx="78" cy="18" r="2" fill="#22c55e" />
              <circle cx="22" cy="82" r="2" fill="#ef4444" />
              <circle cx="78" cy="82" r="2" fill="#ef4444" />
            </svg>
          </div>
        </div>
      `,
      iconSize: [56, 56],
      iconAnchor: [28, 28],
    });

    droneMarkerRef.current = L.marker(initialPos, { icon: droneIcon, zIndexOffset: 1000 }).addTo(map);

    // Auto fit bounds
    map.fitBounds([ORIGIN_COORDS, DEST_COORDS], {
      padding: [70, 70],
      maxZoom: 15,
    });

    return () => {
      map.remove();
      mapInstanceRef.current = null;
    };
  }, []);

  // 2. Persistent Real-Time Flight Tracking (Based on real wall-clock elapsed time)
  useEffect(() => {
    if (order?.status === 'DELIVERED') {
      setFlightSeconds(FLIGHT_DURATION_SECONDS);
      if (droneMarkerRef.current) {
        droneMarkerRef.current.setLatLng(DEST_COORDS);
      }
      if (traveledLineRef.current) {
        traveledLineRef.current.setLatLngs([ORIGIN_COORDS, DEST_COORDS]);
      }
      return;
    }

    // Only fly if Admin dispatched the order to SHIPPING
    if (order?.status === 'SHIPPING') {
      const takeoffTime = getStoredTakeoffTime(order, orderId);

      const updateFlightProgress = () => {
        const elapsed = (Date.now() - takeoffTime) / 1000;

        if (elapsed >= FLIGHT_DURATION_SECONDS) {
          clearInterval(timerRef.current);
          setFlightSeconds(FLIGHT_DURATION_SECONDS);

          if (droneMarkerRef.current) {
            droneMarkerRef.current.setLatLng(DEST_COORDS);
          }
          if (traveledLineRef.current) {
            traveledLineRef.current.setLatLngs([ORIGIN_COORDS, DEST_COORDS]);
          }

          // Auto-mark delivery if not already marked
          paymentApi
            .markDelivered(order?.order_id || orderId)
            .then(() => {
              fetchOrderStatus();
              onDelivered?.(order?.order_id || orderId);
            })
            .catch(console.error);
        } else {
          setFlightSeconds(elapsed);
          const t = elapsed / FLIGHT_DURATION_SECONDS;
          const currentPos = [
            ORIGIN_COORDS[0] + dLat * t,
            ORIGIN_COORDS[1] + dLng * t,
          ];
          if (droneMarkerRef.current) {
            droneMarkerRef.current.setLatLng(currentPos);
          }
          if (traveledLineRef.current) {
            traveledLineRef.current.setLatLngs([ORIGIN_COORDS, currentPos]);
          }
        }
      };

      // Run immediately on mount to reflect current real-time coordinates
      updateFlightProgress();
      timerRef.current = setInterval(updateFlightProgress, 80);

      return () => clearInterval(timerRef.current);
    } else {
      // If still waiting for dispatch, keep drone parked at origin
      setFlightSeconds(0);
      if (droneMarkerRef.current) {
        droneMarkerRef.current.setLatLng(ORIGIN_COORDS);
      }
      if (traveledLineRef.current) {
        traveledLineRef.current.setLatLngs([ORIGIN_COORDS, ORIGIN_COORDS]);
      }
    }
  }, [order?.status, order?.updated_at, orderId, dLat, dLng]);

  // Admin Dispatch Trigger Handler (Available ONLY for Admin role)
  const handleAdminDispatch = async () => {
    setIsDispatching(true);
    try {
      localStorage.setItem(`bookhaven_drone_takeoff_${order?.order_id || orderId}`, Date.now().toString());
      await adminApi.dispatchOrder(order?.order_id || orderId, 'HANOI_DRONE');
      await fetchOrderStatus();
    } catch (err) {
      console.error('Error dispatching drone:', err);
    } finally {
      setIsDispatching(false);
    }
  };

  // Manual Refresh for customer
  const handleManualRefresh = () => {
    setIsRefreshing(true);
    fetchOrderStatus();
  };

  // Derived 3 Main Telemetry Indicators
  // 1. Tốc độ bay (km/h)
  let speedKmh = '0.0';
  if (isShipping && flightSeconds > 0 && flightSeconds < FLIGHT_DURATION_SECONDS) {
    if (flightSeconds < 2) {
      speedKmh = '24.5';
    } else if (flightSeconds > FLIGHT_DURATION_SECONDS - 2) {
      speedKmh = '16.0';
    } else {
      speedKmh = (48.0 + Math.sin(flightSeconds * 1.5) * 2.5).toFixed(1);
    }
  }

  // 2. Thời gian đếm lùi đến đích (ETA)
  let etaText = '--:--';
  if (isDelivered || flightSeconds >= FLIGHT_DURATION_SECONDS) {
    etaText = '00:00 (Đã đến)';
  } else if (isShipping) {
    const remainingSeconds = Math.max(0, Math.ceil(FLIGHT_DURATION_SECONDS - flightSeconds));
    etaText = `00:${remainingSeconds < 10 ? '0' : ''}${remainingSeconds}`;
  } else {
    etaText = 'Chờ điều phối';
  }

  // 3. Khối lượng kiện hàng
  const parcelWeight = order?.total_weight_grams || 430;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-5 bg-stone-950/80 backdrop-blur-md animate-fadeIn">
      <div className="relative w-full max-w-3xl bg-stone-900 border border-stone-800 rounded-3xl shadow-2xl overflow-hidden flex flex-col text-white max-h-[92vh]">

        {/* 1. Header Bar */}
        <div className="px-5 py-3.5 bg-stone-950/90 border-b border-stone-800 flex items-center justify-between z-20 shrink-0">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-2xl bg-emerald-950/80 border border-emerald-500/40 text-emerald-400 flex items-center justify-center text-xl shadow-inner">
              🚁
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="font-serif-title font-bold text-base text-white tracking-wide">
                  Hanoi Drone Express
                </h3>
                <span className={`px-2 py-0.5 rounded-full text-[10px] font-mono font-bold border flex items-center gap-1 ${
                  isShipping
                    ? 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30'
                    : isDelivered
                    ? 'bg-purple-500/20 text-purple-400 border-purple-500/30'
                    : 'bg-amber-500/20 text-amber-400 border-amber-500/30'
                }`}>
                  <span className={`w-1.5 h-1.5 rounded-full ${isShipping ? 'bg-emerald-400 animate-ping' : isDelivered ? 'bg-purple-400' : 'bg-amber-400'}`}></span>
                  {isShipping ? 'ĐANG BAY TRỰC TIẾP' : isDelivered ? 'ĐÃ HOÀN TẤT' : 'CHỜ XUẤT KHO'}
                </span>
                {order?.payment_method === 'COD' && (
                  <span className="px-2 py-0.5 rounded-full bg-amber-500/20 text-amber-400 text-[10px] font-mono font-bold border border-amber-500/30">
                    COD
                  </span>
                )}
              </div>
              <p className="text-[11px] text-stone-400 font-mono">
                Mã vận đơn: <strong className="text-emerald-400">{order?.tracking_code || 'Chờ Admin cấp mã...'}</strong>
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={handleManualRefresh}
              className={`p-2 rounded-full text-stone-400 hover:text-white hover:bg-stone-800 transition ${isRefreshing ? 'animate-spin text-emerald-400' : ''}`}
              title="Làm mới trạng thái không lưu"
            >
              <RefreshCw className="w-4 h-4" />
            </button>
            <button
              onClick={onClose}
              className="p-2 rounded-full text-stone-400 hover:text-white hover:bg-stone-800 transition"
              title="Đóng modal"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* 2. Interactive Map Container (Full Leaflet Canvas) */}
        <div className="relative w-full h-[460px] sm:h-[500px] bg-stone-950 overflow-hidden select-none">
          {/* Leaflet DOM Mounting Node */}
          <div ref={mapContainerRef} className="w-full h-full" />

          {/* Floating Telemetry HUD Card (Top-Left overlay on map) */}
          <div className="absolute top-4 left-4 z-[400] flex flex-wrap gap-2 pointer-events-none">
            {/* Speed Badge */}
            <div className="bg-stone-900/90 backdrop-blur-md border border-stone-700/60 rounded-2xl px-3 py-2 shadow-xl flex items-center gap-2.5">
              <div className="w-7 h-7 rounded-xl bg-cyan-950/80 border border-cyan-500/30 text-cyan-400 flex items-center justify-center">
                <Gauge className="w-4 h-4" />
              </div>
              <div>
                <p className="text-[9px] uppercase font-bold text-stone-400 tracking-wider">Tốc Độ Bay</p>
                <p className="text-xs font-mono font-bold text-cyan-300">
                  {speedKmh} <span className="text-[9px] text-stone-400">km/h</span>
                </p>
              </div>
            </div>

            {/* ETA Countdown Badge */}
            <div className="bg-stone-900/90 backdrop-blur-md border border-stone-700/60 rounded-2xl px-3 py-2 shadow-xl flex items-center gap-2.5">
              <div className="w-7 h-7 rounded-xl bg-emerald-950/80 border border-emerald-500/30 text-emerald-400 flex items-center justify-center">
                <Clock className="w-4 h-4" />
              </div>
              <div>
                <p className="text-[9px] uppercase font-bold text-stone-400 tracking-wider">Thời Gian Đến</p>
                <p className="text-xs font-mono font-bold text-emerald-400">
                  {etaText}
                </p>
              </div>
            </div>

            {/* Package Weight Badge */}
            <div className="bg-stone-900/90 backdrop-blur-md border border-stone-700/60 rounded-2xl px-3 py-2 shadow-xl flex items-center gap-2.5">
              <div className="w-7 h-7 rounded-xl bg-amber-950/80 border border-amber-500/30 text-amber-400 flex items-center justify-center">
                <Package className="w-4 h-4" />
              </div>
              <div>
                <p className="text-[9px] uppercase font-bold text-stone-400 tracking-wider">Khối Lượng</p>
                <p className="text-xs font-mono font-bold text-amber-300">
                  {parcelWeight}g <span className="text-[9px] text-emerald-400">(≤ 2kg)</span>
                </p>
              </div>
            </div>
          </div>

          {/* Floating Bottom Control Card (Bottom overlay on map) */}
          <div className="absolute bottom-4 left-4 right-4 z-[400]">
            <div className="bg-stone-950/92 backdrop-blur-lg border border-stone-800/80 rounded-2xl p-4 shadow-2xl flex flex-col sm:flex-row items-center justify-between gap-3">
              <div className="w-full sm:w-auto flex-1">
                <div className="flex items-center gap-2 mb-1">
                  <span className={`w-2 h-2 rounded-full ${
                    isDelivered ? 'bg-emerald-400' : isShipping ? 'bg-emerald-400 animate-ping' : 'bg-amber-400 animate-pulse'
                  }`}></span>
                  <p className="text-xs font-bold text-white tracking-wide">
                    {isDelivered
                      ? 'Đã hạ cánh an toàn & bàn giao tận tay độc giả!'
                      : isShipping
                      ? 'Hành trình bay thẳng trên không nội đô Hà Nội (Tầm cao 120m)'
                      : '⏳ Đang chờ Thủ kho PTIT duyệt xuất kho & điều phối cất cánh'}
                  </p>
                </div>
                <div className="flex flex-wrap items-center gap-x-3 gap-y-1 text-[11px] text-stone-400">
                  <span>📍 Kho PTIT Hà Đông ➔ Nhà bạn</span>
                  {order?.payment_method === 'COD' && (
                    <span className="font-semibold text-amber-400">
                      💵 Thu tiền mặt COD: {formatVND(order?.final_amount || order?.total_amount || 170000)}
                    </span>
                  )}
                  {isWaitingDispatch && (
                    <span className="text-stone-400 italic">
                      (Tự động cất cánh khi Admin phê duyệt)
                    </span>
                  )}
                </div>
              </div>

              {/* Action Area: Strict Role & State Separation */}
              <div className="w-full sm:w-auto shrink-0">
                {isDelivered ? (
                  <div className="w-full sm:w-auto px-5 py-2.5 rounded-xl bg-emerald-600/20 border border-emerald-500/40 text-emerald-400 font-bold text-xs flex items-center justify-center gap-2">
                    <CheckCircle2 className="w-4 h-4" />
                    ĐƠN HÀNG ĐÃ GIAO THÀNH CÔNG!
                  </div>
                ) : isShipping ? (
                  <div className="w-full sm:w-auto px-5 py-2.5 rounded-xl bg-amber-500/20 border border-amber-500/40 text-amber-300 font-bold text-xs flex items-center justify-center gap-2">
                    <RefreshCw className="w-4 h-4 animate-spin" />
                    Đang Bay Hành Trình...
                  </div>
                ) : isAdmin ? (
                  /* Admin Role: Can trigger dispatch directly from radar modal */
                  <button
                    onClick={handleAdminDispatch}
                    disabled={isDispatching}
                    className="w-full sm:w-auto px-5 py-2.5 rounded-xl bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white font-bold text-xs shadow-lg shadow-emerald-900/30 hover:scale-[1.02] active:scale-[0.98] transition flex items-center justify-center gap-2 disabled:opacity-50"
                  >
                    <Send className="w-4 h-4" />
                    {isDispatching ? 'Đang xuất kho...' : 'Admin Duyệt & Cất Cánh Ngay'}
                  </button>
                ) : (
                  /* Customer Role: Strictly waiting for Admin approval - NO takeoff button */
                  <div className="flex items-center gap-2 px-3 py-2 rounded-xl bg-stone-900/90 border border-stone-800 text-stone-300 text-xs">
                    <span className="w-2 h-2 rounded-full bg-cyan-400 animate-ping"></span>
                    <span>Chờ Quản Trị Viên Duyệt...</span>
                    <button
                      onClick={handleManualRefresh}
                      className="ml-1 px-2 py-1 rounded-lg bg-stone-800 hover:bg-stone-700 text-stone-200 text-[10px] font-bold flex items-center gap-1 transition"
                      title="Kiểm tra trạng thái từ kho"
                    >
                      <RefreshCw className={`w-3 h-3 ${isRefreshing ? 'animate-spin' : ''}`} />
                      Làm mới
                    </button>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>

      </div>
    </div>
  );
}
