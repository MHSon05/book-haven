import { request, formatVND } from './client';

export { formatVND };

// Auth API
export const authApi = {
  login: (username, password) =>
    request('/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password }),
    }),
  getMe: () => request('/auth/me'),
  getUserOrders: () => request('/auth/orders'),
};

// Catalog API
export const catalogApi = {
  getBooks: (params = {}) => {
    const qs = new URLSearchParams(params).toString();
    return request(`/books${qs ? '?' + qs : ''}`);
  },
  getBookDetail: (id) => request(`/books/${id}`),
  getCategories: () => request('/categories'),
};

// Search API
export const searchApi = {
  searchKeyword: (q, categoryId, binding) => {
    const p = new URLSearchParams();
    if (q) p.append('q', q);
    if (categoryId) p.append('category_id', categoryId);
    if (binding) p.append('binding_type', binding);
    return request(`/search/keyword?${p.toString()}`);
  },
  searchSemantic: (query) =>
    request('/search/semantic', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query, limit: 12 }),
    }),
  searchImage: (file) => {
    const formData = new FormData();
    formData.append('file', file);
    return request('/search/image', {
      method: 'POST',
      body: formData,
    });
  },
};

// Cart API
export const cartApi = {
  getCart: () => request('/cart'),
  addToCart: (editionId, quantity = 1) =>
    request('/cart/items', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ edition_id: editionId, quantity }),
    }),
  updateCartItem: (editionId, quantity) =>
    request(`/cart/items/${editionId}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ quantity }),
    }),
  removeCartItem: (editionId) =>
    request(`/cart/items/${editionId}`, {
      method: 'DELETE',
    }),
};

// Checkout & Shipping API
export const checkoutApi = {
  getShippingOptions: (cartId) => request(`/shipping/options?cart_id=${cartId || ''}`),
  checkout: (payload) =>
    request('/checkout', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    }),
};

// Payment & Orders API
export const paymentApi = {
  confirmPayment: (orderId, txnCode) =>
    request('/payments/confirm', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ order_id: orderId, transaction_code: txnCode }),
    }),
  getOrderStatus: (orderId) => request(`/orders/${orderId}/status`),
  markDelivered: (orderId) =>
    request(`/orders/${orderId}/delivered`, {
      method: 'POST',
    }),
};

// Chatbot API
export const chatbotApi = {
  sendMessage: (message) =>
    request('/chatbot/message', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message }),
    }),
};

// Admin API
export const adminApi = {
  getInventory: () => request('/admin/inventory'),
  restock: (editionId, quantity) =>
    request('/admin/inventory/restock', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ edition_id: editionId, quantity: parseInt(quantity, 10) }),
    }),
  getOrders: () => request('/admin/orders'),
  dispatchOrder: (orderId, carrier) =>
    request(`/admin/orders/${orderId}/dispatch`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ carrier }),
    }),
  markDelivered: (orderId) =>
    request(`/admin/orders/${orderId}/delivered`, {
      method: 'POST',
    }),
  getRevenueReport: () => request('/admin/reports/revenue'),
};
