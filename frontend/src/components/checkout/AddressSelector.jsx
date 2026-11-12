import React, { useState, useEffect } from 'react';
import { MapPin, Plus, Check } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

export default function AddressSelector({ selectedAddressId, onSelectAddress }) {
  const { user } = useAuth();
  const [addresses, setAddresses] = useState([]);
  const [isAddingNew, setIsAddingNew] = useState(false);
  const [newName, setNewName] = useState('');
  const [newPhone, setNewPhone] = useState('');
  const [newAddress, setNewAddress] = useState('');

  // Tự động tải địa chỉ từ thông tin hồ sơ của tài khoản đang đăng nhập
  useEffect(() => {
    if (!user) {
      setAddresses([]);
      if (onSelectAddress) onSelectAddress('', null);
      return;
    }

    const list = [];
    if (user.shipping_address) {
      list.push({
        id: 'addr_profile_primary',
        name: user.full_name || 'Khách hàng BookHaven',
        phone: user.phone || '',
        address: user.shipping_address,
        isDefault: true,
      });
    }

    setAddresses(list);
    if (list.length > 0) {
      if (onSelectAddress) onSelectAddress(list[0].id, list[0]);
    } else {
      if (onSelectAddress) onSelectAddress('', null);
    }
  }, [user]);

  const handleAddNew = (e) => {
    e.preventDefault();
    if (!newName || !newPhone || !newAddress) return;

    const newAddrObj = {
      id: 'addr_' + Date.now(),
      name: newName,
      phone: newPhone,
      address: newAddress,
      isDefault: addresses.length === 0,
    };

    const updated = [...addresses, newAddrObj];
    setAddresses(updated);
    if (onSelectAddress) onSelectAddress(newAddrObj.id, newAddrObj);
    setIsAddingNew(false);
    setNewName('');
    setNewPhone('');
    setNewAddress('');
  };

  const handleSelect = (addr) => {
    if (onSelectAddress) onSelectAddress(addr.id, addr);
  };

  return (
    <div className="bg-white rounded-3xl border border-stone-200 p-6 shadow-sm space-y-4">
      <div className="flex items-center justify-between pb-3 border-b border-stone-100">
        <div className="flex items-center gap-2">
          <MapPin className="w-5 h-5 text-crimson-700" />
          <h3 className="font-serif-title font-bold text-base text-stone-900">
            1. Địa Chỉ Nhận Hàng
          </h3>
        </div>
        <button
          type="button"
          onClick={() => setIsAddingNew(!isAddingNew)}
          className="text-xs font-bold text-crimson-700 hover:text-crimson-800 flex items-center gap-1 transition"
        >
          <Plus className="w-3.5 h-3.5" />
          <span>{isAddingNew ? 'Hủy thêm' : 'Thêm địa chỉ mới'}</span>
        </button>
      </div>

      {/* Address List */}
      {addresses.length === 0 && !isAddingNew ? (
        <div className="py-6 text-center text-stone-500 text-xs bg-stone-50 rounded-2xl border border-dashed border-stone-300 space-y-2">
          <p className="font-medium text-stone-600">Bạn chưa lưu địa chỉ nhận hàng nào.</p>
          <button
            type="button"
            onClick={() => setIsAddingNew(true)}
            className="px-4 py-2 rounded-full bg-crimson-700 hover:bg-crimson-800 text-white font-bold transition shadow"
          >
            + Thêm địa chỉ nhận hàng ngay
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {addresses.map((addr) => {
            const isSelected = selectedAddressId === addr.id;
            return (
              <div
                key={addr.id}
                onClick={() => handleSelect(addr)}
                className={`p-4 rounded-2xl border text-left cursor-pointer transition relative flex flex-col justify-between ${
                  isSelected
                    ? 'border-crimson-700 bg-crimson-50/30 ring-2 ring-crimson-700/20'
                    : 'border-stone-200 bg-white hover:border-stone-300'
                }`}
              >
                <div>
                  <div className="flex items-center justify-between mb-1">
                    <span className="font-bold text-xs text-stone-900">{addr.name}</span>
                    <span className="text-[11px] text-stone-500 font-mono">{addr.phone}</span>
                  </div>
                  <p className="text-xs text-stone-600 line-clamp-2">{addr.address}</p>
                </div>

                <div className="flex items-center justify-between mt-3 pt-2 border-t border-stone-100">
                  {addr.isDefault && (
                    <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-stone-100 text-stone-600">
                      Mặc định
                    </span>
                  )}
                  {isSelected && (
                    <span className="text-xs font-bold text-crimson-700 flex items-center gap-1 ml-auto">
                      <Check className="w-3.5 h-3.5" /> Đang chọn
                    </span>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Add New Form */}
      {isAddingNew && (
        <form onSubmit={handleAddNew} className="p-4 rounded-2xl bg-stone-50 border border-stone-200 space-y-3">
          <h4 className="text-xs font-bold text-stone-800">Thêm Địa Chỉ Mới</h4>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <input
              type="text"
              placeholder="Họ và tên người nhận"
              value={newName}
              onChange={(e) => setNewName(e.target.value)}
              required
              className="bg-white border border-stone-300 rounded-xl px-3 py-2 text-xs text-stone-800 focus:outline-none focus:ring-2 focus:ring-crimson-700/20"
            />
            <input
              type="tel"
              placeholder="Số điện thoại"
              value={newPhone}
              onChange={(e) => setNewPhone(e.target.value)}
              required
              className="bg-white border border-stone-300 rounded-xl px-3 py-2 text-xs text-stone-800 focus:outline-none focus:ring-2 focus:ring-crimson-700/20"
            />
          </div>
          <input
            type="text"
            placeholder="Địa chỉ chi tiết (Số nhà, đường, quận/huyện, TP)"
            value={newAddress}
            onChange={(e) => setNewAddress(e.target.value)}
            required
            className="w-full bg-white border border-stone-300 rounded-xl px-3 py-2 text-xs text-stone-800 focus:outline-none focus:ring-2 focus:ring-crimson-700/20"
          />
          <button
            type="submit"
            className="px-4 py-2 rounded-xl bg-crimson-700 hover:bg-crimson-800 text-white text-xs font-bold transition shadow"
          >
            Lưu địa chỉ
          </button>
        </form>
      )}
    </div>
  );
}
