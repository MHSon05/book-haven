import React, { createContext, useContext, useState, useEffect, useCallback, useMemo } from 'react';
import { cartApi } from '../api';
import { useToast } from './ToastContext';
import { useAuth } from './AuthContext';

const CartContext = createContext(null);

export function CartProvider({ children }) {
  const { showToast } = useToast();
  const { token } = useAuth();
  const [cart, setCart] = useState({
    cart_id: '',
    items: [],
    subtotal: 0,
    total_weight_grams: 0,
  });
  const [isCartOpen, setIsCartOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const refreshCart = useCallback(async () => {
    try {
      const data = await cartApi.getCart();
      setCart(data);
    } catch (err) {
      console.error('Failed to load cart:', err);
    }
  }, []);

  useEffect(() => {
    refreshCart();
  }, [token, refreshCart]);

  const addToCart = useCallback(
    async (editionId, quantity = 1) => {
      setIsLoading(true);
      try {
        await cartApi.addToCart(editionId, quantity);
        await refreshCart();
        showToast(`Đã thêm ${quantity} cuốn vào giỏ hàng!`, 'success');
      } catch (err) {
        showToast(err.message, 'error');
        throw err;
      } finally {
        setIsLoading(false);
      }
    },
    [refreshCart, showToast]
  );

  const updateQuantity = useCallback(
    async (editionId, quantity) => {
      if (quantity <= 0) {
        return;
      }
      setIsLoading(true);
      try {
        await cartApi.updateCartItem(editionId, quantity);
        await refreshCart();
      } catch (err) {
        showToast(err.message, 'error');
      } finally {
        setIsLoading(false);
      }
    },
    [refreshCart, showToast]
  );

  const removeItem = useCallback(
    async (editionId) => {
      setIsLoading(true);
      try {
        await cartApi.removeCartItem(editionId);
        await refreshCart();
        showToast('Đã xóa ấn bản khỏi giỏ hàng', 'info');
      } catch (err) {
        showToast(err.message, 'error');
      } finally {
        setIsLoading(false);
      }
    },
    [refreshCart, showToast]
  );

  const openCart = useCallback(() => setIsCartOpen(true), []);
  const closeCart = useCallback(() => setIsCartOpen(false), []);

  const totalItemsCount = useMemo(() => {
    return (cart.items || []).reduce((sum, item) => sum + item.quantity, 0);
  }, [cart.items]);

  const packageWeight = useMemo(() => {
    return (cart.total_weight_grams || 0) + 150;
  }, [cart.total_weight_grams]);

  const isDroneEligible = useMemo(() => {
    return packageWeight <= 2000 && (cart.items || []).length > 0;
  }, [packageWeight, cart.items]);

  return (
    <CartContext.Provider
      value={{
        cart,
        totalItemsCount,
        packageWeight,
        isDroneEligible,
        isCartOpen,
        isLoading,
        openCart,
        closeCart,
        addToCart,
        updateQuantity,
        removeItem,
        refreshCart,
      }}
    >
      {children}
    </CartContext.Provider>
  );
}

export function useCart() {
  const ctx = useContext(CartContext);
  if (!ctx) throw new Error('useCart must be used within CartProvider');
  return ctx;
}
