import React, { useState, useEffect, useRef } from 'react';
import confetti from 'canvas-confetti';
import { Clock, ShieldCheck, CheckCircle2, ArrowRight, Copy, Check } from 'lucide-react';
import { paymentApi, formatVND } from '../../api';
import { useToast } from '../../context/ToastContext';

export default function PaymentView({ orderId, onNavigate }) {
  const { showToast } = useToast();
  const [order, setOrder] = useState(null);
  const [timeLeft, setTimeLeft] = useState(15 * 60); // 15 mins
  const [isConfirming, setIsConfirming] = useState(false);
  const [copiedField, setCopiedField] = useState(null);
  const hasTriggeredSuccess = useRef(false);

  // Load Order Status
  useEffect(() => {
    if (!orderId) return;

    paymentApi
      .getOrderStatus(orderId)
      .then((data) => {
        setOrder(data);
      })
      .catch((err) => {
        showToast('Lỗi nạp đơn hàng: ' + err.message, 'error');
      });
  }, [orderId, showToast]);

  // 15-minute Countdown (BR03)
  useEffect(() => {
    const timer = setInterval(() => {
      setTimeLeft((prev) => {
        if (prev <= 1) {
          clearInterval(timer);
          showToast('Đã hết hạn giữ chỗ tồn kho (15 phút)! Đơn hàng đã tự động hủy.', 'error');
          onNavigate('catalog');
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(timer);
  }, [onNavigate, showToast]);

  // Polling check every 3s
  useEffect(() => {
    if (!orderId) return;

    const pollTimer = setInterval(async () => {
      try {
        const res = await paymentApi.getOrderStatus(orderId);
        if (res.status === 'PAID' && !hasTriggeredSuccess.current) {
          hasTriggeredSuccess.current = true;
          clearInterval(pollTimer);
          triggerSuccessAnimation();
        }
      } catch (e) {
        // quiet fail on polling error
      }
    }, 3000);

    return () => clearInterval(pollTimer);
  }, [orderId]);

  const triggerSuccessAnimation = () => {
    if (hasTriggeredSuccess.current) return;
    hasTriggeredSuccess.current = true;

    confetti({
      particleCount: 120,
      spread: 70,
      origin: { y: 0.6 },
    });
    showToast('Xác nhận thanh toán MBBank thành công!', 'success');
    setTimeout(() => {
      onNavigate('order-success', { orderId });
    }, 1800);
  };

  const handleConfirmPaid = async () => {
    if (isConfirming || hasTriggeredSuccess.current) return;
    setIsConfirming(true);
    try {
      const txnCode = 'MB_' + Date.now().toString().slice(-6);
      await paymentApi.confirmPayment(orderId, txnCode);
      triggerSuccessAnimation();
    } catch (err) {
      showToast(err.message, 'error');
    } finally {
      setIsConfirming(false);
    }
  };

  const copyToClipboard = (text, fieldName) => {
    navigator.clipboard.writeText(text);
    setCopiedField(fieldName);
    showToast(`Đã sao chép: ${text}`, 'info');
    setTimeout(() => setCopiedField(null), 2000);
  };

  const formatCountdown = (secs) => {
    const m = Math.floor(secs / 60).toString().padStart(2, '0');
    const s = (secs % 60).toString().padStart(2, '0');
    return `${m}:${s}`;
  };

  if (!order) {
    return (
      <div className="py-24 text-center">
        <div className="w-10 h-10 border-4 border-crimson-700 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
        <p className="text-xs font-semibold text-stone-500">Đang khởi tạo mã VietQR MBBank...</p>
      </div>
    );
  }

  const finalAmount = order.final_amount ?? order.final_total ?? order.total_amount ?? 0;
  const qrUrl = `https://img.vietqr.io/image/970422-0912345678-compact2.png?amount=${finalAmount}&addInfo=BOOKHAVEN%20${orderId}&accountName=NHA%20SACH%20BOOKHAVEN`;

  return (
    <div className="max-w-4xl mx-auto px-4 py-8 animate-fadeIn">
      {/* Title & 15-min Countdown */}
      <div className="text-center mb-8 space-y-3">
        <span className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-crimson-50 text-crimson-700 text-xs font-bold border border-crimson-200">
          <Clock className="w-4 h-4 animate-spin text-crimson-700" />
          <span>Thời gian giữ chỗ tồn kho (BR03): {formatCountdown(timeLeft)}</span>
        </span>
        <h1 className="font-serif-title font-bold text-2xl md:text-3xl text-stone-900">
          Thanh Toán VietQR Ngân Hàng Quân Đội (MBBank)
        </h1>
        <p className="text-xs text-stone-500 max-w-lg mx-auto">
          Mở ứng dụng Ngân hàng (MB, Vietcombank, Techcombank, Momo...) và quét mã QR bên dưới. Hệ thống sẽ tự động cập nhật ngay khi nhận được tín hiệu.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-12 gap-8 items-start bg-white rounded-3xl border border-stone-200 p-6 md:p-10 shadow-sm">
        {/* QR Code Column */}
        <div className="md:col-span-5 flex flex-col items-center">
          <div className="p-3 bg-white rounded-2xl border-2 border-stone-200 shadow-md">
            <img
              src={qrUrl}
              alt="Mã VietQR Thanh Toán"
              className="w-64 h-auto object-contain rounded-xl"
            />
          </div>
          <div className="mt-3 text-center">
            <span className="text-[11px] font-bold text-stone-600 block">
              Quét mã bằng bất kỳ App Ngân hàng nào
            </span>
            <span className="text-[10px] text-stone-400">Tự động điền số tiền và nội dung</span>
          </div>
        </div>

        {/* Bank Details Column */}
        <div className="md:col-span-7 space-y-5">
          <div className="space-y-3 text-xs">
            <div className="flex items-center justify-between p-3 rounded-xl bg-stone-50 border border-stone-200">
              <span className="text-stone-500">Ngân hàng thụ hưởng:</span>
              <span className="font-bold text-stone-900">MBBank (Ngân hàng Quân Đội)</span>
            </div>

            <div className="flex items-center justify-between p-3 rounded-xl bg-stone-50 border border-stone-200">
              <span className="text-stone-500">Chủ tài khoản:</span>
              <span className="font-bold text-stone-900">NHA SACH BOOKHAVEN</span>
            </div>

            <div className="flex items-center justify-between p-3 rounded-xl bg-stone-50 border border-stone-200">
              <span className="text-stone-500">Số tài khoản:</span>
              <div className="flex items-center gap-2">
                <span className="font-mono font-bold text-sm text-stone-900">0912345678</span>
                <button
                  onClick={() => copyToClipboard('0912345678', 'account')}
                  className="p-1 hover:text-crimson-700 transition"
                  title="Sao chép số tài khoản"
                >
                  {copiedField === 'account' ? (
                    <Check className="w-3.5 h-3.5 text-emerald-600" />
                  ) : (
                    <Copy className="w-3.5 h-3.5" />
                  )}
                </button>
              </div>
            </div>

            <div className="flex items-center justify-between p-3 rounded-xl bg-stone-50 border border-stone-200">
              <span className="text-stone-500">Số tiền cần chuyển:</span>
              <div className="flex items-center gap-2">
                <span className="font-bold text-base text-crimson-700">
                  {formatVND(finalAmount)}
                </span>
                <button
                  onClick={() => copyToClipboard(String(finalAmount), 'amount')}
                  className="p-1 hover:text-crimson-700 transition"
                  title="Sao chép số tiền"
                >
                  {copiedField === 'amount' ? (
                    <Check className="w-3.5 h-3.5 text-emerald-600" />
                  ) : (
                    <Copy className="w-3.5 h-3.5" />
                  )}
                </button>
              </div>
            </div>

            <div className="flex items-center justify-between p-3 rounded-xl bg-amber-50/60 border border-amber-200">
              <span className="text-amber-800 font-medium">Cú pháp chuyển khoản:</span>
              <div className="flex items-center gap-2">
                <span className="font-mono font-bold text-xs text-amber-900">
                  BOOKHAVEN {orderId}
                </span>
                <button
                  onClick={() => copyToClipboard(`BOOKHAVEN ${orderId}`, 'content')}
                  className="p-1 hover:text-crimson-700 transition"
                  title="Sao chép nội dung"
                >
                  {copiedField === 'content' ? (
                    <Check className="w-3.5 h-3.5 text-emerald-600" />
                  ) : (
                    <Copy className="w-3.5 h-3.5" />
                  )}
                </button>
              </div>
            </div>
          </div>

          {/* Real Confirmation Button */}
          <div className="pt-3 border-t border-stone-200 space-y-3">
            <button
              onClick={handleConfirmPaid}
              disabled={isConfirming}
              className="w-full flex items-center justify-center px-6 py-3.5 rounded-full bg-crimson-700 hover:bg-crimson-800 text-white text-xs font-bold transition shadow-lg hover:shadow-crimson-900/20 disabled:opacity-50 cursor-pointer"
            >
              <span>
                {isConfirming ? 'Đang xác nhận giao dịch...' : 'Xác nhận chuyển khoản'}
              </span>
            </button>

            <p className="text-[11px] text-stone-400 text-center">
              Hệ thống đang tự động lắng nghe Webhook ngân hàng mỗi 3 giây.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
