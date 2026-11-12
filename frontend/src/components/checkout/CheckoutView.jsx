import React, { useState, useEffect } from 'react';
import { useCart } from '../../context/CartContext';
import { useAuth } from '../../context/AuthContext';
import { useToast } from '../../context/ToastContext';
import { checkoutApi } from '../../api';
import AddressSelector from './AddressSelector';
import ShippingSelector from './ShippingSelector';
import VoucherBox from './VoucherBox';
import PaymentMethodSelector from './PaymentMethodSelector';
import OrderSummaryCard from './OrderSummaryCard';

export default function CheckoutView({ onNavigate }) {
  const { cart, refreshCart } = useCart();
  const { user, openAuthModal } = useAuth();
  const { showToast } = useToast();

  const [selectedAddressId, setSelectedAddressId] = useState('');
  const [selectedAddressObj, setSelectedAddressObj] = useState(null);
  const [shippingOptions, setShippingOptions] = useState([]);
  const [selectedCarrier, setSelectedCarrier] = useState('GHN_STANDARD');
  const [paymentMethod, setPaymentMethod] = useState('VIETQR');
  const [appliedVoucher, setAppliedVoucher] = useState(null);
  const [discountAmount, setDiscountAmount] = useState(0);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const packageWeight = (cart.total_weight_grams || 0) + 150;

  useEffect(() => {
    checkoutApi
      .getShippingOptions(cart.cart_id)
      .then((data) => {
        const opts = data.options || [];
        setShippingOptions(opts);
        if (opts.length > 0) {
          // If drone is not allowed and selected is drone, fallback to GHN
          if (packageWeight > 2000 && selectedCarrier === 'HANOI_DRONE') {
            setSelectedCarrier('GHN_STANDARD');
          }
        }
      })
      .catch((err) => {
        console.error('Error fetching shipping options:', err);
      });
  }, [cart.cart_id, packageWeight, selectedCarrier]);

  // Nếu chọn Drone, tự động chuyển phương thức thanh toán sang VIETQR nếu đang là COD
  useEffect(() => {
    if (selectedCarrier === 'HANOI_DRONE' && paymentMethod === 'COD') {
      setPaymentMethod('VIETQR');
      showToast('Giao hàng Drone chỉ hỗ trợ thanh toán trực tuyến qua VietQR', 'info');
    }
  }, [selectedCarrier, paymentMethod, showToast]);

  const selectedShippingOption = shippingOptions.find(
    (o) => o.carrier_code === selectedCarrier
  );
  const shippingFee = selectedShippingOption ? selectedShippingOption.fee : 25000;

  const handleApplyVoucher = (code, discount) => {
    setAppliedVoucher(code);
    setDiscountAmount(discount);
  };

  const handleSubmitCheckout = async () => {
    if (!user) {
      showToast('Vui lòng đăng nhập để tiến hành đặt hàng!', 'error');
      openAuthModal();
      return;
    }

    if (!cart.items || cart.items.length === 0) {
      showToast('Giỏ hàng của bạn đang trống!', 'error');
      return;
    }

    const finalAddress = selectedAddressObj?.address || user.shipping_address;
    if (!finalAddress) {
      showToast('Vui lòng chọn hoặc thêm địa chỉ nhận hàng!', 'error');
      return;
    }

    setIsSubmitting(true);
    try {
      const payload = {
        cart_id: cart.cart_id,
        carrier: selectedCarrier,
        shipping_carrier: selectedCarrier,
        payment_method: paymentMethod,
        receiver_name: selectedAddressObj?.name || user.full_name || 'Khách hàng',
        recipient_name: selectedAddressObj?.name || user.full_name || 'Khách hàng',
        receiver_phone: selectedAddressObj?.phone || user.phone || '',
        recipient_phone: selectedAddressObj?.phone || user.phone || '',
        shipping_address: finalAddress,
        voucher_code: appliedVoucher,
      };

      const result = await checkoutApi.checkout(payload);
      showToast('Đặt hàng thành công! Đang chuyển hướng...', 'success');
      await refreshCart();

      if (paymentMethod === 'VIETQR') {
        onNavigate('payment', { orderId: result.order_id });
      } else {
        onNavigate('order-success', { orderId: result.order_id });
      }
    } catch (err) {
      showToast(err.message, 'error');
    } finally {
      setIsSubmitting(false);
    }
  };

  if (!user) {
    return (
      <div className="max-w-xl mx-auto py-16 px-4 text-center animate-fadeIn">
        <div className="bg-white rounded-3xl border border-stone-200 p-8 shadow-sm space-y-4">
          <div className="w-16 h-16 rounded-full bg-crimson-50 text-crimson-700 flex items-center justify-center mx-auto text-2xl font-bold">
            🔒
          </div>
          <h2 className="font-serif-title font-bold text-2xl text-stone-900">
            Yêu Cầu Đăng Nhập
          </h2>
          <p className="text-xs sm:text-sm text-stone-600 max-w-md mx-auto">
            Bạn chưa đăng nhập tài khoản. Vui lòng đăng nhập để tiến hành quản lý địa chỉ nhận hàng, áp dụng voucher và đặt hàng an toàn!
          </p>
          <div className="pt-2 flex justify-center gap-3">
            <button
              onClick={() => onNavigate('catalog')}
              className="px-5 py-2.5 rounded-full border border-stone-300 text-xs font-bold text-stone-700 hover:bg-stone-50 transition"
            >
              Quay lại mua sắm
            </button>
            <button
              onClick={openAuthModal}
              className="px-6 py-2.5 rounded-full bg-crimson-700 hover:bg-crimson-800 text-white text-xs font-bold shadow-md transition"
            >
              Đăng nhập ngay
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (!cart.items || cart.items.length === 0) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-20 text-center animate-fadeIn">
        <span className="text-5xl block mb-4">🛒</span>
        <h2 className="font-serif-title font-bold text-2xl text-stone-900 mb-2">
          Giỏ hàng của bạn đang trống
        </h2>
        <p className="text-xs text-stone-500 mb-6">
          Vui lòng chọn ấn phẩm vào giỏ trước khi tiến hành thanh toán.
        </p>
        <button
          onClick={() => onNavigate('catalog')}
          className="px-6 py-2.5 rounded-full bg-crimson-700 hover:bg-crimson-800 text-white text-xs font-bold transition shadow"
        >
          Khám phá danh mục sách
        </button>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 py-8 animate-fadeIn">
      <h1 className="font-serif-title font-bold text-2xl md:text-3xl text-stone-900 mb-6">
        Tiến Hành Đặt Hàng & Thanh Toán
      </h1>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        {/* Left Column: Blocks 1, 2, 3 (8 cols) */}
        <div className="lg:col-span-8 space-y-6">
          <AddressSelector
            selectedAddressId={selectedAddressId}
            onSelectAddress={(id, addrObj) => {
              setSelectedAddressId(id);
              setSelectedAddressObj(addrObj);
            }}
          />

          <ShippingSelector
            shippingOptions={shippingOptions}
            selectedCarrier={selectedCarrier}
            onSelectCarrier={setSelectedCarrier}
            packageWeight={packageWeight}
          />

          <PaymentMethodSelector
            selectedMethod={paymentMethod}
            onSelectMethod={setPaymentMethod}
            isDroneSelected={selectedCarrier === 'HANOI_DRONE'}
          />
        </div>

        {/* Right Column: Voucher & Order Summary (4 cols) */}
        <div className="lg:col-span-4 space-y-6">
          <VoucherBox
            subtotal={cart.subtotal || 0}
            shippingFee={shippingFee}
            appliedVoucher={appliedVoucher}
            onApplyVoucher={handleApplyVoucher}
          />

          <OrderSummaryCard
            cart={cart}
            shippingFee={shippingFee}
            discountAmount={discountAmount}
            isSubmitting={isSubmitting}
            onSubmit={handleSubmitCheckout}
          />
        </div>
      </div>
    </div>
  );
}
