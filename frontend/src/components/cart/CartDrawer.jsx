import React from 'react';
import { X, ShoppingBag, ArrowRight } from 'lucide-react';
import { useCart } from '../../context/CartContext';
import { useAuth } from '../../context/AuthContext';
import { useToast } from '../../context/ToastContext';
import { formatVND } from '../../api';
import CartItemRow from './CartItemRow';
import DroneWeightGauge from './DroneWeightGauge';

export default function CartDrawer({ onNavigate }) {
  const { cart, isCartOpen, closeCart, updateQuantity, removeItem } = useCart();
  const { user, openAuthModal } = useAuth();
  const { showToast } = useToast();

  if (!isCartOpen) return null;

  const items = cart.items || [];
  const isEmpty = items.length === 0;

  const handleCheckoutClick = () => {
    closeCart();
    if (!user) {
      showToast('Vui lòng đăng nhập để tiến hành đặt hàng!', 'error');
      openAuthModal();
      return;
    }
    onNavigate('checkout');
  };

  return (
    <div className="fixed inset-0 z-50 overflow-hidden">
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-stone-950/50 backdrop-blur-sm transition-opacity"
        onClick={closeCart}
      ></div>

      <div className="fixed inset-y-0 right-0 max-w-full flex pl-10">
        <div className="w-screen max-w-md bg-white shadow-2xl flex flex-col">
          {/* Header */}
          <div className="p-5 border-b border-stone-200 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <ShoppingBag className="w-5 h-5 text-crimson-700" />
              <h2 className="font-serif-title font-bold text-base text-stone-900">
                Giỏ Hàng Của Bạn ({items.reduce((s, i) => s + i.quantity, 0)})
              </h2>
            </div>
            <button
              onClick={closeCart}
              className="p-1.5 rounded-full text-stone-400 hover:text-stone-700 hover:bg-stone-100 transition"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Cart Items List */}
          <div className="flex-1 overflow-y-auto p-5 space-y-4">
            {isEmpty ? (
              <div className="py-20 text-center text-stone-400 space-y-3">
                <span className="text-4xl block">🛒</span>
                <p className="text-xs font-semibold text-stone-600">Giỏ hàng của bạn đang trống</p>
                <button
                  onClick={closeCart}
                  className="px-4 py-2 rounded-full border border-stone-300 text-xs font-bold text-stone-700 hover:bg-stone-50"
                >
                  Tiếp tục chọn sách
                </button>
              </div>
            ) : (
              <>
                <div className="divide-y divide-stone-100">
                  {items.map((item) => (
                    <CartItemRow
                      key={item.edition_id}
                      item={item}
                      onUpdateQty={updateQuantity}
                      onRemove={removeItem}
                    />
                  ))}
                </div>

                {/* Drone Weight Gauge */}
                <DroneWeightGauge totalWeightGrams={cart.total_weight_grams || 0} />
              </>
            )}
          </div>

          {/* Footer Subtotal & Action */}
          {!isEmpty && (
            <div className="p-5 border-t border-stone-200 bg-stone-50 space-y-4">
              <div className="flex items-center justify-between text-xs">
                <span className="text-stone-500">Tạm tính giỏ hàng:</span>
                <span className="text-base font-bold text-crimson-700">
                  {formatVND(cart.subtotal)}
                </span>
              </div>

              <button
                onClick={handleCheckoutClick}
                className="w-full flex items-center justify-center gap-2 px-6 py-3 rounded-full bg-crimson-700 hover:bg-crimson-800 text-white text-xs font-bold transition shadow-lg hover:shadow-crimson-900/30"
              >
                <span>Tiến Hành Đặt Hàng</span>
                <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
