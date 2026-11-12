const API_BASE = '/api';

export async function request(endpoint, options = {}) {
  const headers = { ...options.headers };

  // Hỗ trợ phiên Quản trị độc lập: Ưu tiên bookhaven_admin_token cho các API /admin
  const adminToken = localStorage.getItem('bookhaven_admin_token');
  const userToken = localStorage.getItem('bookhaven_token');
  const token = endpoint.startsWith('/admin') && adminToken ? adminToken : userToken || adminToken;

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const userJson = localStorage.getItem('bookhaven_user');
  const adminJson = localStorage.getItem('bookhaven_admin_user');
  const activeUserJson = endpoint.startsWith('/admin') && adminJson ? adminJson : userJson || adminJson;

  if (token && activeUserJson) {
    try {
      const u = JSON.parse(activeUserJson);
      if (u && u.user_id) {
        headers['x-customer-id'] = u.user_id;
      }
    } catch {
      // ignore JSON parse error
    }
  } else {
    // Chưa đăng nhập: Cấp phát mã khách vãng lai (guest) riêng biệt cho từng trình duyệt
    let guestId = localStorage.getItem('bookhaven_guest_id');
    if (!guestId) {
      guestId = 'GUEST_' + Math.random().toString(36).substring(2, 10);
      localStorage.setItem('bookhaven_guest_id', guestId);
    }
    headers['x-customer-id'] = guestId;
  }

  const res = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers,
  });

  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    const errorMsg = data.detail || data.message || `Lỗi hệ thống (${res.status})`;
    throw new Error(errorMsg);
  }
  return data;
}

export function formatVND(amount) {
  return (amount || 0).toLocaleString('vi-VN') + ' đ';
}
